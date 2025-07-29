# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import monarch
import pytest
import torch
from monarch.mesh_controller import spawn_tensor_engine
from monarch.proc_mesh import proc_mesh


two_gpu = pytest.mark.skipif(
    torch.cuda.device_count() < 2,
    reason="Not enough GPUs, this test requires at least 2 GPUs",
)


@two_gpu
def test_tensor_engine() -> None:
    pm = proc_mesh(gpus=2).get()

    dm = spawn_tensor_engine(pm)
    with dm.activate():
        r = monarch.inspect(2 * torch.zeros(3, 4))

    fm = dm.flatten("all")
    with fm.activate():
        f = monarch.inspect(2 * torch.zeros(3, 4), all=1)

    assert torch.allclose(torch.zeros(3, 4), r)
    assert torch.allclose(torch.zeros(3, 4), f)

    dm.exit()


@two_gpu
def test_proc_mesh_tensor_engine() -> None:
    pm = proc_mesh(gpus=2).get()
    with pm.activate():
        f = 10 * pm.rank_tensor("gpus").cuda()
        a = monarch.inspect(f, hosts=0, gpus=0)
        b = monarch.inspect(f, hosts=0, gpus=1)

    one = pm.slice(gpus=1)
    with one.activate():
        sliced_b = monarch.slice_mesh(f, gpus=1).to_mesh(one)
        c = monarch.inspect(sliced_b * 10)
    assert a == 0
    assert b == 10
    assert c == 100
