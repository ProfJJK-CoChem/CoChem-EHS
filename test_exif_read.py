import sys, os
from datetime import datetime, timedelta
from PIL import Image
import piexif

REAL_IMAGE = os.path.abspath('test.jpg')
img_path = 'test_valid.jpg'
img = Image.open(REAL_IMAGE)
exif_bytes = img.info.get('exif')
if exif_bytes:
    exif_dict = piexif.load(exif_bytes)
else:
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}

dt = datetime.now() - timedelta(hours=1)
exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dt.strftime('%Y:%m:%d %H:%M:%S').encode('ascii')
exif_bytes = piexif.dump(exif_dict)
img.save(img_path, exif=exif_bytes)

sys.path.insert(0, os.path.abspath('src'))
from audit_validator import get_exif_datetime

print("Result:", get_exif_datetime(img_path))
