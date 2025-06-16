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

SPC_INQUIRY    = 0x12
SBC_START_STOP = 0x1B
MMC_READ_12    = 0xA8

from . import cextension

def drive_info(fd: int, timeout: int = 1, verbose: bool = False):
    """ Retrieve drive model info

    Args:
        fd (int): file descriptor
        timeout (int): command timeout in seconds
        verbose (bool): set to True to print more info

    Returns:
        (str): model string
    """
    cmd = bytearray(12)
    buffer = bytearray(36)

    cmd[0] = SPC_INQUIRY
    cmd[4] = len(buffer)

    status = cextension.command_device(fd, cmd, buffer, timeout, verbose)

    vendor = buffer[8:16].decode("utf-8")
    prod_id = buffer[16:32].decode("utf-8")
    prod_rev = buffer[32:36].decode("utf-8")

    return f"{vendor}/{prod_id}/{prod_rev}"

def drive_spin(fd: int, state: bool, timeout: int = 1, verbose: bool = False):
    """ Set the drive spin state. A spin state of True indicates the
    disc is spinning whereas False means the disc is stopped.

    Args:
        fd (int): file descriptor
        state (bool): spin state
        timeout (int): command timeout in seconds
        verbose (bool): set to True to print more info

    Returns:
        (int): command status (-1 means fail)
    """
    if isinstance(state, bool) == False:
        raise TypeError("Spin state must be True or False")

    cmd = bytearray(12)
    buffer = bytearray(8)

    cmd[0] = SBC_START_STOP
    cmd[4] = int(state)

    return cextension.command_device(fd, cmd, buffer, timeout, verbose)
