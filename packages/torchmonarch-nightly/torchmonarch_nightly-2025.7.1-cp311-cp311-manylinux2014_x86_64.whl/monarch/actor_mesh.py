# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import collections
import contextvars
import functools
import inspect

import itertools
import logging
import random
import sys
import traceback

from dataclasses import dataclass
from traceback import extract_tb, StackSummary
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    cast,
    Concatenate,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    ParamSpec,
    Tuple,
    Type,
    TYPE_CHECKING,
    TypeVar,
)

import monarch
from monarch import ActorFuture as Future
from monarch._rust_bindings.hyperactor_extension.telemetry import enter_span, exit_span

from monarch._rust_bindings.monarch_hyperactor.actor import PanicFlag, PythonMessage
from monarch._rust_bindings.monarch_hyperactor.actor_mesh import PythonActorMesh
from monarch._rust_bindings.monarch_hyperactor.mailbox import (
    Mailbox,
    OncePortReceiver,
    OncePortRef,
    PortReceiver as HyPortReceiver,
    PortRef,
)
from monarch._rust_bindings.monarch_hyperactor.proc import ActorId
from monarch._rust_bindings.monarch_hyperactor.shape import Point as HyPoint, Shape

from monarch.common.pickle_flatten import flatten, unflatten
from monarch.common.shape import MeshTrait, NDSlice
from monarch.pdb_wrapper import remote_breakpointhook

if TYPE_CHECKING:
    from monarch.debugger import DebugClient

logger: logging.Logger = logging.getLogger(__name__)

Allocator = monarch.ProcessAllocator | monarch.LocalAllocator

try:
    from __manifest__ import fbmake  # noqa

    IN_PAR = True
except ImportError:
    IN_PAR = False

T1 = TypeVar("T1")
T2 = TypeVar("T2")


class Point(HyPoint, collections.abc.Mapping):
    pass


@dataclass
class MonarchContext:
    mailbox: Mailbox
    proc_id: str
    point: Point

    @staticmethod
    def get() -> "MonarchContext":
        return _context.get()


_context: contextvars.ContextVar[MonarchContext] = contextvars.ContextVar(
    "monarch.actor_mesh._context"
)


T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")
A = TypeVar("A")

# keep this load balancing deterministic, but
# equally distributed.
_load_balancing_seed = random.Random(4)


Selection = Literal["all", "choose"]  # TODO: replace with real selection objects


# standin class for whatever is the serializable python object we use
# to name an actor mesh. Hacked up today because ActorMesh
# isn't plumbed to non-clients
class _ActorMeshRefImpl:
    def __init__(
        self,
        mailbox: Mailbox,
        hy_actor_mesh: Optional[PythonActorMesh],
        shape: Shape,
        actor_ids: List[ActorId],
    ) -> None:
        self._mailbox = mailbox
        self._actor_mesh = hy_actor_mesh
        self._shape = shape
        self._please_replace_me_actor_ids = actor_ids

    @staticmethod
    def from_hyperactor_mesh(
        mailbox: Mailbox, hy_actor_mesh: PythonActorMesh
    ) -> "_ActorMeshRefImpl":
        shape: Shape = hy_actor_mesh.shape
        return _ActorMeshRefImpl(
            mailbox,
            hy_actor_mesh,
            hy_actor_mesh.shape,
            [cast(ActorId, hy_actor_mesh.get(i)) for i in range(len(shape))],
        )

    @staticmethod
    def from_actor_id(mailbox: Mailbox, actor_id: ActorId) -> "_ActorMeshRefImpl":
        return _ActorMeshRefImpl(mailbox, None, singleton_shape, [actor_id])

    @staticmethod
    def from_actor_ref_with_shape(
        ref: "_ActorMeshRefImpl", shape: Shape
    ) -> "_ActorMeshRefImpl":
        return _ActorMeshRefImpl(
            ref._mailbox, None, shape, ref._please_replace_me_actor_ids
        )

    def __getstate__(
        self,
    ) -> Tuple[Shape, List[ActorId], Mailbox]:
        return self._shape, self._please_replace_me_actor_ids, self._mailbox

    def __setstate__(
        self,
        state: Tuple[Shape, List[ActorId], Mailbox],
    ) -> None:
        self._actor_mesh = None
        self._shape, self._please_replace_me_actor_ids, self._mailbox = state

    def send(self, rank: int, message: PythonMessage) -> None:
        actor = self._please_replace_me_actor_ids[rank]
        self._mailbox.post(actor, message)

    def cast(
        self,
        message: PythonMessage,
        selection: Selection,
    ) -> None:
        # TODO: use the actual actor mesh when available. We cannot currently use it
        # directly because we risk bifurcating the message delivery paths from the same
        # client, since slicing the mesh will produce a reference, which calls actors
        # directly. The reason these paths are bifurcated is that actor meshes will
        # use multicasting, while direct actor comms do not. Separately we need to decide
        # whether actor meshes are ordered with actor references.
        #
        # The fix is to provide a first-class reference into Python, and always call "cast"
        # on it, including for load balanced requests.
        if selection == "choose":
            idx = _load_balancing_seed.randrange(len(self._shape))
            actor_rank = self._shape.ndslice[idx]
            self._mailbox.post(self._please_replace_me_actor_ids[actor_rank], message)
            return
        elif selection == "all":
            # replace me with actual remote actor mesh
            call_shape = Shape(
                self._shape.labels, NDSlice.new_row_major(self._shape.ndslice.sizes)
            )
            for i, rank in enumerate(self._shape.ranks()):
                self._mailbox.post_cast(
                    self._please_replace_me_actor_ids[rank],
                    i,
                    call_shape,
                    message,
                )
        else:
            raise ValueError(f"invalid selection: {selection}")

    def __len__(self) -> int:
        return len(self._shape)


class Endpoint(Generic[P, R]):
    def __init__(
        self,
        actor_mesh_ref: _ActorMeshRefImpl,
        name: str,
        impl: Callable[Concatenate[Any, P], Awaitable[R]],
        mailbox: Mailbox,
    ) -> None:
        self._actor_mesh = actor_mesh_ref
        self._name = name
        self._signature: inspect.Signature = inspect.signature(impl)
        self._mailbox = mailbox

    # the following are all 'adverbs' or different ways to handle the
    # return values of this endpoint. Adverbs should only ever take *args, **kwargs
    # of the original call. If we want to add syntax sugar for something that needs additional
    # arguments, it should be implemented as function indepdendent of endpoint like `send`
    # and `Accumulator`
    def choose(self, *args: P.args, **kwargs: P.kwargs) -> Future[R]:
        """
        Load balanced sends a message to one chosen actor and awaits a result.

        Load balanced RPC-style entrypoint for request/response messaging.
        """
        p: Port[R]
        r: PortReceiver[R]
        p, r = port(self, once=True)
        # pyre-ignore
        send(self, args, kwargs, port=p, selection="choose")
        return r.recv()

    def call_one(self, *args: P.args, **kwargs: P.kwargs) -> Future[R]:
        if len(self._actor_mesh) != 1:
            raise ValueError(
                f"Can only use 'call_one' on a single Actor but this actor has shape {self._actor_mesh._shape}"
            )
        return self.choose(*args, **kwargs)

    def call(self, *args: P.args, **kwargs: P.kwargs) -> "Future[ValueMesh[R]]":
        p: Port[R]
        r: RankedPortReceiver[R]
        p, r = ranked_port(self)
        # pyre-ignore
        send(self, args, kwargs, port=p)

        async def process() -> ValueMesh[R]:
            results: List[R] = [None] * len(self._actor_mesh)  # pyre-fixme[9]
            for _ in range(len(self._actor_mesh)):
                rank, value = await r.recv()
                results[rank] = value
            call_shape = Shape(
                self._actor_mesh._shape.labels,
                NDSlice.new_row_major(self._actor_mesh._shape.ndslice.sizes),
            )
            return ValueMesh(call_shape, results)

        def process_blocking() -> ValueMesh[R]:
            results: List[R] = [None] * len(self._actor_mesh)  # pyre-fixme[9]
            for _ in range(len(self._actor_mesh)):
                rank, value = r.recv().get()
                results[rank] = value
            call_shape = Shape(
                self._actor_mesh._shape.labels,
                NDSlice.new_row_major(self._actor_mesh._shape.ndslice.sizes),
            )
            return ValueMesh(call_shape, results)

        return Future(process, process_blocking)

    async def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncGenerator[R, R]:
        """
        Broadcasts to all actors and yields their responses as a stream / generator.

        This enables processing results from multiple actors incrementally as
        they become available. Returns an async generator of response values.
        """
        p, r = port(self)
        # pyre-ignore
        send(self, args, kwargs, port=p)
        for _ in range(len(self._actor_mesh)):
            yield await r.recv()

    def broadcast(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Fire-and-forget broadcast to all actors without waiting for actors to
        acknowledge receipt.

        In other words, the return of this method does not guarrantee the
        delivery of the message.
        """
        # pyre-ignore
        send(self, args, kwargs)


class Accumulator(Generic[P, R, A]):
    def __init__(
        self, endpoint: Endpoint[P, R], identity: A, combine: Callable[[A, R], A]
    ) -> None:
        self._endpoint: Endpoint[P, R] = endpoint
        self._identity: A = identity
        self._combine: Callable[[A, R], A] = combine

    def accumulate(self, *args: P.args, **kwargs: P.kwargs) -> "Future[A]":
        gen: AsyncGenerator[R, R] = self._endpoint.stream(*args, **kwargs)

        async def impl() -> A:
            value = self._identity
            async for x in gen:
                value = self._combine(value, x)
            return value

        return Future(impl)


class ValueMesh(MeshTrait, Generic[R]):
    """
    Container of return values, indexed by rank.
    """

    def __init__(self, shape: Shape, values: List[R]) -> None:
        self._shape = shape
        self._values = values

    def _new_with_shape(self, shape: Shape) -> "ValueMesh[R]":
        return ValueMesh(shape, self._values)

    def item(self, **kwargs) -> R:
        coordinates = [kwargs.pop(label) for label in self._labels]
        if kwargs:
            raise KeyError(f"item has extra dimensions: {list(kwargs.keys())}")

        return self._values[self._ndslice.nditem(coordinates)]

    def __iter__(self):
        for rank in self._shape.ranks():
            yield Point(rank, self._shape), self._values[rank]

    def __len__(self) -> int:
        return len(self._shape)

    def __repr__(self) -> str:
        return f"ValueMesh({self._shape})"

    @property
    def _ndslice(self) -> NDSlice:
        return self._shape.ndslice

    @property
    def _labels(self) -> Iterable[str]:
        return self._shape.labels


def send(
    endpoint: Endpoint[P, R],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    port: "Optional[Port]" = None,
    selection: Selection = "all",
) -> None:
    """
    Fire-and-forget broadcast invocation of the endpoint across all actors in the mesh.

    This sends the message to all actors but does not wait for any result.
    """
    endpoint._signature.bind(None, *args, **kwargs)
    message = PythonMessage(
        endpoint._name,
        _pickle((args, kwargs)),
        None if port is None else port._port_ref,
        None,
    )
    endpoint._actor_mesh.cast(message, selection)


class EndpointProperty(Generic[P, R]):
    def __init__(self, method: Callable[Concatenate[Any, P], Awaitable[R]]) -> None:
        self._method = method

    def __get__(self, instance, owner) -> Endpoint[P, R]:
        # this is a total lie, but we have to actually
        # recognize this was defined as an endpoint,
        # and also lookup the method
        return cast(Endpoint[P, R], self)


def endpoint(
    method: Callable[Concatenate[Any, P], Awaitable[R]],
) -> EndpointProperty[P, R]:
    return EndpointProperty(method)


class Port(Generic[R]):
    def __init__(
        self, port_ref: PortRef | OncePortRef, mailbox: Mailbox, rank: Optional[int]
    ) -> None:
        self._port_ref = port_ref
        self._mailbox = mailbox
        self._rank = rank

    def send(self, method: str, obj: R) -> None:
        self._port_ref.send(
            self._mailbox,
            PythonMessage(method, _pickle(obj), None, self._rank),
        )


# advance lower-level API for sending messages. This is intentially
# not part of the Endpoint API because they way it accepts arguments
# and handles concerns is different.
def port(
    endpoint: Endpoint[P, R], once: bool = False
) -> Tuple["Port[R]", "PortReceiver[R]"]:
    handle, receiver = (
        endpoint._mailbox.open_once_port() if once else endpoint._mailbox.open_port()
    )
    port_ref: PortRef | OncePortRef = handle.bind()
    return Port(port_ref, endpoint._mailbox, rank=None), PortReceiver(
        endpoint._mailbox, receiver
    )


def ranked_port(
    endpoint: Endpoint[P, R], once: bool = False
) -> Tuple["Port[R]", "RankedPortReceiver[R]"]:
    p, receiver = port(endpoint, once)
    return p, RankedPortReceiver[R](receiver._mailbox, receiver._receiver)


class PortReceiver(Generic[R]):
    def __init__(
        self,
        mailbox: Mailbox,
        receiver: HyPortReceiver | OncePortReceiver,
    ) -> None:
        self._mailbox: Mailbox = mailbox
        self._receiver: HyPortReceiver | OncePortReceiver = receiver

    async def _recv(self) -> R:
        return self._process(await self._receiver.recv())

    def _blocking_recv(self) -> R:
        return self._process(self._receiver.blocking_recv())

    def _process(self, msg: PythonMessage) -> R:
        # TODO: Try to do something more structured than a cast here
        payload = cast(R, _unpickle(msg.message, self._mailbox))
        if msg.method == "result":
            return payload
        else:
            assert msg.method == "exception"
            # pyre-ignore
            raise payload

    def recv(self) -> "Future[R]":
        return Future(lambda: self._recv(), self._blocking_recv)


class RankedPortReceiver(PortReceiver[Tuple[int, R]]):
    def _process(self, msg: PythonMessage) -> Tuple[int, R]:
        if msg.rank is None:
            raise ValueError("RankedPort receiver got a message without a rank")
        return msg.rank, super()._process(msg)


singleton_shape = Shape([], NDSlice(offset=0, sizes=[], strides=[]))


class _Actor:
    """
    This is the message handling implementation of a Python actor.

    The layering goes:
        Rust `PythonActor` -> `_Actor` -> user-provided `Actor` instance

    Messages are received from the Rust backend, and forwarded to the `handle`
    methods on this class.

    This class wraps the actual `Actor` instance provided by the user, and
    routes messages to it, managing argument serialization/deserialization and
    error handling.
    """

    def __init__(self) -> None:
        self.instance: object | None = None

    async def handle(
        self, mailbox: Mailbox, message: PythonMessage, panic_flag: PanicFlag
    ) -> None:
        return await self.handle_cast(mailbox, 0, singleton_shape, message, panic_flag)

    async def handle_cast(
        self,
        mailbox: Mailbox,
        rank: int,
        shape: Shape,
        message: PythonMessage,
        panic_flag: PanicFlag,
    ) -> None:
        port = (
            Port(message.response_port, mailbox, rank)
            if message.response_port
            else None
        )
        try:
            ctx: MonarchContext = MonarchContext(
                mailbox, mailbox.actor_id.proc_id, Point(rank, shape)
            )
            _context.set(ctx)

            args, kwargs = _unpickle(message.message, mailbox)

            if message.method == "__init__":
                Class, *args = args
                self.instance = Class(*args, **kwargs)
                return None

            if self.instance is None:
                # This could happen because of the following reasons. Both
                # indicates a possible bug in the framework:
                # 1. the execution of the previous message for "__init__" failed,
                #    but that error is not surfaced to the caller.
                #      - TODO(T229200522): there is a known bug. fix it.
                # 2. this message is delivered to this actor before the previous
                #    message of "__init__" is delivered. Out-of-order delivery
                #    should never happen. It indicates either a bug in the
                #    message delivery mechanism, or the framework accidentally
                #    mixed the usage of cast and direct send.
                raise AssertionError(
                    f"""
                    actor object is missing when executing method {message.method}
                    on actor {mailbox.actor_id}
                    """
                )
            the_method = getattr(self.instance, message.method)._method

            if inspect.iscoroutinefunction(the_method):

                async def instrumented():
                    enter_span(
                        the_method.__module__,
                        message.method,
                        str(ctx.mailbox.actor_id),
                    )
                    try:
                        result = await the_method(self.instance, *args, **kwargs)
                    except Exception as e:
                        logging.critical(
                            "Unahndled exception in actor endpoint",
                            exc_info=e,
                        )
                        raise e
                    exit_span()
                    return result

                result = await instrumented()
            else:
                enter_span(
                    the_method.__module__, message.method, str(ctx.mailbox.actor_id)
                )
                result = the_method(self.instance, *args, **kwargs)
                exit_span()

            if port is not None:
                port.send("result", result)
        except Exception as e:
            traceback.print_exc()
            s = ActorError(e)

            # The exception is delivered to exactly one of:
            # (1) our caller, (2) our supervisor
            if port is not None:
                port.send("exception", s)
            else:
                raise s from None
        except BaseException as e:
            # A BaseException can be thrown in the case of a Rust panic.
            # In this case, we need a way to signal the panic to the Rust side.
            # See [Panics in async endpoints]
            try:
                panic_flag.signal_panic(e)
            except Exception:
                # The channel might be closed if the Rust side has already detected the error
                pass
            raise


def _is_mailbox(x: object) -> bool:
    return isinstance(x, Mailbox)


def _pickle(obj: object) -> bytes:
    _, msg = flatten(obj, _is_mailbox)
    return msg


def _unpickle(data: bytes, mailbox: Mailbox) -> Any:
    # regardless of the mailboxes of the remote objects
    # they all become the local mailbox.
    return unflatten(data, itertools.repeat(mailbox))


class Actor(MeshTrait):
    @functools.cached_property
    def logger(cls) -> logging.Logger:
        lgr = logging.getLogger(cls.__class__.__name__)
        lgr.setLevel(logging.DEBUG)
        return lgr

    @property
    def _ndslice(self) -> NDSlice:
        raise NotImplementedError(
            "actor implementations are not meshes, but we can't convince the typechecker of it..."
        )

    @property
    def _labels(self) -> Tuple[str, ...]:
        raise NotImplementedError(
            "actor implementations are not meshes, but we can't convince the typechecker of it..."
        )

    def _new_with_shape(self, shape: Shape) -> "ActorMeshRef":
        raise NotImplementedError(
            "actor implementations are not meshes, but we can't convince the typechecker of it..."
        )

    @endpoint  # pyre-ignore
    def _set_debug_client(self, client: "DebugClient") -> None:
        point = MonarchContext.get().point
        # For some reason, using a lambda instead of functools.partial
        # confuses the pdb wrapper implementation.
        sys.breakpointhook = functools.partial(  # pyre-ignore
            remote_breakpointhook,
            point.rank,
            point.shape.coordinates(point.rank),
            MonarchContext.get().mailbox.actor_id,
            client,
        )


class ActorMeshRef(MeshTrait, Generic[T]):
    def __init__(
        self, Class: Type[T], actor_mesh_ref: _ActorMeshRefImpl, mailbox: Mailbox
    ) -> None:
        self.__name__: str = Class.__name__
        self._class: Type[T] = Class
        self._actor_mesh_ref: _ActorMeshRefImpl = actor_mesh_ref
        self._mailbox: Mailbox = mailbox
        for attr_name in dir(self._class):
            attr_value = getattr(self._class, attr_name, None)
            if isinstance(attr_value, EndpointProperty):
                setattr(
                    self,
                    attr_name,
                    Endpoint(
                        self._actor_mesh_ref,
                        attr_name,
                        attr_value._method,
                        self._mailbox,
                    ),
                )

    def __getattr__(self, name: str) -> Any:
        # This method is called when an attribute is not found
        # For linting purposes, we need to tell the type checker that any attribute
        # could be an endpoint that's dynamically added at runtime
        # At runtime, we still want to raise AttributeError for truly missing attributes

        # Check if this is a method on the underlying class
        if hasattr(self._class, name):
            attr = getattr(self._class, name)
            if isinstance(attr, EndpointProperty):
                # Dynamically create the endpoint
                endpoint = Endpoint(
                    self._actor_mesh_ref,
                    name,
                    attr._method,
                    self._mailbox,
                )
                # Cache it for future use
                setattr(self, name, endpoint)
                return endpoint

        # If we get here, it's truly not found
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def _create(
        self,
        args: Iterable[Any],
        kwargs: Dict[str, Any],
    ) -> None:
        async def null_func(*_args: Iterable[Any], **_kwargs: Dict[str, Any]) -> None:
            return None

        ep = Endpoint(
            self._actor_mesh_ref,
            "__init__",
            null_func,
            self._mailbox,
        )
        send(ep, (self._class, *args), kwargs)

    def __reduce_ex__(
        self, protocol: ...
    ) -> "Tuple[Type[ActorMeshRef], Tuple[Any, ...]]":
        return ActorMeshRef, (
            self._class,
            self._actor_mesh_ref,
            self._mailbox,
        )

    @property
    def _ndslice(self) -> NDSlice:
        return self._actor_mesh_ref._shape.ndslice

    @property
    def _labels(self) -> Iterable[str]:
        return self._actor_mesh_ref._shape.labels

    def _new_with_shape(self, shape: Shape) -> "ActorMeshRef":
        return ActorMeshRef(
            self._class,
            _ActorMeshRefImpl.from_actor_ref_with_shape(self._actor_mesh_ref, shape),
            self._mailbox,
        )

    def __repr__(self) -> str:
        return f"ActorMeshRef(class={self._class}, shape={self._actor_mesh_ref._shape})"


class ActorError(Exception):
    """
    Deterministic problem with the user's code.
    For example, an OOM resulting in trying to allocate too much GPU memory, or violating
    some invariant enforced by the various APIs.
    """

    def __init__(
        self,
        exception: Exception,
        message: str = "A remote actor call has failed asynchronously.",
    ) -> None:
        self.exception = exception
        self.actor_mesh_ref_frames: StackSummary = extract_tb(exception.__traceback__)
        self.message = message

    def __str__(self) -> str:
        exe = str(self.exception)
        actor_mesh_ref_tb = "".join(traceback.format_list(self.actor_mesh_ref_frames))
        return (
            f"{self.message}\n"
            f"Traceback of where the remote call failed (most recent call last):\n{actor_mesh_ref_tb}{type(self.exception).__name__}: {exe}"
        )


def current_actor_name() -> str:
    return str(MonarchContext.get().mailbox.actor_id)


def current_rank() -> Point:
    ctx = MonarchContext.get()
    return ctx.point


def current_size() -> Dict[str, int]:
    ctx = MonarchContext.get()
    return dict(zip(ctx.point.shape.labels, ctx.point.shape.ndslice.sizes))
