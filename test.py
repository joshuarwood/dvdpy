
import time
import dvdpy.devices

drive = dvdpy.devices.dvd("/dev/sr0")
print(drive.model_info(True))
drive.start()
time.sleep(3)
drive.stop()
