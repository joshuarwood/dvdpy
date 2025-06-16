
SPC_INQUIRY = 0x12
MMC_READ_12 = 0xA8

import cextension

def drive_info(fd: int):

    buffer = bytearray(36)
    cmd = bytearray([
        SPC_INQUIRY, 0, 0, 0, len(buffer), 0, 0, 0, 0, 0, 0, 0])

    cextension.command_device(fd, cmd, buffer, 1, True)

    vendor = buffer[8:16].decode("utf-8")
    prod_id = buffer[16:32].decode("utf-8")
    prod_rev = buffer[32:36].decode("utf-8")

    return f"{vendor}/{prod_id}/{prod_rev}"

fd = cextension.open_device("/dev/sr0")
print("Drive model........:", drive_info(fd))
cextension.close_device(fd)
