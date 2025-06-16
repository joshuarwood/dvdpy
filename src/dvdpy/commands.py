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

SECTOR_SIZE = 2048
RAW_SECTOR_SIZE = 2064
SECTORS_PER_BLOCK = 16

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

def read_sectors(fd: int, sector: int, sectors: int = SECTORS_PER_BLOCK,
                 streaming: bool = False, timeout: int = 1, verbose: bool = False):
    """ Write sectors to the drive cache

    Args:
        fd (int): file descriptor
        sector (int): starting sector
        sectors (int, optional): number of sectors to read (default: 16)
        streaming (int, optional): use streaming mode when True (default: False)
        timeout (int, optional): command timeout in seconds (default: 1)
        verbose (bool, optional): set to True to print more info (default: False)

    Returns:
        (int): command status (-1 means fail)
    """
    cmd = bytearray(12)
    buffer = bytearray(SECTORS_PER_BLOCK * RAW_SECTOR_SIZE)
    sectors = SECTORS_PER_BLOCK

    cmd[0] = MMC_READ_12
    cmd[1] = 0 if streaming else 0x08 # Force Unit Access bit
    cmd[2] =  (sector & 0xFF000000) >> 24 # sector MSB
    cmd[3] =  (sector & 0x00FF0000) >> 16
    cmd[4] =  (sector & 0x0000FF00) >> 8
    cmd[5] =  (sector & 0x000000FF)       # sector LSB
    cmd[6] = (sectors & 0xFF000000) >> 24 # sectors MSB
    cmd[7] = (sectors & 0x00FF0000) >> 16
    cmd[8] = (sectors & 0x0000FF00) >> 8
    cmd[9] = (sectors & 0x000000FF)       # sectors LSB
    cmd[10] = 0x80 if streaming else 0    # streaming bit

    return cextension.command_device(fd, cmd, buffer, timeout, verbose)
