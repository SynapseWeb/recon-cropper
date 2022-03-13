from pyrecon.classes import Transform

def findRealignment(series, local_name, tform_data):
    """Check for and return differences in domain alignment between current local series and global series.
    """
    # store Delta transformations (Dtforms)
    Dtforms = {}
    for section_num in series.sections:
        section = series.sections[section_num]
        # get current current local transform, xshift, and yshift
        xshift_pix = tform_data["LOCAL_" + local_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + local_name][section.name]["yshift_pix"]
        mag = section.images[0].mag
        shift_point = section.images[0].transform.noTranslation().transformPoints([(xshift_pix * mag, yshift_pix * mag)])
        xshift = shift_point[0][0]
        yshift = shift_point[0][1]
        # undo the translate on the current local image tform
        section.transformAllImages(tform=None, xshift= -xshift, yshift= -yshift)
        # get global transform
        global_xcoef = tform_data["GLOBAL"][section.name]["xcoef"]
        global_ycoef = tform_data["GLOBAL"][section.name]["ycoef"]
        global_tform = Transform(xcoef=global_xcoef, ycoef=global_ycoef)
        # get the Dtform (current_tform - global_tform)
        Dtform = global_tform.invert().compose(section.images[0].transform)
        # store in dictionary
        Dtforms[section.name] = Dtform
        # redo the translate on the current local image tform
        section.transformAllImages(tform=None, xshift=xshift, yshift=yshift)
    return Dtforms

def saveAsGlobal(series, tform_data):
    for section_num in series.sections:
        section = series.sections[section_num]
        tform_data["GLOBAL"][section.name]["xcoef"] = section.images[0].transform.xcoef
        tform_data["GLOBAL"][section.name]["ycoef"] = section.images[0].transform.ycoef
        tform_data["GLOBAL"][section.name]["src"] = section.images[0].src

def switchToGlobal(series, obj_name, tform_data):
    """Switch focus to the uncropped series from a cropped version.
    """
    # check for transformations that deviate from the global alignment
    Dtforms = findRealignment(series, obj_name, tform_data)
    for section_num in series.sections:
        section = series.sections[section_num]
        Dtform = Dtforms[section.name]
        # get the translation coordinates
        xshift_pix = tform_data["LOCAL_" + obj_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + obj_name][section.name]["yshift_pix"]
        mag = section.images[0].mag
        shift_point = section.images[0].transform.noTranslation().transformPoints([(xshift_pix * mag, yshift_pix * mag)])
        xshift = shift_point[0][0]
        yshift = shift_point[0][1]        
        # store the new Delta transformation in tform_data
        tform_data["LOCAL_" + obj_name][section.name]["xcoef"] = Dtform.xcoef
        tform_data["LOCAL_" + obj_name][section.name]["ycoef"] = Dtform.ycoef
        # change the transformations
        section.transformAllContours(Dtform.invert())
        section.transformAllImages(Dtform.invert(), -xshift, -yshift)
        # change the image source
        section.images[0].src = tform_data["GLOBAL"][section.name]["src"]
        tform_data["FOCUS"] = "GLOBAL"

def switchToCrop(series, obj_name, tform_data):
    """Switch focus from an uncropped series to a cropped one.
    """    
    # save current alignment as global
    saveAsGlobal(series, tform_data)
    for section_num in series.sections:
        section = series.sections[section_num]
        Dtform_xcoef = tform_data["LOCAL_" + obj_name][section.name]["xcoef"]
        Dtform_ycoef = tform_data["LOCAL_" + obj_name][section.name]["ycoef"]
        Dtform = Transform(xcoef=Dtform_xcoef, ycoef=Dtform_ycoef)
        # get the translation coordinates
        xshift_pix = tform_data["LOCAL_" + obj_name][section.name]["xshift_pix"]
        yshift_pix = tform_data["LOCAL_" + obj_name][section.name]["yshift_pix"]
        mag = section.images[0].mag
        global_tform = section.images[0].transform
        shift_point = global_tform.noTranslation().transformPoints([(xshift_pix * mag, yshift_pix * mag)])
        xshift = shift_point[0][0]
        yshift = shift_point[0][1] 
        # transform all contours by Dtform
        section.transformAllContours(Dtform)
        # transform and translate all image transforms
        section.transformAllImages(Dtform, xshift, yshift)
        # change the image source
        section.images[0].src = tform_data["LOCAL_" + obj_name][section.name]["src"]  
        tform_data["FOCUS"] = "LOCAL_" + obj_name
