# MAIN P1: Ensuring that modules are installed in the correct place

print("Getting modules...")

# default modules
import os
import sys
import subprocess
import pkg_resources

# custom modules
from pyrecon.tools.reconcropper.explore_files import findFile
from pyrecon.tools.reconcropper.update import readAll, writeAll
from pyrecon.tools.reconcropper.switch import switchToGlobal, switchToCrop
from pyrecon.tools.reconcropper.guided_crop import guidedCrop

required = {'numpy', 'pillow', 'scikit-image', 'lxml'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("\nThe following modules were not found:")
    for mod in missing:
        print("-", mod)
    input("\nPress enter to install these modules.")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

# MAIN P2: Executing the program

# function for clearing output
def clearScreen():
    """ Clear the output.
    """
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

# MAIN P2: Cropping and user interface for switching crops
    
print("\nPlease ensure that Reconstruct is closed before running this program.")
input("Press enter to continue.")

# prompt user to select series file
input("\nPress enter to select the series file.")
series_path = findFile("Series File", "ser")

# read from series file
print("\nLoading series data...")
series, tform_data = readAll(series_path)

# open the menu
master_choice = " "
while master_choice != "":
    clearScreen()

    print("\n----------------------------MENU----------------------------")

    focus = tform_data["FOCUS"]
    if focus == "GLOBAL":
        print("\nThis series is currently set to the uncropped set of images.")
    else:
        focus_obj_name = focus[len("LOCAL_"):]
        print("\nThis series is currently focused on crop: " + focus_obj_name)
    
    print("\nPlease select from the following options:")
    print("1: Switch to the uncropped set of images")
    print("2: Switch to an existing set of images cropped around an object")
    print("3: Create a new guided crop around a RECONSTRUCT object")
    master_choice = input("\nEnter your menu choice (or press enter to exit): ")

    if master_choice == "1":
        if focus == "GLOBAL":
            print("\nThe focus is already set to the uncropped images.")
        else:
            print("Switching to uncropped series...")
            switchToGlobal(series, focus_obj_name, tform_data)
            print("Writing data to files...")
            writeAll(series, tform_data)
            print("\nSuccess!")
    
    elif master_choice == "2":
        new_obj_name = input("\nPlease enter the name of the object you would like to focus on: ")
        if new_obj_name == focus_obj_name:
            print("\nThe focus is already set to this object.")
        else:
            crop_found = False
            try:
                tform_data["LOCAL_" + new_obj_name]
                crop_found = True
            except KeyError:
                crop_found = False
                print("\nThis crop does not exist.")
                print("Please enter the number 3 in the main menu if you wish to create one.")
            if crop_found:
                if focus != "GLOBAL":
                    print("\nSwitching to the uncropped series to prepare...")
                    switchToGlobal(series, focus_obj_name, tform_data)
                    print("Success!")
                print("\nSwitching to the requested crop...")
                switchToCrop(series, new_obj_name, tform_data)
                print("\nWriting data to files...")
                writeAll(series, tform_data)
                print("\nSuccess!")
    
    elif master_choice == "3":
        new_obj_name = input("\nPlease enter the name of the object you would like to crop around: ")
        try:
            tform_data["LOCAL_" + new_obj_name]
            crop_found = True
            print("This crop already exists.")
            print("Please enter the number 2 in the main menu if you wish to switch to it.")
        except KeyError:
            crop_found = False
        if not crop_found:
            if focus != "GLOBAL":
                print("\nSwitching to the uncropped series to prepare...")
                switchToGlobal(series, focus_obj_name, tform_data)
                print("Success!")
            guidedCrop(series, new_obj_name, tform_data)
            print("\nSwitching to your new set of cropped images...")
            switchToCrop(series, new_obj_name, tform_data)
            print("\nWriting data to files...")
            writeAll(series, tform_data)
            print("\nSuccess!")


