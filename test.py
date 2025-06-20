
import time
import dvdpy.devices
import dvdpy.commands

drive = dvdpy.devices.dvd("/dev/sr0")
print("\nDrive model is:", drive.model_info(True))
drive.start()

#dvdpy.commands.read_sectors(drive.fd, 712980, verbose=True) # replaces read_dummy
#dvdpy.commands.read_sectors(drive.fd, 2295012, verbose=True) # replaces read_dummy

dvdpy.commands.read_sectors(drive.fd, 0, streaming=True, verbose=True)
status, data = dvdpy.commands.read_raw_bytes(drive.fd, 0, 16*2064, verbose=True)

print("\nFirst Sector:")
for i in range(16):
    for j in range(10):
        print(" %02x" % data[i * dvdpy.commands.RAW_SECTOR_SIZE + j], end='')
    print("")

f = open("test.bin", "wb")
f.write(data)
f.close()
