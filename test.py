
import time
import dvdpy.devices
import dvdpy.commands

drive = dvdpy.devices.dvd("/dev/sr0")
t0 = time.time()
print(drive.model_info(True))
print(f"took {time.time()-t0:.6f} sec")
drive.start()
#time.sleep(3)
#drive.stop()
dvdpy.commands.read_sectors(drive.fd, 712980, verbose=True) # replaces read_dummy
dvdpy.commands.read_sectors(drive.fd, 2295012, verbose=True) # replaces read_dummy

dvdpy.commands.read_sectors(drive.fd, 80, streaming=True, verbose=True)
dvdpy.commands.read_sectors(drive.fd, 0, streaming=True, verbose=True)
t0 = time.time()
status, data = dvdpy.commands.read_raw_bytes(drive.fd, 0, 16*2064, verbose=True)
print("raw read to %.6f sec" % (time.time() - t0))

for i in range(16):
    for j in range(10):
        print(" %02x" % data[i * dvdpy.commands.RAW_SECTOR_SIZE + j], end='')
    print("")

