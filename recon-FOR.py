"""Convert SWiFT c_afm output for Reconstruct."""

import sys
import copy
import os
import time
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def line_count(file_name):
    """Count lines in a file."""
    with open(file_name, "r") as f:
        line_count = sum(1 for _ in f)
    return line_count

def import_swift(file_name):
    """Get SWifT transformations as a list and strip of newline tags."""
    with open(file_name, "r") as input_file:
        output = input_file.readlines()
    output = [x.strip() for x in output]
    return output

def swift2matrix(transforms, sec):
    """Change SWiFT transformations to matrix."""
    sec_T = transforms[sec].split()  # Split line
    sec_T = list(map(float, sec_T))  # Convert to floats
    return np.array([[sec_T[1], sec_T[2], sec_T[3]],
                     [sec_T[4], sec_T[5], sec_T[6]],
                     [0,        0,        1]])

def matrix2recon(transform, dim):
    """Change frame of reference for SWiFT transforms to work in Reconstruct."""
    new_transform = copy.deepcopy(transform)

    # Calculate bottom left corner translation
    BL_corner = np.array([[0], [dim], [1]])  # BL corner from image height in px
    BL_translation = np.matmul(transform, BL_corner) - BL_corner

    # Add BL corner translation to SWiFT matrix
    new_transform[0, 2] = round(BL_translation[0, 0], 5)  # x translation
    new_transform[1, 2] = round(BL_translation[1, 0], 5)  # y translation

    # Flip y axis - change signs a2, b1, and b3
    new_transform[0, 1] *= -1  # a2
    new_transform[1, 0] *= -1  # b1
    new_transform[1, 2] *= -1  # b3

    # Stop-gap measure for Reconchonky
    new_transform = np.linalg.inv(new_transform)

    return new_transform

def swift2recon(swift_transforms, sec, dim):
    """Convert a single SWiFT transformation to Reconstruct frame of reference."""
    transform = swift2matrix(swift_transforms, sec)
    recon_matrix = matrix2recon(transform, dim)
    matrix_list = np.hstack([recon_matrix[0], recon_matrix[1]])
    #matrix_list = ' '.join(map(str, matrix_list))
    matrix_string = ""
    for x in range(matrix_list.shape[0]):
        # Awkward code to avoid scientific notation in .dat file output
        format_element = np.format_float_positional(matrix_list[x], trim='-') 
        matrix_string += format_element  + " "
    matrix_list = str(sec) + " " + matrix_string.strip()  # Remove last whitespace char
    return matrix_list

def print_success():
    print("                  (\n SUCCESSSSSSS!\n              (   ()   )")
    print("    ) ________    //  )\n ()  |\       \  //\n( \\\\__ \ ______\\//")
    print("   \\__) |       |\n     |  |       |\n      \\ |       |\n       \\|_______|")
    print("       //    \\\n      ((     ||\n       \\\\    ||")
    print("     ( ()    ||\n      (      () ) )")

def convert_transforms(swift_afm, new_file, img_height):
    """
    Return file with Reconstruct-edited transformations.

    Provide c_afm filename, an output filename, and the image height. If the new file already exists in directory, it will be overwritten.
    """

    # Remove new_file if already exists
    # if os.path.isfile(new_file):
    #     os.remove(new_file)

    swift_output = import_swift(swift_afm)
    sec_n = line_count(swift_afm)

    for i in range(sec_n):
        current_sec = i
        new_matrix = swift2recon(swift_output, current_sec, img_height)
        f = open(new_file, 'a')
        print(new_matrix, file = f)
        f.close()

# RUN SCRIPTS --------------------------------------------------------------------

# # DEBUGGING
# dir_path = "/home/michael/Dropbox/Medicine and Neuroscience/KH-lab/tools-project/swift-transforms/"
# data_file = "CSYSR_SWiFT_transforms_brOFF.dat"
# img_height = 24576

dir_path = os.path.dirname(sys.argv[0])
new_file = "recon_c_afm.dat"

os.chdir(dir_path)

print("\nThis script will convert SWiFT transformations to the frame of reference used by Reconstruct. Its output can be used with reconchonky.py.")

input("\nPress <enter> to select the .dat file that contains SWiFT transformations.")
Tk().withdraw()
data_file = askopenfilename()

img_height = int(input("\nProvide height of the pre-aligned raw images in pixels (e.g., 24576): "))

# Clear screen for results
if os.name == "nt":
    _ = os.system('cls')

print("\nHold please...")

time.sleep(2)

if os.name == "nt":
    _ = os.system('cls')

convert_transforms(data_file, new_file, img_height)

print_success()

print("\n\n-----------------------------------------------------------------------")
print("\nYour new transformations are stored in:")
print("\n" + os.getcwd() + "\\" + new_file)
print("\n-----------------------------------------------------------------------")

input("\n\nHave a pleasant day aligning! :D\n\nHit <enter> to exit...")

# # DEBUGGING--------------------------------
# # print section from old file
# that_file = import_swift(data_file)
# print(that_file[0])

# # print section from new file
# this_file = import_swift(new_file)
# print(this_file[0])
