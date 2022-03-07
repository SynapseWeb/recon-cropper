"""Functions for recon-cropper.py."""

import os
import numpy as np


def findBounds(fileName, obj):
    """Finds the bounds of a specified object on a single trace file."""
    
    # open trace file, read lines, and close
    sectionFile = open(fileName, 'r')
    lines = sectionFile.readlines()    
    sectionFile.close()

    # get the domain transformation
    domainIndex = 0
    line = lines[domainIndex]
    
    # check for domain in the text to find domain origin index
    while not '"domain1"' in line:
        domainIndex += 1
        line = lines[domainIndex]

    # grab xcoef transformation
    xcoef = [float(x) for x in lines[domainIndex-4].replace('"',"").split()[1:4]]

    # grab ycoef transformation
    ycoef = [float(y) for y in lines[domainIndex-3].replace('">',"").split()[1:4]]

    # convert to transformation matrix
    domain_trans = coefToMatrix(xcoef, ycoef)
    
    # create variables: min for points with and without inverse domain transformation
    xmin = 0
    xmin_idomain = 0
    xmax = 0
    xmax_idomain = 0
    ymin = 0
    ymin_idomain = 0
    ymax = 0
    ymax_idomain = 0
    
    # recording: set to True whenever the points in the file are being recorded
    recording = False
    
    for lineIndex in range(len(lines)):
        
        # grab line
        line = lines[lineIndex]
        
        # if data points are being recorded from the trace file...
        if recording:
            
            # the first point starts with "points=" in the text file; remove this part
            if firstLine:
                line = line.replace('points="', '')
                firstLine = False
            
            #remove commas
            line = line.replace(',', '')
            
            # split line into x and y coords
            coords = line.split()
            
            # check if there are still points there and add to sum (with matrix transformation)
            if len(coords) == 2:
                
                # set up points and transformation matrix
                coords_mat = np.array([[float(coords[0])],
                                       [float(coords[1])],
                                       [1]]) # matrix for the point
                trans_mat = coefToMatrix(xcoef, ycoef) # transformation 
                inv_domain_trans = np.linalg.inv(domain_trans) # inverse domain transformation

                trans_coords = np.matmul(trans_mat, coords_mat) # point fixed in reconstruct space (to return)
                trans_coords_idomain = np.matmul(inv_domain_trans, trans_coords) # point fixed to the image (to check)

                # if no points recorded yet, set min and maxes
                if xmin == 0 and xmax == 0 and ymin == 0 and ymax == 0:
                    xmin = trans_coords[0][0]
                    xmax = trans_coords[0][0]
                    ymin = trans_coords[1][0]
                    ymax = trans_coords[1][0]
                    xmin_idomain = trans_coords_idomain[0][0]
                    xmax_idomain = trans_coords_idomain[0][0]
                    ymin_idomain = trans_coords_idomain[1][0]
                    ymax_idomain = trans_coords_idomain[1][0]

                # otherwise, check for min and max values for both x and y
                # points fixed to the image are checked
                else:
                    if trans_coords_idomain[0][0] < xmin_idomain:
                        xmin = trans_coords[0][0]
                        xmin_idomain = trans_coords_idomain[0][0]
                    if trans_coords_idomain[0][0] > xmax_idomain:
                        xmax = trans_coords[0][0]
                        xmax_idomain = trans_coords_idomain[0][0]
                    if trans_coords_idomain[1][0] < ymin_idomain:
                        ymin = trans_coords[1][0]
                        ymin_idomain = trans_coords_idomain[1][0]
                    if trans_coords_idomain[1][0] > ymax_idomain:
                        ymax = trans_coords[1][0]
                        ymax_idomain = trans_coords_idomain[1][0]
            
            # stop recording otherwise
            else:
                recording = False
            
        # if not recording data points...
        else:
            
            # check for object name in the line
            if ('"' + obj + '"') in line:
                recording = True
                firstLine = True
                
                # backtrack through the trace file to find the xcoef and ycoef
                xcoefIndex = lineIndex
                while not ("xcoef" in lines[xcoefIndex]):
                    xcoefIndex -= 1
                
                # set the xcoef and ycoef
                xcoef = [float(x) for x in lines[xcoefIndex].split()[1:4]]
                ycoef = [float(y) for y in lines[xcoefIndex+1].split()[1:4]]
    
    # if the trace is not found in the section
    if xmin == 0 and xmax == 0 and ymin == 0 and ymax == 0:
        return None
    
    # return bounds (fixed to Reconstruct space)
    return xmin, xmax, ymin, ymax



def fillInBounds(bounds_dict):
    """Fills in bounds data where object doesn't exist with bounds data from previous sections."""
    
    # if the first section(s) do not have the object, then fill it in with first object instance
    firstInstanceFound = False
    prevBounds = None
    for bounds in bounds_dict:
        if bounds_dict[bounds] != None and not firstInstanceFound:
            prevBounds = bounds_dict[bounds]
            firstInstanceFound = True
    
    # set any bounds points that are None to the previous bounds
    for bounds in bounds_dict:
        if bounds_dict[bounds] == None:
            bounds_dict[bounds] = prevBounds
        prevBounds = bounds_dict[bounds]
    
    return bounds_dict



def getSectionInfo(fileName):
    """Gets the transformation, magnification, and image source from a single trace file."""
    
    # open trace file, read lines, and close
    traceFile = open(fileName, "r")
    lines = traceFile.readlines()
    traceFile.close()
    
    # set up iterator
    domainIndex = 0
    line = lines[domainIndex]
    
    # check for domain in the text to find domain origin index
    while not '"domain1"' in line:
        domainIndex += 1
        line = lines[domainIndex]

    # grab xcoef transformation
    xcoef = [float(x) for x in lines[domainIndex-4].replace('"',"").split()[1:4]]

    # grab ycoef transformation
    ycoef = [float(y) for y in lines[domainIndex-3].replace('">',"").split()[1:4]]

    # get magnification and image source
    mag = float(lines[domainIndex-2].split('"')[1])
    src = lines[domainIndex-1].split('"')[1]    

    return xcoef, ycoef, mag, src

    
def getSeriesInfo(fileName):
    """Return the series name and number of sections."""

    # get only the name
    seriesName = fileName.replace(".ser", "")
    
    # find out how many sections there are
    sectionNums = []
    
    # search each file in the folder that ends with a number
    for file in os.listdir():
        try:
            sectionNums.append(int(file[file.rfind(".")+1:]))
        except:
            pass

    # sort the section numbers so they are in order
    sectionNums.sort()

    return seriesName, sectionNums


def switchToUncropped(seriesName, objName):
    """Switch focus to the uncropped series from a cropped version."""

    # check for transformations that deviate from the global alignment
    iDtrans_dict = checkForRealignment(seriesName, objName)

    # open and read the transformation file
    localTrans = open(objName + "_LOCAL_TRANSFORMATIONS.txt", "r")
    lines = localTrans.readlines()
    localTrans.close()

    # create new transformation file
    newLocalTrans = open(objName + "_LOCAL_TRANSFORMATIONS.txt", "w")

    # store the new transformations and grab shifts for each section
    for line in lines:
        if "Section" in line:
            sectionNum = int(line.split()[1]) # get section number
        elif "xshift" in line:
            xshift_pix = int(line.split()[1]) # get shifted origin
        elif "yshift" in line:
            yshift_pix = int(line.split()[1]) # get shifted origin

        # transform all the traces so that they match the global transformations and save transformation data for the cropped version    
        elif "Dtrans" in line:
            transformAllTraces(seriesName + "." + str(sectionNum),
                               iDtrans_dict[sectionNum], # transform all the traces by this matrix
                               -xshift_pix, -yshift_pix, "") # additionally, move domain and change image source
            
            # store the transformation matrix going from uncropped to cropped
            Dtrans = np.linalg.inv(iDtrans_dict[sectionNum])
            line = "Dtrans: "
            line += str(Dtrans[0,0]) + " "
            line += str(Dtrans[0,1]) + " "
            line += str(Dtrans[0,2]) + " "
            line += str(Dtrans[1,0]) + " "
            line += str(Dtrans[1,1]) + " "
            line += str(Dtrans[1,2]) + "\n"
                
        newLocalTrans.write(line)

    newLocalTrans.close()
            

def switchToCrop(seriesName, objName):
    """Switch focus from an uncropped series to a cropped one."""

    # open transformation files
    localTrans = open(objName + "_LOCAL_TRANSFORMATIONS.txt", "r")
    lines = localTrans.readlines()
    localTrans.close()

    # get section numbers
    sectionNums = []
    for line in lines:
        if "Section" in line:
            sectionNums.append(int(line.split()[1]))
    
    # save current alignment on uncropped version
    saveGlobalTransformations(seriesName, sectionNums)

    # grab transformation data from each of the files
    for line in lines:
        if "Section" in line:
            sectionNum = int(line.split()[1]) # get the section number
        elif "xshift" in line:
            xshift_pix = int(line.split()[1]) # get shifted origin
        elif "yshift" in line:
            yshift_pix = int(line.split()[1]) # get shifted origin

        # transform all traces to saved aligment, shift origin, and change image source
        elif "Dtrans" in line:

            # create the new alignment matrix
            Dtrans = [float(z) for z in line.split()[1:7]]
            DtransMatrix = [[Dtrans[0],Dtrans[1],Dtrans[2]],
                                 [Dtrans[3],Dtrans[4],Dtrans[5]],
                                 [0,0,1]]

            # transform all the traces by the Dtrans matrix
            transformAllTraces(seriesName + "." + str(sectionNum),
                               DtransMatrix, # shift all traces by this matrix
                               xshift_pix, yshift_pix, objName) # shift the origins change image source


def checkForRealignment(seriesName, objName):
    """Check for differences in domain alignment between cropped and uncropped series."""

    # open the two transformation files
    globalTransFile = open("GLOBAL_TRANSFORMATIONS.txt", "r")
    localTransFile = open(objName + "_LOCAL_TRANSFORMATIONS.txt", "r")

    # store trasnformations
    iDtransList = {}

    # read through local and global transformations simultaneously
    for localLine in localTransFile.readlines():
        if "Section" in localLine:
            globalTransFile.readline() # skip line in global transformations file
            sectionNum = int(localLine.split()[1]) # get the section number
            
            # get new domain transformation info for this section
            sectionInfo = getSectionInfo(seriesName + "." + str(sectionNum))
            local_xcoef = sectionInfo[0]
            local_ycoef = sectionInfo[1]
        
        elif "xshift" in localLine:
            xshift = int(localLine.split()[1]) * sectionInfo[2] # get origin shift

            # get global domain transformation info for this section
            globalLine = globalTransFile.readline() 
            global_xcoef = [float(x) for x in globalLine.split()[1:4]]
            
        elif "yshift" in localLine:
            yshift = int(localLine.split()[1]) * sectionInfo[2] # get origin shift

            # get global domain transformation info for this section
            globalLine = globalTransFile.readline()
            global_ycoef = [float(y) for y in globalLine.split()[1:4]]

        # check for realignment using the two matrices
        elif "Dtrans" in localLine:
            
            # set up the two matrices
            local_matrix = coefToMatrix(local_xcoef, local_ycoef) # new transformation
            global_matrix = coefToMatrix(global_xcoef, global_ycoef) # global transformation

            # transform the shifted origin by ONLY the shear/stretch components of the new transformation
            transformedShiftCoords = np.matmul(local_matrix[:2,:2], [[xshift],[yshift]])

            # cancel out xshift and yshift from new transformation to match global
            local_matrix[0][2] -= transformedShiftCoords[0][0]
            local_matrix[1][2] -= transformedShiftCoords[1][0]
            
            # get the "difference" between the two matrices and store the result
            iD_matrix = np.matmul(global_matrix, np.linalg.inv(local_matrix))
            iDtransList[sectionNum] = iD_matrix
        
    globalTransFile.close()
    localTransFile.close()

    return iDtransList

def changeGlobalTransformations(seriesName, sectionNums, new_trans, startTrans):
    """Change the global transformation of a series based on a .dat file"""

    # get transformations for all sections
    sectionInfo = {}
    firstSection = True
    for sectionNum in sectionNums:
        sectionInfo[sectionNum] = getSectionInfo(seriesName + "." + str(sectionNum))
        if firstSection:
            micPerPix = sectionInfo[sectionNum][2]
            trans_offset = startTrans - sectionNum
            firstSection = False

    # go through each section and get the change transformation
    all_Dtrans = {}
    i = 0
    for sectionNum in sectionNums:
        if i - trans_offset < 0:
            Dtrans = np.array([[1,0,0],[0,1,0],[0,0,1]]) # no transformation if section is not changed
        else:
            Dtrans = np.matmul(new_trans[i - trans_offset],
                               np.linalg.inv(coefToMatrix(sectionInfo[sectionNum][0],
                                                          sectionInfo[sectionNum][1])))
        all_Dtrans[sectionNum] = Dtrans

        # transform all of the traces AND the domain by the change transformation
        transformAllTraces(seriesName + "." + str(sectionNum), Dtrans, 0, 0, "")
        
        i += 1

    # change the global transformations file
    globalTransFile = open("GLOBAL_TRANSFORMATIONS.txt", "w")
    i = 0
    for sectionNum in sectionNums:
        if i - trans_offset < 0:

            # if there is no transformation data for the section, keep the old transformation
            globalTransFile.write("Section " + str(sectionNum) + "\n" +
                                "xcoef: " + str(sectionInfo[sectionNum][0][0]) +
                                " " + str(sectionInfo[sectionNum][0][1]) +
                                " " + str(sectionInfo[sectionNum][0][2]) + " 0 0 0\n" +
                                "ycoef: " + str(sectionInfo[sectionNum][1][0]) +
                                " " + str(sectionInfo[sectionNum][1][1]) +
                                " " + str(sectionInfo[sectionNum][1][2]) + " 0 0 0\n")
        else:
            itransMatrix = np.linalg.inv(new_trans[i - trans_offset]) # get the inverse

            # write the new transformation data to the global transformations file
            globalTransFile.write("Section " + str(sectionNum) + "\n" +
                                "xcoef: " + str(itransMatrix[0][2]) + " " + str(itransMatrix[0][0]) +
                                " " + str(itransMatrix[0][1]) + " 0 0 0\n" +
                                "ycoef: " + str(itransMatrix[1][2]) + " " + str(itransMatrix[1][0]) +
                                " " + str(itransMatrix[1][1]) + " 0 0 0\n")
        i += 1
    
    globalTransFile.close()
        

def getNewTransformations(baseTransformations, micPerPix, is_from_SWIFT, img_height):
    """Returns all of the transformation matrices from a .dat file"""

    # store file information
    baseTransFile = open(baseTransformations, "r")
    lines = baseTransFile.readlines()
    baseTransFile.close()
    
    all_transformations = []

    # iterate through each line (or section)
    for line in lines:

        # get info from line
        splitLine = line.split()
        matrixLine = [float(num) for num in splitLine[1:7]]
        transMatrix = [[matrixLine[0],matrixLine[1],matrixLine[2]],
                       [matrixLine[3],matrixLine[4],matrixLine[5]],
                       [0,0,1]]
        
        if is_from_SWIFT:
            transMatrix = matrix2recon(transMatrix, img_height)

        # convert the translation components so that fit microns
        transMatrix[0][2] *= micPerPix
        transMatrix[1][2] *= micPerPix

        all_transformations.append(transMatrix)

    return all_transformations


### MICHAEL CHIRILLO'S FUNCTION ###
def matrix2recon(transform, dim):
    """Change frame of reference for SWiFT transforms to work in Reconstruct."""
    new_transform = transform.copy()

    # Calculate bottom left corner translation
    BL_corner = np.array([[0], [dim], [1]])  # BL corner from image height in px
    BL_translation = np.matmul(transform, BL_corner) - BL_corner

    # Add BL corner translation to SWiFT matrix
    new_transform[0][2] = round(BL_translation[0][0], 5)  # x translation
    new_transform[1][2] = round(BL_translation[1][0], 5)  # y translation

    # Flip y axis - change signs a2, b1, and b3
    new_transform[0][1] *= -1  # a2
    new_transform[1][0] *= -1  # b1
    new_transform[1][2] *= -1  # b3

    # Stop-gap measure for Reconchonky
    new_transform = np.linalg.inv(new_transform)

    return new_transform


def transformAllTraces(fileName, transformation, xshift_pix, yshift_pix, objName):
    """Multiply all of the traces on a section by a transformation matrix; also chang the image domain and source."""

    seriesName, sectionNum = fileName.split(".")

    # get section info
    sectionInfo = getSectionInfo(fileName)
    sectionNum = int(fileName[fileName.rfind(".")+1:])

    # check if transformation is needed
    transformation = np.array(transformation)
    noTrans = np.array([[1,0,0],[0,1,0],[0,0,1]])
    needsTransformation = not (np.round(transformation, decimals = 8) == noTrans).all()

    # make the domain transformation matrix
    existingDomainTrans = coefToMatrix(sectionInfo[0],sectionInfo[1]) # get existing domain transformation

    # transform the shifted origin by ONLY shear/stretch component of transformation
    transformedShiftCoords = np.matmul(existingDomainTrans[:2,:2],
                                       [[xshift_pix*sectionInfo[2]],[yshift_pix*sectionInfo[2]]])
    transformedShiftCoords = np.matmul(transformation[:2,:2], transformedShiftCoords)

    # add the transformed shifts to the matrix that will transform the domain
    domainTransformation = transformation.copy()
    domainTransformation[0][2] += transformedShiftCoords[0][0]
    domainTransformation[1][2] += transformedShiftCoords[1][0]
    
    # open and read the section file    
    sectionFile = open(fileName, "r")
    lines = sectionFile.readlines()
    sectionFile.close()

    # check for domain in the text to find domain origin index
    domainIndex = 0
    line = lines[domainIndex]
    while not '"domain1"' in line:
        domainIndex += 1
        line = lines[domainIndex]

    # create the new section file
    newSectionFile = open(fileName, "w")

    # read through the file
    for i in range(len(lines)):
        line = lines[i]

        # make sure the dimension is set to three
        if '<Transform dim="0"' in line:
            line = line.replace("0", "3")

        # if iterator is on the domain xcoef line
        elif i == domainIndex - 4:
            
            # gather the matrices and multiply them by the transformation matrix
            xcoef = [float(x) for x in line.split()[1:4]]
            ycoef = [float(y) for y in lines[i+1].split()[1:4]]
            newMatrix = np.linalg.inv(np.matmul(domainTransformation, coefToMatrix(xcoef, ycoef)))

            # set up strings for both xcoef and ycoef to write to file
            
            xcoef_line = ' xcoef=" '
            xcoef_line += str(newMatrix[0,2]) + " "
            xcoef_line += str(newMatrix[0,0]) + " "
            xcoef_line += str(newMatrix[0,1]) + " "
            xcoef_line += '0 0 0"\n'

            ycoef_line = ' ycoef=" '
            ycoef_line += str(newMatrix[1,2]) + " "
            ycoef_line += str(newMatrix[1,0]) + " "
            ycoef_line += str(newMatrix[1,1]) + " "
            ycoef_line += '0 0 0">\n'

            line = xcoef_line

        # if iterator is on domain ycoef line
        elif i == domainIndex - 3:

            # write line that was set in previous elif statement
            line = ycoef_line

        # if iterator is on the image source line
        elif i == domainIndex - 1:
            imageFile = line.split('"')[1] # get the current image source
            if "/" in imageFile and objName == "": # if image source is focused on a crop and switching to uncropped
                imageFile = imageFile[imageFile.find("/")+1:]
            elif not "/" in imageFile and objName != "": # if image source is set to uncropped and switching to a crop
                imageFile = seriesName + "_" + objName + "/" + imageFile
            # otherwise, don't mess with the image source
                
            line = ' src="' + imageFile + '" />\n'

        # if non-identity transformation and iterator is on xcoef that isn't domain
        elif needsTransformation and "xcoef" in line:
            
            # gather the matrices and multiply them by the transformation matrix
            xcoef = [float(x) for x in line.split()[1:4]]
            ycoef = [float(y) for y in lines[i+1].split()[1:4]]
            newMatrix = np.linalg.inv(np.matmul(transformation, coefToMatrix(xcoef, ycoef)))

            # set up strings for both xcoef and ycoef to write to file
            
            xcoef_line = ' xcoef=" '
            xcoef_line += str(newMatrix[0,2]) + " "
            xcoef_line += str(newMatrix[0,0]) + " "
            xcoef_line += str(newMatrix[0,1]) + " "
            xcoef_line += '0 0 0"\n'

            ycoef_line = ' ycoef=" '
            ycoef_line += str(newMatrix[1,2]) + " "
            ycoef_line += str(newMatrix[1,0]) + " "
            ycoef_line += str(newMatrix[1,1]) + " "
            ycoef_line += '0 0 0">\n'

            line = xcoef_line

        # if non-identity transformation and iterator is on ycoef that isn't domain
        elif needsTransformation and "ycoef" in line:

            # write line that was set up in previous elif statement
            line = ycoef_line

        newSectionFile.write(line)

    newSectionFile.close()


def getCropFocus(sectionFileName, seriesName):
    """Find the current crop focus based on the image source of the first section."""

    # open the section file
    with open(sectionFileName, "r") as sectionFile:
        lines = sectionFile.readlines()

    # find the image file
    lineIndex = 0
    while 'src="' not in lines[lineIndex]:
        lineIndex += 1
    imageFile = lines[lineIndex].split('"')[1]

    # analyze the image file name
    if "/" in imageFile:
        folder = imageFile.split("/")[0]
        cropFocus = folder[folder.find(seriesName)+len(seriesName)+1:]
    else:
        cropFocus = ""

    return cropFocus


def saveGlobalTransformations(seriesName, sectionNums):
    """Save the current set of trasnformations to the GLOBAL_TRANSFORMATIONS.txt file"""

    # open the global transformations file
    transformationsFile = open("GLOBAL_TRANSFORMATIONS.txt", "w")

    for sectionNum in sectionNums:

        # get existing transformations
        sectionInfo = getSectionInfo(seriesName + "." + str(sectionNum))

        # turn existing transformation into strings
        xcoef_str = ""
        for x in sectionInfo[0]:
            xcoef_str += str(x) + " "
        ycoef_str = ""
        for y in sectionInfo[1]:
            ycoef_str += str(y) + " "

        # write the new xcoef and ycoef to the file
        transformationsFile.write("Section " + str(sectionNum) + "\n"
                                  "xcoef: " + xcoef_str + "\n" +
                                  "ycoef: " + ycoef_str + "\n")
    transformationsFile.close()


def coefToMatrix(xcoef, ycoef):
    """Turn a set of x and y coef into a transformation matrix."""
    
    return np.linalg.inv(np.array([[xcoef[1], xcoef[2], xcoef[0]],
                       [ycoef[1], ycoef[2], ycoef[0]],
                       [0, 0, 1]]))


def intInput(inputStr):
    """Force user to give an integer input."""
    
    isInt = False
    while not isInt:
        try:
            num = int(input(inputStr))
            isInt = True
        except ValueError:
            print("Please enter a valid integer.")
    return num

def floatInput(inputStr):
    """Force user to give a float input."""
    
    isFloat = False
    while not isFloat:
        try:
            num = float(input(inputStr))
            isFloat = True
        except ValueError:
            print("Please enter a valid number.")
    return num

def ynInput(inputStr):
    """Force user to give y/n input."""
    
    response = input(inputStr)
    while response != "y" and response != "n":
        print("Please enter y or n.")
        response = input(inputStr)
    if response == "y":
        return True
    return False

def clearScreen():
  
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')
