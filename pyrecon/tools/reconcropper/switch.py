from pyrecon.classes import Transform

def findRealignment(series, local_name, tform_data):
    """Check for and return differences in domain alignment between current local series and global series.
    """
    # store Delta transformations (Dtforms)
    Dtforms = {}
    for section in series.sections:
        # get current current local transform, xshift, and yshift
        current_tform = section.images[0].transform
        xshift_pix = tform_data["LOCAL_" + local_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + local_name][section.name]["yshift_pix"]
        # undo the translate on the current local tform
        mag = series.images[0].mag
        translated_tform = current_tform.translate(-xshift_pix * mag, -yshift_pix * mag)
        # get global transform
        global_xcoef = tform_data["GLOBAL"][section.name]["xcoef"]
        global_ycoef = tform_data["GLOBAL"][section.name]["ycoef"]
        global_tform = Transform(xcoef=global_xcoef, ycoef=global_ycoef)
        # get the Dtform (current_tform - global_tform)
        Dtform = translated_tform.compose(global_tform.invert())
        # store in dictionary
        Dtforms[section.name] = Dtform
    return Dtforms

def saveAsGlobal(series, tform_data):
    for section in series.sections:
        tform_data["GLOBAL"][section.name]["xcoef"] = section.images[0].transform.xcoef
        tform_data["GLOBAL"][section.name]["ycoef"] = section.images[0].transform.ycoef
        tform_data["GLOBAL"][section.name]["src"] = section.images[0].src

def switchToGlobal(series, obj_name, tform_data):
    """Switch focus to the uncropped series from a cropped version.
    """
    # check for transformations that deviate from the global alignment
    Dtforms = findRealignment(series, obj_name, tform_data)
    for section in series.sections:
        Dtform = Dtforms[section.name]
        xshift_pix = tform_data["LOCAL_" + obj_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + obj_name][section.name]["yshift_pix"]
        mag = section.images[0].mag
        # store the new Delta transformation in tform_data
        tform_data["LOCAL_" + obj_name][section.name]["xcoef"] = Dtform.xcoef
        tform_data["LOCAL_" + obj_name][section.name]["ycoef"] = Dtform.ycoef
        # change the transformations
        section.transformAllContours(Dtform.inverse())
        section.transformAllImages(Dtform.inverse(), -xshift_pix*mag, -yshift_pix*mag)
        # change the image source
        section.images[0].src = tform_data["GLOBAL"][section.name]["src"]
        tform_data["FOCUS"] = "GLOBAL"

def switchToCrop(series, obj_name, tform_data):
    """Switch focus from an uncropped series to a cropped one.
    """    
    # save current alignment as global
    saveAsGlobal(series, tform_data)
    for section in series.sections:
        Dtform_xcoef = tform_data["LOCAL_" + obj_name][section.name]["xcoef"]
        Dtform_ycoef = tform_data["LOCAL_" + obj_name][section.name]["ycoef"]
        Dtform = Transform(xcoef=Dtform_xcoef, ycoef=Dtform_ycoef)
        xshift_pix = tform_data["LOCAL_" + obj_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + obj_name][section.name]["yshift_pix"]
        mag = section.images[0].mag
        # transform all contours by Dtform
        section.transformAllContours(Dtform)
        # transform and translate all image transforms
        section.transformAllImages(Dtform, xshift_pix*mag, yshift_pix*mag)
        # change the image source
        section.images[0].src = tform_data["LOCAL_" + obj_name][section.name]["src"]  
        tform_data["FOCUS"] = "LOCAL_" + obj_name
