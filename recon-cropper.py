# MAIN P1: Ensuring that modules are installed in the correct place

print("Loading modules...")

# default modules
import os
import sys
import json
import subprocess
import pkg_resources

# installable modules
required = {'numpy', 'pillow', 'scikit-image', 'lxml'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("\nThe following modules were not found:")
    for mod in missing:
        print("-", mod)
    input("\nPress enter to install these modules.")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', "--upgrade", "pip"], stdout=subprocess.DEVNULL)
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

# custom modules
from pyrecon.tools.reconcropper.get_input import ynInput
from pyrecon.tools.reconcropper.explore_files import findDir
from pyrecon.tools.reconcropper.update import readAll, writeAll
from pyrecon.tools.reconcropper.switch import switchToGlobal, switchToCrop
from pyrecon.tools.reconcropper.guided_crop import guidedCrop
from pyrecon.tools.reconcropper.chunk_crop import newChunkCrop
from pyrecon.tools.reconcropper.import_transforms import changeGlobalTransformations

print("\nModules successfully loaded.")

# MAIN P2: Cropping and user interface for switching crops

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
    
print("\nPlease ensure that Reconstruct is closed before running this program.")

if os.path.isfile(os.path.dirname(__file__) + "/save.json"):
    # load previous working directory
    with open(os.path.dirname(__file__) + "/save.json", "r") as save_file:
        save_data = json.load(save_file)
    series_dir = save_data["lastdir"]
    print("\nThe last folder you worked on is:")
    print(series_dir)
    keep_dir = ynInput("\nWould you like to keep working on this folder? (y/n): ")
else:
    save_data = {}
    keep_dir = False
if not keep_dir:
    # prompt user to select series file
    print("\nPress enter to select the folder containing the series file.")
    input("(select an empty folder if you wish to create a new chunked series)")
    series_dir = findDir()

os.chdir(series_dir)
print("\nLocating series file...")
series_found = False
for file in os.listdir("."):
    if file.endswith(".ser"):
        series_found = True
        series_path = file

# create a chunked series if there is no series file
if not series_found:
    print("\nNo series file was found in this folder.")
    input("Press enter to create a chunked series.")
    newChunkCrop()
    input("Press enter to continue.")

# read from series file
print("\nLoading series data...")
series, tform_data = readAll(series_dir)

# check if the series has been chunked
is_chunked = "LOCAL_0,0" in list(tform_data.keys())

# open the menu
master_choice = " "
while master_choice != "":
    #clearScreen()

    print("\n----------------------------MENU----------------------------")
    print("\nCurrent working directory:\n" + series_dir)

    focus = tform_data["FOCUS"]
    if focus == "GLOBAL":
        print("\nThis series is currently set to the uncropped set of images.")
    else:
        focus_obj_name = focus[len("LOCAL_"):]
        print("\nThis series is currently focused on crop: " + focus_obj_name)
    
    print("\nPlease select from the following options:")
    print("1: Switch to the uncropped set of images")
    print("2: Switch to an existing chunk or object crop")
    print("3: Create a new guided crop around a RECONSTRUCT object")
    print("4: Divide series into chunks [NOT IMPLEMENTED YET]")
    print("5: Import new transformations")
    print("0: Change folders")
    master_choice = input("\nEnter your menu choice (or press enter to exit): ")

    if master_choice == "1":
        if focus == "GLOBAL":
            print("\nThe focus is already set to the uncropped images.")
        else:
            print("\nSwitching to uncropped series...")
            switchToGlobal(series, focus_obj_name, tform_data)
            print("\nWriting data to files...")
            writeAll(series, tform_data)
            print("Success!")
    
    elif master_choice == "2":
        print("\nPlease enter the name of the crop you would like to focus on.")
        print("- for object crops, enter the name of the object")
        if is_chunked:
            print("- for chunks, enter the coordinates as x,y with no space or parentheses")
        new_obj_name = input("Enter here: ")
        if focus != "GLOBAL" and new_obj_name == focus_obj_name:
            print("\nThe focus is already set to this crop.")
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
                print("Success!")
    
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
            print("Success!")
    
    elif master_choice == "5":
        if focus != "GLOBAL":
            print("\nSwitching to the uncropped series to prepare...")
            switchToGlobal(series, focus_obj_name, tform_data)
            print("Success!")
        changeGlobalTransformations(series, tform_data)
        print("\nWriting data to files...")
        writeAll(series, tform_data)
        print("Success!")
    
    elif master_choice == "0":
        series_found = False
        while series_found == False:
            input("\nPress enter to select the folder containing the series file.")
            series_dir = findDir()
            os.chdir(series_dir)
            print("\nLocating series file...")
            series_found = False
            for file in os.listdir("."):
                if file.endswith(".ser"):
                    series_found = True
            if series_found:
                print("\nLoading series data...")
                series, tform_data = readAll(series_dir)
                is_chunked = "LOCAL_0,0" in list(tform_data.keys())
                print("Success!")
            else:
                print("\nPlease select a folder that contains a series.")

        
    elif master_choice:
        print("\nThat is not a valid option.")

    if master_choice != "":
        input("\nPress enter to return to the menu.")

# save the working directory
print("\nSaving workspace data...")
save_data["lastdir"] = os.getcwd()
with open(os.path.dirname(__file__) + "/save.json", "w") as save_file:
    json.dump(save_data, save_file)
print("Success!")

print("\nGoodbye! :)")
