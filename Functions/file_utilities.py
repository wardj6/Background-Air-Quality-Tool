from pathlib import Path
import pandas as pd
import numpy as np
import os
import shutil


## THESE FUNCTIONS ARE NOT CURRENTLY USED IN THE BACKGROUND TOOL - THEY WERE CREATED FOR A NOW UNUSED GRAL WIND ROSE PULLING PROGRAM


def check_file_exists(file: str) -> bool:
    """
    CHecks if file existis
    :param file: path to check
    :return: True if exists
    """
    if os.path.isfile(file):
        return True
    else:
        return False


def copy_files_as_zip(dir: str, filetype: str):
    """

    :param dir:
    :param filetype:
    :return:
    """
    files = get_files(dir, filetype)
    new_folder = dir + "\\unzipped_gff_files\\"
    if os.path.isdir(new_folder):
        pass
    else:
        os.mkdir(new_folder)
    count = 1
    for file in files:
        file_path = Path(file)
        file_name = file_path.name
        shutil.copy(dir + "\\" + file_name, new_folder + file_path.stem + ".zip")
        print(f"Copied file # {count} as zip file")
        count += 1


def unzip_files(dir: str, type: str):
    files = get_files(dir, type)
    import zipfile
    count = 1
    for file in files:
        print(f"Unzipping file # {count}")
        count += 1
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(dir)


def get_files(dir: str, extension: str) -> list:
    file_list = os.listdir(dir)
    return [dir + "\\" + filename for filename in file_list if filename.endswith(extension)]


def convert_con_file(file: str) -> np.array:
    # structure of con file datatypes according to GRAL
    dtp = np.dtype([('x', np.dtype('i4')), ('y', np.dtype('i4')), ('con', np.dtype('f4'))])
    # open confile, skip 4 byte header and convert it to numpy array
    with open(file, "rb") as f:
        f.seek(4)
        arr = np.fromfile(f, dtype=dtp)
    return arr


def convert_gff_file(file: str) -> (np.array, np.array):
    # gff file datatypes for header and data
    hdr = np.dtype([('nk', np.dtype('i4')), ('nj', np.dtype('i4')), ('ni', np.dtype('i4')), ('dir', np.dtype('f4')),
                    ('spd', np.dtype('f4')), ('ak', np.dtype('i4')), ('cs', np.dtype('f4')),
                    ('hd', np.dtype('i4'))])
    # data type is integer for u,v,w
    dtw = np.dtype([('u', np.dtype('i2')), ('v', np.dtype('i2')), ('w', np.dtype('i2'))])
    # convert binary gff to numpy array
    with open(file, "rb") as f:
        # header
        h = np.fromfile(f, dtype=hdr, count=1)

        # uvw values are stored as integers, convert to float array
        c = np.fromfile(f, dtype=dtw).astype(np.dtype([('u', np.dtype('<f2')), ('v', np.dtype('<f2')), ('w', np.dtype('<f2'))]))
    return h, c


def print_grid_params(file: str) -> (str, list):
    geb_df = pd.read_fwf(file)
    geb_df = geb_df.iloc[:,0]
    cell_size = geb_df.iloc[0]
    numx = geb_df.iloc[2]
    numy = geb_df.iloc[3]
    sw_corner_x = geb_df.iloc[6]
    sw_corner_y = geb_df.iloc[8]
    print_text = "\nGrid Parameters for the selected GRAL model are:\n--- Grid spacing = " + str(cell_size) + "\n" \
              "--- Number of grid cells = " + str(numx) + "(X) and " + str(numy) + "(Y)\n" \
                "--- SW Corner coordinates = " + str(sw_corner_x) + " " + str(sw_corner_y) + "\n"
    return print_text, [float(cell_size), int(numx), int(numy), int(sw_corner_x), int(sw_corner_y)]