"""Main recon-cropper program."""

import sys
import os
from datetime import datetime
from funs.helpers import *

print("Getting modules...")

###############################################################################
###############################################################################
#
# # Consider the following to import missing modules:
# #
# # https://stackoverflow.com/questions/44210656/how-to-check-if-a-module-is-installed-in-python-and-if-not-install-it-within-t
#
# import sys
# import subprocess
# import pkg_resources

# required = {'mutagen', 'gTTS'}
# installed = {pkg.key for pkg in pkg_resources.working_set}
# missing = required - installed

# if missing:
#     python = sys.executable
#     subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
#
###############################################################################
###############################################################################

# boolean to keep track if module needs to be imported
needs_import = False

# find the site-packages folder to put the modules into
for p in sys.path:
    if p.endswith("site-packages"):
        module_dir = p

# raise an error if there is no site-packages folder
if not module_dir:
    raise Exception("There is no site-packages folder located on the path.")

# try to import numpy
try:
    import numpy as np
    numpy_bat = ""
except ModuleNotFoundError:
    # if not found, inform user and set up batch text
    needs_import = True
    print("\nThe numpy module is not found in the current path.")
    numpy_bat = "pip install numpy --target " + module_dir + "\n"

# try to import tkinter (should already be a part of python)
try:
    from tkinter import *
    from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
    tkinter_bat = ""
except ModuleNotFoundError:
    # if not found, inform user and set up batch text
    needs_import = True
    print("\nThe tkinter module is not found in the current path.")
    tkinter_bat = "pip install tk --target " + module_dir + "\n"

# try to import Pillow
try:
    from PIL import Image as PILImage
    PILImage.MAX_IMAGE_PIXELS = None # turn off image size restriction
    Pillow_bat = ""
except ModuleNotFoundError:
    # if not found, inform user and set up batch text
    needs_import = True
    print("\nThe Pillow module is not found in the current path.")
    Pillow_bat = "pip install Pillow --target " + module_dir + "\n"

# do nothing if all modules found
if not needs_import:
    print("\nAll required modules have been successfully located.")

# install modules that were not found
else:
    #ask user if they want to direct the program to the modules
    directing = ynInput("Would you like to find the site-packages folder containing the required modules? (y/n): ")
    
    if directing:
        site_packages_dir = input("Please paste the path for the site-packages directory containing the required modules.")
        sys.path.append(site_packages_dir)

        # try to import all of the required modules again
        try:
            import numpy as np
            from tkinter import *
            from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
            from PIL import Image as PILImage
            PILImage.MAX_IMAGE_PIXELS = None # turn off image size restriction
            print("Modules have been found.")

        # if given folder still doesn't contain module, download them
        except ModuleNotFoundError:
            print("Modules were not found in provided folder.")
            directing = False
        
    # download modules if user does not locate them
    if not directing:
        input("\nPress enter for confirmation to automatically download the modules.")
        
        # create the batch file
        bat = open("InstallModules.bat", "w")
        bat.write(numpy_bat)
        bat.write(tkinter_bat)
        bat.write(Pillow_bat)
        bat.close()

        # run the batch file with subprocess module
        print("\nOpening Command Prompt to install required modules...")    
        import subprocess
        subprocess.call(["InstallModules.bat"])

        # delete the batch
        os.remove("InstallModules.bat")

        # import the modules that were just installed
        if numpy_bat:
            import numpy as np
        if tkinter_bat:
            from tkinter import *
            from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
        if Pillow_bat:
            from PIL import Image as PILImage
            PILImage.MAX_IMAGE_PIXELS = None

        print("\nThe necessary modules have been installed.")

# MAIN P2: Cropping and user interface for switching crops
    
print("\nPlease ensure that Reconstruct is closed before running this program.")
input("Press enter to continue.")

# prompt user to select new directory
input("\nPress enter to select the working directory.")

# create tkinter object but don't display extra window
root = Tk()
root.attributes("-topmost", True)
root.withdraw()

# open file explorer to select new working directory
new_dir = []
while not new_dir:
    new_dir = askdirectory(title="Select Folder")

print("Working directory: " + new_dir)
os.chdir(new_dir)
    
# locate the series file and get series name if found
print("\nLocating series file...")
seriesFileName = ""
for file in os.listdir("."):
    if file.endswith(".ser"):
        seriesFileName = str(file)

# prompt user to switch crops if there is an existing series file
if seriesFileName:

    master_choice = " "

    while master_choice != "":
    
        # gather series info data
        seriesName, sectionNums = getSeriesInfo(seriesFileName)

        clearScreen()

        print("\n----------------------------MENU----------------------------")

        # find and output the current crop focus
        cropFocus = getCropFocus(seriesName + "." + str(sectionNums[0]), seriesName)
        if cropFocus:
            print("\nThis series is currently focused on crop: " + cropFocus)
        else:
            print("\nThis series is currently set to the uncropped set of images.")

        isChunked = os.path.isdir(seriesName + "_0,0")

        print("\nPlease select from the following options:")
        print("1: Switch to the uncropped set of images")
        print("2: Switch to set of images cropped around an object")
        if isChunked:
            print("3: Switch to a specific chunk")
        print("0: Import transformations")

        master_choice = input("\nEnter your menu choice (or press enter to exit): ")

        # if changing alignment
        if master_choice == "0":

            if cropFocus != "":
                print("\nSwitching back to the uncropped series...")
                switchToUncropped(seriesName, cropFocus)
                print("Successfully set the uncropped series as the focus.")

            input("\nPress enter to select the file containing the transformations.")
            
            # open file explorer for user to select files
            root = Tk()
            root.attributes("-topmost", True)
            root.withdraw()        
            newTransFile = askopenfilename(title="Select Transformation File",
                                   filetypes=(("Data File", "*.dat"),
                                              ("All Files","*.*")))

            is_from_SWIFT = ynInput("\nIs this from SWIFT output? (y/n): ")

            if not is_from_SWIFT:
                print("Each line in the trasnformation file should contain the following information:")
                print("[section number] [six numbers indicating transformation applied to picture]")
                print("\nFor example:")
                print("0 1 0 0 0 1 0")
                print("1 1.13 0.1 0.53 0 0.9 0.6")
                print("2 1.11 0 0.51 0.01 0.92 0.9")
                print("...")
                print("\nPlease ensure that your file fits this format.")
                input("\nPress enter to continue.")
            
            # section 0 is often the grid and does not get aligned
            startTrans = intInput("\nWhat section do the transformations start on?: ")

            # save existing transformations and mark with date and time
            print("\nSaving existing transformations...")

            time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            fileName = "SAVED_GLOBAL_TRANSFORMATIONS_" + time_str + ".txt"

            saved_trans = open(fileName, "w")
            global_trans = open("GLOBAL_TRANSFORMATIONS.txt", "r")

            for line in global_trans.readlines():
                saved_trans.write(line)

            saved_trans.close()
            global_trans.close()

            print(fileName + " has been saved.")

            # get image height if needed
            last_section_info = getSectionInfo(seriesName + "." + str(sectionNums[-1]))
            micPerPix = last_section_info[2]
            img_height = 0
            if is_from_SWIFT:
                try:
                    last_sec_img = PILImage.open(last_section_info[3]) # open the last section image
                    img_height = last_sec_img.size[1] # get the last section image height
                except:
                    print("\nUncropped images not found.")
                    img_height = intInput("Please enter the height (in pixels) of the UNCROPPED images: ")

            new_trans = getNewTransformations(newTransFile, micPerPix, is_from_SWIFT, img_height)

            # apply new transformations
            print("\nChanging global transformations...")       
            changeGlobalTransformations(seriesName, sectionNums, new_trans, startTrans)

            print("Completed!")

            reset_local_trans = ynInput("\nWould you like to reset all of the local transformations? (y/n): ")

            if reset_local_trans:
                for file in os.listdir():
                    if os.path.isfile(file) and "LOCAL_TRANSFORMATIONS.txt" in file:
                        local_trans = open(file, "r")
                        lines = local_trans.readlines()
                        local_trans.close()
                        
                        new_trans = open(file, "w")
                        for line in lines:
                            if line.startswith("Dtrans:"):
                                line = "Dtrans: 1 0 0 0 1 0\n"
                            new_trans.write(line)
                        new_trans.close()

            print("\nLocal transformations have been reset.")

            if cropFocus != "":
                print("\nSwitching back to previous focus...")
                switchToCrop(seriesName, cropFocus)
                print("Successfully reset focus to " + cropFocus + ".")

        # if switching to uncropped
        elif master_choice == "1":
            
            # if already on uncropped
            if cropFocus == "":
                print("\nThe uncropped series is already set as the focus.")                                    

            # switch to uncropped if not
            else: 
                print("\nSwitching to the uncropped series...")
                switchToUncropped(seriesName, cropFocus)
                print("Successfully set the uncropped series as the focus.")

        # if switching to crop
        elif master_choice == "2" or master_choice == "3" and isChunked:

            # get the name of the desired object
            newFocus = ""
            while newFocus == "":
                if master_choice == "2":
                    newFocus = input("\nPlease enter the name of the object you would like to focus on: ")
                if master_choice == "3":
                    newFocus = input("\nPlease enter the coordinates you would like to focus on.\n" +
                                     "(x,y with no spaces or parenthesis): ")
                if newFocus == "":
                    print("Please enter a valid object name.")

            # if already on desired crop
            if cropFocus == newFocus:
                print("\n" + newFocus + " is already set as the focus.")

            # if switching to an existing crop
            elif os.path.isdir(seriesName + "_" + newFocus):

                # switch to the uncropped version if not already on
                if cropFocus != "":
                    print("\nSwitching to the uncropped series to prepare...")
                    switchToUncropped(seriesName, cropFocus)
                    print("Successfully set the uncropped series as the focus.")
                
                print("\nSwitching to " + newFocus + "...")
                switchToCrop(seriesName, newFocus)
                print("Successfully set " + newFocus + " as the focus.")

            # if crop does not exist, make the guided crop
            elif not os.path.isdir(seriesName + "_" + newFocus) and master_choice == "2":
                print("\nThis crop does not exist.")
                input("Press enter to create a new crop for this object.")
                
                obj = newFocus # set obj variable as newFocus variable

                # switch to the uncropped version if not on already
                if cropFocus != "":
                    print("\nSwitching to uncropped series...")
                    switchToUncropped(seriesName, cropFocus)
                
                print("\nLocating the object...")

                # create a dictionary: key = section number, value = list of bounds
                bounds_dict = {}
                for sectionNum in sectionNums:
                    bounds_dict[sectionNum] = findBounds(seriesName + "." + str(sectionNum), obj)
                bounds_dict = fillInBounds(bounds_dict)

                # check to see if the object was found
                noTraceFound = True
                for bounds in bounds_dict:
                    if bounds_dict[bounds] != None:
                        noTraceFound = False
                
                if noTraceFound:
                    print("\nThis trace does not exist in this series.")

                # if trace was found, continue
                else:
                    print("Completed successfully!")

                    # get section info for every section
                    sectionInfo = {}
                    for sectionNum in sectionNums:
                        sectionInfo[sectionNum] = getSectionInfo(seriesName + "." + str(sectionNum))

                    # check if section images are all in the directory
                    images_in_dir = True
                    for sectionNum in sectionNums:
                        images_in_dir = images_in_dir and os.path.isfile(sectionInfo[sectionNum][3])

                    # get the original series images to make the guided crop if all images are not found
                    if not images_in_dir:
                        input("\nPress enter to select the uncropped series images.")

                        # create tkinter object but don't display extra window
                        root = Tk()
                        root.attributes("-topmost", True)
                        root.withdraw()

                        # open file explorer for user to select the image files
                        imageFiles = list(askopenfilenames(title="Select Image Files",
                                                   filetypes=(("Image Files", "*.tif"),
                                                              ("All Files","*.*"))))

                        # stop program if user does not select images
                        if len(imageFiles) == 0:
                            raise Exception("No pictures were selected.")

                    
                    # ask the user for the cropping rad
                    rad = floatInput("\nHow many microns around the object would you like to have in the crop?: ")
                    
                    # create the folder for the cropped images
                    newLocation = seriesName + "_" + obj
                    os.mkdir(newLocation)

                    # create new trace files with shift domain origins
                    print("\nCreating new domain origins file...")
                    newTransformationsFile = open(obj + "_LOCAL_TRANSFORMATIONS.txt", "w")

                    # shift the domain origins to bottom left corner of planned crop
                    for sectionNum in sectionNums:

                        # fix the coordinates to the picture
                        inv_global_trans = np.linalg.inv(coefToMatrix(sectionInfo[sectionNum][0], sectionInfo[sectionNum][1])) # get the inverse section transformation
                        min_coords = np.matmul(inv_global_trans, [[bounds_dict[sectionNum][0]],[bounds_dict[sectionNum][2]],[1]]) # transform the bottom left corner coordinates

                        # translate coordinates to pixels
                        pixPerMic = 1.0 / sectionInfo[sectionNum][2] # get image magnification
                        xshift_pix = int((min_coords[0][0] - rad) * pixPerMic)
                        if xshift_pix < 0:
                            xshift_pix = 0
                        yshift_pix = int((min_coords[1][0] - rad) * pixPerMic)
                        if yshift_pix < 0:
                            yshift_pix = 0

                        # write the shifted origin to the transformations file
                        newTransformationsFile.write("Section " + str(sectionNum) + "\n" +
                                                     "xshift: " + str(xshift_pix) + "\n" +
                                                     "yshift: " + str(yshift_pix) + "\n" +
                                                     "Dtrans: 1 0 0 0 1 0\n")

                    newTransformationsFile.close()

                    print(obj + "_LOCAL_TRANSFORMATIONS.txt has been stored.")
                    print("Do NOT delete this file.")

                    print("\nCropping images around bounds...")
                    
                    # crop each image
                    counter = 0
                    for sectionNum in sectionNums:

                        # get the name of the desired image file
                        if images_in_dir:
                            fileName = sectionInfo[sectionNum][3]
                            filePath = fileName
                        else:
                            filePath = imageFiles[counter]
                            fileName = filePath[filePath.rfind("/")+1:]
                            counter += 1

                        print("\nWorking on " + fileName + "...")
                        
                        # open original image
                        img = PILImage.open(filePath)

                        # get image dimensions
                        img_length, img_height = img.size
                        
                        # get magnification
                        pixPerMic = 1.0 / sectionInfo[sectionNum][2]
                        
                        # get the bounds coordinates in pixels
                        inv_global_trans = np.linalg.inv(coefToMatrix(sectionInfo[sectionNum][0], sectionInfo[sectionNum][1]))
                        min_coords = np.matmul(inv_global_trans, [[bounds_dict[sectionNum][0]],[bounds_dict[sectionNum][2]],[1]])
                        max_coords = np.matmul(inv_global_trans, [[bounds_dict[sectionNum][1]],[bounds_dict[sectionNum][3]],[1]])

                        # get the pixel coordinates for each corner of the crop
                        left = int((min_coords[0][0] - rad) * pixPerMic)
                        bottom = img_height - int((min_coords[1][0] - rad) * pixPerMic)
                        right = int((max_coords[0][0] + rad) * pixPerMic)
                        top = img_height - int((max_coords[1][0] + rad) * pixPerMic)
                        
                        # if crop exceeds image boundary, cut it off
                        if left < 0: left = 0
                        if right >= img_length: right = img_length-1
                        if top < 0: top = 0
                        if bottom >= img_height: bottom = img_height-1

                        # crop the photo
                        cropped = img.crop((left, top, right, bottom))
                        cropped.save(newLocation + "/" + fileName)
                        
                        print("Saved!")

                    print("\nCropping has run successfully!")

                    print("\nSwitching to new crop...")
                    switchToCrop(seriesName, obj)

                    print("Successfully set " + obj + " as the focus.")

            # if the user enters invalid coords
            elif not os.path.isdir(seriesName + "_" + newFocus) and master_choice == "3":
                print("\nThese coordinates do not exist.")

        elif master_choice != "":
            print("\nPlease enter a valid response from the menu.")

        if master_choice != "": input("\nPress enter to return to the menu.")

# cropping a new set of images if there is no detected series file
else:
    print("\nThere does not appear to be an existing series.")

    # force user to give a series name
    seriesName = ""
    while seriesName == "":
        seriesName = input("\nPlease enter the desired name for the series: ")
        if seriesName == "":
            print("Please enter a valid series name.")
    
    input("\nPress enter to select the pictures you would like to crop.")

    # create tkinter object but don't display extra window
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    # open file explorer for user to select images
    imageFiles = list(askopenfilenames(title="Select Image Files",
                               filetypes=(("Image Files", "*.tif"),
                                          ("All Files","*.*"))))

    # stop program if user does not select images
    if len(imageFiles) == 0:
        raise Exception("No pictures were selected.")

    # get grid information
    xchunks = intInput("\nHow many horizontal chunks would you like to have?: ")
    ychunks = intInput("How many vertical chunks would you like to have?: ")
    overlap = floatInput("How many microns of overlap should there be between chunks?: ")
    
    # get series information
    startSection = intInput("\nWhat section number would you like your new series to start on?\n" +
                            "(when calibration grid is included, 0 is the standard): ")
    sectionThickness = floatInput("\nWhat would you like to set as the section thickness? (in microns): ")

    # check if series has already been calibrated
    isCalibrated = ynInput("\nHas this series been calibrated? (y/n): ")

    if isCalibrated:
        
        micPerPix = floatInput("How many microns per pixel are there for this series?: ")

        # check if there is an existing transformation file
        isTrans = ynInput("\nIs there an existing transformation file for this series? (y/n): ")
        
        if isTrans:
            input("Press enter to select the file containing the transformations.")
            baseTransformations = askopenfilename(title="Select Transformation File",
                                   filetypes=(("Data File", "*.dat"),
                                              ("All Files","*.*")))

            # check if transformations are meant for Reconstruct or SWIFT output
            is_from_SWIFT = ynInput("\nIs this from SWIFT output? (y/n): ")

            # section 0 is often the grid and does not get aligned
            trans_offset = intInput("\nWhat section do the transformations start on?: ") - startSection

    else:

        micPerPix = 0.00254
        print("\nMicrons per pixel has been set to default value of 0.00254.")
        
        isTrans = False
        print("\nREAD THE FOLLOWING INSTRUCTIONS:")
        print("If you wish to apply a set of existing transformations to this series, please calibrate it first.")
        print("When calibrating, traces can be made in any quadrant, but you MUST perform the actual calibration")
        print("after switching back to the uncropped series. You do not need the uncropped images to calibrate.")
        print("Then you will be able to apply transformations using this program after calibrating the series in Reconstruct.")

        input("\nPress enter to continue crop the images.")

    # create each folder
    print("\nCreating folders...")
    for x in range(xchunks):
        for y in range(ychunks):
            os.mkdir(seriesName + "_" + str(x) + "," + str(y))

    # store new domain origins
    newDomainOrigins = []

    # store max image length and height
    img_length_max = 0
    img_height_max = 0

    # start iterating through each of the images
    for i in range(len(imageFiles)):

        file_path = imageFiles[i]
        file_name = file_path[file_path.rfind("/")+1:]

        print("\nWorking on " + file_name + "...")

        # open image and get dimensions
        img = PILImage.open(imageFiles[i])
        img_length, img_height = img.size
        if img_length > img_length_max:
            img_length_max = img_length
        if img_height > img_height_max:
            img_height_max = img_height
        
        # iterate through each chunk and calculate the coords for each of the corners
        for x in range(xchunks):
            newDomainOrigins.append([])
            for y in range(ychunks):
                
                left = int((img_length-1) * x / xchunks - overlap/2 / micPerPix)
                if left < 0:
                    left = 0
                right = int((img_length-1) * (x+1) / xchunks + overlap/2 / micPerPix)
                if right >= img_length:
                    right = img_length - 1
                
                top = int((img_height-1) * (ychunks - y-1) / ychunks - overlap/2 / micPerPix)
                if top < 0:
                      top = 0 
                bottom = int((img_height-1) * (ychunks - y) / ychunks + overlap/2 / micPerPix)
                if bottom >= img_height:
                    bottom = img_height - 1

                # crop the photo
                cropped = img.crop((left, top, right, bottom))
                
                newDomainOrigins[x].append((left, int(img_height-1 - bottom)))

                # save as uncompressed TIF
                cropped.save(seriesName + "_" + str(x) + "," + str(y) + "/" + file_name)

        print("Completed!")

    # iterate through each of the chunks to create the local transformations file
    for x in range(xchunks):
        for y in range(ychunks):
            newTransformationsFile = open(str(x) + "," + str(y) +
                                         "_LOCAL_TRANSFORMATIONS.txt", "w")
            for i in range(len(imageFiles)):
                
                # shift the domain origins to bottom left corner of planned crop
                xshift_pix = newDomainOrigins[x][y][0]
                yshift_pix = newDomainOrigins[x][y][1]
                newTransformationsFile.write("Section " + str(i + startSection) + "\n" +
                                             "xshift: " + str(xshift_pix) + "\n" +
                                             "yshift: " + str(yshift_pix) + "\n" +
                                             "Dtrans: 1 0 0 0 1 0\n")
            newTransformationsFile.close()

    print("\nA LOCAL_TRANSFORMATIONS.txt has been stored for each quadrant.")
    print("Do NOT delete these files.")

    # if the series does have an existing transformation, apply it
    if isTrans:

        all_transformations = getNewTransformations(baseTransformations, micPerPix, is_from_SWIFT, img_height_max)

        globalTransFile = open("GLOBAL_TRANSFORMATIONS.txt", "w")
        for i in range(len(imageFiles)):
            if i - trans_offset < 0:
                globalTransFile.write("Section " + str(i + startSection) + "\n" +
                                      "xcoef: 0 1 0 0 0 0\n" +
                                      "ycoef: 0 0 1 0 0 0\n")
            else:
                itransMatrix = np.linalg.inv(all_transformations[i - trans_offset]) # get the inverse

                # write the transformation data to the global transformations file
                globalTransFile.write("Section " + str(i + startSection) + "\n" +
                                    "xcoef: " + str(itransMatrix[0][2]) + " " + str(itransMatrix[0][0]) +
                                    " " + str(itransMatrix[0][1]) + " 0 0 0\n" +
                                    "ycoef: " + str(itransMatrix[1][2]) + " " + str(itransMatrix[1][0]) +
                                    " " + str(itransMatrix[1][1]) + " 0 0 0\n")
        globalTransFile.close()
        
    # if the series does not have an existing transformation file, then set all transformations to identity
    else:
        globalTransFile = open("GLOBAL_TRANSFORMATIONS.txt", "w")
        for i in range(len(imageFiles)):
            globalTransFile.write("Section " + str(i + startSection) + "\n" +
                                      "xcoef: 0 1 0 0 0 0\n" +
                                      "ycoef: 0 0 1 0 0 0\n")
        globalTransFile.close()

    print("\nGLOBAL_TRANSFORMATIONS.txt has been stored.")
    print("Do NOT delete this file.")

    print("\nCreating new section and series files...")

    # store a blank section file in the program
    # could be stored in txt file but having everything in one file keeps it simple for user
    blankSectionFile = """<?xml version="1.0"?>
<!DOCTYPE Section SYSTEM "section.dtd">
<Section index="[SECTION_INDEX]" thickness="[SECTION_THICKNESS]" alignLocked="false">
<Transform dim="[TRANSFORM_DIM]"
 xcoef="[XCOEF]"
 ycoef="[YCOEF]">
<Image mag="[IMAGE_MAG]" contrast="1" brightness="0" red="true" green="true" blue="true"
 src="[IMAGE_SOURCE]" />
<Contour name="domain1" hidden="false" closed="true" simplified="false" border="1 0 1" fill="1 0 1" mode="11"
 points="0 0,
        [IMAGE_LENGTH] 0,
        [IMAGE_LENGTH] [IMAGE_HEIGHT],
        0 [IMAGE_HEIGHT],
        "/>
</Transform>
</Section>"""

    # replace the unknowns in the section file with known info
    blankSectionFile = blankSectionFile.replace("[SECTION_THICKNESS]", str(sectionThickness))
    blankSectionFile = blankSectionFile.replace("[TRANSFORM_DIM]", "3")
    blankSectionFile = blankSectionFile.replace("[IMAGE_MAG]", str(micPerPix))
    blankSectionFile = blankSectionFile.replace("[IMAGE_LENGTH]", str(int(img_length_max)))
    blankSectionFile = blankSectionFile.replace("[IMAGE_HEIGHT]", str(int(img_height_max)))

    globalTrans = open("GLOBAL_TRANSFORMATIONS.txt", "r")

    # iterate through each section and create the section file
    for i in range(len(imageFiles)):

        file_path = imageFiles[i]
        file_name = file_path[file_path.rfind("/")+1:]
        
        newSectionFile = open(seriesName + "." + str(i + startSection), "w")

        # retrieve global transformations
        globalTrans.readline()
        xcoef_data = globalTrans.readline()
        xcoef_str = xcoef_data[xcoef_data.find(":")+1 : xcoef_data.find("\n")]
        ycoef_data = globalTrans.readline()
        ycoef_str = ycoef_data[ycoef_data.find(":")+1 : ycoef_data.find("\n")]

        # replace section-specific unknowns with known info
        sectionFileText = blankSectionFile.replace("[SECTION_INDEX]", str(i + startSection))
        sectionFileText = sectionFileText.replace("[IMAGE_SOURCE]", file_name)
        sectionFileText = sectionFileText.replace("[XCOEF]", xcoef_str)
        sectionFileText = sectionFileText.replace("[YCOEF]", ycoef_str)

        newSectionFile.write(sectionFileText)
        newSectionFile.close()

    # create the series file
    blankSeriesFile = """<?xml version="1.0"?>
<!DOCTYPE Series SYSTEM "series.dtd">
<Series index="[SECTION_NUM]" viewport="0 0 0.00254"
        units="microns"
        autoSaveSeries="true"
        autoSaveSection="true"
        warnSaveSection="true"
        beepDeleting="true"
        beepPaging="true"
        hideTraces="false"
        unhideTraces="false"
        hideDomains="false"
        unhideDomains="false"
        useAbsolutePaths="false"
        defaultThickness="0.05"
        zMidSection="false"
        thumbWidth="128"
        thumbHeight="96"
        fitThumbSections="false"
        firstThumbSection="1"
        lastThumbSection="2147483647"
        skipSections="1"
        displayThumbContours="true"
        useFlipbookStyle="false"
        flipRate="5"
        useProxies="true"
        widthUseProxies="2048"
        heightUseProxies="1536"
        scaleProxies="0.25"
        significantDigits="6"
        defaultBorder="1.000 0.000 1.000"
        defaultFill="1.000 0.000 1.000"
        defaultMode="9"
        defaultName="domain$+"
        defaultComment=""
        listSectionThickness="true"
        listDomainSource="true"
        listDomainPixelsize="true"
        listDomainLength="false"
        listDomainArea="false"
        listDomainMidpoint="false"
        listTraceComment="true"
        listTraceLength="false"
        listTraceArea="true"
        listTraceCentroid="false"
        listTraceExtent="false"
        listTraceZ="false"
        listTraceThickness="false"
        listObjectRange="true"
        listObjectCount="true"
        listObjectSurfarea="false"
        listObjectFlatarea="false"
        listObjectVolume="false"
        listZTraceNote="true"
        listZTraceRange="true"
        listZTraceLength="true"
        borderColors="0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                "
        fillColors="0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                0.000 0.000 0.000,
                "
        offset3D="0 0 0"
        type3Dobject="0"
        first3Dsection="1"
        last3Dsection="2147483647"
        max3Dconnection="-1"
        upper3Dfaces="true"
        lower3Dfaces="true"
        faceNormals="false"
        vertexNormals="true"
        facets3D="8"
        dim3D="-1 -1 -1"
        gridType="0"
        gridSize="1 1"
        gridDistance="1 1"
        gridNumber="1 1"
        hueStopWhen="3"
        hueStopValue="50"
        satStopWhen="3"
        satStopValue="50"
        brightStopWhen="0"
        brightStopValue="100"
        tracesStopWhen="false"
        areaStopPercent="999"
        areaStopSize="0"
        ContourMaskWidth="0"
        smoothingLength="7"
        mvmtIncrement="0.022 1 1 1.01 1.01 0.02 0.02 0.001 0.001"
        ctrlIncrement="0.0044 0.01 0.01 1.002 1.002 0.004 0.004 0.0002 0.0002"
        shiftIncrement="0.11 100 100 1.05 1.05 0.1 0.1 0.005 0.005"
        >
<Contour name="a$+" closed="true" border="1.000 0.500 0.000" fill="1.000 0.500 0.000" mode="13"
 points="-3 1,
        -3 -1,
        -1 -3,
        1 -3,
        3 -1,
        3 1,
        1 3,
        -1 3,
        "/>
<Contour name="b$+" closed="true" border="0.500 0.000 1.000" fill="0.500 0.000 1.000" mode="13"
 points="-2 1,
        -5 0,
        -2 -1,
        -4 -4,
        -1 -2,
        0 -5,
        1 -2,
        4 -4,
        2 -1,
        5 0,
        2 1,
        4 4,
        1 2,
        0 5,
        -1 2,
        -4 4,
        "/>
<Contour name="pink$+" closed="true" border="1.000 0.000 0.500" fill="1.000 0.000 0.500" mode="-13"
 points="-6 -6,
        6 -6,
        0 5,
        "/>
<Contour name="X$+" closed="true" border="1.000 0.000 0.000" fill="1.000 0.000 0.000" mode="-13"
 points="-7 7,
        -2 0,
        -7 -7,
        -4 -7,
        0 -1,
        4 -7,
        7 -7,
        2 0,
        7 7,
        4 7,
        0 1,
        -4 7,
        "/>
<Contour name="yellow$+" closed="true" border="1.000 1.000 0.000" fill="1.000 1.000 0.000" mode="-13"
 points="8 8,
        8 -8,
        -8 -8,
        -8 6,
        -10 8,
        -10 -10,
        10 -10,
        10 10,
        -10 10,
        -8 8,
        "/>
<Contour name="blue$+" closed="true" border="0.000 0.000 1.000" fill="0.000 0.000 1.000" mode="9"
 points="0 7,
        -7 0,
        0 -7,
        7 0,
        "/>
<Contour name="magenta$+" closed="true" border="1.000 0.000 1.000" fill="1.000 0.000 1.000" mode="9"
 points="-6 2,
        -6 -2,
        -2 -6,
        2 -6,
        6 -2,
        6 2,
        2 6,
        -2 6,
        "/>
<Contour name="red$+" closed="true" border="1.000 0.000 0.000" fill="1.000 0.000 0.000" mode="9"
 points="6 -6,
        0 -6,
        0 -3,
        3 0,
        12 3,
        6 6,
        3 12,
        -3 6,
        -6 0,
        -6 -6,
        -12 -6,
        -3 -12,
        "/>
<Contour name="green$+" closed="true" border="0.000 1.000 0.000" fill="0.000 1.000 0.000" mode="9"
 points="-12 4,
        -12 -4,
        -4 -4,
        -4 -12,
        4 -12,
        4 -4,
        12 -4,
        12 4,
        4 4,
        4 12,
        -4 12,
        -4 4,
        "/>
<Contour name="cyan$+" closed="true" border="0.000 1.000 1.000" fill="0.000 1.000 1.000" mode="9"
 points="0 12,
        4 8,
        -12 -8,
        -8 -12,
        8 4,
        12 0,
        12 12,
        "/>
<Contour name="a$+" closed="true" border="1.000 0.500 0.000" fill="1.000 0.500 0.000" mode="13"
 points="-3 1,
        -3 -1,
        -1 -3,
        1 -3,
        3 -1,
        3 1,
        1 3,
        -1 3,
        "/>
<Contour name="b$+" closed="true" border="0.500 0.000 1.000" fill="0.500 0.000 1.000" mode="13"
 points="-2 1,
        -5 0,
        -2 -1,
        -4 -4,
        -1 -2,
        0 -5,
        1 -2,
        4 -4,
        2 -1,
        5 0,
        2 1,
        4 4,
        1 2,
        0 5,
        -1 2,
        -4 4,
        "/>
<Contour name="pink$+" closed="true" border="1.000 0.000 0.500" fill="1.000 0.000 0.500" mode="-13"
 points="-6 -6,
        6 -6,
        0 5,
        "/>
<Contour name="X$+" closed="true" border="1.000 0.000 0.000" fill="1.000 0.000 0.000" mode="-13"
 points="-7 7,
        -2 0,
        -7 -7,
        -4 -7,
        0 -1,
        4 -7,
        7 -7,
        2 0,
        7 7,
        4 7,
        0 1,
        -4 7,
        "/>
<Contour name="yellow$+" closed="true" border="1.000 1.000 0.000" fill="1.000 1.000 0.000" mode="-13"
 points="8 8,
        8 -8,
        -8 -8,
        -8 6,
        -10 8,
        -10 -10,
        10 -10,
        10 10,
        -10 10,
        -8 8,
        "/>
<Contour name="blue$+" closed="true" border="0.000 0.000 1.000" fill="0.000 0.000 1.000" mode="9"
 points="0 7,
        -7 0,
        0 -7,
        7 0,
        "/>
<Contour name="magenta$+" closed="true" border="1.000 0.000 1.000" fill="1.000 0.000 1.000" mode="9"
 points="-6 2,
        -6 -2,
        -2 -6,
        2 -6,
        6 -2,
        6 2,
        2 6,
        -2 6,
        "/>
<Contour name="red$+" closed="true" border="1.000 0.000 0.000" fill="1.000 0.000 0.000" mode="9"
 points="6 -6,
        0 -6,
        0 -3,
        3 0,
        12 3,
        6 6,
        3 12,
        -3 6,
        -6 0,
        -6 -6,
        -12 -6,
        -3 -12,
        "/>
<Contour name="green$+" closed="true" border="0.000 1.000 0.000" fill="0.000 1.000 0.000" mode="9"
 points="-12 4,
        -12 -4,
        -4 -4,
        -4 -12,
        4 -12,
        4 -4,
        12 -4,
        12 4,
        4 4,
        4 12,
        -4 12,
        -4 4,
        "/>
<Contour name="cyan$+" closed="true" border="0.000 1.000 1.000" fill="0.000 1.000 1.000" mode="9"
 points="0 12,
        4 8,
        -12 -8,
        -8 -12,
        8 4,
        12 0,
        12 12,
        "/>
</Series>"""

    blankSeriesFile = blankSeriesFile.replace("[SECTION_NUM]", str(startSection))

    newSeriesFile = open(seriesName + ".ser", "w")
    newSeriesFile.write(blankSeriesFile)
    newSeriesFile.close()
    globalTrans.close()
    print("Completed!")

    print("\nSwitching focus to 0,0...")
    switchToCrop(seriesName, "0,0")
    print("Completed!")

    input("\nPress enter to exit.")
