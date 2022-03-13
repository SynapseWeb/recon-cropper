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
    for section in series.sections:
        tform_data["GLOBAL"][section.name] = {}
        tform_data["GLOBAL"][section.name]["xcoef"] = section.images[0].transform.xcoef
        tform_data["GLOBAL"][section.name]["ycoef"] = section.images[0].transform.ycoef
        tform_data["GLOBAL"][section.name]["src"] = section.images[0].src
    new_file = open("tform_data.json", "w")
    json.dump(tform_data, new_file)
    new_file.close()
    return tform_data


def readAll(series_path):
    """ Import series and tform data.
    """
    series = rr.process_series_directory(series_path)
    working_dir = series_path[:series_path.rfind("/")]
    os.chdir(working_dir)
    if not os.path.isfile("tform_data.json"):
        tform_data = newJSON(series)
    else:
        data_file = open("tform_data.json", "r")
        tform_data = json.load(data_file)
        data_file.close()
    return series, tform_data

def writeAll(series, tform_data):
    """ Export series and tform data to saved files.
    """
    directory = os.getcwd()
    rw.write_series(series, directory)
    new_file = open("tform_data.json", "w")
    json.dump(tform_data, new_file)
    new_file.close()