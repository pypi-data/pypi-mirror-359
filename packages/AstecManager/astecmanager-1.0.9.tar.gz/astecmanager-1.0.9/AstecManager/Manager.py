from datetime import datetime
import os
from threading import Thread
from pathlib import Path
import shutil
from dataclasses import dataclass
from tqdm import tqdm
from collections import defaultdict
import time
import copy
import traceback
import AstecManager.omerotools as omerolib
from multiprocessing import cpu_count
import numpy as np
from AstecManager.libs.lineage import AddNodeToXML,get_longid,count_cells,GetCellMinTimePoint,Get_Cell_Names,get_id_t,Get_Cell_Values_Float,LoadCellList,get_gen_from_cell_name,GetCellLifetime
from AstecManager.libs.analyze import apply_analysis, plotsignaltonoise
from AstecManager.libs.data import imread,imsave
from AstecManager.libs.jsonlib import addDictToMetadata,retrieveMicroscopeMetadata
from AstecManager.libs.lineage_distance import generate_lineage_comparison
import subprocess
from AstecManager.libs.contourlib import compute_contour, compute_contour_from_junctions, \
    compute_segmentation_from_junctions, compute_membranes_from_junctions,fill_image
import xml.etree.ElementTree as ET

xml_metadata = "metadata.xml"
devmode = True # SHOULD USE PARAMETERS EMBEDDED IN PARAM FILES , NOT THIS THING


def compute_atlas():
    """This function is used to find the path to the ATLAS properties files used in the automatic naming of an embryo

    :returns: Path to properties files inside AstecManager folder of atlas embryos
    :rtype: list
    """
    from importlib_resources import files
    return [str(files("AstecManager.atlas").joinpath("pm1.xml")), str(files("AstecManager.atlas").joinpath("pm3.xml")),
            str(files("AstecManager.atlas").joinpath("pm4.xml")), str(files("AstecManager.atlas").joinpath("pm5.xml")),
            str(files("AstecManager.atlas").joinpath("pm7.xml")), str(files("AstecManager.atlas").joinpath("pm8.xml")),
            str(files("AstecManager.atlas").joinpath("pm9.xml"))]


def get_omero_config(parameters):
    """Search for omero_config_file in parameters, format it and return it. 2 keys are possible "omero_config_file" or "omero_authentication_file"

    :param parameters: list of parameters given to the AstecManager step
    :type parameters: dict
    :return: The path to the configuration file
    :rtype: string
    """
    omero_config_file = None
    if "omero_config_file" in parameters:
        if parameters["omero_config_file"] is not None and parameters["omero_config_file"] != "None":
            omero_config_file = parameters["omero_config_file"].replace('"', '').replace("'", "")
        if omero_config_file is not None and not os.path.isfile(omero_config_file):
            return None
    else:
        if "omero_authentication_file" in parameters:
            if parameters["omero_authentication_file"] is not None and parameters[
                "omero_authentication_file"] != "None":
                omero_config_file = parameters["omero_authentication_file"].replace('"', '').replace("'", "")
            if omero_config_file is not None and not os.path.isfile(omero_config_file):
                return None
    return omero_config_file


def Fiji_autocontrast(path_in):
    """Python code applying the Fiji autocontrast algorithm on a given image ( source : Soltius on ImageSc forums)

    :param path_in: path to the images
    :type path_in: string

    """
    import cv2
    im = cv2.imread(path_in, -1)
    im_type = im.dtype
    # minimum and maximum of image
    im_min = np.min(im)
    im_max = np.max(im)

    # converting image =================================================================================================

    # case of color image : contrast is computed on image cast to grayscale
    if len(im.shape) == 3 and im.shape[2] == 3:
        # depending on the options you chose in ImageJ, conversion can be done either in a weighted or unweighted way
        # go to Edit > Options > Conversion to verify if the "Weighted RGB conversion" box is checked.
        # if it's not checked, use this line
        # im = np.mean(im, axis = -1)
        # instead of the following
        im = 0.3 * im[:, :, 2] + 0.59 * im[:, :, 1] + 0.11 * im[:, :, 0]
        im = im.astype(im_type)

    # histogram computation

    # parameters of histogram computation depend on image dtype.
    # following https://imagej.nih.gov/ij/developer/macro/functions.html#getStatistics
    # 'The histogram is returned as a 256 element array. For 8-bit and RGB images, the histogram bin width is one.
    # for 16-bit and 32-bit images, the bin width is (max-min)/256.'
    if im_type == np.uint8:
        hist_min = 0
        hist_max = 256
    elif im_type in (np.uint16, np.int32):
        hist_min = im_min
        hist_max = im_max
    else:
        raise NotImplementedError(f"Not implemented for dtype {im_type}")

    # compute histogram
    histogram = np.histogram(im, bins=256, range=(hist_min, hist_max))[0]
    bin_size = (hist_max - hist_min) / 256

    # compute output min and max bins =================================================================================

    # various algorithm parameters
    h, w = im.shape[:2]
    pixel_count = h * w
    # the following values are taken directly from the ImageJ file.
    limit = pixel_count / 10
    const_auto_threshold = 5000
    auto_threshold = 0

    auto_threshold = const_auto_threshold if auto_threshold <= 10 else auto_threshold / 2
    threshold = int(pixel_count / auto_threshold)

    # setting the output min bin
    i = -1
    found = False
    # going through all bins of the histogram in increasing order until you reach one where the count if more than
    # pixel_count/auto_threshold
    while not found and i <= 255:
        i += 1
        count = histogram[i]
        if count > limit:
            count = 0
        found = count > threshold
    hmin = i
    found = False

    # setting the output max bin: same thing but starting from the highest bin.
    i = 256
    while not found and i > 0:
        i -= 1
        count = histogram[i]
        if count > limit:
            count = 0
        found = count > threshold
    hmax = i

    # compute output min and max pixel values from output min and max bins
    if hmax >= hmin:
        min_ = hist_min + hmin * bin_size
        max_ = hist_min + hmax * bin_size
        # bad case number one, just return the min and max of the histogram
        if min_ == max_:
            min_ = hist_min
            max_ = hist_max
    # bad case number two, same
    else:
        min_ = hist_min
        max_ = hist_max

    # apply the contrast
    imr = (im - min_) / (max_ - min_) * 255
    cv2.imwrite(path_in, imr)


def compute_images_from_movie(image):
    """ Compute all the images from the movie image, that will be used for video generation

    :param image:  Path to intra-registration movie to get images from
    :type image: string
    :return: List of image paths for mp4 movie, images height and images width
    :rtype: tuple list of strings , int , int

    """
    from PIL import Image
    from os.path import join
    print("-> Reading image")
    image_movie = imread(image)

    shape = image_movie.shape
    z_stack_count = shape[2]
    img_array = []
    height = None
    width = None
    for i in range(0, z_stack_count):
        img_array.append(image_movie[:, :, i])
    image_list = []
    image_folder = "./images/"
    if not os.path.isdir(image_folder):
        os.makedirs(image_folder)
    print("-> Writing video file")
    for i in tqdm(range(len(img_array))):
        PIL_image = Image.fromarray(img_array[i])
        image_link = join(image_folder, 'frame' + str(i) + '.png')
        image_list.append(image_link)
        PIL_image.save(image_link)
        Fiji_autocontrast(image_link)
        height, width = img_array[i].shape
    return image_list, height, width


def compute_video_from_movie(intraregistration_folder, fuse_folder,begin,end):
    """Use the movie image generated by intraregistration of fusion to create a video

    :param intraregistration_folder: Intrareg experiment folder to get movie from (suffix of folder name)
    :type intraregistration_folder: string
    :param fuse_folder: Fusion Experiment folder to get movie from (suffix of folder name)
    :type fuse_folder: string
    :return: Path to the generated video file
    :rtype: string
    """
    import cv2
    from os.path import join, isfile
    from os import listdir
    path = "."
    fuse_exp = fuse_folder
    print("Writing the video from the movie")
    if isinstance(fuse_folder, list):
        fuse_exp = fuse_folder[0]
    else:
        if "[" in fuse_folder:
            fuse_exp = fuse_folder.replace("'", "").replace('"', '').replace("[", "").replace("]", "").split(
                ",")[0]
    path_intrareg = join(join(path, "INTRAREG"), "INTRAREG_" + str(intraregistration_folder) + "/MOVIES_t"+"{:03d}".format(begin)+"-"+"{:03d}".format(end))
    path_fuse = join(path_intrareg, join("FUSE", "FUSE_" + str(fuse_exp))).replace('"', '').replace("'", "")
    final_path = join(join(path, "analysis").replace("'", "").replace('"', ''), "fusion")
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    print("Reading intra-registration movie to extract frames")
    image_files = [f for f in listdir(path_fuse) if isfile(join(path_fuse, f)) and (".nii" in f or ".mha" in f)]
    image_list, height, width = compute_images_from_movie(os.path.join(path_fuse, image_files[0]))
    ouputname = join(final_path, 'fusion_movie.avi')
    framerate = int(len(image_list) / 15)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(ouputname, fourcc, framerate, (width, height))
    if not video.isOpened():
        print('Error cannot create ' + 'fusion_movie.avi')
        quit()

    print("Saving image by image")
    for image in tqdm(image_list):
        img = cv2.imread(image)
        video.write(img)
        os.system("rm " + str(image))
    cv2.destroyAllWindows()
    video.release()
    print("Generating video from image list")
    os.system('ffmpeg -i ' + ouputname + '  ' + ouputname.replace('.avi', '.mp4'))
    os.system('rm -f ' + ouputname)
    return final_path


def plot_fusion_intensity_profile(embryo_name, fuse_exp="01"):
    """ Generate the plot graph corresponding to fusion images average and standard deviation intensities

    :param embryo_name:
    :type embryo_name: string
    :param fuse_exp: Fusion experiment folder suffix (Default value = "01")
    :type fuse_exp: string

    """
    import matplotlib.pyplot as plt
    fuse_files = []
    fuse_folder = "./FUSE/FUSE_" + fuse_exp
    if isinstance(fuse_folder, list):
        fuse_folder = "./FUSE/FUSE_" + fuse_exp[0]
    else:
        if "[" in fuse_exp:
            fuse_folder = "./FUSE/FUSE_" + \
                          fuse_exp.replace("'", "").replace('"', '').replace("[", "").replace("]", "").split(
                              ",")[0]
    for file in os.listdir(fuse_folder):
        # check only text files
        if "_fuse" in file:
            fuse_files.append(file)
    means_by_t = {}
    std_by_t = {}
    neg_std_by_t = {}

    means_by_t_b = {}
    std_by_t_b = {}
    neg_std_by_t_b = {}
    print("=> Analyzing images")
    for fuse_file in tqdm(fuse_files):
        print("     -> " + str(fuse_file))
        time = int(fuse_file.split("_fuse_t")[1].split(".")[0])
        image_path = os.path.join(fuse_folder, fuse_file)
        npimage = imread(image_path)
        mean_intensities = np.mean(npimage)
        std_intensities = np.std(npimage)
        means_by_t[time] = mean_intensities
        std_by_t[time] = std_intensities + mean_intensities
        neg_std_by_t[time] = mean_intensities - std_intensities
        min_im = np.min(npimage)
        nobackground = npimage[npimage != min_im]
        mean_intensities = np.mean(nobackground)
        std_intensities = np.std(nobackground)
        means_by_t_b[time] = mean_intensities
        std_by_t_b[time] = std_intensities + mean_intensities
        neg_std_by_t_b[time] = mean_intensities - std_intensities

    print("=> Saving result plot")
    sorted_means = dict(sorted(means_by_t.items()))
    sorted_std = dict(sorted(std_by_t.items()))
    sorted_neg_std = dict(sorted(neg_std_by_t.items()))
    sorted_means_b = dict(sorted(means_by_t_b.items()))
    sorted_std_b = dict(sorted(std_by_t_b.items()))
    sorted_neg_std_b = dict(sorted(neg_std_by_t_b.items()))
    plt.title("$\mu$ and $\pm \sigma$ in fused images for embryo " + str(embryo_name))
    times = list(sorted_means.keys())
    plt.plot(times, list(sorted_means.values()), label="intensities with background")
    plt.plot(times, list(sorted_means_b.values()), label="intensities without background")
    plt.fill_between(times, list(sorted_std.values()), list(sorted_neg_std.values()), alpha=0.5)
    plt.fill_between(times, list(sorted_std_b.values()), list(sorted_neg_std_b.values()), alpha=0.5)
    plt.legend(loc="upper left")
    plt.xlabel("Time points sequence")
    plt.ylabel("Intensities")

    path = "."
    folder_out = os.path.join(os.path.join(path, "analysis"), "fusion")
    if not os.path.isdir(folder_out):
        os.makedirs(folder_out)
    plt.savefig(os.path.join(folder_out, "fusion_images_intensities.png"))


def compute_user(parameters):
    """Retrieve user from the list of parameters.
    This user will be saved to metadata

    :param parameters: list of parameters for steps
    :type parameters: dict
    :return: Found user initials
    :rtype: string

    """
    user = "UI"
    if "user" in parameters:
        user = parameters["user"]
    return user


def compute_astec_command(astec_command):
    """Compute the command to start the ASTEC process depending on step

    :param astec_command:
    :type astec_command: string
    :return: command to start the ASTEC process
    :rtype: string

    """
    final_command_arg0 = ""
    if "fuse" in astec_command.lower():
        final_command_arg0 = "astec_fusion"
    if "drift" in astec_command.lower():
        final_command_arg0 = "astec_drift"
    if "mars" in astec_command.lower():
        final_command_arg0 = "astec_mars"
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        final_command_arg0 = "astec_astec"
    if "post" in astec_command.lower():
        final_command_arg0 = "astec_postcorrection"
    if "properties" in astec_command.lower():
        final_command_arg0 = "astec_embryoproperties"
    if "intra" in astec_command.lower():
        final_command_arg0 = "astec_intraregistration"
    return final_command_arg0


def compute_astec_dir(astec_command, params_dict):
    """compute the running dirs of ASTEC depending on parameters and step

    :param astec_command:
    :type astec_command: string
    :param params_dict:
    :type params_dict: dict of astec parameters
    :return: the list of directories where astec images will be stored
    :rtype: list of string

    """
    dir_to_create = []
    if "fuse" in astec_command.lower():
        if "EXP_FUSE" in params_dict:
            if isinstance(params_dict["EXP_FUSE"], list):
                splitted_fuse = params_dict["EXP_FUSE"]
            else:
                splitted_fuse = params_dict["EXP_FUSE"].replace("'", "").replace('"', '').replace("[", "").replace("]",
                                                                                                                   "").split(
                    ",")
            for fuse in splitted_fuse:
                dir_to_create.append("FUSE/FUSE_" + fuse)
        else:
            dir_to_create.append("FUSE/FUSE_RELEASE")
    if "drift" in astec_command.lower():
        if "EXP_DRIFT" in params_dict:
            if isinstance(params_dict["EXP_DRIFT"], list):
                splitted_fuse = params_dict["EXP_DRIFT"]
            else:
                splitted_fuse = params_dict["EXP_DRIFT"].replace("'", "").replace('"', '').replace("[", "").replace("]",
                                                                                                                   "").split(
                    ",")
            for fuse in splitted_fuse:
                dir_to_create.append("DRIFT/DRIFT_" + fuse)
        else:
            dir_to_create.append("DRIFT/DRIFT_RELEASE")
    if "mars" in astec_command.lower():
        if "EXP_SEG" in params_dict:
            dir_to_create.append("SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"', ''))
        else:
            dir_to_create.append("SEG/SEG_RELEASE")
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        if "EXP_SEG" in params_dict:
            dir_to_create.append("SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"', ''))
        else:
            dir_to_create.append("SEG/SEG_RELEASE")
    if "post" in astec_command.lower():
        if "EXP_POST" in params_dict:
            dir_to_create.append("POST/POST_" + params_dict["EXP_POST"].replace("'", "").replace('"', ''))
        else:
            dir_to_create.append("POST/POST_RELEASE")
    if "properties" in astec_command.lower():
        if "EXP_INTRAREG" in params_dict:
            dir_to_create.append("INTRAREG/INTRAREG_" + params_dict["EXP_INTRAREG"].replace("'", "").replace('"', ''))
        else:
            dir_to_create = "INTRAREG/INTRAREG_RELEASE"
    if "intra" in astec_command.lower():
        intrareg_temp_path = "INTRAREG/INTRAREG_RELEASE"
        if "EXP_INTRAREG" in params_dict:
            intrareg_temp_path = "INTRAREG/INTRAREG_" + params_dict["EXP_INTRAREG"].replace("'", "").replace('"', '')
        if "EXP_FUSE" in params_dict:
            dir_to_create.append(os.path.join(intrareg_temp_path,"FUSE/FUSE_" + params_dict["EXP_FUSE"].replace("'", "").replace('"', '')))
        if "EXP_SEG" in params_dict:
            dir_to_create.append(os.path.join(intrareg_temp_path,"SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"','')))
        if "EXP_POST" in params_dict:
            dir_to_create.append(os.path.join(intrareg_temp_path,"POST/POST_" + params_dict["EXP_POST"].replace("'", "").replace('"','')))
    return dir_to_create


def compute_astec_tag(astec_command):
    """ Compute the tag to add to OMERO dataset during upload depending on step

    :param astec_command:
    :type astec_command: string
    :return: the tag to add to OMERO dataset during upload depending on step
    :rtype: string

    """
    tag = ""
    if "fuse" in astec_command.lower():
        tag = "fuse"
    if "drift" in astec_command.lower():
        tag = "drift"
    elif "mars" in astec_command.lower() or "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        tag = "seg"
    elif "post" in astec_command.lower():
        tag = "post"
    elif "intra" in astec_command.lower():
        tag = "intrareg"
    elif "properties" in astec_command.lower():
        tag = "embryoproperties"
    return tag


def is_file_image(file):
    """ Check if a file is an image by extension (exclude compressed image)
    Image files can be with extension nii, mha, inr or tif

    :param file: Path to the image to test
    :type file: string
    :return: True if the file is an image, False otherwise
    :rtype: bool
    """
    return file.endswith('.mha') or file.endswith('nii') or file.endswith(".inr") or file.endswith(".tif")


def is_file_image_or_compressed(file):
    """ Check if a file is an image or compressed image by extension (include compressed image)
    Image files can be with extension nii, mha, inr or tif (+ .gz for compressed)

    :param file: Path to the image to test
    :type file: string
    :return: True if the file is an image compressed or not, False otherwise
    :rtype: bool

    """
    return file.endswith('.mha') or file.endswith('nii') or file.endswith('.mha.gz') or file.endswith(
        'nii.gz') or file.endswith(".inr") or file.endswith(".inr.gz") or file.endswith(".tif") or file.endswith(".tif.gz")


@dataclass
class astec_instance:
    """ Class to hold the ASTEC instance information """
    astec_command: str
    folder_embryo: str
    embryo_name: str
    mars_path: str = None
    compress_result: bool = True
    params_dict: dict = defaultdict
    begin_time: int = -1
    end_time: int = -1
    omero_result: bool = True
    omero_config_file: str = ""
    tag_list: list = None
    keep_temp: bool = False
    envastec: str = "astec"
    paramsuffix: str = ""
    omero_input: bool = False
    input_project: str = ""
    input_set: str = ""


class start_astec_cleaner(Thread):
    """  This thread is started to clean the ASTEC instances data (upload to datamanager, compression, ...)"""

    def __init__(self, astec_command, params_dict, name_embryo, send_to_omero, begin, end, compress_result=True,
                 omero_config_file="", tag_list=None, keep_temp=False):
        Thread.__init__(self)
        self.cleaner_folder = ""
        self.astec_command = astec_command
        self.name_embryo = name_embryo
        self.params_dict = params_dict
        self.stop_signal = False
        self.omero_result = send_to_omero
        self.compress_result = compress_result
        self.omero_files = []
        self.omero_files_reconstruction = []
        self.omero_config_file = omero_config_file
        self.omero_project_name = ""
        self.omero_dataset_name = []
        self.dataset_ids = []
        self.begin = int(begin)
        self.end = int(end)
        self.project_id = -1
        self.tag_list = tag_list
        self.keep_temp = keep_temp

    def stop_cleaning(self):
        """ Receive signal from the main thread,
        flagging that the instance is finished, and the management of output data should be stopped """
        self.stop_signal = True

    def list_images(self, folder):
        """ List all images inside a given folder

        :param folder: Path to the folder
        :type folder: string
        :return: list of image paths inside the folder
        :rtype: list

        """
        images = []
        onlyfiles = [f for f in os.listdir(folder) if
                     os.path.isfile(os.path.join(folder, f))]
        for file in onlyfiles:
            if is_file_image(file):
                images.append(file)
        return images

    def get_images_at_t(self, time_point, folder):
        """ Retrieve all images inside a given folder at time point

        :param time_point: Time point for the images
        :type time_point: int
        :param folder: folder to find the images in
        :type folder: string
        :return: list of image paths inside the folder at given time point
        :rtype: list of string

        """
        images = self.list_images(folder)
        result = []
        for image in images:
            if "_t{:03d}".format(time_point) in image:
                result.append(image)
        return result

    def image_t_exists(self, time, folder):
        """ Check if an image exists inside a given folder for a time point

        :param time:
        :type time: Int
        :param folder:
        :type folder: String
        :return: True if the image exists inside the folder for a time point, False otherwise
        :rtype: bool

        """
        images = self.list_images(folder)
        flag = False
        for image in images:
            if "_t{:03d}".format(time) in image:
                flag = True
        return flag

    def compress_and_delete(self, file):
        """ Run the compression of a file, and then delete if the compression has worked

        :param file: File to compress
        :type file: string

        """
        subprocess.run(["gzip", "-f", file])
        if os.path.isfile(file + ".gz"):
            subprocess.run(["rm", file])

    def copy_mha_to_nii(self, image_path):
        """ Use ASTEC copy process to convert mha image given by path to nii format

        :param image_path: Path to the image to convert
        :type image_path: String
        :return: The path to the nii image if worked, None otherwise
        :rtype: string

        """
        new_path = image_path.replace(".mha", ".nii")
        os.system("conda run -n astec copy " + image_path + " " + new_path)
        if os.path.isfile(new_path):
            os.system("rm " + image_path)
            return new_path
        return None

    def clean_at_t(self, time, pyom):
        """ Process the cleaning for a time point that finished (compression, upload, reconstruction and temp folder management)

        :param time: Time point to clean
        :type time: int
        :param pyom: instance of OMERO communication if needed
        :type pyom: OMERO communication

        """

        print("Cleaning embryo : " + str(self.name_embryo) + " at t = " + str(time))
        print("finding " + str(len(self.cleaner_folder)) + " folder to clean at t = " + str(time))
        for i in range(0,
                       len(self.cleaner_folder)):  # can have multiple working folder (for example multi channel fusion)
            if not i in self.omero_files:  # list of files already uploaded
                self.omero_files.insert(i, [])
            list_images = pyom.get_images_filename(self.dataset_ids[i])
            for image_name in list_images:  # fill the list of files already existing on OMERO
                if not image_name in self.omero_files[i]:
                    self.omero_files[i].append(image_name)
            clean = self.cleaner_folder[i]
            print("Cleaning folder : " + clean)
            images = self.get_images_at_t(time, clean)
            for image in images:  # clean image
                if image is not None and is_file_image(image):
                    imagepath = os.path.join(clean, image)
                    if imagepath.endswith(".mha"):
                        new_path = self.copy_mha_to_nii(imagepath)
                        if new_path is not None:
                            imagepath = new_path
                    if self.omero_result:  # uppload if needed
                        if not image in self.omero_files[i]:
                            print("Uploading image : " + str(imagepath) + " to dataset with id : " + str(
                                self.dataset_ids[i]))
                            pyom.add_image_to_dataset_java(imagepath, self.dataset_ids[i])
                            self.omero_files[i].append(image)
                            if self.compress_result:
                                print("Compressing image : " + str(imagepath))
                                self.compress_and_delete(str(imagepath))
                    elif self.compress_result:  # compress if needed
                        print("Compressing image : " + str(imagepath))
                        self.compress_and_delete(imagepath)

        for recon in self.reconstructions_folder:  # multi reconstruction folders (ex : segmentation)
            print("Reconstruction : " + str(recon))
            if os.path.isdir(recon):
                images_reconstruction = self.get_images_at_t(time, recon)
                for image_reconstruction in images_reconstruction:
                    if image_reconstruction is not None:
                        recon_path = os.path.join(recon, image_reconstruction)
                        if self.omero_result and "REC-MEMBRANE" in recon:  #Only upload REC MEMBRANE
                            if self.reco_dataset_id is not None:
                                if not image_reconstruction in self.omero_files_reconstruction:
                                    if image_reconstruction.endswith(".mha"):
                                        new_path = self.copy_mha_to_nii(recon_path)
                                        if new_path is not None:
                                            recon_path = new_path
                                    print("Uploading image : " + str(recon_path))
                                    pyom.add_image_to_dataset_java(recon_path, self.reco_dataset_id)
                                    self.omero_files_reconstruction.append(image_reconstruction)
                        if is_file_image(recon_path) and not ".gz" in images_reconstruction:  # if compress
                            print("Compressing reconstruction : " + str(recon_path))
                            self.compress_and_delete(recon_path)
        if self.keep_temp:  # if we keep temp , compress it because its heavy
            for clean in self.cleaner_folder:
                temp_folder = clean + "/TEMP_{:03d}/".format(time)
                if os.path.isdir(temp_folder):
                    images = []
                    onlyfiles = [f for f in os.listdir(temp_folder) if
                                 os.path.isfile(os.path.join(temp_folder, f))]
                    print("Compressing TEMP : " + "/TEMP_{:03d}/".format(time))
                    for file2 in onlyfiles:
                        self.compress_and_delete(os.path.join(temp_folder, file2))

    def compute_recon_dir(self, params_dict):
        """ Compute the list of reconstruction directories from ASTEC parameters (for segmentation)

        :param params_dict: ASTEC parameters
        :type params_dict: dict
        :return: list of the reconstruction directories path
        :rtype: list

        """
        reconstruction_dir = []
        for dir in self.cleaner_folder:
            reconstruction_dir.append(dir + "/RECONSTRUCTION/")
        if "EXP_RECONSTRUCTION" in params_dict:
            reconstruction_dir.append(
                "REC-MEMBRANE/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"', '').replace("'", ""))
            reconstruction_dir.append(
                "REC-SEED/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"', '').replace("'", ""))
            reconstruction_dir.append(
                "REC-MORPHOSNAKE/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"', '').replace("'", ""))
        else:
            if "EXP_SEG" in params_dict:
                reconstruction_dir.append(
                    "REC-MEMBRANE/REC_" + params_dict["EXP_SEG"].replace('"', '').replace("'", ""))
                reconstruction_dir.append("REC-SEED/REC_" + params_dict["EXP_SEG"].replace('"', '').replace("'", ""))
                reconstruction_dir.append(
                    "REC-MORPHOSNAKE/REC_" + params_dict["EXP_SEG"].replace('"', '').replace("'", ""))
        return reconstruction_dir

    def copy_logs_files(self, source_folder, target_folder):
        """ Copy logs files between two folders (used to stack all steps log files into the same folders in the end)

        :param source_folder: Directory to extract logs from
        :type source_folder: string
        :param target_folder: directory to copy into
        :type target_folder: string
        """
        range_t = len(source_folder)
        for i in range(0, range_t):
            if len(source_folder) > i and len (target_folder) > i:
                source = source_folder[i]
                target = target_folder[i]
                if os.path.isdir(source):
                    if not os.path.isdir(target):
                        os.makedirs(target)
                    onlyfiles = [f for f in os.listdir(source) if
                                 os.path.isfile(os.path.join(source, f)) and (".py" in f or ".log" in f)]
                    for file in onlyfiles:
                        print("copy " + str(file) + " to " + str(target))
                        subprocess.run(["cp", os.path.join(source, file), target])

    def run(self):
        """ Run the cleaning process """
        dirs = compute_astec_dir(self.astec_command, self.params_dict)  #extract all folders to clean
        self.cleaner_folder = []
        input_folder = []
        target_logs = []
        source_logs = []
        for dir in dirs:
            self.cleaner_folder.append(dir.replace('"', '').replace("'", ""))
            input_folder = dir.replace('"', '').replace("'", "")
        for clean in self.cleaner_folder:
            target_logs = os.path.join(clean, "LOGS")
        for input in input_folder:
            source_logs = os.path.join(input, "LOGS")
        for clean in self.cleaner_folder:
            while not os.path.isdir(clean):
                time.sleep(5)

        self.reconstructions_folder = self.compute_recon_dir(self.params_dict)

        pyom = None
        tag_step = compute_astec_tag(self.astec_command)
        if self.omero_result:  # if upload to omero , connect
            # Connect to OMERO
            pyom = omerolib.connect(file_path=self.omero_config_file)
            # Determine ASTEC folder depending on the step
            astec_dir = compute_astec_dir(self.astec_command, self.params_dict)
            # OMERO Dataset depending of ASTEC parameters
            for i in range(0, len(astec_dir)):
                self.omero_dataset_name.append(
                    astec_dir[i].replace("POST/", "").replace("DRIFT/","").replace("SEG/", "").replace("FUSE/", "").replace("INTRAREG/","").replace(
                        '"', '').replace("'", "").replace("/","_"))
            self.omero_dataset_recon_name = None
            for recon in self.reconstructions_folder:
                if "REC-MEMBRANE" in recon:
                    self.omero_dataset_recon_name = recon.replace("REC-MEMBRANE/", "").replace('"', '').replace("'", "")

            # Compute all projects and datasets that will be used, create them if needed
            self.omero_project_name = self.name_embryo
            # GET or CREATE project
            if pyom.get_project_by_name(self.omero_project_name) is None:
                pyom.create_project(self.omero_project_name)
            self.o_project = pyom.get_project_by_name(self.omero_project_name)
            self.project_id = self.o_project.getId()
            # GET or CREATE dataset
            for omero_name in self.omero_dataset_name:
                if pyom.get_dataset_by_name(omero_name, self.project_id) is None:
                    pyom.create_dataset(omero_name, self.project_id)
            if self.omero_dataset_recon_name is not None and pyom.get_dataset_by_name(self.omero_dataset_recon_name,
                                                                                      self.project_id) is None:
                pyom.create_dataset(self.omero_dataset_recon_name, self.project_id)
                self.reco_dataset_id = pyom.get_dataset_by_name(self.omero_dataset_recon_name, self.project_id).getId()
            for omero_name in self.omero_dataset_name:
                self.dataset_ids.append(pyom.get_dataset_by_name(omero_name, self.project_id).getId())
        for i in range(0, len(self.cleaner_folder)):
            if not i in self.omero_files:
                self.omero_files.insert(i, [])
            list_images = pyom.get_images_filename(self.dataset_ids[i])
            for image_name in list_images:
                if not image_name in self.omero_files[i]:
                    self.omero_files[i].append(image_name)
        # Manage time points at runtime
        for current_time in range(self.begin,
                                  self.end + 1):  # Clean all the time points one by one as soon as it's done (and wait for t+2 for segmentation)
            if current_time < self.end:
                for dir in self.cleaner_folder:
                    while not self.image_t_exists(current_time + 1, dir):
                        time.sleep(10)
                    self.clean_at_t(current_time, pyom)
            else:
                for dir in self.cleaner_folder:
                    while not self.image_t_exists(self.end, dir):
                        time.sleep(10)
                    self.clean_at_t(current_time, pyom)
        if self.astec_command == "astec_fusion" and len(
                self.cleaner_folder) > 1:  # Fusion has specific processing (no need to wait)
            for current_time in range(self.begin, self.end + 1):
                self.clean_at_t(current_time, pyom)  # Upload what hasn't been uploaded after while

        # upload xml and attachements at the end
        if self.omero_result:
            onlyfiles = []
            for dir in self.cleaner_folder:
                for f in os.listdir(dir):
                    if os.path.isfile(os.path.join(dir, f)):
                        onlyfiles.append(os.path.join(dir, f))
            for file in onlyfiles:
                if not is_file_image_or_compressed(file):
                    if pyom is not None:
                        print("Upload attachment file")
                        pyom.add_file_to_dataset(self.dataset_ids[0], file)
            if self.tag_list is not None and len(self.tag_list) > 0:
                dataset = pyom.get_dataset_by_id(self.dataset_ids[0], project=self.project_id)
                if dataset is not None:
                    for tag in self.tag_list:
                        pyom.add_tag(dataset, tag)
                    if tag_step != "":
                        pyom.add_tag(dataset, tag_step)
                else:
                    print("could not find dataset : " + str(self.dataset_ids[0]))
        self.copy_logs_files(source_logs, target_logs)  # Copy logs files to keep tracks of embryo history
        if self.omero_result:
            if os.path.isfile(xml_metadata):
                pyom.add_file_to_dataset(self.dataset_ids[0], xml_metadata)
        if pyom is not None:
            pyom.o_close()  #To prevent omero communication problems


def compute_input_folder(astec_command, params_dict):
    """ Compute input folder for Astec command depending on Parameters

    :param astec_command:
    :type astec_command: Str
    :param params_dict: list of parameters
    :type params_dict: dict
    :return: List of the folders used as input for step
    :rtype: list

    """
    dir_to_create = ""
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        if "EXP_FUSE" in params_dict:
            dir_to_create = "FUSE/FUSE_" + params_dict["EXP_FUSE"].replace("'", "").replace('"', '')
        else:
            dir_to_create = "FUSE/FUSE_RELEASE"
    elif "post" in astec_command.lower():
        if "EXP_SEG" in params_dict:
            dir_to_create = "SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"', '')
        else:
            dir_to_create = "SEG/SEG_RELEASE"
    else:
        return None
    return dir_to_create


class start_astec_command(Thread):
    """ Thread that is started to perform the ASTEC instance corresponding to current step """

    def __init__(self, astec_instance):
        Thread.__init__(self)
        self.astec_command = astec_instance.astec_command  #command to start
        self.embryo_folder = astec_instance.folder_embryo  #most of the time "."
        self.name_embryo = astec_instance.embryo_name
        self.begin = astec_instance.begin_time
        self.end = astec_instance.end_time
        self.mars_path = astec_instance.mars_path  #path to first time point for segmentation
        self.params_dict = astec_instance.params_dict  #list of parameters
        self.keep_temp = astec_instance.keep_temp  # true if we keep temp , false otherwise
        self.use_omero_input = astec_instance.omero_input  # should we use OMERO dataset as an input ?
        self.omero_config_file = astec_instance.omero_config_file  # path to omero authentication file
        self.omero_project_name = astec_instance.input_project  # project of the dataset to use in input
        self.omero_dataset_name = astec_instance.input_set  # dataset used as input
        self.astecenv = astec_instance.envastec  # which astec env to use : default "astec"
        self.paramsuffix = astec_instance.paramsuffix  #parameter file suffix for multi instances concurrent (should not be used)
        self.running_dir = ""

    def copy_logs_files(self, source_folder, target_folder):
        """ Copy logs files from source folder to target folder

        :param source_folder: 
        :param target_folder: 

        """
        range_t = len(source_folder)
        for i in range(0, range_t):
            if len(source_folder) > i and len (target_folder) > i:
                source = source_folder[i]
                target = target_folder[i]
                if os.path.isdir(source):
                    if not os.path.isdir(target):
                        os.makedirs(target)
                    onlyfiles = [f for f in os.listdir(source) if
                                 os.path.isfile(os.path.join(source, f)) and (".py" in f or ".log" in f)]
                    print("Copying logs from "+str(source))
                    for file in tqdm(onlyfiles):
                        subprocess.run(["cp", os.path.join(source, file), target])

    def run(self):
        """ Start the step running process, after handling data """
        print("Managining data for " + self.astec_command + " on embryo " + self.embryo_folder)
        final_command_arg0 = compute_astec_command(self.astec_command)
        self.running_dir = compute_astec_dir(self.astec_command, self.params_dict)  #retrieve working dir
        if self.use_omero_input:  # if we use omero for input data
            folder_target = compute_input_folder(self.astec_command,
                                                 self.params_dict)  # compute the corresponding folder
            if folder_target is None:
                print("Unable to comput input files folders , exiting")
                return
            for folder_t in folder_target:
                os.makedirs(folder_t)
            pyom = omerolib.connect(file_path=self.omero_config_file)
            pyom.download_omero_set(self.omero_project_name, self.omero_project_name,
                                    folder_target[0],min_time=self.begin,max_time=self.end)  # download the input data
        if final_command_arg0 != "astec_embryoproperties":  # all the process except properties needs a folder
            for dir in self.running_dir:
                if dir != "":
                    final_dir = dir.replace('"', '').replace("'", "").replace("[", "").replace("]", "")
                    if not os.path.isdir(final_dir):
                        os.makedirs(final_dir, mode=0o777)
            if self.mars_path is not None and final_command_arg0 == "astec_astec":  # for segmentation copy mars in the seg folder
                if not os.path.isdir(self.running_dir[0].replace("'", "").replace('"', '')):
                    os.makedirs(self.running_dir[0].replace("'", "").replace('"', ''), mode=0o777)
                print("Copying mars for " + self.astec_command + " on embryo " + self.embryo_folder)
                os.system("cp " + str(self.mars_path).replace("'", "").replace('"', '') + " " + str(
                    self.running_dir[0]).replace("'", "").replace('"', '') + "/")
        print("Generating parameters for " + self.astec_command + " on embryo " + self.embryo_folder)
        # create ASTEC parameters file and write it
        parameters_name = self.astec_command + "_" + self.running_dir[0].replace("/", "_").replace("\\",
                                                                                                   "_").replace(
            '"', '') + "_" + self.paramsuffix + ".py"
        parameter_content = ""
        parameter_content += 'PATH_EMBRYO = "."\n'
        parameter_content += 'EN = "' + str(self.name_embryo).replace("'", "").replace('"', '') + '"\n'
        parameter_content += 'begin = ' + str(int(self.begin)) + '\n'
        if self.end != -1:
            parameter_content += 'end = ' + str(int(self.end)) + '\n'
        for dict_key in self.params_dict:
            if not dict_key == "mars_path" and not dict_key == "begin" and not dict_key == "end" and not dict_key == "raw_delay" and not dict_key == "delta":  # manual exclude params that crash if string TODO: work to make this automatic
                value_param = self.params_dict[dict_key]
                #print("working on param "+dict_key+" -> "+str(value_param))
                if not isinstance(self.params_dict[dict_key], bool) and isinstance(self.params_dict[dict_key],
                                                                                   str) and not isinstance(
                        self.params_dict[dict_key], list):  # treat string params
                    #print("need to add the quotes")
                    if not '"' in self.params_dict[dict_key] and not "'" in self.params_dict[dict_key]:
                        value_param = "'" + self.params_dict[dict_key] + "'"
                parameter_content += str(dict_key) + ' = ' + str(value_param) + '\n'  # non string params
        print("Writing parameters file for " + self.astec_command)
        f = open(parameters_name, "w+")
        f.write(parameter_content)
        f.close()
        commandrun = ""
        if self.keep_temp:  #add -k to keep temps
            commandrun = " conda run -n " + self.astecenv + " " + final_command_arg0 + " -k -p " + parameters_name
        else:
            commandrun = " conda run -n " + self.astecenv + " " + final_command_arg0 + " -p " + parameters_name
        os.system(commandrun)
        print("Command finished for " + self.astec_command)
        inputf = compute_input_folder(self.astec_command, self.params_dict)
        if inputf is not None:
            source_logs = []
            target_logs = []
            for folder_i in inputf:
                source_logs.append(os.path.join(folder_i, "LOGS"))
            for inputfold in self.running_dir:
                target_logs.append(os.path.join(inputfold, "LOGS"))
            self.copy_logs_files(source_logs, target_logs)  # copy all log files
        os.system("rm " + parameters_name)


class Manager:
    """ The manager class that use parameters to determine steps , and what to do. This is called in the parameters files """

    def __init__(self, astec_env="astec"):
        self.running_sessions = []
        self.running_cleaners = []
        self.to_run_list = []
        self.stop_run = False
        self.astec_instance = astec_env

    def add_to_run(self, astec_command, folder_embryo, embryo_name, begin_time, params_dict=None, end_time=-1,
                   mars_path=None, compress_result=False, omero_result=False, omero_config_file="", tag_list=None,
                   keep_temp=False, paramsuffix="", omeroinput=False, inputproject=None,
                   inputset=None):
        """ This function adds an ASTEC instance to queue, but does not start it !

        :param astec_command: Command to start
        :type astec_command: str
        :param folder_embryo: embryo where to run everything (should be current folder)
        :type folder_embryo: str
        :param embryo_name:
        :type embryo_name: str
        :param begin_time:  First time point for the step
        :type begin_time: int
        :param params_dict:  dict of all parameters (astec or not) (Default value = None)
        :type params_dict: dict
        :param end_time:  Last time point if needed (Default value = -1)
        :type end_time: int
        :param mars_path:  Path to the first time point if segmentation (Default value = None)
        :type mars_path: str
        :param compress_result: Should we compress all the images generated  (Default value = False)
        :type compress_result: bool
        :param omero_result:  Should we upload to datamanager (Default value = False)
        :type omero_result: bool
        :param omero_config_file:  If upload to omero , path to authentication file (Default value = "")
        :type omero_config_file: str
        :param tag_list: List of tag to add to OMERO if uploaded (Default value = None)
        :type tag_list: list
        :param keep_temp: Should we keep temporary images generated by ASTEC (SHOULD ONLY BE USED FOR TESTS) (Default value = False)
        :type keep_temp: bool
        :param paramsuffix: Suffix added to parameters file (SHOULD NOT BE USED) (Default value = "")
        :type paramsuffix: str
        :param omeroinput: Should we use OMERO to retrieve ASTEC input files (Default value = False)
        :type omeroinput: bool
        :param inputproject: Project name for OMERO input files (Default value = None)
        :type inputproject: str
        :param inputset: Dataset name for OMERO input files (Default value = None)
        :type inputset: str

        """
        ai = astec_instance(astec_command, folder_embryo, embryo_name, mars_path, compress_result,
                            copy.deepcopy(params_dict),
                            begin_time, end_time, omero_result, omero_config_file, tag_list, keep_temp,
                            self.astec_instance,
                            paramsuffix, omeroinput, inputproject, inputset)
        self.to_run_list.append(ai)

    def generate_lineage(self, parameters):
        """ Generate the lineage and volume properties from a folder (that has to be a segmentation folder)

        :param parameters: Dict of parameters used to generate the lineage (embryo_name, begin, end, EXP_FUSE, EXP_SEG)
        :type parameters: dict
        :return: List of lineage and volume properties
        """
        if not "embryo_name" in parameters:
            print("embryo name is needed to generate lineage , exiting")
            return
        if not "begin" in parameters:
            print("begin time point (kexy : begin) is needed to generate lineage , exiting")
            return
        if not "end" in parameters:
            print("end time point (key : end) is needed to generate lineage , exiting")
            return
        fuse_exp = "01"
        seg_exp = "01"
        if "EXP_FUSE" in parameters:
            fuse_exp = parameters["EXP_FUSE"]
        if "EXP_SEG" in parameters:
            seg_exp = parameters["EXP_SEG"]
        embryo_name = parameters["embryo_name"]
        begin = int(parameters["begin"])
        end = int(parameters["end"])
        fuse_path = "FUSE/FUSE_" + str(fuse_exp) + "/"
        seg_path = "SEG/SEG_" + str(seg_exp) + "/"
        image_files = [f for f in os.listdir(fuse_path) if
                       os.path.isfile(os.path.join(fuse_path, f)) and (".nii" in f or ".mha" in f)]
        propertyfile = embryo_name + "_seg_lineage.xml"
        fuse_image_template = ""
        formatted_fuse_begin = "_t{:03d}".format(begin)
        for image in image_files:
            if formatted_fuse_begin in image:
                fuse_image_template = image.replace(formatted_fuse_begin, "_t%03d")
                break
        image_files = [f for f in os.listdir(seg_path) if
                       os.path.isfile(os.path.join(seg_path, f)) and (".nii" in f or ".mha" in f)]
        seg_image_template = ""
        formatted_seg_begin = "_t{:03d}".format(begin)
        for image in image_files:
            if formatted_seg_begin in image:
                seg_image_template = image.replace(formatted_seg_begin, "_t%03d")
                break
        command = "conda run -n astec mc-cellProperties -segmentation-format " + os.path.join(
            seg_path, seg_image_template) + " -first " + str(begin) + " -last " + str(end) + " -o " + os.path.join(
            seg_path, str(propertyfile)) + " -feature lineage -feature volume"
        os.system(command)
        if os.path.isfile(os.path.join(seg_path, str(propertyfile))):
            return True
        return False

    def start_running(self, thread_number=-1):
        """ Process all the queue of instances to run via threads

        :param thread_number: The number of threads that can run at the same time, if -1 will be automatically computed  (Default value = -1)
        :type thread_number: int

        """
        cpuCount = cpu_count()
        thread_count = cpuCount * 2 / 6
        if thread_number != -1:
            thread_count = thread_number
        for param in self.to_run_list:
            if len(self.running_sessions) >= thread_count:
                tc = self.running_sessions.pop(0)
                tc.join()
            tc = start_astec_command(param)  #start the command processing
            tc.start()
            if param.compress_result or param.omero_result:  # If we clean the output data
                tc2 = start_astec_cleaner(param.astec_command, param.params_dict, param.embryo_name, param.omero_result,
                                          param.begin_time, param.end_time,
                                          param.compress_result, param.omero_config_file, param.tag_list,
                                          param.keep_temp)
                tc2.start()
            self.running_sessions.append(tc)
            if param.compress_result or param.omero_result:
                self.running_cleaners.append(tc2)
            while len(self.running_sessions) > 0:
                tc = self.running_sessions.pop(0)
                if param.compress_result or param.omero_result:
                    tc2 = self.running_cleaners.pop(0)
                if tc is not None:
                    tc.join()
                if (param.compress_result or param.omero_result) and tc2 is not None:
                    tc2.stop_cleaning()
                    tc2.join()
        self.running_sessions = []
        self.running_cleaners = []
        self.to_run_list = []

    def compute_graphs_test_segmentation(self, embryo_name, begin, end, added_lineages=None,contourless=False):
        """ Generate the analysis data for test segmentation. This function uses the POST correction of segmentations
        generated during the test segmentation step. Other properties files can be added using the "added_lineages" parameter (list)

        If the test segmentation was run without contour images, set the "contourless" parameter at True
        Two plots are generated:
            - A graph of cell count evolution through time
            - A distribution of missing cells for each segmentation, by analyzing the lineage tree for each cell at first time point

        :param embryo_name:
        :type embryo_name: str
        :param begin: First time point of seg
        :type begin: int
        :param end:  Last time point of seg
        :type end: int
        :param added_lineages: Properties files to add to the computation (Default value = None)
        :type added_lineages: list
        :param contourless: Should this generate the graphs for segmentation ran without contours ?
        :type contourless: bool

        """

        folder_out = os.path.join("analysis/", "test_segmentation")
        lineages = [
            "POST/POST_test_maximum_gace/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_maximum_no_enhancment/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_addition_gace/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_addition_no_enhancment/" + embryo_name + "_post_lineage.xml"]
        names = ["POST_test_maximum_gace", "POST_test_maximum_no_enhancement", "POST_test_addition_gace",
                 "POST_test_addition_no_enhancement"]
        if contourless:
            lineages = [
                "POST/POST_test_maximum_gace_contourless/" + embryo_name + "_post_lineage.xml",
                "POST/POST_test_maximum_no_enhancment_contourless/" + embryo_name + "_post_lineage.xml",
                "POST/POST_test_addition_gace_contourless/" + embryo_name + "_post_lineage.xml",
                "POST/POST_test_addition_no_enhancment_contourless/" + embryo_name + "_post_lineage.xml"]
            names = ["POST_test_maximum_gace_contourless", "POST_test_maximum_no_enhancement_contourless", "POST_test_addition_gace_contourless",
                     "POST_test_addition_no_enhancement_contourless"]
        if added_lineages is not None:
            for lineage in added_lineages:
                lineages.append("POST/POST_" + str(lineage) + "/" + embryo_name + "_post_lineage.xml")
                names.append("POST_" + str(lineage))
        apply_analysis(lineages, names, folder_out, embryo_name, begin, end,data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")

    def compute_graphs_from_files(self, embryo_name, begin, end, lineage_list, name_list=None):
        """ Generate the analysis data for a given list of properties files, and their corresponding names displayed in the graphs legend

        Two plots are generated:
            - A graph of cell count evolution through time
            - A distribution of missing cells for each segmentation, by analyzing the lineage tree for each cell at first time point

        :param embryo_name:
        :type embryo_name: str
        :param begin: First time point of seg
        :type begin: int
        :param end:  Last time point of seg
        :type end: int
        :param lineage_list: List of xml to add to the computation
        type lineage_list: list
        :param name_list: Names for each lineage in lineage_list (Default value = None)

        """
        folder_out = os.path.join("analysis/", "post_segmentation")

        apply_analysis(lineage_list, name_list, folder_out, embryo_name, begin, end,
                       is_test=False,data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")

    def compute_graphs_post(self, embryo_name, begin, end, post_list, name_list=None):
        """ Generate the analysis data for a given list of POST correction experiments, and their corresponding names displayed in the graphs legend

        Two plots are generated:
            - A graph of cell count evolution through time
            - A distribution of missing cells for each segmentation, by analyzing the lineage tree for each cell at first time point

        :param embryo_name:
        :type embryo_name: str
        :param begin: First time point of seg
        :type begin: int
        :param end:  Last time point of seg
        :type end: int
        :param post_list: xml files to add to the computation
        :type post_list: list
        :param name_list: Names for each lineage in post_list (Default value = None)
        :type name_list: list

        """
        folder_out = os.path.join("analysis/", "post_segmentation")
        lineages = []
        names = []
        for exp_post in post_list:
            lineages.append("." + "/POST/POST_" + str(exp_post) + "/" + embryo_name + "_post_lineage.xml")
            names.append("POST_" + str(exp_post))
        if name_list is not None:
            names = name_list

        apply_analysis(lineages, names, folder_out, embryo_name, begin, end,
                       is_test=True, data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")

    def plot_signal_to_noise(self, embryo_name, parameters, one_stack_only=False, stack_chosen=0):
        """ Generate the plot of intensities means and std deviations in Raw Images determined by ASTEC parameters

        :param embryo_name:
        :type embryo_name: str
        :param parameters: Instance parameters to get raw data
        :type parameters: dict
        :param one_stack_only: Should we use only one stack in raw (Default value = False)
        :type one_stack_only: bool
        :param stack_chosen:  If we use only one stack , which one (Default value = 0)
        :type stack_chosen: int

        """
        print(
            "-> Analyzing raw data intensities, this step may be long (you can continue the pipeline , please do not delete Raw Images)")
        plotsignaltonoise(embryo_name, parameters, one_stack_only=one_stack_only, stack_chosen=stack_chosen)

    def generate_surface(self, exp_fuse, exp_post, begin, end, xml_output, embryo_name, exp_intraregistration):
        """ Generate surfaces in a post-correction instance of an intra-registration determined by the suffixes exp_fuse, exp_post and exp_intraregistration.
        The surface generation is done using the ASTEC process "mc-cellProperties"

        :param exp_fuse: suffix of fuse folder
        :type exp_fuse: str
        :param exp_post: suffix of post folder
        :type exp_post: str
        :param begin: first time point
        :type begin: int
        :param end: last time point
        :type end: int
        :param xml_output: path to the property file that will contain the surface property
        :type xml_output: str
        :param embryo_name:
        :type embryo_name: str
        :param exp_intraregistration: suffix to intrareg folder
        :type exp_intraregistration: str

        """
        fuse_path = "./INTRAREG/INTRAREG_" + str(exp_intraregistration) + "/FUSE/FUSE_" + str(exp_fuse)
        fuse_template = os.path.join(fuse_path, embryo_name + "_intrareg_fuse_t%03d.nii").replace("'", "").replace('"',
                                                                                                                   '')
        post_path = "./INTRAREG/INTRAREG_" + str(exp_intraregistration) + "/POST/POST_" + str(exp_post)
        post_template = os.path.join(post_path, embryo_name + "_intrareg_post_t%03d.nii").replace("'", "").replace('"',
                                                                                                                   '')
        os.system("conda run -n astec mc-cellProperties  -fusion-format " + str(
            fuse_template) + " -segmentation-format " + str(post_template) + " -first " + str(
            begin) + " -last " + str(end) + " -o " + str(
            xml_output) + " -feature contact-surface -feature barycenter -v -v -v -v -v")

    def generate_prop_naming_parameters(self, xml_folder, xml_file, embryo_name):
        """ Generate the parameter file used by ASCIDIAN process to propagate naming in a property file, and save it to disk

        :param xml_folder: folder containing the property file
        :type xml_folder: str
        :param xml_file: name of the file in the xml folder
        :type xml_file: str
        :param embryo_name:
        :type embryo_name: str
        :returns: path to the property file and list of atlas files used to propagate
        :rtype: tuple

        """
        atlas_path = compute_atlas()
        atlases_files = []
        now = datetime.now()
        parameters_name = "prop_naming" + str(now.timestamp()).replace('.', '') + ".py"
        txt = ""
        final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
        txt += "inputFile = '" + str(final_file) + "'" + "\n"
        txt += "outputFile = '" + str(final_file) + "'" + "\n"
        txt += "confidence_atlases_nmin = 2" + "\n"
        txt += "write_selection = False" + "\n"
        txt += "confidence_atlases_percentage = 0" + "\n"
        txt += 'atlasFiles = ' + str(atlas_path) + "\n"
        atlases_files.append("pm9.xml")
        f = open(parameters_name, "w+")
        f.write(txt)
        f.close()
        return parameters_name, atlas_path

    def backup_xml(self, xml_file):
        """ Perform a backup of a property file (used before naming)

        :param xml_file: Property file to back up
        :type xml_file: str

        """
        split_name = xml_file[1:len(xml_file)].split(".")
        backup_name = split_name[0] + "_backup." + split_name[1]
        os.system("cp " + str(xml_file) + " ." + str(backup_name))

    def compute_cell_count(self, first_time_point_segmentation):
        """ Read first time point segmentation image and compute the number of cells by counting labels

        :param first_time_point_segmentation: Path to segmentation image
        :type first_time_point_segmentation: str
        :returns: number of cells
        :rtype: int

        """
        count = -1
        image_first = imread(first_time_point_segmentation)
        if image_first is not None:
            count = len(np.unique(image_first)) - 1
        return count

    def generate_init_naming(self, xml_folder, xml_file, begin_time_name, embryo_name, exp_fuse, exp_post, begin, end,
                             exp_intraregistration,cell_count=None):
        """ Generate the naming of an embryo in a property file using ASCIDIAN atlas naming

        :param xml_folder: Folder containing the property file
        :type xml_folder: str
        :param xml_file: Name of the property file
        :type xml_file: str
        :param begin_time_name: Name of the first time point image
        :type begin_time_name: str
        :param embryo_name:
        :type embryo_name: str
        :param exp_fuse: Name of the fuse experiment
        :type exp_fuse: str
        :param exp_post: Name of the post experiment
        :type exp_post: str
        :param begin: First time point
        :type begin: int
        :param end: Last time point
        :type end: int
        :param exp_intraregistration: Name of the intrareg experiment
        :type exp_intraregistration: str

        """

        print(" -> Generate init naming")
        xml_path = os.path.join(xml_folder, xml_file)
        mars_path = os.path.join(xml_folder, begin_time_name)
        source = open(xml_path)
        tree = ET.parse(source)
        tree = tree.getroot()
        lineage_elem = tree.find("cell_contact_surface")
        print("     - backup xml")
        self.backup_xml(xml_path)
        surface_xml = xml_path.replace("lineage", "lineage_surfaces")
        print(xml_path)
        if lineage_elem is None:
            print("     - generate surfaces in side xml")
            self.generate_surface(exp_fuse, exp_post, begin, end, surface_xml, embryo_name, exp_intraregistration)
            print("     - merging 2 xml")
            os.system(
                "conda run -n astec astec_embryoproperties -i " + xml_path + " " + surface_xml + " -o " + xml_path)
            print("     - cleaning temp xml")
            os.system("rm " + str(surface_xml))
        print("     - compute cell count from mars")
        if cell_count is None:
            cell_count = self.compute_cell_count(mars_path)
        print("     - generate naming parameter file")
        parameter_file = self.generate_init_naming_parameters(cell_count, xml_folder, xml_file, embryo_name)
        print("     - running naming")

        os.system("conda run -n ascidian ascidian_naming_timepoint -v -v -v -p " + str(
            parameter_file))
        os.system("rm " + str(parameter_file))

    def propagate_naming(self, xml_folder, xml_file, embryo_name):
        """ Apply the propagation of a naming in a property file using ASCIDIAN contact naming

        :param xml_folder: Folder containing the property file
        :type xml_folder: str
        :param xml_file: Name of the property file
        :type xml_file: str
        :param embryo_name:
        :type embryo_name: str

        :returns: Atlas files used for naming
        :rtype: list

        """
        print(" -> Propagate naming")
        print("     - generate parameters")
        parameter_file, atlases_files = self.generate_prop_naming_parameters(xml_folder, xml_file, embryo_name)
        print("     - propagation of naming")
        os.system("conda run -n ascidian ascidian_naming_propagation -v -v -v -p " + str(
            parameter_file))
        print("     - cleaning")
        os.system("rm " + str(parameter_file))
        return atlases_files

    def writeStepToJson(self, parameters, step, embryo_folder=".", logFolder=None):
        """ Write the current step metadata and logs from parameter and logFolder to the metadata file

        :param parameters: Instance parameters
        :type parameters: dict
        :param step: which step
        :type step: str
        :param embryo_folder:  (Default value = ".")
        :type embryo_folder: str
        :param logFolder: folder containing the log files (Default value = None)
        :type logFolder: str

        """
        parameters["step"] = step
        addDictToMetadata(embryo_folder, parameters, addDate=True, logFolder=logFolder)

    def generate_shift_to_boundingbox(self,parameters):
        """ Read all the images of given post corrected segmentation, and generate for each cell, the ratio between the cell bounding box volume and the cell volume.
        The segmentation is given by the EXP_POST, post experiment suffix, and the EXP_INTRAREG, intraregestration experiment suffix. The background value can be provided
        by the "BACKGROUND" parameter. If BACKGROUND parameter is not set, "1" is used as a background value.
        The code has the possibility to compute inside the non-registered image (only in the POST/POST_**), or in the registered image (in INTRAREG/INTRAREG_**/POST/POST_**). Use the "generate_in_intraregistration" parameters (shoudl be True or False)
        The ratio values by cell are stored in the properties files

        :param parameters: Dict of parameters for the generation, see above for details
        :type parameters: dict

        """
        from skimage.measure import regionprops
        area_by_t_id = {}
        bboxarea_by_t_id = {}
        background = 1
        generate_in_intra = False
        EXP_INTRA = "01"
        if "EXP_INTRAREG" in parameters:
            EXP_INTRA = parameters["EXP_INTRAREG"]
        if "generate_in_intraregistration" in parameters:
            generate_in_intra = bool(parameters["generate_in_intraregistration"])
        if "BACKGROUND" in parameters:
            background = int(parameters["BACKGROUND"])
        post_path = "POST/POST_"
        if "EXP_POST" in parameters:
            post_path += parameters["EXP_POST"]
        else:
            post_path += "RELEASE"
        if generate_in_intra:
            post_path = "INTRAREG/INTRAREG_"+str(EXP_INTRA)+"/"+post_path
        if not os.path.exists(post_path):
            print("POST folder is not found, please verify that the segmentation processed without errors")
            return
        print(post_path)
        xmls = [f for f in os.listdir(post_path) if
                os.path.isfile(os.path.join(post_path, f)) and f.endswith("lineage.xml")]
        properties_path = os.path.join(post_path, xmls[0])
        image_files = [f for f in os.listdir(post_path) if
                       os.path.isfile(os.path.join(post_path, f)) and f.endswith((".nii",".mha",".nii.gz",".mha.gz"))]
        if not os.path.isfile(properties_path):
            print(
                "Error during generation , input file does not exist or can't be accessed. Check the path, and the rights of the file. ")
            return
        min_time = 9999999
        max_time = -1
        cell_list = LoadCellList(properties_path)
        for cell in cell_list:
            cell_t, cell_id = get_id_t(str(cell))
            if cell_t < min_time:
                min_time = cell_t
            if cell_t > max_time:
                max_time = cell_t
        if min_time == 9999999:
            print(
                "Unable to find the minimum time point in the 'cell_lineage' property. Please verify that the property is correct")
            return
        if max_time == -1:
            print(
                "Unable to find the maximum time point in the 'cell_lineage' property. Please verify that the property is correct")
            return
        for cell_t in range(min_time, max_time + 1):
            if len( [f for f in image_files if "_t{:03d}".format(cell_t) in f]) > 0 :
                found_image = os.path.join(post_path, [f for f in image_files if "_t{:03d}".format(cell_t) in f][0])
                if os.path.exists(found_image) and os.path.isfile(found_image):
                    image = imread(found_image)
                    # list_ids = np.unique(image)
                    objects = regionprops(image)
                    for obj in objects:
                        if obj["label"] != background:
                            volume = obj["area"]
                            roivolume = obj["area_bbox"]
                            if volume > 0 and roivolume > 0:
                                if not cell_t in area_by_t_id:
                                    area_by_t_id[cell_t] = {}
                                if not obj["label"] in area_by_t_id[cell_t]:
                                    area_by_t_id[cell_t][obj["label"]] = volume
                                if not cell_t in bboxarea_by_t_id:
                                    bboxarea_by_t_id[cell_t] = {}
                                if not obj["label"] in bboxarea_by_t_id[cell_t]:
                                    bboxarea_by_t_id[cell_t][obj["label"]] = roivolume
                            else:
                                print("Volume or ROI volume is 0")
                else:
                    print("Image not found for time point : " + str(cell_t) + " please verify path to : " + found_image)
        ratio_by_id = {}
        bb_by_id = {}
        vol_by_id = {}
        for timepoint in area_by_t_id:
            if timepoint in bboxarea_by_t_id:
                for label in bboxarea_by_t_id[timepoint]:
                    cell_name = get_longid(timepoint, label)
                    bb_by_id[cell_name] = bboxarea_by_t_id[timepoint][label]
            if timepoint in area_by_t_id:
                for label in area_by_t_id[timepoint]:
                    cell_name = get_longid(timepoint, label)
                    vol_by_id[cell_name] = area_by_t_id[timepoint][label]
            if timepoint in bboxarea_by_t_id:
                for label in area_by_t_id[timepoint]:
                    if label in bboxarea_by_t_id[timepoint]:
                        ratio = bboxarea_by_t_id[timepoint][label] / area_by_t_id[timepoint][label]
                        cell_name = get_longid(timepoint, label)
                        ratio_by_id[cell_name] = ratio
        intraxmls = [f for f in os.listdir(post_path) if
                     os.path.isfile(os.path.join(post_path, f)) and f.endswith("post_lineage.xml")]
        final_xml = os.path.join(post_path, intraxmls[0])
        AddNodeToXML(final_xml, ratio_by_id, "float_boundingbox_to_cell_ratio", "cell", identifier_text="cell-id")
        AddNodeToXML(final_xml, bb_by_id, "float_scikit_boundingbox_volume", "cell", identifier_text="cell-id")
        AddNodeToXML(final_xml, vol_by_id, "float_scikit_cell_volume", "cell", identifier_text="cell-id")
    def load_data_for_lineage(self,lineage1, target_generation=-1, info_name="float_boundingbox_to_cell_ratio"):
        names_lineage_1 = Get_Cell_Names(lineage1)
        cell_list_lineage_1 = LoadCellList(lineage1)
        cell_count_by_t_lineage_1 = count_cells(lineage1)
        sorted_cellcount_lineage_1 = dict(sorted(cell_count_by_t_lineage_1.items()))
        min1, max1, ratio_lineage_1 = Get_Cell_Values_Float(lineage1, info_name, filter_background=True)
        ratio_by_cell_lineage_1 = {}
        ratio_history_by_name_lineage_1 = {}
        ratios_by_t_lineage_1 = {}
        for cell in names_lineage_1:
            if cell in ratio_lineage_1:
                ratio_by_cell_lineage_1[cell] = float(ratio_lineage_1[cell])

        min_t_lineage_1 = 999
        max_t_lineage_1 = -1
        min_val_ratio = 1000000
        max_val_ratio = -1
        for cell in names_lineage_1:
            gen = int(get_gen_from_cell_name(names_lineage_1[cell]))
            if (target_generation == gen or target_generation == -1) and cell in ratio_by_cell_lineage_1:
                print("Cell is from the chosen gen : " + names_lineage_1[cell])
                cell_min = GetCellMinTimePoint(cell_list_lineage_1[cell])  # we can be more efficient
                cell_minid = str(get_longid(cell_min.t, cell_min.id))
                if cell_minid in names_lineage_1:
                    print(cell_minid)
                    if not names_lineage_1[cell_minid] in ratio_history_by_name_lineage_1:
                        history = {}
                        celllife = GetCellLifetime(cell_list_lineage_1[cell_minid])
                        for cellval in celllife:
                            cell_minid_val = str(get_longid(cellval.t, cellval.id))
                            if cell_minid_val in ratio_by_cell_lineage_1:
                                if min_t_lineage_1 > cellval.t:
                                    min_t_lineage_1 = cellval.t
                                if max_t_lineage_1 < cellval.t:
                                    max_t_lineage_1 = cellval.t
                                if (ratio_by_cell_lineage_1[cell_minid_val] < min_val_ratio):
                                    min_val_ratio = ratio_by_cell_lineage_1[cell_minid_val]
                                if (ratio_by_cell_lineage_1[cell_minid_val] > max_val_ratio):
                                    max_val_ratio = ratio_by_cell_lineage_1[cell_minid_val]
                                if not cellval.t in ratios_by_t_lineage_1:
                                    ratios_by_t_lineage_1[cellval.t] = []
                                ratios_by_t_lineage_1[cellval.t].append(ratio_by_cell_lineage_1[cell_minid_val])
                                history[cellval.t] = ratio_by_cell_lineage_1[cell_minid_val]
                            ratio_history_by_name_lineage_1[names_lineage_1[cell_minid]] = history
        return ratios_by_t_lineage_1, ratio_history_by_name_lineage_1, min_t_lineage_1, max_t_lineage_1, min_val_ratio, max_val_ratio, sorted_cellcount_lineage_1

    def plot_found_ratios(self,parameters):
        """ Using a list of POST experiment names, a list of intrareg experiment names, plot on a graph and save this graph to file, the evolution of the ratio
        between the volume of the bounding box of a cell, and the volume of this cell. Will compute the same graph for the whole embryo.

        If the parameter compute_individual_cells is set to True, a graph is created for each named cell.
        The code has the possibility to compute inside the non-registered image (only in the POST/POST_**), or in the registered image (in INTRAREG/INTRAREG_**/POST/POST_**). Use the "generate_in_intraregistration" parameters (shoudl be True or False)

        :param parameters: Dict of parameters for the graph, detailed above
        :type parameters: dict
        """
        import matplotlib.pyplot as plt
        generate_in_intra = False
        if "generate_in_intraregistration" in parameters:
            generate_in_intra = bool(parameters["generate_in_intraregistration"])

        target_generations = parameters["target_generations"]
        exp_post = parameters["EXP_POST"]
        exp_intrareg = []
        names = parameters["EXP_POST"]
        if "NAMES" in parameters:
            names = parameters["NAMES"]
        if "EXP_INTRAREG" in parameters:
            exp_intrareg = parameters["EXP_INTRAREG"]
        compute_individual_cells = parameters["compute_individuals_cells"]
        lineage_list = []
        final_names = []
        for i in range(0, len(exp_post)):
            if generate_in_intra:
                postpath = "INTRAREG/INTRAREG_" + str(exp_intrareg[i]) + "/POST/POST_" + str(exp_post[i]) + "/"
            else :
                postpath = "POST/POST_" + str(exp_post[i]) + "/"
            xmls = [f for f in os.listdir(postpath) if
                    os.path.isfile(os.path.join(postpath, f)) and f.endswith("lineage.xml")]
            if len(xmls) > 0:
                properties_path = os.path.join(postpath, xmls[0])
                if os.path.isfile(properties_path):
                    lineage_list.append(properties_path)
                    final_names.append(names[i])
        # compute for all cells , independant of generation
        final_max = -1
        final_min = 99999
        final_min_val_ratio = 999
        final_max_val_ratio = -1
        ratios_by_t_list = []
        ratios_history_by_name_lineage_list = {}
        sorted_cellcount_by_t_list = []
        plt.figure(figsize=(10, 6))  # Setup figure
        plt.title("Volume ratio between bounding box and cell for all generations ")
        plt.xlabel("Time")
        plt.ylabel("Ratio")
        path = os.path.join("analysis", "bbox_to_cell_ratio", "all_gen")
        if not os.path.exists(path):
            os.makedirs(path)
        image = os.path.join(path, "ratio_by_t.png")
        for i in range(0, len(lineage_list)):
            lineage_path = lineage_list[i]
            ratios_by_t_lineage_1, ratio_history_by_name_lineage_1, min_t_lineage_1, max_t_lineage_1, min_val_ratio, max_val_ratio, sorted_cellcount_lineage_1 = self.load_data_for_lineage(
                lineage_path)
            if min_t_lineage_1 < final_min:
                final_min = min_t_lineage_1
            if max_t_lineage_1 > final_max:
                final_max = max_t_lineage_1
            if min_val_ratio < final_min_val_ratio:
                final_min_val_ratio = min_val_ratio
            if max_val_ratio < final_max_val_ratio:
                final_max_val_ratio = max_val_ratio
            ratios_by_t_list.append(ratios_by_t_lineage_1)
            sorted_cellcount_by_t_list.append(sorted_cellcount_lineage_1)
            # ratios_history_by_name_lineage_list.append(ratio_history_by_name_lineage_1)
            for name in ratio_history_by_name_lineage_1:
                if not name in ratios_history_by_name_lineage_list:
                    ratios_history_by_name_lineage_list[name] = {}
                ratios_history_by_name_lineage_list[name][lineage_list[i]] = ratio_history_by_name_lineage_1[name]
        for i in range(0, len(lineage_list)):
            timepointlist = []
            value = []
            stddevminus = []
            stddevplus = []
            sorted_dict = dict(sorted(ratios_by_t_list[i].items()))
            for timepoint in sorted_dict:
                timepointlist.append(timepoint)
                value.append(np.mean(sorted_dict[timepoint]))
                stddevminus.append(np.mean(sorted_dict[timepoint]) - np.std(sorted_dict[timepoint]))
                stddevplus.append(np.mean(sorted_dict[timepoint]) + np.std(sorted_dict[timepoint]))
            plt.plot(timepointlist, value, '-', alpha=0.5, label=final_names[i])
            plt.fill_between(timepointlist, stddevminus, stddevplus, alpha=0.2)
            plt.xlim(final_min, final_max)
        plt.legend()
        plt.tight_layout()
        plt.savefig(image)
        plt.clf()

        for target_generation in target_generations:
            final_max = -1
            final_min = 99999
            final_min_val_ratio = 999
            final_max_val_ratio = -1
            ratios_by_t_list = []
            ratios_history_by_name_lineage_list = {}
            sorted_cellcount_by_t_list = []
            plt.figure(figsize=(10, 6))  # Setup figure
            plt.title("Volume ratio between bounding box and cell for generation " + str(target_generation))
            plt.xlabel("Time")
            plt.ylabel("Ratio")
            path = os.path.join("analysis", "bbox_to_cell_ratio", "gen_" + str(target_generation))
            if not os.path.exists(path):
                os.makedirs(path)
            image = os.path.join(path, "ratio_by_t.png")
            for i in range(0, len(lineage_list)):
                lineage_path = lineage_list[i]
                ratios_by_t_lineage_1, ratio_history_by_name_lineage_1, min_t_lineage_1, max_t_lineage_1, min_val_ratio, max_val_ratio, sorted_cellcount_lineage_1 = self.load_data_for_lineage(
                    lineage_path, target_generation=target_generation)
                if min_t_lineage_1 < final_min:
                    final_min = min_t_lineage_1
                if max_t_lineage_1 > final_max:
                    final_max = max_t_lineage_1
                if min_val_ratio < final_min_val_ratio:
                    final_min_val_ratio = min_val_ratio
                if max_val_ratio < final_max_val_ratio:
                    final_max_val_ratio = max_val_ratio
                ratios_by_t_list.append(ratios_by_t_lineage_1)
                sorted_cellcount_by_t_list.append(sorted_cellcount_lineage_1)
                # ratios_history_by_name_lineage_list.append(ratio_history_by_name_lineage_1)
                for name in ratio_history_by_name_lineage_1:
                    if not name in ratios_history_by_name_lineage_list:
                        ratios_history_by_name_lineage_list[name] = {}
                    ratios_history_by_name_lineage_list[name][lineage_list[i]] = ratio_history_by_name_lineage_1[name]
            for i in range(0, len(lineage_list)):
                timepointlist = []
                value = []
                stddevminus = []
                stddevplus = []
                sorted_dict = dict(sorted(ratios_by_t_list[i].items()))
                for timepoint in sorted_dict:
                    timepointlist.append(timepoint)
                    value.append(np.mean(sorted_dict[timepoint]))
                    stddevminus.append(np.mean(sorted_dict[timepoint]) - np.std(sorted_dict[timepoint]))
                    stddevplus.append(np.mean(sorted_dict[timepoint]) + np.std(sorted_dict[timepoint]))
                plt.plot(timepointlist, value, '-', alpha=0.5, label=final_names[i])
                plt.fill_between(timepointlist, stddevminus, stddevplus, alpha=0.2)
                plt.xlim(final_min, final_max)
            plt.legend()
            plt.tight_layout()
            plt.savefig(image)
            plt.clf()
            if compute_individual_cells:
                for i in range(0, len(lineage_list)):
                    for name_key in ratios_history_by_name_lineage_list:
                        path = os.path.join("analysis", "bbox_to_cell_ratio", "gen_" + str(target_generation))
                        if not os.path.exists(path):
                            os.makedirs(path)
                        image = os.path.join(path, name_key + ".png")
                        plt.figure(figsize=(10, 6))  # Setup figure
                        plt.title("Volume ratio between bounding box and cell for generation " + str(target_generation))
                        plt.xlabel("Time")
                        plt.ylabel("Ratio")
                        plt.xlim(final_min, final_max)
                        for lineage in ratios_history_by_name_lineage_list[name_key]:
                            timepointlist = []
                            value = []
                            sorted_dict = dict(sorted(ratios_history_by_name_lineage_list[name_key][lineage].items()))
                            for timepoint in sorted_dict:
                                timepointlist.append(timepoint)
                                value.append(sorted_dict[timepoint])
                            plt.plot(timepointlist, value, '-', alpha=0.5,
                                     label=final_names[i])
                        plt.legend()
                        plt.tight_layout()
                        plt.savefig(image)
                        plt.clf()
    def downscale_post_folder(self, parameters):
        """ Apply a downscaling to a specific folder (mainly used for Fusion images)

        :param parameters: Dict of parameters for downscaling step, cf doc for more details
        :type parameters: dict


        """
        voxel_size = float(parameters["resolution"])
        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "POST/POST_" + str(parameters["EXP_POST"]))
        output_folder = os.path.join(embryo_folder, "POST/POST_" + str(parameters["EXP_POST"])+"_down06")
        template_format = parameters["template_file"]
        input_voxel_size = 0.3
        if not "input_resolution" in parameters:
            parameters["input_resolution"] = input_voxel_size
        else:
            input_voxel_size = float(parameters["input_resolution"])
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        print("Downscaling folder : "+str(input_folder))
        for file in tqdm(files):
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_folder, file)
                time = int(file.split("_t")[1].split(".")[0])
                img_t = os.path.join(output_folder, file)
                img_template = template_format.format(time)
                os.system("conda run -n astec setVoxelSize " + str(img_path) + " " + str(
                    input_voxel_size) + " " + str(input_voxel_size) + " " + str(input_voxel_size))
                os.system("conda run -n astec applyTrsf -ref " + str(img_template) + " -iso " + str(
                    voxel_size) + " " + img_path + " " + img_t)
    def downscale_folder(self, parameters):
        """ Apply a downscaling to a specific folder (mainly used for Fusion images)

        :param parameters: Dict of parameters for downscaling step, cf doc for more details
        :type parameters: dict


        """
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        omero_config_file = get_omero_config(parameters)
        voxel_size = float(parameters["resolution"])
        input_voxel_size = 0.3
        if not "input_resolution" in parameters:
            parameters["input_resolution"] = input_voxel_size
        else:
            input_voxel_size = float(parameters["input_resolution"])
        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]))
        output_folder = os.path.join(embryo_folder,
                                     "FUSE/FUSE_" + str(parameters["EXP_FUSE"]) + "_down0" + str(voxel_size).split(".")[
                                         1])
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        print("Downscaling folder : "+str(input_folder))
        for file in tqdm(files):
            img_path = os.path.join(input_folder, file)
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                os.system("conda run -n astec setVoxelSize " + str(img_path) + " " + str(
                    input_voxel_size) + " " + str(input_voxel_size) + " " + str(input_voxel_size))
                img_t = os.path.join(output_folder, file)
                os.system("conda run -n astec applyTrsf -iso " + str(voxel_size) + " " + img_path + " " + img_t)

        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name,
                                 "FUSE_" + str(parameters["EXP_FUSE"]) + "_down0" + str(voxel_size).split(".")[1],
                                 output_folder)

    def downscale_contour_folder(self, parameters):
        """ Apply a downscaling to specific contour images computed from parameters

        :param parameters: Dict of parameters used for downscaling step, cf doc for more details
        :type parameters: dict

        """
        voxel_size = float(parameters["resolution"])
        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "CONTOUR/CONTOUR_" + str(parameters["EXP_CONTOUR"]))
        output_folder = os.path.join(embryo_folder, "CONTOUR/CONTOUR_" + str(parameters["EXP_CONTOUR_DOWNSCALED"]))
        template_format = parameters["template_file"]
        input_voxel_size = 0.3
        if not "input_resolution" in parameters:
            parameters["input_resolution"] = input_voxel_size
        else:
            input_voxel_size = float(parameters["input_resolution"])
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        print("Downscaling folder : " + str(input_folder))
        for file in tqdm(files):
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_folder, file)
                time = int(file.split("_t")[1].split(".")[0])
                print("     -> " + str(img_path))
                img_t = os.path.join(output_folder, file)
                img_template = template_format.format(time)
                os.system("conda run -n astec setVoxelSize " + str(img_path) + " " + str(
                    input_voxel_size) + " " + str(input_voxel_size) + " " + str(input_voxel_size))
                os.system("conda run -n astec applyTrsf -ref " + str(img_template) + " -iso " + str(
                    voxel_size) + " " + img_path + " " + img_t)

    def save_upload_parameters(self, omero_project_name, omero_dataset_name, embryo_folder, user=None,min_time=1,max_time=1):
        """ Write the metadata corresponding to a datamanager upload to the metadata file of the embryo

        :param omero_project_name: Name of the project on omero
        :type omero_project_name: str
        :param omero_dataset_name: Name of the dataset on omero
        :type omero_dataset_name: str
        :param embryo_folder: folder of the embryo (most of the time ".")
        :type embryo_folder: str
        :param user: User who performed the step (Default value = None)
        :type user: str
        :param min_time: Minimum time (Default value = 1)
        :type min_time: int
        :param max_time: Maximum time (Default value = 1)
        :type max_time: int
        """
        parameters = {}
        parameters["user"] = user
        parameters["omero_project"] = omero_project_name
        parameters["omero_dataset"] = omero_dataset_name
        parameters["input_folder"] = embryo_folder
        parameters["min_time"] = min_time
        parameters["max_time"] = max_time
        self.writeStepToJson(parameters, "upload_to_omero", embryo_folder=".")

    def upload_on_omero(self, config_file, omero_project_name, omero_dataset_name, input_folder, include_logs=False,
                        embryo_name=None, user=None,min_time=-1,max_time=-1,update_comment=False,params=None):
        """ Process the upload on OMERO data manager of a folder

        :param config_file: Authentication file for OMERO
        :str omero_project_name: Name of the project on omero
        :param omero_project_name: Name of the project on OMERO , project is created if it doesn't exist
        :type omero_project_name: str
        :param omero_dataset_name: Name of the dataset on OMERO, dataset is created if it doesn't exist
        :type omero_dataset_name: str
        :param input_folder: Path to the folder to upload (has to contain images)
        :type input_folder: str
        :param include_logs:  If True , will include logs folder content as annotation (Default value = False)
        :type include_logs: bool
        :param user: User who process upload (Default value = None)
        :type user: str
        :param min_time: Minimum time (Default value = -1)
        :type min_time: int
        :param max_time: Maximum time (Default value = -1)
        :type max_time: int
        :param update_comment: If set to True , change comment of the dataset on OMERO using the parameters list
        :type update_comment: bool
        :param params: If update comment is True, is those parameters as comment on Omero
        :type params: dict
        """
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        om_group = config_array['group']
        om_secure = config_array['secure']
        embryo_folder = "."
        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        pyom.upload_omero_set(omero_project_name.replace("'", "").replace('"', '').strip(),
                              omero_dataset_name.replace("'", "").replace('"', '').strip(),
                              input_folder.replace("'", "").replace('"', ''), include_logs=include_logs,min_time=min_time,max_time=max_time,update_comment=update_comment,params=params)
        self.save_upload_parameters(omero_project_name, omero_dataset_name, embryo_folder, user,min_time=min_time,max_time=max_time)
        self.upload_file_to_project(omero_project_name.replace("'", "").replace('"', ''), os.path.join(embryo_folder, "metadata.json"), pyom)

    def download_from_omero_all(self, dataset, project, output_folder, om_login, om_pw, om_host, om_port, om_group="",
                                om_secure=False,min_time=-1,max_time=-1,download_metadata=False,metadata_folder="."):
        """ Process the download from OMERO datamanager dataset, into a specific folder

        :param dataset: Name of the dataset on OMERO
        :type dataset: str
        :param project: Name of the project on OMERO
        :type project: str
        :param output_folder: Path to the folder that will contain the downloaded images
        :type output_folder: str
        :param om_login: Login in datamanager
        :type om_login: str
        :param om_pw: User password in datamanager
        :type om_pw: str
        :param om_host: URL of the OMERO instance
        :type om_host: str
        :param om_port: Port of the OMERO instance
        :type om_port: int
        :param om_group: Group that contains the dataset (Default value = "")
        :type om_group: str
        :param om_secure: Type of connection used for download (vary depending on the instance) (Default value = False)
        :type om_secure: bool
        :param min_time: Minimum time to download the images (Default value = -1)
        :type min_time: int
        :param max_time: Maximum time to download the images (Default value = -1)
        :type max_time: int

        """
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        pyom.download_omero_set(project.replace("'", "").replace('"', ''),
                                dataset.replace("'", "").replace('"', ''),
                                output_folder.replace("'", "").replace('"', ''),min_time=min_time,max_time=max_time)
        if download_metadata:
            pyom.get_file_from_project(project.replace("'", "").replace('"', ''),metadata_folder)


    def parse_no_suffix(self, dataset_name):
        """ Determine the subfolder to download from the name of the dataset, used for whole project download

        :param dataset_name: Omero Dataset name
        :type dataset_name: str
        :returns: Relative path to save image
        :rtype: str

        """
        if dataset_name.lower() == "mars":
            return "SEG/MARS"
        if dataset_name.lower() == "seg":
            return "SEG/SEG_RELEASE"
        if dataset_name.lower() == "post":
            return "POST/POST_RELEASE"
        if dataset_name.lower() == "fuse":
            return "FUSE/FUSE_RELEASE"
        if dataset_name.lower() == "background":
            return "BACKGROUND/BACKGROUND_RELEASE"
        if dataset_name.lower() == "contour":
            return "CONTOUR/CONTOUR_RELEASE"
        return None

    def parse_subfolder(self, dataset_subname):
        """ Determine what subfolder will be used to store downloaded images, used for whole project download

        :param dataset_subname: OMERO dataset split subname
        :type dataset_subname: str
        :returns: Name of the folder in embryo folder
        :rtype: str

        """
        if dataset_subname.lower() in ["fuse", "fusion"]:
            return "FUSE"
        if dataset_subname.lower() in ["seg", "segmentation", "astec"]:
            return "SEG"
        if dataset_subname.lower() in ["post", "postcorr"]:
            return "POST"
        if dataset_subname.lower() == "background":
            return "BACKGROUND"
        if dataset_subname.lower() == "contour":
            return "CONTOUR"
        return None

    def compute_dataset_path(self, dataset_name):
        """ Using a dataset name on OMERO, determine the folder where it should be downloaded on disk, used for whole project download.
        The architecture of the folders is adapted for lemaire lab usage

        :param dataset_name: Name of the dataset on OMERO
        :type dataset_name: str
        :returns: Where to save the dataset
        :rtype: str

        """
        moved_corr = False
        splitted_name = dataset_name.split("_")
        print(splitted_name)
        if splitted_name[0].lower() in ["corr", "curated"]:  # Moving CORR to the end
            elem = splitted_name.pop(0)
            splitted_name.insert(len(splitted_name), elem)
            moved_corr = True
            print(splitted_name)
        if not "_" in dataset_name:
            return self.parse_no_suffix(dataset_name)
        elif len(splitted_name) == 2 and moved_corr:
            parsed = self.parse_no_suffix(splitted_name[0])
            if parsed is None:
                return None
            return parsed + "_" + splitted_name[-1]
        else:
            no_intra_name = False
            if splitted_name[0].lower() in ["int", "intrareg"]:
                path = "INTRAREG/INTRAREG_"
                if len(splitted_name) > 1:
                    if splitted_name[1].lower() not in ["fuse", "post", "seg"]:
                        path += splitted_name[1]
                    else:
                        path += "RELEASE"
                        no_intra_name = True
                if len(splitted_name) == 2 and no_intra_name:
                    suffix = self.parse_no_suffix(splitted_name[1])
                    if suffix is None:
                        return None
                    path += "/" + suffix + "/" + suffix + "_RELEASE/"
                    return path
                if len(splitted_name) > 2:
                    if (len(splitted_name) == 3 and not no_intra_name) or (
                            len(splitted_name) == 4 and moved_corr and not no_intra_name) or (
                            len(splitted_name) == 4 and not moved_corr and no_intra_name) and (
                            len(splitted_name) == 5 and moved_corr and no_intra_name):
                        suffix = self.parse_no_suffix(splitted_name[1])
                        if suffix is None:
                            return None
                        if len(splitted_name) == 3:
                            path += "/" + suffix + "/"
                        if len(splitted_name) == 4 and moved_corr:
                            path += "/" + suffix + splitted_name[-1] + "/"
                    else:
                        if no_intra_name:
                            subfolder = self.parse_subfolder(splitted_name[1])
                            if subfolder is None:
                                return None
                            path += "/" + subfolder + "/"
                            path += subfolder
                            for i in range(2, len(splitted_name)):
                                path += "_" + splitted_name[i]
                            path += "/"
                        else:
                            subfolder = self.parse_subfolder(splitted_name[2])
                            if subfolder is None:
                                return None
                            path += "/" + subfolder + "/"
                            path += subfolder
                            for i in range(3, len(splitted_name)):
                                path += "_" + splitted_name[i]
                            path += "/"
                return path
            else:
                path = ""
                if len(splitted_name) > 1:
                    subfolder = self.parse_subfolder(splitted_name[0])
                    if subfolder is None:
                        return None
                    path += subfolder + "/"
                    path += subfolder
                    for i in range(1, len(splitted_name)):
                        path += "_" + splitted_name[i]
                    path += "/"
                else:
                    return None
                return path

    def download_whole_embryo(self, parameters):
        """ Download a complete project on OMERO datamanager, and save it to a specific architecture (embryo like) on disk.
        More details can be found in AstecManager Documentation

        :param parameters: Parameters for download
        :type parameters: dict

        """
        config_file = get_omero_config(parameters)
        omero_project_name = parameters["project_name"].replace('"', '').replace("'", "")
        output_folder = parameters["output_folder"]
        if config_file is None:
            print("OMERO config file is not bound, unable to upload")
            return
        if not os.path.isfile(config_file):
            print("Unable to find OMERO config file , unable to upload")
            return
        embryo_dir = os.path.join(output_folder, omero_project_name)
        if not os.path.isdir(embryo_dir):
            os.makedirs(embryo_dir)
        if not os.path.isdir(embryo_dir):
            print("Unable to create embryo directory")
            return
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        min_time = -1
        if "min_time" in parameters:
            min_time = int(parameters["min_time"])
        max_time = -1
        if "max_time" in parameters:
            max_time = int(parameters["max_time"])
        om_group = ""
        if 'group' in config_array:
            om_group = config_array['group']
        om_secure = config_array['secure']
        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        datasets = []
        project = None
        for p in pyom.list_projects():
            if p.getName().lower() == omero_project_name.lower():
                project = p
                datasets = list(p.listChildren())
                break
        if project is None:
            print("Embryo not found on OMERO")
            return
        if len(datasets) < 1:
            print("No datasets in embryo on OMERO")
            return
        print("Downloading project : " + project.getName())
        for dataset in datasets:
            # Compute outputfolder
            print("Downloading dataset : " + dataset.getName())
            dataset_subfolder = self.compute_dataset_path(dataset.getName())
            if dataset_subfolder is not None:
                dataset_ouput_folder = os.path.join(embryo_dir, dataset_subfolder)
                print(" - in : " + dataset_ouput_folder)
                pyom.download_omero_set_by_id(dataset.getId(), dataset_ouput_folder,min_time=min_time,max_time=max_time)  # TESTS ONLY
            else:
                print("Unable to compute path for dataset : " + dataset.getName())
        pyom.get_file_from_project(project.replace("'", "").replace('"', ''), ".")

    def mha_to_nii(self, parameters):
        """ Convert all images at mha format from the folder to nii format
        :param parameters: List of parameters (should only contain key folder)
        :type parameters: dict

        """
        image_folder = parameters["folder"]
        if os.path.isdir(image_folder):
            onlyfiles = [f for f in os.listdir(image_folder) if
                         os.path.isfile(os.path.join(image_folder, f)) and ".mha" in f]
            print("Converting to omero friendly format")
            for file in tqdm(onlyfiles):
                new_path = file.replace(".mha", ".nii")
                os.system("conda run -n astec copy " + os.path.join(image_folder, file) + " " + os.path.join(image_folder,new_path))
                if os.path.isfile(os.path.join(image_folder, new_path)):
                    os.system("rm " + os.path.join(image_folder, file))

    def upload_step_dir(self, project_name, step_folder, pyom, prefix=""):
        """ Upload the result of AstecManager step to OMERO, into a given project , by creating a new dataset

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param step_folder: Folder where to find the images
        :type step_folder: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object
        :param prefix: add prefix to dataset name (Default value = "")
        :type prefix: str

        """
        print("intrareg upload from  : "+str(step_folder))
        step_subdirs = [f for f in os.listdir(step_folder) if os.path.isdir(os.path.join(step_folder, f))]
        current_step = step_folder.split("/")[-1]
        print("current step : "+str(current_step))
        print("found subdirs : "+str(step_subdirs))
        for subdir in step_subdirs:
            print("subdir : "+str(subdir))
            if subdir.lower().startswith(current_step.lower()):  # Only upload data folders, not system ones
                try:
                    self.convert_step_dir(os.path.join(step_folder, subdir))
                except:
                    print("Unable to convert images to OMERO format, but continue uploading")
                print("uploading : "+str(os.path.join(step_folder, subdir)))
                print("to : "+str(prefix + subdir))
                print("for project : "+str(project_name))
                pyom.upload_omero_set(project_name, prefix + subdir, os.path.join(step_folder, subdir), include_logs=(
                    os.path.isdir(os.path.join(os.path.join(step_folder, subdir), "LOGS"))))
    def upload_transform_step_dir(self, project_name, step_folder, pyom, prefix=""):
        """ Upload the transformation files computed during intra-registration into a given project

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param step_folder: Folder where to find the images
        :type step_folder: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object
        :param prefix: add prefix to dataset name (Default value = "")
        :type prefix: str

        """
        print("intrareg upload from  : "+str(step_folder))
        current_step = step_folder.split("/")[-1]
        pyom.upload_omero_set(project_name, prefix + current_step, step_folder, include_logs=False)

    def convert_step_dir(self, dir, extension="mha"):
        """ Convert the images contained in the given directory from given extension to "nii"

        :param dir: Folder where to find the images
        :type dir: str
        :param extension: Input file extension (Default value = "mha")
        :type extension: str

        """
        mhaimagefiles = [f for f in os.listdir(dir) if
                         os.path.isfile(os.path.join(dir, f)) and "." + extension in f]
        print("Conversion ")
        for image in tqdm(mhaimagefiles):
            mhaimage = os.path.join(dir, image)
            niiimage = mhaimage.replace("." + extension, ".nii")
            if not os.path.isfile(niiimage):
                os.system("conda run -n astec copy " + mhaimage + " " + niiimage)

    def upload_rec_dir(self, project_name, step_folder, pyom, prefix=""):
        """ Upload the reconstruction temporary images from ASTEC segmentation to OMERO

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param step_folder: Folder where to find the images
        :type step_folder: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object
        :param prefix: add prefix to dataset name (Default value = "")
        :type prefix: str

        """
        step_subdirs = [f for f in os.listdir(step_folder) if os.path.isdir(os.path.join(step_folder, f))]
        for subdir in step_subdirs:
            splitted_subs = subdir.split("_")
            dataset_name = subdir
            if prefix != "":
                dataset_name = splitted_subs[0] + "_" + prefix
                for i in range(1, len(splitted_subs)):
                    dataset_name += "_" + splitted_subs[i]
            try:
                self.convert_step_dir(os.path.join(step_folder, subdir))
            except:
                print("Unable to convert images to OMERO format, but continue uploading")
            pyom.upload_omero_set(project_name, dataset_name, os.path.join(step_folder, subdir),
                                  include_logs=(os.path.isdir(os.path.join(os.path.join(step_folder, subdir), "LOGS"))))

    def upload_file_to_project(self, project_name, filepath, pyom):
        """ Call OmeroTools library to add a file by path to a project attachments list

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param filepath: Path to the file to be uploaded
        :type filepath: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object

        """
        pyom.add_file_to_project(project_name, filepath)

    def upload_file_to_dataset(self, dataset_id, filepath, pyom):
        """ Call OmeroTools library to add a file by path to a dataset attachments list

        :param dataset_id: ID of the dataset on OMERO
        :type dataset_id: str
        :param filepath: Path to the file to be uploaded
        :type filepath: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object

        """
        pyom.add_file_to_dataset(dataset_id, filepath)

    def upload_analysis_dir(self, project_name, step_folder, pyom):
        """ Upload the analysis graphs from AstecManager segmentations to OMERO attachments

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param step_folder: Folder where to find the images
        :type step_folder: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object

        """
        analysis_subdirs = [f for f in os.listdir(step_folder) if os.path.isdir(os.path.join(step_folder, f))]
        for subdir in analysis_subdirs:
            print("# TODO")
            dir = os.path.join(step_folder, subdir)
            to_upload = [f for f in os.listdir(dir) if
                         os.path.isfile(os.path.join(dir, f)) and (".mp4" in f or ".png" in f)]
            for filename in to_upload:
                filepath = os.path.join(dir, filename)
                self.upload_file_to_project(project_name, filepath, pyom)

    def upload_intrareg_dir(self, project_name, step_folder, pyom):
        """ Upload an intrareg instance of AstecManager to OMERO (separate function because different architectures)

        :param project_name: Name of the project on OMERO
        :type project_name: str
        :param step_folder: Folder where to find the images
        :type step_folder: str
        :param pyom: OMERO client object (omerotools lib)
        :type pyom: omerotools client object

        """
        print("Uploading intrareg")
        step_subdirs = [f for f in os.listdir(step_folder) if os.path.isdir(os.path.join(step_folder, f))]

        for subdir in step_subdirs:
            print("listing in : "+str(subdir))
            final_prefix = subdir + "_"
            intra_subdirs = [f for f in os.listdir(os.path.join(step_folder, subdir)) if
                             os.path.isdir(os.path.join(os.path.join(step_folder, subdir), f)) and f.lower() in ["fuse",
                                                                                                                 "seg",
                                                                                                                 "post",
                                                                                                                 "background",
                                                                                                                 "contour",
                                                                                                                 "rec-membrane"]]
            for isd in intra_subdirs:
                self.upload_step_dir(project_name, os.path.join(os.path.join(step_folder, subdir), isd), pyom,
                                     prefix=final_prefix)

            # UPLOAD TRANSFORMATION FILES
            intra_trsfdirs = [f for f in os.listdir(os.path.join(step_folder, subdir)) if
                            os.path.isdir(os.path.join(os.path.join(step_folder, subdir), f)) and f.lower().startswith("trsfs_")]

            for trsf in intra_trsfdirs:
                print("Uploading transformation folder : "+str(trsf))
                self.upload_transform_step_dir(project_name, os.path.join(os.path.join(step_folder, subdir), trsf), pyom,
                                     prefix=final_prefix)

    def upload_whole_embryo(self, parameters):
        """Upload a complete project on OMERO datamanager, from a specific architecture (embryo like) on disk.
        More details can be found in AstecManager Documentation

        :param parameters: Parameters for upload
        :type parameters: dict
        """
        print("Uploading whole embryo ")
        config_file = get_omero_config(parameters)
        embryo_name = parameters["project_name"].replace('"', '').replace("'", "").strip()
        input_folder = parameters["embryo_folder"]
        if config_file is None:
            print("OMERO config file is not bound, unable to upload")
            return
        if not os.path.isfile(config_file):
            print("Unable to find OMERO config file , unable to upload")
            return
        embryo_dir = input_folder
        if not os.path.isdir(embryo_dir):
            print("Embryo dir does not exist")
            return
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        om_group = ""
        if 'group' in config_array:
            om_group = config_array['group']
        om_secure = config_array['secure']
        print("Loaded omero config")
        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        #upload_omero_set(self,project_name,dataset_name,input_folder,mintime=None,maxtime=None,tag_list=None,include_logs=False)
        project = None
        project_name = None
        for p in pyom.list_projects():
            if p.getName().lower() == embryo_name.lower():
                project = p.getName()
                project_name = p.getName()
                break
        if project is None:
            print("Embryo not found on OMERO")
            # create it
            project = pyom.create_project(embryo_name)
            project_name = embryo_name
        if project is None:
            print("Unable to create OMERO project")
            return
        print("Found project")
        step_subdirs = [f for f in os.listdir(embryo_dir) if
                        os.path.isdir(os.path.join(embryo_dir, f)) and f.lower() in ["fuse", "seg", "post",
                                                                                     "background", "contour",
                                                                                     "rec-membrane", "rec-seed"]]
        for step_subdir in step_subdirs:
            print("Uploading "+str(step_subdir))
            if "rec-" in step_subdir.lower():
                prefix = "MEMBRANE"
                if "seed" in step_subdir.lower():
                    prefix = "SEED"
                self.upload_rec_dir(project_name, os.path.join(embryo_dir, step_subdir), pyom, prefix=prefix)
            else:
                self.upload_step_dir(project_name, os.path.join(embryo_dir, step_subdir), pyom)
        print("Finding intrareg to upload")
        intra_subdirs = [f for f in os.listdir(embryo_dir) if
                         os.path.isdir(os.path.join(embryo_dir, f)) and f.lower() == "intrareg"]
        for intra in intra_subdirs:
            self.upload_intrareg_dir(project_name, os.path.join(embryo_dir, intra), pyom)
        if os.path.isdir(os.path.join(embryo_dir, "analysis")):
            self.upload_analysis_dir(project_name, os.path.join(embryo_dir, "analysis"), pyom)
        if os.path.isfile(os.path.join(embryo_dir, "metadata.json")):
            self.upload_file_to_project(project_name, os.path.join(embryo_dir, "metadata.json"), pyom)

    def download_from_omero(self, parameters):
        """ Download a given dataset from omero to disk. Parameters are given by a dict, more details can be found in AstecManager documentation

        :param parameters: Dict of download parameters
        :type parameters: dict

        """
        config_file = get_omero_config(parameters)
        omero_project_name = parameters["project_name"].replace('"', '').replace("'", "")
        omero_dataset_name = parameters["dataset_name"]
        output_folder = parameters["destination_folder"]
        if config_file is None:
            print("OMERO config file is not bound, unable to upload")
            exit()
        if not os.path.isfile(config_file):
            print("Unable to find OMERO config file , unable to upload")
            exit()
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        min_time = -1
        if "min_time" in parameters:
            min_time = int(parameters["min_time"])
        max_time = -1
        if "max_time" in parameters:
            max_time = int(parameters["max_time"])
        om_group = ""
        if 'group' in config_array:
            om_group = config_array['group']
        om_secure = config_array['secure']
        download_metadata = True
        if os.path.isfile("metadata.json"):
            download_metadata = False
        self.download_from_omero_all(omero_dataset_name, omero_project_name, output_folder, om_login, om_pw, om_host,
                                     om_port, om_group, om_secure,min_time=min_time,max_time=max_time,download_metadata=download_metadata,metadata_folder=".")

    def compute_segmentation_from_junctions(self, parameters):
        """ Compute semantic segmentations from a given junction instance. Refer to AstecManager documentation for more details


        :param parameters: Dict of parameters for semantic segmentation
        :type parameters: dict


        """

        omero_config_file = get_omero_config(parameters)
        junction_folder_name = "JUNC_" + parameters["EXP_JUNC"]
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        user = compute_user(parameters)
        embryo_folder = "./"
        semantic_seg_path, semantic_seg_name = compute_segmentation_from_junctions(embryo_folder, junction_folder_name)
        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, semantic_seg_name,
                                 semantic_seg_path,update_comment=True,params=parameters)
        parameters["contour_folder"] = semantic_seg_path
        self.writeStepToJson(parameters, "compute_semantic_seg", embryo_folder=".")

    def compute_data_from_junctions(self, parameters):
        """ Start the generation of images from the Semantic images generated by deep learning. It can be :

         - Computation of contours images by extracting external membranes (this is working but is not the best)
         - Membrane segmentation of the semantic images by labeling

         Refer to AstecManager documentation for more details

        :param parameters: Dict of parameters for contour and semantic segmentation (many are commons)
        :type parameters: dict
        """
        compute_contour = True
        compute_segmentation = True
        if parameters["compute_contour"] is not None:
            compute_contour = bool(parameters["compute_contour"])
        if parameters["compute_segmentation"] is not None:
            compute_segmentation = bool(parameters["compute_segmentation"])
        if compute_contour:
            self.compute_contours_from_junctions(parameters)
        if compute_segmentation:
            self.compute_segmentation_from_junctions(parameters)

    def compute_contours_from_junctions(self, parameters):
        """ Computation of contours images by extracting external membranes from semantic images (this is working but is not the best)

         Refer to AstecManager documentation for more details


        :param parameters: Dict of parameters for contour
        :type parameters: dict

        """

        omero_config_file = get_omero_config(parameters)
        normalisation = parameters["normalisation"]
        junction_folder_name = "JUNC_" + parameters["EXP_JUNC"]
        voxel_size = parameters["resolution"]
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        embryo_folder = "./"
        folder_contour_path, folder_contour_name = compute_contour_from_junctions(embryo_folder, junction_folder_name,
                                                                                  reducvoxelsize=float(voxel_size),
                                                                                  target_normalization_max=normalisation,
                                                                                  correction_vsize=True)
        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, folder_contour_name,
                                 folder_contour_path,update_comment=True,params=parameters)
        parameters["contour_folder"] = folder_contour_path
        self.writeStepToJson(parameters, "compute_contour", embryo_folder=".")

    def filter_segmentation_with_background(self,parameters,background_value=1):
        """ Filter the segmentation by applying background value , where the background is detected in background
        detector image

        :param parameters: Dict of parameters for contour
        :type parameters: dict
        :param background_value: value to apply as background in the segmentation image , default value = 1
        :type background_value: int

        """
        exp_background = parameters["EXP_BACKGROUND"]
        background_folder = "BACKGROUND/BACKGROUND_" + exp_background+"/"
        begin = int(parameters["begin"])
        end = int(parameters["end"])
        if os.path.isdir(background_folder):
            segmentation_folder = parameters["segmentation_folder"]
            if os.path.isdir(segmentation_folder):
                for i in range(begin,end+1):
                    segmentation_files = [f for f in os.listdir(segmentation_folder) if os.path.isfile(os.path.join(segmentation_folder, f)) and (".nii" in f or ".mha" in f) and "_t{:03d}".format(i) in f]
                    background_files = [f for f in os.listdir(background_folder) if
                                        os.path.isfile(os.path.join(background_folder, f)) and (
                                                    ".nii" in f or ".mha" in f) and "_background_t{:03d}".format(i) in f]
                    for file in segmentation_files:
                        seg_img,voxel_size = imread(os.path.join(segmentation_folder,file),voxel_size=True)
                        filtered_background,voxel_size = fill_image(background_files[0],background_folder)
                        background_coords = np.where(filtered_background==False)
                        seg_img[background_coords] = background_value
                        imsave(os.path.join(segmentation_folder,file),seg_img,voxel_size=voxel_size)

    def compute_membranes_from_junctions(self, parameters):
        """ Generate enhanced membranes images that will be used as inputs in ASTEC from semantic images.

        This is done using a semantic images folder computed by the deep learning network, extract all membranes and apply a smoothing and normalization.

        Refer to AstecManager documentation for more details


        :param parameters: Dict of parameters for contour
        :type parameters: dict

        """

        omero_config_file = get_omero_config(parameters)
        normalisation = parameters["normalisation"]
        junction_folder_name = "JUNC_" + parameters["EXP_JUNC"]
        voxel_size = parameters["resolution"]
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        embryo_folder = "./"
        flat_normalization = ("flat_normalization" in parameters and parameters["flat_normalization"])
        folder_contour_path, folder_contour_name = compute_membranes_from_junctions(embryo_folder,
                                                                                    junction_folder_name,
                                                                                    reducvoxelsize=float(voxel_size),
                                                                                    target_normalization_max=normalisation,
                                                                                    correction_vsize=True,flat_normalization=flat_normalization)

        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, folder_contour_name,
                                 folder_contour_path,update_comment=True,params=parameters)
        parameters["contour_folder"] = folder_contour_path
        self.writeStepToJson(parameters, "compute_membranes", embryo_folder=".")


    def compute_contours(self, parameters):
        """ Compute contours from a given background instance.

        Refer to AstecManager documentation for more details


        :param parameters: Dict of parameters for contour
        :type parameters: dict


        """

        omero_config_file = get_omero_config(parameters)
        normalisation = parameters["normalisation"]
        background_folder_name = parameters["EXP_BACKGROUND"]
        voxel_size = parameters["resolution"]
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        user = compute_user(parameters)
        embryo_folder = "./"
        folder_contour_path, folder_contour_name = compute_contour(embryo_folder, background_folder_name,
                                                                   reducvoxelsize=float(voxel_size),
                                                                   target_normalization_max=normalisation,
                                                                   correction_vsize=True)
        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, folder_contour_name,
                                 folder_contour_path,update_comment=True,params=parameters)
        parameters["contour_folder"] = folder_contour_path
        self.writeStepToJson(parameters, "compute_contour", embryo_folder=".")

    def name_embryo(self, parameters):
        """ Start the naming of an embryo : generate surfaces of contact if missing, then generates an initial naming by atlas.

        Finally, propagate this name by ascidian atlas naming

        Refer to AstecManager documentation for more details

        :param parameters: Dict of naming parameters
        :type parameters: dict

        """
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        begin = parameters["begin"]
        end = parameters["end"]
        cell_count = None
        if "cell_count" in parameters:
            cell_count = parameters["cell_count"]
        lineage_path = "./INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]) + "/POST/POST_" + parameters[
            "EXP_POST"] + "/"
        mars_prefix = "_intrareg_post_t{:03d}.nii"
        lineage_name = embryo_name + "_intrareg_post_lineage.xml"
        mars_filename = embryo_name + mars_prefix.format(begin)
        mars_path = os.path.join(lineage_path, embryo_name + mars_prefix.format(begin))
        print("working on mars : " + mars_path)
        if not os.path.isfile(mars_path):
            mars_filename = mars_filename + ".gz"
        self.generate_init_naming(lineage_path.replace('"', '').replace("'", ""),
                                  lineage_name.replace('"', '').replace("'", ""),
                                  mars_filename.replace('"', '').replace("'", ""),
                                  embryo_name.replace('"', '').replace("'", ""),
                                  str(parameters["EXP_FUSE"]).replace('"', '').replace("'", ""),
                                  str(parameters["EXP_POST"]).replace('"', '').replace("'", ""), begin, end,
                                  str(parameters["EXP_INTRAREG"]).replace('"', '').replace("'", ""),cell_count=cell_count)
        self.propagate_naming(lineage_path.replace('"', '').replace("'", ""),
                              lineage_name.replace('"', '').replace("'", ""),
                              embryo_name.replace('"', '').replace("'", ""))
        parameters["atlas"] = compute_atlas()
        logFolder = "./INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]).replace('"', '').replace("'",
                                                                                                      "") + "/LOGS/"
        self.writeStepToJson(parameters, "name_embryo", embryo_folder=".", logFolder=logFolder)

    def load_microscope_metadata(self,raw_folder):
        """
        This function find JSON metadata files from Raw Images, and read them to extract the necessary metadata, to save them in the embryo metadata

        :param raw_folder: Path to folder containing the Raw Images stack and channel folders
        :type raw_folder: str
        :returns: Extracted metadata
        :rtype: dict
        """
        path = Path(raw_folder)
        if path.exists():
            globjson = path.glob("*/*.json")
            for result in globjson:
                if result.name.lower().startswith("cam_left") or result.name.lower().startswith("cam_right"):
                    final_data = retrieveMicroscopeMetadata(str(result))
                    return final_data
        return None

    def copy_raw_data(self, parameters):
        """ Start the copy of embryo Raw Data from distant folder.
        It is possible to add a delay in minutes by using "delay_before_copy" parameters.

        After the copy, a backup can be made on another server, and then compression on this backup server.

        Refer to AstecManager documentation for more details.

        :param parameters: Dict of parameters for copy
        :type parameters: dict

        """

        searcher = compute_user(parameters)
        if not "embryo_name" in parameters:
            print("Embryo name is not provided in parameters ")
            exit()
        if not "distant_folder" in parameters:
            print("Distant raw data folder path is not provided in parameters")
            exit()
        input_folder = parameters["distant_folder"]
        delay_before_copy = 0
        if "delay_before_copy" in parameters:
            delay_before_copy = int(parameters["delay_before_copy"])
        embryo_dir = "."
        if not os.path.isdir(embryo_dir):
            os.makedirs(embryo_dir)
        raw_data_output = os.path.join(embryo_dir, "RAWDATA")
        copy_on_cold_storage = ("copy_on_distant_storage" in parameters and parameters["copy_on_distant_storage"])
        compress = ("compress_on_distant_storage" in parameters and parameters["compress_on_distant_storage"])
        if not os.path.isdir(raw_data_output):
            os.makedirs(raw_data_output)
        if delay_before_copy > 0:
            print("Sleeping " + str(delay_before_copy) + " minutes before copying RAW DATA")
            time.sleep(delay_before_copy * 60)  #delay is given in minutes, transform in seconds
        try:
            command = "rsync -avzr --exclude=.DS_Store --exclude=*.py --exclude=*.log "+str(str(input_folder)+"/*")+" "+str(raw_data_output + "/")
            print("Synchronizing from distant input folder to current")
            subprocess.run(command,shell=True)
            microscopemetadata = self.load_microscope_metadata(raw_data_output)
            if microscopemetadata is not None:
                for key in microscopemetadata:
                    parameters[key] = microscopemetadata[key]
            self.writeStepToJson(parameters, "copy_rawdata", embryo_folder=".")
            if copy_on_cold_storage:
                cold_storage_container = parameters["distant_storage_folder"]
                cold_storage_address = parameters["distant_storage_address"]
                if not cold_storage_container.endswith("/"):
                    cold_storage_container = cold_storage_container + "/"
                folder_to_copy = os.path.join("..", parameters["embryo_name"])
                try:
                    print("Copying the synchronized data to distant storage folder")
                    command = "rsync -avzr --exclude=.DS_Store --exclude=*.py --exclude=*.log " + str(folder_to_copy) + " " + cold_storage_address+":"+cold_storage_container
                    subprocess.run(command,shell=True)
                    if compress:
                        #print("Compressing on distant storage")
                        #print(command)
                        command = "ssh "+str(cold_storage_address)+" 'cd "+str(os.path.join(cold_storage_container, parameters["embryo_name"]))+" ; gzip */*/*.h5'"
                        subprocess.run(command,shell=True)
                        #print(command)
                        command = "ssh "+str(cold_storage_address)+" 'cd "+str(os.path.join(cold_storage_container, parameters["embryo_name"]))+" ; gzip  */*.h5'"
                        subprocess.run(command, shell=True)
                except subprocess.CalledProcessError:
                    print(
                        'Error during the copy of the data on the distant storage , please verify the access to the storage')
        except subprocess.CalledProcessError:
            print('Error during the copy of the data on the local computer , please verify the parameters and try again')


    def downscale_mars(self, parameters):
        """ Apply the downscaling to the first time point segmentation, using the corresponding fusion image for template.
        Refer to AstecManager documentation for more details on parameters

        :param parameters: Mars downscaling parameters
        :type parameters: dict

        """
        voxel_size = parameters["resolution"]
        if not "mars_file" in parameters:
            print("Please specify a MARS file path")
            exit()
        if not "output_folder" in parameters:
            print("Please specify the folder for the downscaled file")
            exit()
        if not "template_file" in parameters:
            print("Please specify the corresponding fusion image (downscaled version)")
            exit()
        mars = parameters["mars_file"]
        if not os.path.isfile(mars):
            print(str(mars))
            print("MARS file does not exist")
            exit()
        fusion = parameters["template_file"]
        if not os.path.isfile(fusion):
            print("template file does not exist")
            exit()
        output_folder = parameters["output_folder"]
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        marsname = mars.replace("\\", "/").split("/")[-1]
        output_file = os.path.join(output_folder, marsname)
        input_voxel_size = 0.3
        if not "input_resolution" in parameters:
            parameters["input_resolution"] = input_voxel_size
        else:
            input_voxel_size = float(parameters["input_resolution"])
        os.system("conda run -n astec setVoxelSize " + str(mars) + " " + str(
            input_voxel_size) + " " + str(input_voxel_size) + " " + str(input_voxel_size))
        os.system("conda run -n astec applyTrsf -ref " + str(fusion) + " -interpolation nearest -iso " + str(
            voxel_size) + " " + str(mars) + " " + str(output_file))
        self.writeStepToJson(parameters, "downscale_mars", embryo_folder=".")

    def apply_downscaling(self, parameters):
        """ Apply a downscaling on the following images for an embryo : fusion , contour and first time point segmentation.
        The same downscaling parameters are used for all three.

        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of parameters for downscaling
        :type parameters: dict

        """
        downscale_contour = bool(parameters["apply_on_contour"])
        if not "embryo_name" in parameters:
            print("Please specify a embryo name")
            exit()
        if not "begin" in parameters:
            print("Please specify a begin point")
            exit()
        if not "EXP_FUSE" in parameters:
            print("Please specify a fuse exp")
            exit()
        if downscale_contour and not "EXP_CONTOUR" in parameters:
            print("Please specify a contour exp")
            exit()
        if downscale_contour and not "EXP_CONTOUR_DOWNSCALED" in parameters:
            print("Please specify a contour exp downscaled")
            exit()
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        embryo_folder = "."
        voxel_size = 0.6
        input_voxel_size = 0.3
        time_point = 0
        if "begin" in parameters:
            time_point = int(parameters["begin"])
        if not "resolution" in parameters:
            parameters["resolution"] = voxel_size
        else:
            voxel_size = float(parameters["resolution"])
        if not "input_resolution" in parameters:
            parameters["input_resolution"] = input_voxel_size
        else:
            input_voxel_size = float(parameters["input_resolution"])
        mars_path = os.path.join(embryo_folder, "MARS/" + embryo_name + "_mars_t{:03d}.nii".format(time_point))
        parameters["mars_file"] = mars_path
        mars_output_path = os.path.join(embryo_folder, "MARS0" + str(voxel_size).split(".")[1] + "/")
        parameters["output_folder"] = mars_output_path

        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]))
        fusion_output_dir = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]) + "_down0" +
                                         str(voxel_size).split(".")[1])
        input_fuse_template = os.path.join(fusion_output_dir, embryo_name + "_fuse_t{:03d}.nii".format(time_point))
        parameters["template_file"] = input_fuse_template
        print("     > Downscaling Fusion")
        self.downscale_folder(parameters)
        print("     > Downscaling Mars")
        self.downscale_mars(parameters)
        input_fuse_template = os.path.join(fusion_output_dir, embryo_name + "_fuse_t{:03d}.nii")
        parameters["template_file"] = input_fuse_template
        #Create function that downscale countours
        if downscale_contour:
            print("     > Downscaling Contours")
            self.downscale_contour_folder(parameters)

    def generate_init_naming_parameters(self, cell_count, xml_folder, xml_file, embryo_name):
        """ Generate the parameter files needed for ASCIDIANS initial naming.

        :param cell_count: Number of cells for starting time point
        :type cell_count: int
        :param xml_folder: Folder containing property file to name
        :type xml_folder: str
        :param xml_file: Name of the property file to use for naming
        :type xml_file: str
        :param embryo_name: Name of the embryo
        :type embryo_name: str

        :returns: path to the parameter file created
        :rtype: str
        """
        atlas_path = compute_atlas()
        now = datetime.now()
        parameters_name = "init_naming" + str(now.timestamp()).replace('.', '') + ".py"
        final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
        txt = ""
        txt += "inputFile = '" + str(final_file) + "'" + "\n"
        txt += "outputFile = '" + str(final_file) + "'" + "\n"
        txt += "cell_number = " + str(cell_count) + "\n"
        txt += 'atlasFiles = ' + str(atlas_path) + "\n"
        txt += "check_volume=False" + "\n"
        f = open(parameters_name, "w+")
        f.write(txt)
        f.close()
        return parameters_name

    def test_fusion(self, parameters, parameter_exploration=False, rerun=False, one_stack_only=False, stack_chosen=0):
        """ Start the step of test fusion in the pipeline.
        The default behavior is to test only one fusion, with the usually working parameters.

        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of parameters for fusion
        :type parameters: dict
        :param parameter_exploration: If True, the test will be run in 4 instances, to test different sets of parameters (Default value = False)
        :type parameter_exploration: bool
        :param rerun: Deprecated, use parameter_exploration (Default value = False)
        :type rerun: bool
        :param one_stack_only: If true, only use one stack for fusion (Default value = False)
        :type one_stack_only: bool
        :param stack_chosen: If one stack only fusion is chosen , index of the stack to use (0 or 1) (Default value = 0)
        :type stack_chosen: int


        """
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        parameters["fusion_xzsection_extraction"] = True
        # TESTS DEPENDENT PARAMETERS, DO NOT CHANGE
        #
        #
        #
        if rerun or parameter_exploration:
            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_right_hierarchical"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters, run_now=False, keep_temp=False, one_stack_only=one_stack_only,
                              stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "direct-fusion"
            parameters["EXP_FUSE"] = "01_right_direct"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters, run_now=False, keep_temp=False, one_stack_only=one_stack_only,
                              stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_left_hierarchical"
            parameters["acquisition_orientation"] = "left"

            self.start_fusion(parameters, run_now=False, keep_temp=False, one_stack_only=one_stack_only,
                              stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "direct-fusion"
            parameters["EXP_FUSE"] = "01_left_direct"
            parameters["acquisition_orientation"] = "left"

            self.start_fusion(parameters, run_now=False, keep_temp=False, one_stack_only=one_stack_only,
                              stack_chosen=stack_chosen)
            self.start_running(thread_number=4)
        else:
            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_test"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters, keep_temp=False, one_stack_only=one_stack_only, stack_chosen=stack_chosen)

    def start_fusion(self, parameters, run_now=True, keep_temp=False, channel_count=1, one_stack_only=False,
                     stack_chosen=0):
        """ Start a fusion step of the pipeline with the provided parameters.


        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of fusion parameters
        :type parameters: dict
        :param run_now: If true, the fusion will be run now. If false, it will not be run , and its expected that it is started later (Default value = True)
        :type run_now: bool
        :param keep_temp: If true, ASTEC temporary files will be kept (Default value = False)
        :type keep_temp: bool
        :param channel_count: The number of channel during the fusion (Default value = 1)
        :type channel_count: int
        :param one_stack_only: If true, only use one stack for fusion (Default value = False)
        :type one_stack_only: bool
        :param stack_chosen: If one stack only fusion is chosen , index of the stack to use (0 or 1) (Default value = 0)
        :type stack_chosen: int
        :returns: The parameters dictionary updated with all the parameters automatically added
        :rtype: dict
        """
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")

        begin = parameters["begin"]
        end = parameters["end"]
        real_parameters = {}
        real_parameters["acquisition_resolution"] = (.195, .195, 1.)
        real_parameters["target_resolution"] = .3
        real_parameters["result_image_suffix"] = 'nii'
        real_parameters["acquisition_slit_line_correction"] = True
        real_parameters["acquisition_cropping_opening"] = 2
        real_parameters["acquisition_cropping"] = False
        real_parameters["raw_crop"] = True
        real_parameters["fusion_crop"] = True

        real_parameters["fusion_preregistration_compute_registration"] = True
        real_parameters["fusion_preregistration_normalization"] = False
        real_parameters["fusion_registration_normalization"] = False
        real_parameters["fusion_stack_preregistration_normalization"] = False
        real_parameters["fusion_stack_registration_normalization"] = False
        real_parameters["fusion_xzsection_extraction"] = False

        # DATA DEPENDENT PARAMETERS , SHOUD NOT CHANGE IF UPDATED ONCE
        #
        #
        #

        real_parameters["DIR_RAWDATA"] = "RAWDATA"
        if (one_stack_only and stack_chosen == 0) or not one_stack_only:
            real_parameters["DIR_LEFTCAM_STACKZERO"] = "stack_0_channel_0_obj_left"
            real_parameters["DIR_RIGHTCAM_STACKZERO"] = "stack_0_channel_0_obj_right"
        if (one_stack_only and stack_chosen == 1) or not one_stack_only:
            real_parameters["DIR_LEFTCAM_STACKONE"] = "stack_1_channel_0_obj_left"
            real_parameters["DIR_RIGHTCAM_STACKONE"] = "stack_1_channel_0_obj_right"
        if channel_count > 1:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_1"] = "stack_0_channel_1_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_1"] = "stack_0_channel_1_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_1"] = "stack_1_channel_1_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_1"] = "stack_1_channel_1_obj_right"
        if channel_count > 2:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_2"] = "stack_0_channel_2_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_2"] = "stack_0_channel_2_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_2"] = "stack_1_channel_2_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_2"] = "stack_1_channel_2_obj_right"
        if channel_count > 3:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_3"] = "stack_0_channel_3_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_3"] = "stack_0_channel_3_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_3"] = "stack_1_channel_3_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_3"] = "stack_1_channel_3_obj_right"
        real_parameters["acquisition_leftcam_image_prefix"] = "Cam_Left_000"
        real_parameters["acquisition_rightcam_image_prefix"] = "Cam_Right_000"
        real_parameters["fusion_weighting"] = "ramp"
        real_parameters["fusion_strategy"] = 'hierarchical-fusion'

        real_parameters["acquisition_orientation"] = 'right'
        real_parameters["acquisition_mirrors"] = False
        real_parameters["acquisition_leftcamera_z_stacking"] = 'direct'
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        if not "EXP_FUSE" in real_parameters:
            real_parameters["EXP_FUSE"] = "01"
            if channel_count == 2:
                real_parameters["EXP_FUSE"] = ['01', '02']
            if channel_count == 3:
                real_parameters["EXP_FUSE"] = ['01', '02', '03']
            if channel_count > 3:
                print("Can't fuse more than 3 channels ! ")
                exit()
        self.add_to_run("FUSE", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        omero_result=(omero_config_file is not None), omero_config_file=omero_config_file,
                        keep_temp=keep_temp)
        if run_now:
            self.start_running(thread_number=1)
            if isinstance(real_parameters["EXP_FUSE"], list):
                splitted_fuse = real_parameters["EXP_FUSE"]
            else:
                splitted_fuse = real_parameters["EXP_FUSE"].replace("'", "").replace('"', '').replace("[", "").replace(
                    "]",
                    "").split(
                    ",")
            logFolder = "./FUSE/FUSE_" + splitted_fuse[0] + "/LOGS/"
            self.writeStepToJson(real_parameters, "fusion", ".", logFolder=logFolder)
        return real_parameters

    def compute_fusion_movie(self, parameters):
        """ Compute the intra-registration step to generate fusion movie, and then generate the video file.
        For video generation to work, ffmpeg needs to be installed.

        Please refer to AstecManager documentation for more detail.
        :param parameters: Dict of parameters (should include fusion parameters too)
        :type parameters: dict

        """
        real_parameters = {}
        real_parameters["EXP_INTRAREG"] = '01_TEST'
        real_parameters["intra_registration_movie_fusion_images"] = True
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        omero_config_file = get_omero_config(parameters)
        begin = parameters["begin"]
        end = parameters["end"]
        for key in parameters:
            real_parameters[key] = parameters[key]

        try:
            self.add_to_run("INTRAREG",".", embryo_name, begin, real_parameters, omero_result=(omero_config_file is not None), omero_config_file=omero_config_file, end_time=end, compress_result=False)

            self.start_running(thread_number=1)
            logFolder = "./INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]).replace("'", "").replace('"',
                                                                                                               '') + "/LOGS/"
            self.writeStepToJson(real_parameters, "intrareg_movie", ".", logFolder=logFolder)

            compute_video_from_movie(real_parameters["EXP_INTRAREG"], real_parameters["EXP_FUSE"],begin,end)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error fusion movie : " + str(strlog))

    def downscaled_fusion(self, parameters, one_stack_only=False, stack_chosen=0):
        """
        Start the downscaled fusion step of the pipeline, which is done to verify that an embryo didn't rotate during
        the acquisition. This fusion is only made to be able to see the intra-registration movie, and doesn't need to
        be kept

        :param parameters: Fusion parameters
        :type parameters: dict
        :param one_stack_only: If true, only use one stack for fusion (Default value = False)
        :type one_stack_only: bool
        :param stack_chosen: If one stack only fusion is chosen , index of the stack to use (0 or 1) (Default value = 0)
        :type stack_chosen: int

        """
        number_of_channels = 1
        if "number_of_channels" in parameters:
            try:
                number_of_channels = int(parameters["number_of_channels"])
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error number of channel is not an integer: " + str(strlog))
        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = "01_downscaled"
            if number_of_channels == 2:
                parameters["EXP_FUSE"] = ['01_downscaled', '02_downscaled']
            if number_of_channels == 3:
                parameters["EXP_FUSE"] = ['01_downscaled', '02_downscaled', '03_downscaled']
            if number_of_channels > 3:
                print("Can't fuse more than 3 channels ! ")
                exit()
        if not "target_resolution" in parameters:
            parameters["target_resolution"] = 0.6
        real_parameters = self.start_fusion(parameters, channel_count=number_of_channels, one_stack_only=one_stack_only,
                                            stack_chosen=stack_chosen)
        try:
            self.compute_fusion_movie(real_parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during movie computation : " + str(strlog))
    def final_fusion(self, parameters, one_stack_only=False, stack_chosen=0):
        """
        Start the final fusion step of the pipeline, with all the substeps (fusion, intra-registration , ...).

        After the fusion, an intra-registration will be computed to extract a 2D plane though time,
        to verify the quality of the segmentation.

        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of fusion parameters
        :type parameters: dict
        :param one_stack_only: If true, only use one stack for fusion (Default value = False)
        :type one_stack_only: bool
        :param stack_chosen: If one stack only fusion is chosen, index of the stack to use (0 or 1) (Default value = 0)
        :type stack_chosen: int

        """
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        number_of_channels = 1
        if "number_of_channels" in parameters:
            try:
                number_of_channels = int(parameters["number_of_channels"])
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error number of channel is not an integer: " + str(strlog))
        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = "01"
            if number_of_channels == 2:
                parameters["EXP_FUSE"] = ['01', '02']
            if number_of_channels == 3:
                parameters["EXP_FUSE"] = ['01', '02', '03']
            if number_of_channels > 3:
                print("Can't fuse more than 3 channels ! ")
                exit()
        real_parameters = self.start_fusion(parameters, channel_count=number_of_channels, one_stack_only=one_stack_only,
                                            stack_chosen=stack_chosen)

        try:
            if "EXP_DRIFT" in real_parameters and real_parameters["EXP_DRIFT"] is not None and real_parameters["EXP_DRIFT"] != "":
                self.upload_transformations_for_last_iteration(real_parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during upload of drift transformations and scores : " + str(strlog))
        try:
            self.compute_fusion_movie(real_parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during movie computation : " + str(strlog))
        try:
            plot_fusion_intensity_profile(embryo_name, str(real_parameters["EXP_FUSE"]))

        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during fusion signal plot: " + str(strlog))

        try:
            print("PLotting intensities"
                  "")
            self.plot_signal_to_noise(embryo_name, real_parameters, one_stack_only=one_stack_only,
                                      stack_chosen=stack_chosen)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during signal plot: " + str(strlog))

    def start_mars(self, parameters):
        """ Start an instance of MARS algorithm for Astec Pipeline.

        Please refer to AstecManager documentation for more details.

        :param parameters: Parameters for first time point segmentation
        :type parameters: dict
        :returns: Updated parameters
        :rtype: dict

        """
        use_contour = parameters["use_membranes"]
        normalize_images = parameters["apply_normalisation"]
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        embryo_dir = "."
        begin = int(parameters["begin"])
        end = int(parameters["end"])

        voxel_size = parameters["resolution"]
        real_parameters = {}

        real_parameters["sigma_TV"] = 4.5
        real_parameters["result_image_suffix"] = "nii"
        real_parameters["intensity_enhancement"] = 'gace'

        if use_contour:
            exp_fuse = parameters["EXP_FUSE"]
            real_parameters["EXP_CONTOUR"] = exp_fuse
            real_parameters["outer_contour_enhancement"] = 'from_contour_image'
        if normalize_images:
            normalisation = 1000
            if "normalisation" in parameters:
                normalisation = parameters["normalisation"]
            real_parameters["enhancement_normalization_max_value"] = normalisation
            real_parameters["enhancement_transformation"] = "normalization_to_u16"
            real_parameters["normalization_max_value"] = normalisation
            real_parameters["intensity_transformation"] = "normalization_to_u16"
        user = None
        if "user" in parameters:
            user = parameters["user"]
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("MARS", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        omero_result=(omero_config_file is not None), omero_config_file=omero_config_file,
                        keep_temp=False)
        self.start_running(thread_number=1)
        real_parameters["uploaded_to_omero"] = (omero_config_file is not None)
        logFolder = "./SEG/SEG_" + str(real_parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(real_parameters, "mars", ".", logFolder=logFolder)

        return real_parameters

    def test_mars(self, parameters):
        """Start the first time point segmentation step of the pipeline, and all the substeps related.
        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of first time point segmentation parameters
        :type parameters: dict

        """

        if not "resolution" in parameters:
            parameters["resolution"] = 0.3
        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = '01'
        if not "use_membranes" in parameters:
            parameters["use_membranes"] = True
        if not "apply_normalisation" in parameters:
            parameters["apply_normalisation"] = True
        if not "normalisation" in parameters:
            parameters["normalisation"] = 1000
        if not "morphosnake_correction" in parameters:
            parameters["morphosnake_correction"] = False
        parameters["EXP_SEG"] = "mars_gace_addition"
        parameters["reconstruction_images_combination"] = "addition"
        real_parameters = self.start_mars(parameters)

        real_parameters["EXP_SEG"] = "mars_gace_maximum"
        real_parameters["reconstruction_images_combination"] = "maximum"
        self.start_mars(real_parameters)

        real_parameters["EXP_SEG"] = "mars_no_gace_maximum"
        real_parameters["intensity_enhancement"] = "None"
        real_parameters["reconstruction_images_combination"] = "maximum"
        self.start_mars(real_parameters)

        real_parameters["EXP_SEG"] = "mars_no_gace_addition"
        real_parameters["intensity_enhancement"] = "None"
        real_parameters["reconstruction_images_combination"] = "maximum"
        self.start_mars(real_parameters)


    def test_segmentation(self, parameters):
        """ Start the segmentation test step of the ppipeline , including all the substeps related.
        Please refer to AstecManager documentation for more details.


        :param parameters: Dict of segmentation parameters
        :type parameters: dict

        """

        try_without_contour = ("test_no_contour" in parameters and parameters["test_no_contour"])
        # TESTS DEPENDENT PARAMETERS, DO NOT CHANGE
        #
        #
        #

        add_gace_exp_seg = "test_addition_gace"
        max_gace_exp_seg = "test_maximum_gace"
        add_noenhanc_exp_seg = "test_addition_no_enhancment"
        max_noenhanc_exp_seg = "test_maximum_no_enhancment"
        """parameters["EXP_SEG"] = "test_addition_glace"
        parameters["reconstruction_images_combination"] = "addition"
        parameters["intensity_enhancement"] = "glace"
        self.start_segmentation(parameters, run_now=True)
        logFolder = "./SEG/SEG_" + str(parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
        """
        parameters2 = parameters
        parameters2["EXP_SEG"] = add_gace_exp_seg
        parameters2["reconstruction_images_combination"] = "addition"
        parameters2["intensity_enhancement"] = "gace"
        self.start_segmentation(parameters2, run_now=False)
        logFolder2 = "./SEG/SEG_" + str(parameters2["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
        """
        parameters3 = parameters
        parameters3["EXP_SEG"] = "test_maximum_glace"
        parameters3["reconstruction_images_combination"] = "maximum"
        parameters3["intensity_enhancement"] = "glace"
        logFolder3 = "./SEG/SEG_" + str(parameters3["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.start_segmentation(parameters3, run_now=False)
        """
        parameters4 = parameters
        parameters4["EXP_SEG"] = max_gace_exp_seg
        parameters4["reconstruction_images_combination"] = "maximum"
        parameters4["intensity_enhancement"] = "gace"

        self.start_segmentation(parameters4, run_now=False)
        logFolder4 = "./SEG/SEG_" + str(parameters4["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

        parameters5 = parameters
        parameters5["EXP_SEG"] = max_noenhanc_exp_seg
        parameters5["reconstruction_images_combination"] = "maximum"
        parameters5["intensity_enhancement"] = "None"

        self.start_segmentation(parameters5, run_now=False)
        logFolder5 = "./SEG/SEG_" + str(parameters5["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

        parameters6 = parameters
        parameters6["EXP_SEG"] = add_noenhanc_exp_seg
        parameters6["reconstruction_images_combination"] = "addition"
        parameters6["intensity_enhancement"] = "None"

        self.start_segmentation(parameters6, run_now=False)
        logFolder6 = "./SEG/SEG_" + str(parameters6["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

        self.start_running(thread_number=4)
        #self.writeStepToJson(parameters, "segmentation_test", ".", logFolder=logFolder)
        self.writeStepToJson(parameters2, "segmentation_test", ".", logFolder=logFolder2)
        #self.writeStepToJson(parameters3, "segmentation_test", ".", logFolder=logFolder3)
        self.writeStepToJson(parameters4, "segmentation_test", ".", logFolder=logFolder4)
        self.writeStepToJson(parameters5, "segmentation_test", ".", logFolder=logFolder5)
        self.writeStepToJson(parameters6, "segmentation_test", ".", logFolder=logFolder6)

        # Embryo dependant parameters

        parameters["EXP_SEG"] = max_gace_exp_seg
        parameters["EXP_POST"] = max_gace_exp_seg

        self.start_post_correction(parameters, run_now=False)
        """
        parameters2 = parameters
        parameters2["EXP_SEG"] = 'test_addition_glace'
        parameters2["EXP_POST"] = 'test_addition_glace'
        
        self.start_post_correction(parameters2, run_now=False)
        """
        parameters3 = parameters
        parameters3["EXP_SEG"] = add_gace_exp_seg
        parameters3["EXP_POST"] = add_gace_exp_seg

        self.start_post_correction(parameters3, run_now=False)
        """
        parameters4 = parameters
        parameters4["EXP_SEG"] = 'test_maximum_glace'
        parameters4["EXP_POST"] = 'test_maximum_glace'

        self.start_post_correction(parameters4, run_now=False)
        """
        parameters5 = parameters
        parameters5["EXP_SEG"] = max_noenhanc_exp_seg
        parameters5["EXP_POST"] = max_noenhanc_exp_seg

        self.start_post_correction(parameters5, run_now=False)

        parameters6 = parameters
        parameters6["EXP_SEG"] = add_noenhanc_exp_seg
        parameters6["EXP_POST"] = add_noenhanc_exp_seg

        self.start_post_correction(parameters6, run_now=False)

        self.start_running(thread_number=4)
        self.compute_graphs_test_segmentation(parameters["embryo_name"], parameters["begin"], parameters["end"])
        logFolder = "./POST/POST_" + str(parameters["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters, "post_correction_test", ".", logFolder=logFolder)
        #logFolder2 = "./POST/POST_" + str(parameters2["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        #self.writeStepToJson(parameters2, "post_correction_test", ".", logFolder=logFolder2)
        logFolder3 = "./POST/POST_" + str(parameters3["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters3, "post_correction_test", ".", logFolder=logFolder3)
        #logFolder4 = "./POST/POST_" + str(parameters4["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        #self.writeStepToJson(parameters4, "post_correction_test", ".", logFolder4)
        logFolder5 = "./POST/POST_" + str(parameters5["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters5, "post_correction_test", ".", logFolder5)
        logFolder6 = "./POST/POST_" + str(parameters6["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters6, "post_correction_test", ".", logFolder6)

        if try_without_contour:
            parameters["use_membranes"] = False
            parameters["apply_normalisation"] = False
            """
            parameters["EXP_SEG"] = "test_addition_glace_contourless"
            parameters["reconstruction_images_combination"] = "addition"
            parameters["intensity_enhancement"] = "glace"
            self.start_segmentation(parameters, run_now=False)
            logFolder = "./SEG/SEG_" + str(parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            """
            parameters2 = parameters
            parameters2["EXP_SEG"] = "test_addition_gace_contourless"
            parameters2["reconstruction_images_combination"] = "addition"
            parameters2["intensity_enhancement"] = "gace"
            self.start_segmentation(parameters2, run_now=False)
            logFolder2 = "./SEG/SEG_" + str(parameters2["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            """
            parameters3 = parameters
            parameters3["EXP_SEG"] = "test_maximum_glace_contourless"
            parameters3["reconstruction_images_combination"] = "maximum"
            parameters3["intensity_enhancement"] = "glace"
            logFolder3 = "./SEG/SEG_" + str(parameters3["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.start_segmentation(parameters3, run_now=False)
            """
            parameters4 = parameters
            parameters4["EXP_SEG"] = "test_maximum_gace_contourless"
            parameters4["reconstruction_images_combination"] = "maximum"
            parameters4["intensity_enhancement"] = "gace"

            self.start_segmentation(parameters4, run_now=False)
            logFolder4 = "./SEG/SEG_" + str(parameters4["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

            parameters5 = parameters
            parameters5["EXP_SEG"] = "test_maximum_no_enhancment_contourless"
            parameters5["reconstruction_images_combination"] = "maximum"
            parameters5["intensity_enhancement"] = "None"

            self.start_segmentation(parameters5, run_now=False)
            logFolder5 = "./SEG/SEG_" + str(parameters5["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

            parameters6 = parameters
            parameters6["EXP_SEG"] = "test_addition_no_enhancment_contourless"
            parameters6["reconstruction_images_combination"] = "addition"
            parameters6["intensity_enhancement"] = "None"

            self.start_segmentation(parameters6, run_now=False)
            logFolder6 = "./SEG/SEG_" + str(parameters6["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

            self.start_running(thread_number=4)
            #self.writeStepToJson(parameters, "segmentation_test", ".", logFolder=logFolder)
            self.writeStepToJson(parameters2, "segmentation_test", ".", logFolder=logFolder2)
            #self.writeStepToJson(parameters3, "segmentation_test", ".", logFolder=logFolder3)
            self.writeStepToJson(parameters4, "segmentation_test", ".", logFolder=logFolder4)
            self.writeStepToJson(parameters5, "segmentation_test", ".", logFolder=logFolder5)
            self.writeStepToJson(parameters6, "segmentation_test", ".", logFolder=logFolder6)

            # Embryo dependant parameters

            parameters["EXP_SEG"] = 'test_maximum_gace_contourless'
            parameters["EXP_POST"] = 'test_maximum_gace_contourless'

            self.start_post_correction(parameters, run_now=False)
            """
            parameters2 = parameters
            parameters2["EXP_SEG"] = 'test_addition_glace_contourless'
            parameters2["EXP_POST"] = 'test_addition_glace_contourless'

            self.start_post_correction(parameters2, run_now=False)
            """
            parameters3 = parameters
            parameters3["EXP_SEG"] = 'test_addition_gace_contourless'
            parameters3["EXP_POST"] = 'test_addition_gace_contourless'

            self.start_post_correction(parameters3, run_now=False)
            """
            parameters4 = parameters
            parameters4["EXP_SEG"] = 'test_maximum_glace_contourless'
            parameters4["EXP_POST"] = 'test_maximum_glace_contourless'

            self.start_post_correction(parameters4, run_now=False)
"""
            parameters5 = parameters
            parameters5["EXP_SEG"] = 'test_maximum_no_enhancment_contourless'
            parameters5["EXP_POST"] = 'test_maximum_no_enhancment_contourless'

            self.start_post_correction(parameters5, run_now=False)

            parameters6 = parameters
            parameters6["EXP_SEG"] = 'test_addition_no_enhancment_contourless'
            parameters6["EXP_POST"] = 'test_addition_no_enhancment_contourless'

            self.start_post_correction(parameters6, run_now=False)
            self.start_running(thread_number=4)
            self.compute_graphs_test_segmentation(parameters["embryo_name"], parameters["begin"], parameters["end"],contourless=True)
            logFolder = "./POST/POST_" + str(parameters["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(parameters, "post_correction_test", ".", logFolder=logFolder)
            #logFolder2 = "./POST/POST_" + str(parameters2["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            #self.writeStepToJson(parameters2, "post_correction_test", ".", logFolder=logFolder2)
            logFolder3 = "./POST/POST_" + str(parameters3["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            #self.writeStepToJson(parameters3, "post_correction_test", ".", logFolder=logFolder3)
            #logFolder4 = "./POST/POST_" + str(parameters4["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(parameters4, "post_correction_test", ".", logFolder4)
            logFolder5 = "./POST/POST_" + str(parameters5["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(parameters5, "post_correction_test", ".", logFolder5)
            logFolder6 = "./POST/POST_" + str(parameters6["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(parameters6, "post_correction_test", ".", logFolder6)

    def compute_fuse_and_drift(self,parameters):
        """
        Starts the computation of the drift : first, fuse both stack independantly, and than compute drift for each stack

        This function should only be called the first time drift is computed !

        :param parameters: Parameters for the drift
        :type parameters: Dict
        """
        print("Starting computation of initial drift")
        params_stack_0,params_stack_1 = self.start_independent_stack_fusion(parameters)
        self.start_initial_drift(params_stack_0, params_stack_1)


    def drift_round(self,parameters):
        print("Starting drift for each stack")
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        begin = parameters["begin"]
        end = parameters["end"]
        stack = int(parameters["stack"])
        real_parameters = {}
        real_parameters["xy_movie_fusion_images"] = True
        real_parameters["xz_movie_fusion_images"] = True
        real_parameters["yz_movie_fusion_images"] = False
        real_parameters["resolution"] = 0.6
        real_parameters["template_type"] = "FUSION"
        real_parameters["template_threshold"] = 140
        if not "EXP_DRIFT" in real_parameters:
            if stack == 0:
                real_parameters["EXP_DRIFT"] = "stack0"
            elif stack == 1:
                real_parameters["EXP_DRIFT"] = "stack1"
        if not "EXP_FUSE" in real_parameters:
            if stack == 0:
                real_parameters["EXP_FUSE"] = "stack0"
            elif stack == 1:
                real_parameters["EXP_FUSE"] = "stack1"
        refining_parameters = ["score_threshold","corrections_to_be_done","corrections_to_be_added","rotation_sphere_radius"]
        stop_flag = True
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
            if key_param in refining_parameters: # If we don't find one of those parameters , no point computing a new round of drift
                stop_flag = False
        if stop_flag:
            print("The drift round is here to refine the previous drift round, but no refined parameters found. "
                  "If it's the first round of drift, please use initial drift")
            print("Possible parameters for refining a drift : ")
            print(str(refining_parameters))
            return None
        print(" Parameters for stack  "+str(stack))
        for param in real_parameters:
            print("     " + str(param) + " -> " + str(real_parameters[param]))

        self.add_to_run("DRIFT", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)

        self.start_running(thread_number=1)

        if isinstance(real_parameters["EXP_DRIFT"], list):
            splitted_fuse = real_parameters["EXP_DRIFT"]
        else:
            splitted_fuse = real_parameters["EXP_DRIFT"].replace("'", "").replace('"', '').replace("[",
                                                                                                           "").replace(
                "]",
                "").split(
                ",")
        logFolder = "./DRIFT/DRIFT_" + splitted_fuse[0] + "/LOGS/"
        self.generate_drift_images_for_last_iteration(real_parameters)
        self.writeStepToJson(real_parameters, "drift", ".", logFolder=logFolder)

        return real_parameters

    def run_inter_stack_drift(self,parameters):
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        begin = parameters["begin"]
        end = parameters["end"]

        if not "score_threshold" in parameters:
            print("score_threshold parameter is missing , please fill the score and run again")
            return

        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = ['stack1', 'stack0']

        if not "second_angle_drift_exp" in parameters:
            parameters["second_angle_drift_exp"] = 'stack1'

        real_parameters = {"EXP_DRIFT": parameters["second_angle_drift_exp"],
                           "score_threshold": parameters["score_threshold"], "EXP_FUSE": parameters["EXP_FUSE"]}

        self.add_to_run("DRIFT", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)
        self.start_running(thread_number=1)

        if isinstance(real_parameters["EXP_DRIFT"], list):
            splitted_fuse = real_parameters["EXP_DRIFT"]
        else:
            splitted_fuse = real_parameters["EXP_DRIFT"].replace("'", "").replace('"', '').replace("[","").replace("]","").split(",")
        log_folder = "./DRIFT/DRIFT_" + splitted_fuse[0] + "/LOGS/"
        self.writeStepToJson(real_parameters, "drift", ".", logFolder=log_folder)
        self.generate_drift_images_interstack(real_parameters,embryo_name,begin)
        return real_parameters

    def start_initial_drift(self,parameters_stack_0,parameters_stack_1):
        """
        Starts the computation of the first drift round for each stack of the embryo
        Don't use this function to continue the drift, only the initial one

        :param parameters_stack_0: Drift parameters for stack 0 , including parameters of previous fusion
        :type parameters_stack_0: dict
        :param parameters_stack_1: Drift parameters for stack 0 , including parameters of previous fusion
        :type parameters_stack_1: dict
        :returns: Dict parameters of each drift, stack 0 first, stack 1 second
        :rtype: tuple
        """
        print("Starting drift for each stack")
        embryo_name = parameters_stack_0["embryo_name"].replace('"', '').replace("'", "")
        begin = parameters_stack_0["begin"]
        end = parameters_stack_0["end"]
        real_parameters_stack_1 = {}
        real_parameters_stack_1["xy_movie_fusion_images"] = True
        real_parameters_stack_1["xz_movie_fusion_images"] = True
        real_parameters_stack_1["yz_movie_fusion_images"] = False
        real_parameters_stack_1["resolution"] = 0.6
        real_parameters_stack_1["template_type"] = "FUSION"
        real_parameters_stack_1["template_threshold"] = 140
        real_parameters_stack_1["EXP_DRIFT"] = "stack1"
        real_parameters_stack_1["EXP_FUSE"] = "stack1"
        real_parameters_stack_0 = {}
        real_parameters_stack_0["xy_movie_fusion_images"] = True
        real_parameters_stack_0["xz_movie_fusion_images"] = True
        real_parameters_stack_0["yz_movie_fusion_images"] = False
        real_parameters_stack_0["resolution"] = 0.6
        real_parameters_stack_0["template_type"] = "FUSION"
        real_parameters_stack_0["template_threshold"] = 140
        real_parameters_stack_0["EXP_DRIFT"] = "stack0"
        real_parameters_stack_0["EXP_FUSE"] = "stack0"
        for key_param in parameters_stack_0:
            real_parameters_stack_0[key_param] = parameters_stack_0[key_param]
        for key_param in parameters_stack_1:
            real_parameters_stack_1[key_param] = parameters_stack_1[key_param]

        print(" Parameters for stack 0 : ")
        for param in real_parameters_stack_0:
            print("     "+str(param)+" -> "+str(real_parameters_stack_0[param]))
        print(" Parameters for stack 1 : ")
        for param in real_parameters_stack_1:
            print("     "+str(param)+" -> "+str(real_parameters_stack_1[param]))

        self.add_to_run("DRIFT", ".", embryo_name, begin, real_parameters_stack_0, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)

        self.add_to_run("DRIFT", ".", embryo_name, begin, real_parameters_stack_1, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)
        self.start_running(thread_number=2)

        if isinstance(real_parameters_stack_0["EXP_DRIFT"], list):
            splitted_fuse = real_parameters_stack_0["EXP_DRIFT"]
        else:
            splitted_fuse = real_parameters_stack_0["EXP_DRIFT"].replace("'", "").replace('"', '').replace("[",
                                                                                                          "").replace(
                "]",
                "").split(
                ",")
        logFolder = "./DRIFT/DRIFT_" + splitted_fuse[0] + "/LOGS/"
        self.writeStepToJson(real_parameters_stack_0, "drift", ".", logFolder=logFolder)
        if isinstance(real_parameters_stack_1["EXP_DRIFT"], list):
            splitted_fuse = real_parameters_stack_1["EXP_DRIFT"]
        else:
            splitted_fuse = real_parameters_stack_1["EXP_DRIFT"].replace("'", "").replace('"', '').replace("[",
                                                                                                          "").replace(
                "]",
                "").split(
                ",")
        logFolder = "./DRIFT/DRIFT_" + splitted_fuse[0] + "/LOGS/"
        self.writeStepToJson(real_parameters_stack_1, "drift", ".", logFolder=logFolder)
        self.generate_drift_images_for_last_iteration(real_parameters_stack_0)
        self.generate_drift_images_for_last_iteration(real_parameters_stack_1)
        return real_parameters_stack_0, real_parameters_stack_1

    def generate_drift_images_interstack(self,parameters,embryo_name,begin):
        drif_exp = parameters["EXP_DRIFT"]
        drift_folder = "./DRIFT/DRIFT_" + str(drif_exp)
        co_stack_folder = os.path.join(drift_folder,"CO-STACK")
        if not os.path.isdir(co_stack_folder):
            print("Weird, drift inter stack didn't generate CO-STACK folder : "+str(co_stack_folder))
            return
        image_name = embryo_name+"_fuse_t{:03d}".format(begin)+"_costack.nii"
        input_image = os.path.join(co_stack_folder,image_name)
        if not os.path.isfile(input_image):
            print("Weird , no image costack found")
            return
        analysis_dir = "./analysis/drift/costack/"
        if not os.path.isdir(analysis_dir):
            os.makedirs(analysis_dir)
        final_image_name = os.path.join(analysis_dir,image_name)
        os.rename(input_image,final_image_name)


    def generate_drift_images_for_last_iteration(self,parameters):
        import re
        drif_exp = parameters["EXP_DRIFT"]
        fuse_exp = parameters["EXP_FUSE"]
        drift_folder = "./DRIFT/DRIFT_"+str(drif_exp)
        res = [x for x in os.listdir(drift_folder) if os.path.isdir(os.path.join(drift_folder,x)) and "ITER" in x and "CO-SCORE" in x]
        found_iteration = -1
        for folder in res:
            curr_ite = int(re.search(r'\d+', folder).group())
            if curr_ite > found_iteration:
                found_iteration = curr_ite
        if found_iteration > -1:
            print("Analyzing ITER : "+str(found_iteration))
            analysis_dir = "./analysis/drift/"+str(drif_exp)
            output_image_dir = os.path.join(analysis_dir,"iter_"+str(found_iteration))
            if not os.path.isdir(output_image_dir):
                os.makedirs(output_image_dir)
            score_path = os.path.join(drift_folder,"ITER"+str(found_iteration)+"-CO-SCORE")
            movie_path = os.path.join(drift_folder,"ITER"+str(found_iteration)+"-MOVIES_t{0:03}".format(parameters["begin"])+"-{0:03}".format(parameters["end"]),"FUSE","FUSE_"+str(fuse_exp))
            python_score_file = os.path.join(score_path,"figure_iter"+str(found_iteration)+"_coregistration_analyze.py")
            if os.path.isfile(python_score_file):
                os.system("conda run -n astec python3 "+str(python_score_file))
                ouputpng = os.path.join("iter"+str(found_iteration)+"_coregistration_analyze.png")
                finalpng = os.path.join(output_image_dir,"iter"+str(found_iteration)+"_coregistration_analyze.png")
                print("moving " + str(ouputpng) + " to " + str(finalpng))
                if os.path.isfile(ouputpng):
                    os.rename(ouputpng,finalpng)
            print(movie_path)
            if os.path.isdir(movie_path):
                shutil.copytree(movie_path,os.path.join(output_image_dir,"movies"))



    def upload_transformations_for_last_iteration(self,parameters):
        import re
        omero_config_file = get_omero_config(parameters)
        drif_experiments = parameters["EXP_DRIFT"]
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        for drif_exp in drif_experiments:
            print("Drift exp : "+str(drif_exp))
            drift_folder = "./DRIFT/DRIFT_"+str(drif_exp)
            res = [x for x in os.listdir(drift_folder) if os.path.isdir(os.path.join(drift_folder,x)) and "ITER" in x and "CO-SCORE" in x]
            found_iteration = -1
            for folder in res:
                curr_ite = int(re.search(r'\d+', folder).group())
                if curr_ite > found_iteration:
                    found_iteration = curr_ite
            if found_iteration > -1:
                print("Uploading ITER : "+str(found_iteration))
                score_path = os.path.join(drift_folder,"ITER"+str(found_iteration)+"-CO-SCORE")
                transformations_path = os.path.join(drift_folder,"ITER"+str(found_iteration)+"-CO-TRSFS")
                if os.path.isdir(score_path):
                    print("Uploading scores ")
                    self.upload_on_omero(omero_config_file,embryo_name,"DRIFT_"+str(drif_exp)+"_ITER"+str(found_iteration)+"-CO-SCORE",score_path)
                if os.path.isdir(transformations_path):
                    print("Uploading transformations")
                    self.upload_on_omero(omero_config_file,embryo_name,"DRIFT_"+str(drif_exp)+"_ITER"+str(found_iteration)+"-CO-TRSFS",transformations_path)



    def start_independent_stack_fusion(self, parameters):
        """ Starts the fusion of each stack in half resolution (voxel size 0.6 micrometer), to perform drift later


        :param parameters: Dict of fusion parameters
        :type parameters: dict
        :returns: Dict parameters of each fusion, stack 0 first, stack 1 second
        :rtype: tuple

        """

        print("Starting initial independant fusion")

        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")

        begin = parameters["begin"]
        end = parameters["end"]
        real_parameters_stack_1 = {}
        real_parameters_stack_1["DIR_RAWDATA"] = "RAWDATA"
        real_parameters_stack_1["acquisition_resolution"] = (.195, .195, 1.)
        real_parameters_stack_1["target_resolution"] = 0.6
        real_parameters_stack_1["result_image_suffix"] = 'nii'
        real_parameters_stack_1["acquisition_slit_line_correction"] = True
        real_parameters_stack_1["acquisition_cropping_opening"] = 2
        real_parameters_stack_1["acquisition_z_cropping"] = True
        real_parameters_stack_1["raw_crop"] = True
        real_parameters_stack_1["fusion_crop"] = True
        real_parameters_stack_1["acquisition_leftcamera_z_stacking"] = 'direct'

        real_parameters_stack_1["fusion_preregistration_compute_registration"] = True
        real_parameters_stack_1["acquisition_mirrors"] = False
        real_parameters_stack_1["fusion_preregistration_normalization"] = False
        real_parameters_stack_1["fusion_registration_normalization"] = False
        real_parameters_stack_1["fusion_stack_preregistration_normalization"] = False
        real_parameters_stack_1["fusion_stack_registration_normalization"] = False
        real_parameters_stack_1["fusion_xzsection_extraction"] = False
        real_parameters_stack_1["DIR_LEFTCAM_STACKZERO"] = '""'
        real_parameters_stack_1["DIR_RIGHTCAM_STACKZERO"] = '""'
        real_parameters_stack_1["DIR_LEFTCAM_STACKONE"] = "stack_1_channel_0_obj_left"
        real_parameters_stack_1["DIR_RIGHTCAM_STACKONE"] = "stack_1_channel_0_obj_right"
        real_parameters_stack_1["fusion_weighting"] = "ramp"
        real_parameters_stack_1["fusion_strategy"] = 'direct-fusion'

        real_parameters_stack_0 = {}
        real_parameters_stack_0["DIR_RAWDATA"] = "RAWDATA"
        real_parameters_stack_0["acquisition_resolution"] = (.195, .195, 1.)
        real_parameters_stack_0["target_resolution"] = 0.6
        real_parameters_stack_0["result_image_suffix"] = 'nii'
        real_parameters_stack_0["acquisition_slit_line_correction"] = True
        real_parameters_stack_0["acquisition_cropping_opening"] = 2
        real_parameters_stack_0["acquisition_z_cropping"] = True
        real_parameters_stack_0["raw_crop"] = True
        real_parameters_stack_0["fusion_crop"] = True
        real_parameters_stack_0["acquisition_leftcamera_z_stacking"] = 'direct'

        real_parameters_stack_0["fusion_preregistration_compute_registration"] = True
        real_parameters_stack_0["acquisition_mirrors"] = False
        real_parameters_stack_0["fusion_preregistration_normalization"] = False
        real_parameters_stack_0["fusion_registration_normalization"] = False
        real_parameters_stack_0["fusion_stack_preregistration_normalization"] = False
        real_parameters_stack_0["fusion_stack_registration_normalization"] = False
        real_parameters_stack_0["fusion_xzsection_extraction"] = False
        real_parameters_stack_0["DIR_LEFTCAM_STACKZERO"] = "stack_0_channel_0_obj_left"
        real_parameters_stack_0["DIR_RIGHTCAM_STACKZERO"] = "stack_0_channel_0_obj_right"
        real_parameters_stack_0["DIR_LEFTCAM_STACKONE"] = '""'
        real_parameters_stack_0["DIR_RIGHTCAM_STACKONE"] = '""'
        real_parameters_stack_0["fusion_weighting"] = "ramp"
        real_parameters_stack_0["fusion_strategy"] = 'direct-fusion'


        for key_param in parameters:
            real_parameters_stack_0[key_param] = parameters[key_param]
            real_parameters_stack_1[key_param] = parameters[key_param]
        if not "EXP_FUSE" in real_parameters_stack_0:
            real_parameters_stack_0["EXP_FUSE"] = "stack0"
        if not "EXP_FUSE" in real_parameters_stack_1:
            real_parameters_stack_1["EXP_FUSE"] = "stack1"

        print(" Parameters for stack 0 : ")
        for param in real_parameters_stack_0:
            print("     "+str(param)+" -> "+str(real_parameters_stack_0[param]))
        print(" Parameters for stack 1 : ")
        for param in real_parameters_stack_1:
            print("     "+str(param)+" -> "+str(real_parameters_stack_1[param]))
        self.add_to_run("FUSE", ".", embryo_name, begin, real_parameters_stack_0, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)

        self.add_to_run("FUSE", ".", embryo_name, begin, real_parameters_stack_1, end_time=end, compress_result=False,
                        omero_result=False, omero_config_file="",
                        keep_temp=False)
        self.start_running(thread_number=2)

        if isinstance(real_parameters_stack_0["EXP_FUSE"], list):
            splitted_fuse = real_parameters_stack_0["EXP_FUSE"]
        else:
            splitted_fuse = real_parameters_stack_0["EXP_FUSE"].replace("'", "").replace('"', '').replace("[", "").replace(
                "]",
                "").split(
                ",")
        logFolder = "./FUSE/FUSE_" + splitted_fuse[0] + "/LOGS/"
        self.writeStepToJson(real_parameters_stack_0, "fusion", ".", logFolder=logFolder)
        if isinstance(real_parameters_stack_1["EXP_FUSE"], list):
            splitted_fuse = real_parameters_stack_1["EXP_FUSE"]
        else:
            splitted_fuse = real_parameters_stack_1["EXP_FUSE"].replace("'", "").replace('"', '').replace("[", "").replace(
                "]",
                "").split(
                ",")
        logFolder = "./FUSE/FUSE_" + splitted_fuse[0] + "/LOGS/"
        self.writeStepToJson(real_parameters_stack_1, "fusion", ".", logFolder=logFolder)
        return real_parameters_stack_0,real_parameters_stack_1


    def start_segmentation(self, parameters, run_now=True):
        """ Run a segmentation step of the pipeline

        :param parameters: Dict of segmentation parameters
        :type parameters: dict
        :param run_now: If True, the segmentation will process now, if False, segmentation will process when user starts it (Default value = True)
        :type run_now: bool
        :returns: Dict of segmentation parameters updated with computed parameters
        :rtype: dict

        """
        use_contour = parameters["use_membranes"]
        normalize_images = parameters["apply_normalisation"]
        omero_config_file = get_omero_config(parameters)
        voxel_size = parameters["resolution"]

        MARS_PATH = parameters["mars_path"]
        embryo_name = parameters["embryo_name"].replace("'", "").replace('"', '')
        begin = int(parameters["begin"])
        end = int(parameters["end"])

        real_parameters = {}

        real_parameters["sigma_TV"] = 4.5
        real_parameters["result_image_suffix"] = "nii"
        real_parameters["intensity_enhancement"] = 'gace'
        real_parameters["EXP_FUSE"] = "01"
        if use_contour:
            exp_fuse = parameters["EXP_FUSE"]
            real_parameters["EXP_CONTOUR"] = exp_fuse
            real_parameters["outer_contour_enhancement"] = "from_contour_image"
        if normalize_images:
            normalisation = 1000
            if "normalisation" in parameters:
                normalisation = parameters["normalisation"]
            real_parameters["enhancement_normalization_max_value"] = normalisation
            real_parameters["enhancement_transformation"] = "normalization_to_u16"
            real_parameters["normalization_max_value"] = normalisation
            real_parameters["intensity_transformation"] = "normalization_to_u16"

        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("SEG", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        mars_path=MARS_PATH, omero_result=(omero_config_file is not None),
                        omero_config_file=omero_config_file)
        if run_now:
            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./SEG/SEG_" + str(parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters, "segmentation", ".", logFolder=logFolder)
            #self.segmentation_parameters(real_parameters)
        return real_parameters

    def start_post_correction(self, parameters, run_now=True):
        """Start a post correction step of the pipeline, and the analysis coming with it

        :param parameters: Dict of the post correction parameters
        :type parameters: dict
        :param run_now: If True, the segmentation will process now, if False, segmentation will process when user starts it (Default value = True)
        :type run_now: bool
        :returns: Dict of segmentation parameters updated with computed parameters
        :rtype: dict

        """
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        omero_config_file = get_omero_config(parameters)
        begin = int(parameters["begin"])
        end = int(parameters["end"])
        voxel_size = parameters["resolution"]
        real_parameters = {}
        real_parameters["EXP_POST"] = '01'
        real_parameters["intra_registration_resolution"] = voxel_size
        real_parameters["test_branch_length"] = True
        real_parameters["test_early_division"] = True
        real_parameters["test_volume_correlation"] = True
        real_parameters["test_postponing_division"] = True
        real_parameters["result_image_suffix"] = 'nii'
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("POST", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,
                        omero_result=(omero_config_file is not None), omero_config_file=omero_config_file)
        if run_now:
            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./POST/POST_" + str(parameters["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters, "post_correction", ".", logFolder=logFolder)
            #self.post_correction_parameters(parameters)
            try:
                self.compute_graphs_post(embryo_name, begin, end, [parameters["EXP_POST"]])
            except:
                strlog = traceback.format_exc()
                print("Error during computation of the Post correction graphs" + str(strlog))
        return real_parameters

    def apply_intrareg(self, parameters,properties=False):
        """Start the intraregistration step of the pipeline, and the substeps coming with it (upload).
        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of the intraregistration parameters
        :type parameters: dict
        :returns: Dict of segmentation parameters updated with computed parameters
        :rtype: dict
        """
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace("'", "").replace('', '"')
        begin = parameters["begin"]
        end = parameters["end"]
        real_parameters = {}
        real_parameters["EXP_INTRAREG"] = "01"
        real_parameters["delta"] = 1
        real_parameters["raw_delay"] = 0
        real_parameters["intra_registration_template_type"] = 'POST-SEGMENTATION'
        real_parameters["intra_registration_template_threshold"] = 2
        real_parameters["intra_registration_margin"] = 20
        real_parameters["intra_registration_resample_post_segmentation_images"] = True
        real_parameters["intra_registration_resample_segmentation_images"] = True
        real_parameters["intra_registration_resample_reconstruction_images"] = True
        if "EXP_RECONSTRUCTION" in real_parameters and real_parameters["EXP_RECONSTRUCTION"].lower() == "none":
            real_parameters["intra_registration_resample_reconstruction_images"] = False
        real_parameters["intra_registration_movie_post_segmentation_images"] = True
        real_parameters["intra_registration_movie_segmentation_images"] = False
        real_parameters["intra_registration_rebuild_template"] = True
        if not "EXP_RECONSTRUCTION" in real_parameters:
            if "EXP_POST" in real_parameters:
                real_parameters["EXP_RECONSTRUCTION"] = real_parameters["EXP_POST"]
            elif "EXP_SEG" in real_parameters:
                real_parameters["EXP_RECONSTRUCTION"] = real_parameters["EXP_SEG"]
            else:
                real_parameters["EXP_RECONSTRUCTION"] = "01"
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]

        # PRODUCTION PARAMETERS, UPDATE WITH THE TEST CHOSEN PREVIOUSLY
        #
        #
        #

        try:
            self.add_to_run("INTRAREG", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False)

            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]).replace("'", "").replace('"',
                                                                                                               '') + "/LOGS/"
            self.writeStepToJson(real_parameters, "intraregistration", ".", logFolder=logFolder)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during seg intrareg: " + str(strlog))
        if properties:
            try :
                self.compute_properties(real_parameters)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during seg properties: " + str(strlog))

        if omero_config_file is not None:
            try:
                intra_folder = "INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]) + "/POST/POST_" + str(
                    real_parameters["EXP_POST"])
                self.upload_on_omero(omero_config_file, embryo_name, "INT_"+str(real_parameters["EXP_INTRAREG"])+"_"+"POST_" + str(real_parameters["EXP_POST"]),
                                     intra_folder, include_logs=True)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during intrareg post upload: " + str(strlog))
            try:
                intra_fuse_folder = "INTRAREG/INTRAREG_" + str(
                    real_parameters["EXP_INTRAREG"]) + "/FUSE/FUSE_" + str(real_parameters["EXP_FUSE"])
                self.upload_on_omero(omero_config_file, embryo_name, "INT_"+str(real_parameters["EXP_INTRAREG"])+"_"+"FUSE_" + str(real_parameters["EXP_FUSE"]),
                                     intra_fuse_folder, include_logs=True)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during intrareg fuse upload: " + str(strlog))
            try:
                trsfs_folder = [f for f in os.listdir("INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"])) if f.lower().startswith("trsfs_")]
                for folder in trsfs_folder:
                    self.upload_on_omero(omero_config_file, embryo_name, "INT_"+str(real_parameters["EXP_INTRAREG"])+"_"+str(folder),
                                         os.path.join("INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]),folder), include_logs=False)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during intrareg transform upload: " + str(strlog))

            try:
                rec = None
                if "EXP_RECONSTRUCTION" in real_parameters:
                    rec = "REC_" + real_parameters["EXP_RECONSTRUCTION"].replace('"', '').replace("'", "")
                else:
                    if "EXP_SEG" in real_parameters:
                        rec = "REC_" + real_parameters["EXP_SEG"].replace('"', '').replace("'", "")
                intra_rec_folder = "INTRAREG/INTRAREG_" + str(
                    parameters["EXP_INTRAREG"]) + "/REC-MEMBRANE/" + rec
                self.upload_on_omero(omero_config_file, embryo_name, "INT_" + rec, intra_rec_folder, include_logs=False)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during intrareg membrane upload: " + str(strlog))
        return real_parameters

    def compute_properties(self, parameters):
        """Start the properties computing step of the pipeline. It includes properties, naming and symetric cells distance.
        Please refer to AstecManager documentation for more details.

        :param parameters: Dict of the properties parameters
        :type parameters: dict
        """
        embryo_name = parameters["embryo_name"]
        begin = parameters["begin"]
        end = parameters["end"]
        try:
            self.add_to_run("PROPERTIES", ".", embryo_name, begin, parameters, end_time=end, compress_result=False)
            self.start_running(thread_number=1)
            logFolder = "./INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]).replace("'", "").replace('"',
                                                                                                          '') + "/LOGS/"
            self.writeStepToJson(parameters, "embryo_properties", ".", logFolder=logFolder)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during seg properties: " + str(strlog))
        try:
            self.name_embryo(parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during naming : " + str(strlog))
        try:
            embryo_name = embryo_name.replace('"', '').replace("'", "")
            lineage_path = "./INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]) + "/POST/POST_" + parameters[
                "EXP_POST"] + "/"
            lineage_name = embryo_name + "_intrareg_post_lineage.xml"
            lineage_complete_path = os.path.join(lineage_path, lineage_name)
            generate_lineage_comparison(lineage_complete_path, begin)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during lineage distance : " + str(strlog))
        try :
            parameters = {
                "EXP_POST" : parameters["EXP_POST"],
                "EXP_INTRAREG" : parameters["EXP_INTRAREG"],
            }
            self.generate_shift_to_boundingbox(parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during ratio of cells volume : " + str(strlog))
        try :
            parameters = {
                "EXP_POST": [parameters["EXP_POST"]],
                "EXP_INTRAREG": [parameters["EXP_INTRAREG"]],
                "target_generations": [7, 8, 9, 10],
                "compute_individuals_cells": False,
            }
            self.plot_found_ratios(parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during ratio of cells volume graph: " + str(strlog))

    def generate_lineage_distance(self,properties_path):
        """ Start the creation of 2 properties in the properties file : distances between symetric cells lineage

        :param properties_path: path to the properties file to use
        :type properties_path: str

        """
        if not os.path.isfile(properties_path):
            print("Error during generation , input file does not exist or can't be accessed. Check the path, and the rights of the file. ")
            return
        if Get_Cell_Names(properties_path) is None:
            print("No naming found in the properties path, please name your cells before comparing them")
            return

        min_time = 9999999
        cell_list = LoadCellList(properties_path)
        for cell in cell_list:
            cell_t, cell_id = get_id_t(str(cell))
            if cell_t < min_time:
                min_time = cell_t
        if min_time == 9999999:
            print("Unable to find the minimum time point in the 'cell_lineage' property. Please verify that the property is correct")
            return
        print("Found minimum time point : "+str(min_time))
        generate_lineage_comparison(properties_path,min_time)

    def prod_segmentation(self, parameters):
        """

        :param parameters: 

        """
        parameters["embryo_name"] = parameters["embryo_name"].replace('"', '').replace("'", "")
        if "begin" in parameters:
            parameters["begin"] = int(parameters["begin"])
        if "end" in parameters:
            parameters["end"] = int(parameters["end"])
        if not "EXP_SEG" in parameters:
            parameters["EXP_SEG"] = '01'
        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = "01"
        if not "EXP_CONTOUR" in parameters:
            parameters["EXP_CONTOUR"] = "01"
        if not "resolution" in parameters:
            parameters["resolution"] = 0.3
        if not "morphosnake_correction" in parameters:
            parameters["morphosnake_correction"] = False
        if not "mars_path" in parameters:
            parameters["mars_path"] = "./MARS/" + str(parameters["embryo_name"]) + "_mars_t{:03d}".format(parameters["begin"]) + ".nii"  # Path to the curated first time point image , do not change if located in embryo_name/MARS/ folder
        if not "use_membranes" in parameters:
            parameters["use_membranes"] = True
        if not "apply_normalisation" in parameters:
            parameters["apply_normalisation"] = True
        if not "normalisation" in parameters:
            parameters["normalisation"] = 1000
        omero_file = parameters["omero_authentication_file"]
        parameters["omero_authentication_file"] = "None"
        parameters["cell_count"] = parameters["automatic_naming_init_cell_count"]
        real_parameters = self.start_segmentation(parameters)
        omero_config_file = get_omero_config(real_parameters)
        rec_folder = 'REC-MEMBRANE/REC_'
        rec_exp = ""
        try :
            if "EXP_RECONSTRUCTION" in real_parameters:
                rec_folder += real_parameters["EXP_RECONSTRUCTION"]
                rec_exp = real_parameters["EXP_RECONSTRUCTION"]
            elif "EXP_POST" in real_parameters:
                rec_folder += real_parameters["EXP_POST"]
                rec_exp = real_parameters["EXP_POST"]
            elif "EXP_SEG" in real_parameters:
                rec_folder += real_parameters["EXP_SEG"]
                rec_exp = real_parameters["EXP_SEG"]
            if rec_folder != 'REC-MEMBRANE/REC_':
                self.mha_to_nii(parameters={'folder':rec_folder})
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during convert of reconstruction: " + str(strlog))
        if omero_config_file is not None:
            try:
                seg_folder = "SEG/SEG_" + str(real_parameters["EXP_SEG"])
                self.upload_on_omero(omero_config_file, real_parameters["embryo_name"],
                                     "SEG_" + str(real_parameters["EXP_SEG"]),
                                     seg_folder, include_logs=True,update_comment=True,params=real_parameters)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during segmentation seg upload: " + str(strlog))

        # Embryo dependant parameters
        if not "EXP_POST" in real_parameters:
            real_parameters["EXP_POST"] = real_parameters["EXP_SEG"]
        real_parameters = self.start_post_correction(real_parameters)
        if omero_config_file is not None:
            try:
                post_folder = "POST/POST_" + str(real_parameters["EXP_POST"])
                self.upload_on_omero(omero_config_file, real_parameters["embryo_name"],
                                     "POST_" + str(real_parameters["EXP_POST"]),
                                     post_folder, include_logs=True,update_comment=True,params=real_parameters)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during segmentation post upload: " + str(strlog))

        if omero_config_file is not None:
            if rec_folder != 'REC-MEMBRANE/REC_' and rec_exp != "":
                try:
                    self.upload_on_omero(omero_config_file, real_parameters["embryo_name"],
                                         "REC_MEMBRANE_" + str(rec_exp),
                                         rec_folder, include_logs=True,update_comment=True,params=real_parameters)
                except Exception as e:
                    strlog = traceback.format_exc()
                    print("Error during reconstruction  upload: " + str(strlog))

        real_parameters["omero_authentication_file"] = omero_file
        if not "EXP_INTRAREG" in real_parameters:
            real_parameters["EXP_INTRAREG"] = '01'
        real_parameters = self.apply_intrareg(real_parameters)

        self.compute_properties(real_parameters)

    def upload_data(self, parameters):
        """ Upload a specific folder to a OMERO dataset, including logs or not

        :param parameters: Dict of parameters for upload
        :type parameters: dict

        """
        omero_config_file = get_omero_config(parameters)
        project_name = parameters["project_name"].strip()
        dataset_name = parameters["dataset_name"].strip()
        input_folder = parameters["input_folder"]
        min_time = -1
        if "min_time" in parameters:
            min_time = int(parameters["min_time"])
        max_time = -1
        if "max_time" in parameters:
            max_time = int(parameters["max_time"])
        if omero_config_file is None:
            print("OMERO config file is not bound, unable to upload")
            exit()
        if not os.path.isfile(omero_config_file):
            print("Unable to find OMERO config file , unable to upload")
            exit()
        try:
            self.convert_step_dir(input_folder)
        except:
            print("Unable to convert images to OMERO format, but continue uploading")
        self.upload_on_omero(omero_config_file, project_name, dataset_name, input_folder,
                             include_logs=True,min_time=min_time,max_time=max_time)
