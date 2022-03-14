import os
import json
from PIL import Image as PILImage
from pyrecon.tools.reconcropper.explore_files import findFiles
from pyrecon.tools.reconcropper.get_input import intInput, floatInput, ynInput
from pyrecon.tools.reconcropper.text_files import getBlankSection, getBlankSeries

def newChunkCrop():
    """Create a chunked series WITHOUT existing series or section files.
    """
    # force user to give a series name
    series_name = ""
    while series_name == "":
        series_name = input("\nPlease enter the desired name for your new series: ")
        if series_name == "" or "/" in series_name:
            print("Please enter a valid series name.")

    # open file explorer for user to select images
    input("\nPress enter to select the images you would like to crop.")
    image_files = findFiles("Image Files", "tif")
    image_files = sorted(image_files)

    # get grid information
    xchunks = intInput("\nHow many horizontal chunks would you like to have?: ")
    ychunks = intInput("How many vertical chunks would you like to have?: ")
    overlap = floatInput("How many microns of overlap should there be between chunks?: ")

    # get series information
    start_section = intInput("\nWhat section number would you like your new series to start on?\n" +
                            "(when calibration grid is included, 0 is the standard): ")
    section_thickness = floatInput("\nWhat would you like to set as the section thickness? (in microns): ")

    # check if series has already been calibrated
    is_calibrated = ynInput("\nHas this series already been calibrated? (y/n): ")

    if is_calibrated:
        mic_per_pix = floatInput("How many microns per pixel are there for this series?: ")
    else:
        mic_per_pix = 0.00254
        print("\nMicrons per pixel has been set to default value of 0.00254.")
        print("\nREAD THE FOLLOWING INSTRUCTIONS:")
        print("If you wish to apply a set of existing transformations to this series, please calibrate it first.")
        print("When calibrating, traces can be made in any quadrant, but you MUST perform the actual calibration")
        print("after switching back to the uncropped series. You do not need the uncropped images to calibrate.")
        print("Then you will be able to apply transformations using this program after calibrating the series in Reconstruct.")
        input("\nPress enter to continue crop the images.")

    # create each folder
    print("\nCreating folders...")
    os.mkdir("Cropped Images")
    for x in range(xchunks):
        for y in range(ychunks):
            os.mkdir("Cropped Images/" + str(x) + "," + str(y))

    # store new domain origins
    newDomainOrigins = []

    # create new tform_data file
    tform_data = {}
    tform_data["GLOBAL"] = {}

    # store max image length and height
    img_lengths = {}
    img_heights = {}

    # start iterating through each of the images
    for i in range(len(image_files)):

        file_path = image_files[i]
        file_name = file_path[file_path.rfind("/")+1:]

        print("\nWorking on " + file_name + "...")

        # add data to GLOBAL tform_data and set focus to GLOBAL
        section_name = series_name + "." + str(i + start_section)
        tform_data["GLOBAL"][section_name] = {}
        tform_data["GLOBAL"][section_name]["src"] = file_name
        tform_data["GLOBAL"][section_name]["xcoef"] = [0,1,0,0,0,0]
        tform_data["GLOBAL"][section_name]["ycoef"] = [0,0,1,0,0,0]
        tform_data["FOCUS"] = "GLOBAL"

        # open image and get dimensions
        img = PILImage.open(file_path)
        img_length, img_height = img.size
        img_lengths[section_name] = img_length
        img_heights[section_name] = img_height
        
        # iterate through each chunk and calculate the coords for each of the corners
        for x in range(xchunks):
            newDomainOrigins.append([])
            for y in range(ychunks):
                
                left = int((img_length-1) * x / xchunks - overlap/2 / mic_per_pix)
                if left < 0:
                    left = 0
                right = int((img_length-1) * (x+1) / xchunks + overlap/2 / mic_per_pix)
                if right >= img_length:
                    right = img_length - 1
                
                top = int((img_height-1) * (ychunks - y-1) / ychunks - overlap/2 / mic_per_pix)
                if top < 0:
                        top = 0 
                bottom = int((img_height-1) * (ychunks - y) / ychunks + overlap/2 / mic_per_pix)
                if bottom >= img_height:
                    bottom = img_height - 1

                # crop the photo
                cropped = img.crop((left, top, right, bottom))
                
                newDomainOrigins[x].append((left, int(img_height-1 - bottom)))
                xshift_pix = left
                yshift_pix = int(img_height-1 - bottom)

                # save as uncompressed TIF
                image_path = "Cropped Images/" + str(x) + "," + str(y) + "/" + file_name
                cropped.save(image_path)

                # store data in tform_data file
                if i == 0:
                    tform_data["LOCAL_" + str(x) + "," + str(y)] = {}
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name] = {}
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name]["xshift_pix"] = xshift_pix
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name]["yshift_pix"] = yshift_pix
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name]["xcoef"] = [0,1,0,0,0,0]
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name]["ycoef"] = [0,0,1,0,0,0]
                tform_data["LOCAL_" + str(x) + "," + str(y)][section_name]["src"] = image_path

        print("Completed!")

    print("\nCreating new section and series files...")

    # store tform_data in JSON file
    new_data = open("data.json", "w")
    json.dump(tform_data, new_data)
    new_data.close()

    # replace the unknowns in the section file with known info
    blank_section_txt = getBlankSection()
    blank_section_txt = blank_section_txt.replace("[SECTION_THICKNESS]", str(section_thickness))
    blank_section_txt = blank_section_txt.replace("[TRANSFORM_DIM]", "3")
    blank_section_txt = blank_section_txt.replace("[IMAGE_MAG]", str(mic_per_pix))

    # iterate through each section and create the section file
    for i in range(len(image_files)):

        file_path = image_files[i]
        file_name = file_path[file_path.rfind("/")+1:]

        section_name = series_name + "." + str(i + start_section)        
        newSectionFile = open(section_name, "w")

        # retrieve global transformations
        xcoef_list = tform_data["GLOBAL"][section_name]["xcoef"]
        ycoef_list = tform_data["GLOBAL"][section_name]["ycoef"]
        xcoef_str = str(xcoef_list).replace("[","").replace("]","").replace(",","")
        ycoef_str = str(ycoef_list).replace("[","").replace("]","").replace(",","")
    
        # replace section-specific unknowns with known info
        section_file_text = blank_section_txt.replace("[SECTION_INDEX]", str(i + start_section))
        section_file_text = section_file_text.replace("[IMAGE_SOURCE]", file_name)
        section_file_text = section_file_text.replace("[XCOEF]", xcoef_str)
        section_file_text = section_file_text.replace("[YCOEF]", ycoef_str)
        section_file_text = section_file_text.replace("[IMAGE_LENGTH]", str(int(img_lengths[section_name])))
        section_file_text = section_file_text.replace("[IMAGE_HEIGHT]", str(int(img_heights[section_name])))

        newSectionFile.write(section_file_text)
        newSectionFile.close()

    # create the series file
    blank_series_txt = getBlankSeries()
    blank_series_txt = blank_series_txt.replace("[SECTION_NUM]", str(start_section))

    new_series_file = open(series_name + ".ser", "w")
    new_series_file.write(blank_series_txt)
    new_series_file.close()
    print("Completed!")

    print("\nThe chunked series has been successfully created!")