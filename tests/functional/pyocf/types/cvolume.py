#
# Copyright(c) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#

from ctypes import (
    c_int,
    c_uint32,
    c_uint64,
    c_void_p,
    c_char_p,
    byref,
    cast,
    create_string_buffer,
)

from ..ocf import OcfLib
from .ctx import OcfCtx
from .io import Io, IoDir
from .queue import Queue
from .shared import OcfError, Uuid


class CVolume:
    def __init__(self, ctx):
        self.lib = OcfLib.getInstance()
        self.ctx = ctx
        self.cvol = c_void_p()

    def __enter__(self):
        ret = lib.ocf_composite_volume_create(byref(self.cvol), self.ctx.ctx_handle)

        if ret != 0:
            raise OcfError("Composite volume creation failed", ret)

        return self

    def __exit__(self, *args):
        self.lib.ocf_composite_volume_destroy(self.cvol)

    def add(self, vol):
        uuid = Uuid(
            _data=cast(create_string_buffer(vol.uuid.encode("ascii")), c_char_p),
            _size=len(vol.uuid) + 1,
        )

        volume = c_void_p()
        ocf_vol_type = self.ctx.ocf_volume_type[type(vol)]

        ret = self.lib.ocf_composite_volume_add(
            self.cvol, ocf_vol_type, byref(uuid), c_void_p()
        )

        if ret != 0:
            raise OcfError("Failed to add volume to a composite volume", ret)

    def new_io(
        self,
        queue: Queue,
        addr: int,
        length: int,
        direction: IoDir,
        io_class: int,
        flags: int,
    ):
        io = self.lib.ocf_volume_new_io(
            self.cvol,
            queue.handle if queue else c_void_p(),
            addr,
            length,
            direction,
            io_class,
            flags,
        )
        return Io.from_pointer(io)

    def open(self):
        self.lib.ocf_volume_open(self.cvol, c_void_p())

    def close(self):
        self.lib.ocf_volume_close(self.cvol)


lib = OcfLib.getInstance()
lib.ocf_composite_volume_create.restype = c_int
lib.ocf_composite_volume_create.argtypes = [c_void_p, c_void_p]
lib.ocf_composite_volume_destroy.argtypes = [c_void_p]
lib.ocf_composite_volume_add.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
lib.ocf_composite_volume_add.restype = c_int
lib.ocf_volume_new_io.argtypes = [
    c_void_p,
    c_void_p,
    c_uint64,
    c_uint32,
    c_uint32,
    c_uint32,
    c_uint64,
]
lib.ocf_volume_new_io.restype = c_void_p
lib.ocf_volume_open.restype = c_int
lib.ocf_volume_open.argtypes = [c_void_p, c_void_p]
lib.ocf_volume_close.argtypes = [c_void_p]
