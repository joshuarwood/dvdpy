# Copyright (C) 2025     Josh Wood
# 
# Very closely based on the unscrambler project
# written by:
#              Victor Muñoz (xt5@ingenieria-inversa.cl)
#              https://github.com/saramibreak/unscrambler
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


# LSFR = Linear Shift Feedback Register

# 15 bit LSFR with bits 10 and 14 as taps (probably equivalent to polynomial?)

def generate_cypher(seed, length):

    # initialize the shift register
    lfsr = seed

    # create an empty cypher of the requested length
    # where each value is 0x00, to be filled later
    cypher = bytearray(length)

    # loop to calculate bytes by shifting lfsr and
    # then updating lfsr using taps at bits 10, 14
    for i in range(length):
        for bit in range(8):
            # compute bit
            bit = (lfsr >> 14)
            # update cyphre byte with this bit
            cypher[i] = (cypher[i] << 1) | bit
            # update the shift register
            n = ((lfsr >> 14) ^ (lfsr >> 10)) & 1
            lfsr = ((lfsr << 1) | n) & 0x7FFF

    return cypher
