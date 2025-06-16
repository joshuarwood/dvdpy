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

from . import commands
from . import cextension

__all__ = ['dvd']

class dvd:
    """ A class for the DVD drive interface

    Parameters:
        address (str): path to drive
        timeout (int): command timeout in seconds
    """
    def __init__(self, address, timeout=1):
        self.fd = cextension.open_device(address)
        self.timeout = timeout

    def __del__(self):
        cextension.close_device(self.fd)

    def model_info(self, verbose: bool = False):
        return commands.drive_info(self.fd, self.timeout, verbose) 

    def start(self, verbose: bool = False):
        return commands.drive_spin(self.fd, True, self.timeout, verbose)

    def stop(self, verbose: bool = False):
        return commands.drive_spin(self.fd, False, self.timeout, verbose)
