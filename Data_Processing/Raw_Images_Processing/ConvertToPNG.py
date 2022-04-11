import numpy as np
from osgeo import gdal
from PIL import Image
import os

def tif2numpyarray(input_file):
    """
    read GeoTiff and convert to numpy.ndarray.
    Inputs:
        input_file (str) : the name of input tiff file
    return:
        image(np.array) : image for each bands
    """
    # read the file and construct a zero numpy
    dataset = gdal.Open(input_file, gdal.GA_ReadOnly)
    image = np.zeros((dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount),
                     dtype=float)
    #print("******************************")

    # read the 4 bands in each geoTiff
    band1 = dataset.GetRasterBand(1)
    band2 = dataset.GetRasterBand(2)
    band3 = dataset.GetRasterBand(3)
    band4 = dataset.GetRasterBand(4)

    # assign each band to the corresponding location in the array inline with RGB requirements
    image[:, :, 0] = band1.ReadAsArray()
    image[:, :, 1] = band2.ReadAsArray()
    image[:, :, 2] = band3.ReadAsArray()
    image[:, :, 3] = band4.ReadAsArray()
    return image

def normalize(array,band):
    """
    Normalizes numpy arrays into scale 0.0 - 1.0 to be used in RGB mapping
    Inputs:
        array: array to be normalized between 0-1
    return:
        normalized array
    """
    #get min and max to normalize
    #min = [352.5, 422, 504, 228]
    #max = [5246, 4056, 3918, 3577]

    min = [0, 0, 0, 0]
    max = [0.2856778204, 0.3260027468, 0.3961989582, 0.4650869071]
    array_min, array_max = array.min(), array.max()
    return ((array - min[band-1])/(max[band-1] - min[band-1]))


def convert_to_PNG(path):
    """
    Construct a new image from the normalized numpy array
    Changes bands order to fit the colors in original image
    This function uses the normalize and tif2numpyarray
    Inputs:
        path : string path to the geoTiff file
    return:
        Image from array
    """

    # Convert the image to numpy array using tif2numpyarray function
    im  = tif2numpyarray(path)
    #print(im)

    # Normalize each band separately
    a_image2 = np.empty_like(im)
    a_image2 = im
    #a_image2[:,:,0] = normalize(im[:,:,0],1)
    #a_image2[:,:,1] = normalize(im[:,:,1],2)
    #a_image2[:,:,2] = normalize(im[:,:,2],3)
    #a_image2[:,:,3] = normalize(im[:,:,3],4)
    #print(a_image2)

    # get RGB relevant value by multiplying * 255
    a_image3 = a_image2*255

    # remove any decimal point
    a_image4 = np.around(a_image3, decimals=0)

    #a_image4[:,:,3] = 255
    a_image4[:, :, 3]
    a_image5 = np.copy(a_image4)
    a_image4[:, :, 0] = a_image5[:, :, 0]
    a_image4[:, :, 1] = a_image5[:, :, 1]
    a_image4[:, :, 2] = a_image5[:, :, 2]

    imr = Image.fromarray(np.uint8(a_image4))

    return imr

# This code loop through all tiff generated and convert them to PNG file for further processing in the ML pipeline

BASE_PATH = r"C:\Users\minaf\Documents\GWU\Capstone\Data\lagos"
# Mode is TEST or TRAIN which will either convert tiff images from the train or the test folders
MODE = "TRAIN"

# If PROCESS_NON_BUILDUP is set to false then only two labels will be created for 0 and 1 (deprived and buildup)
# If PROCESS_NON_BUILDUP is set to true then three labels will be processed
PROCESS_NON_BUILTUP = False

# Check and create folders
path = BASE_PATH + r'\Raw_Images'

png_path  = path + r"\{}\png".format(MODE)

# Check whether the specified path exists or not
isExist = os.path.exists(png_path)
if not isExist:
    os.makedirs(path + r"\{}\png\0".format(MODE))
    os.makedirs(path + r"\{}\png\1".format(MODE))
    if PROCESS_NON_BUILTUP:
        os.makedirs(path + r"\{}\png\2".format(MODE))

##########

BUILTUP_PATH    = path + r"\{}\tif\0".format(MODE)
DEPRIVED_PATH   = path + r"\{}\tif\1".format(MODE)
NONBUILDUP_PATH = path + r"\{}\tif\2".format(MODE)


for filename in os.listdir(BUILTUP_PATH):
    img_path = BUILTUP_PATH + '\\' + filename
    print(img_path)
    tmp_image = convert_to_PNG(img_path)
    tmp_image.save(path + r"\{}\png\0\{}.png".format(MODE, filename))


for filename in os.listdir(DEPRIVED_PATH):
    img_path = DEPRIVED_PATH + '\\' + filename
    print(img_path)
    tmp_image = convert_to_PNG(img_path)
    tmp_image.save(path + r"\{}\png\1\{}.png".format(MODE, filename))

if PROCESS_NON_BUILTUP:
    for filename in os.listdir(NONBUILDUP_PATH):
        img_path = NONBUILDUP_PATH + '\\' + filename
        print(img_path)
        tmp_image = convert_to_PNG(img_path)
        tmp_image.save(path + r"\{}\png\2\{}.png".format(MODE, filename))

