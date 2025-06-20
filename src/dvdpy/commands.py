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

HITACHI_MEM_BASE = 0x80000000

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
    cmd = bytes([
        SPC_INQUIRY, #  0. model inquiry command
        0,           #  1. empty
        0,           #  2. empty
        0,           #  3. empty
        36,          #  4. return buffer length
        0,           #  5. empty
        0,           #  6. empty
        0,           #  7. empty
        0,           #  8. empty
        0,           #  9. empty
        0,           # 10. empty
        0            # 11. empty
    ])

    status, buffer = cextension.command_device(fd, cmd, cmd[4], timeout, verbose)

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

    cmd = bytes([
        SBC_START_STOP, #  0. start/stop command
        0,              #  1. empty
        0,              #  2. empty
        0,              #  3. empty
        int(state),     #  4. start = 1, stop = 0
        0,              #  5. empty
        0,              #  6. empty
        0,              #  7. empty
        0,              #  8. empty
        0,              #  9. empty
        0,              # 10. empty
        0               # 11. empty
    ])

    status, buffer = cextension.command_device(fd, cmd, 8, timeout, verbose)

    return status

def read_sectors(fd: int, sector: int, sectors: int = SECTORS_PER_BLOCK,
                 streaming: bool = False, timeout: int = 1, verbose: bool = False):
    """ Read 2048 byte user data sectors from the drive. These do not
    include the first 12 bytes (ID, IED, CPR_MAI) or last 4 bytes (EDC)
    found in raw sectors.

    Args:
        fd (int): file descriptor
        sector (int): starting sector
        sectors (int, optional): number of sectors to read (default: 16)
        streaming (int, optional): use streaming mode when True (default: False)
        timeout (int, optional): command timeout in seconds (default: 1)
        verbose (bool, optional): set to True to print more info (default: False)

    Returns:
        (int, bytearray): tuple with (command status, buffer)
    """
    cmd = bytes([
        MMC_READ_12,                  #  0. read command
        0 if streaming else 0x08,     #  1. force unit access bit
        (sector & 0xFF000000) >> 24,  #  2. sector MSB
        (sector & 0x00FF0000) >> 16,  #  3. sector continued
        (sector & 0x0000FF00) >> 8,   #  4. sector continued
        (sector & 0x000000FF),        #  5. sector LSB
        (sectors & 0xFF000000) >> 24, #  6. sectors MSB
        (sectors & 0x00FF0000) >> 16, #  7. sectors continued
        (sectors & 0x0000FF00) >> 8,  #  8. sectors continued
        (sectors & 0x000000FF),       #  9. sectors LSB
        0x80 if streaming else 0,     # 10. streaming bit
        0                             # 11. empty
    ])

    return cextension.command_device(fd, cmd, sectors * SECTOR_SIZE, timeout, verbose)

def read_raw_bytes(fd: int, offset: int, nbyte: int = RAW_SECTOR_SIZE,
                   timeout: int = 1, verbose: bool = False):
    """ Reads raw bytes from the drive cache. This cache consists of
    2064 byte raw sectors with ID, IED, CPR_MAI, USER DATA, and EDC fields.

    Note you must do the following before using this command:
      1. Execute a read_sectors() command with streaming = True to fill the cache.
      2. Ensure you're running the command with root privileges.
         The command will not work with regular user privileges.

    Args:
        fd (int): file descriptor
        offset (int): starting memory offset within cache
        nbyte (int, optional): number of memory bytes to read starting from offset (default: 2064)
        timeout (int, optional): command timeout in seconds (default: 1)
        verbose (bool, optional): set to True to print more info (default: False)

    Returns:
        (int, bytearray): tuple with (command status, buffer)
    """
    address = HITACHI_MEM_BASE + offset;

    if nbyte <= 0 or nbyte > 65535:
	    raise ValueError("invalid nbyte (valid: 1 - 65535)")

    # Note: bytes 1-3 = HIT which is likely short for HITACHI
    cmd = bytes([
        0xE7,                         #  0. vendor specific command (discovered by DaveX)
        0x48,                         #  1. H
        0x49,                         #  2. I
        0x54,                         #  3. T
        0x01,                         #  4. read MCU memory sub-command
        0,                            #  5. empty
        (address & 0xFF000000) >> 24, #  6. address MSB
        (address & 0x00FF0000) >> 16, #  7. address continued
        (address & 0x0000FF00) >> 8,  #  8. address continued
        (address & 0x000000FF),       #  9. address LSB
        (nbyte & 0xFF00) >> 8,        # 10. nbyte MSB
        (nbyte & 0x00FF)              # 11. nbyte LSB
    ])

    return cextension.command_device(fd, cmd, nbyte, timeout, verbose)
