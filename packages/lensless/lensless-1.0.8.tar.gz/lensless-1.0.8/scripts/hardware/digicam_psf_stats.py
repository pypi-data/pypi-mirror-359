import os
import glob

folder = "/root/LenslessPiCam/digicam_rect_20250612_100253"

# get subfolders
subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]