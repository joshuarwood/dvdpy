# Copyright (C) 2025     Josh Wood
# 
# This portion is based on the friidump project written by:
#              Arep
#              https://github.com/bradenmcd/friidump
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

__version__ = "0.3"

SPC_INQUIRY    = 0x12
SBC_START_STOP = 0x1B
MMC_READ_12    = 0xA8

from .cextension import open_device, close_device, command_device

class dvd_device:
    def __init__(self, address):
        self.fd = open_device(address)

    def __del__(self):
        close_device(self.fd)

    def model_info(self):

        cmd = bytearray(12)
        buffer = bytearray(36)

        cmd[0] = SPC_INQUIRY
        cmd[4] = len(buffer)

        command_device(self.fd, cmd, buffer, 1, True)

        vendor = buffer[8:16].decode("utf-8")
        prod_id = buffer[16:32].decode("utf-8")
        prod_rev = buffer[32:36].decode("utf-8")

        return f"{vendor}/{prod_id}/{prod_rev}"
