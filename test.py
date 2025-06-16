
import dvdpy

device = dvdpy.dvd_device("/dev/sr0")
print(device.model_info())
