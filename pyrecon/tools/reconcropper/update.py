import os
import json
from pyrecon.tools import reconstruct_writer as rw
from pyrecon.tools import reconstruct_reader as rr

def newJSON(series):
    """ Create a new JSON file for an existing uncropped series.
    """
    tform_data = {}
    tform_data["GLOBAL"] = {}
    tform_data["FOCUS"] = "GLOBAL"
    print(series.sections)
    for section_num in series.sections:
        section = series.sections[section_num]
        tform_data["GLOBAL"][section.name] = {}
        tform_data["GLOBAL"][section.name]["xcoef"] = section.images[0].transform.xcoef
        tform_data["GLOBAL"][section.name]["ycoef"] = section.images[0].transform.ycoef
        tform_data["GLOBAL"][section.name]["src"] = section.images[0].src
    new_file = open("data.json", "w")
    json.dump(tform_data, new_file)
    new_file.close()
    return tform_data


def readAll(series_dir):
    """ Import series and tform data.
    """
    series = rr.process_series_directory(series_dir)
    os.chdir(series_dir)
    if not os.path.isfile("data.json"):
        tform_data = newJSON(series)
    else:
        data_file = open("data.json", "r")
        tform_data = json.load(data_file)
        data_file.close()
    return series, tform_data

def writeAll(series, tform_data):
    """ Export series and tform data to saved files.
    """
    directory = os.getcwd()
    rw.write_series(series, directory, sections=True, overwrite=True)
    new_file = open("data.json", "w")
    json.dump(tform_data, new_file)
    new_file.close()