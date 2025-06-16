
SPC_INQUIRY    = 0x12
SBC_START_STOP = 0x1B
MMC_READ_12    = 0xA8

import time
import dvdpy.cextension

def drive_info(fd: int):

    cmd = bytearray(12)
    buffer = bytearray(36)

    cmd[0] = SPC_INQUIRY
    cmd[4] = len(buffer)

    dvdpy.cextension.command_device(fd, cmd, buffer, 1, True)

    vendor = buffer[8:16].decode("utf-8")
    prod_id = buffer[16:32].decode("utf-8")
    prod_rev = buffer[32:36].decode("utf-8")

    return f"{vendor}/{prod_id}/{prod_rev}"

def drive_spin(fd: int, state: bool):

    if isinstance(state, bool) == False:
        raise TypeError("Spin state must be True or False")

    cmd = bytearray(12)
    buffer = bytearray(8)

    cmd[0] = SBC_START_STOP
    cmd[4] = int(state)

    dvdpy.cextension.command_device(fd, cmd, buffer, 1, True)

fd = dvdpy.cextension.open_device("/dev/sr0")
print("Drive model........:", drive_info(fd))
drive_spin(fd, state=True)
time.sleep(1)
drive_spin(fd, state=False)
dvdpy.cextension.close_device(fd)
