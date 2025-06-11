# Copyright (C) 2025     Josh Wood
# 
# This portion is closely based on the friidump project
# written by:
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

import os
import dvdpy
import argparse

def welcome():
    print("\ndvdpy - Copyright (C) 2025  Josh Wood\n\n"
          "This program is free software; you can redistribute it and/or modify\n"
          "it under the terms of the GNU General Public License as published by\n"
          "the Free Software Foundation; either version 2 of the License, or\n"
          "(at your option) any later version.\n\n"
          "This program is distributed in the hope that it will be useful,\n"
          "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
          "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
          "GNU General Public License for more details.\n\n"
          "You should have received a copy of the GNU General Public License along\n"
          "with this program; if not, write to the Free Software Foundation, Inc.,\n"
          "51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.\n\n"
          "Source Code: https://github.com/joshuarwood/dvdpy\n",
          flush=True)

if __name__ == "__main__":
    welcome()

    parser = argparse.ArgumentParser(
        "python3 " + os.path.basename(__file__),
        description="Command line interface for DVD operations")
    parser.add_argument("-d", "--device", default="/dev/sr0", help="Path to DVD drive (default /dev/sr0)")
    args = parser.parse_args()

    fd = dvdpy.open_device("/dev/sr0")
    dvdpy.drive_info(fd)
    dvdpy.close_device(fd)
