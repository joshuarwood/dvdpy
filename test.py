
import time
import dvdpy.devices
import dvdpy.commands

drive = dvdpy.devices.dvd("/dev/sr0")
print(drive.model_info(True))
drive.start()
#time.sleep(3)
#drive.stop()
dvdpy.commands.read_sectors(drive.fd, 712980, verbose=True) # replaces read_dummy
dvdpy.commands.read_sectors(drive.fd, 2295012, verbose=True) # replaces read_dummy

dvdpy.commands.read_sectors(drive.fd, 80, streaming=True, verbose=True)
dvdpy.commands.read_sectors(drive.fd, 0, streaming=True, verbose=True)
