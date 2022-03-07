
# Table of Contents

1.  [Opening the Program](#org0f9ad45)
2.  [Choosing Your Working Directory](#org10aca4a)
3.  [Operating on an Existing Series](#org8d70cf6)
4.  [Creating a New Local Crop around a Reconstruct Object](#orgaa65e7b)
5.  [Switching to an Existing Crop](#orgf93476a)
6.  [Backing Up Your Files](#org1161cac)
7.  [To be added](#org9f5ef2b)
    1.  [Minor changes](#orgbc936b1)
    2.  [More involved changes](#org663dd62)



<a id="org0f9ad45"></a>

# Opening the Program

-   Python 3+ needs to be downloaded on your computer to run this program.
-   If you are running the recon-cropper for the first time, it will automatically install the necessary modules. 
    -   The program will ask you if you want to manually locate the site-packages folder. If you say no, the program will automatically find it for you.


<a id="org10aca4a"></a>

# Choosing Your Working Directory

-   The program will ask you to select your “working directory,” which the folder that you will work in.
    -   If you have an existing series, this is the folder that contains the series file.
    -   If you are creating a new series, select or create an empty folder.


<a id="org8d70cf6"></a>

# Operating on an Existing Series

-   If you select a working directory with a series file, the program will open the main menu, giving you the following options:
    -   Option 1: Switch Reconstruct focus to the uncropped set of images.
    -   Option 2: Switch Reconstruct focus to a local crop (or create a new object crop).
    -   Option 3: If the series is chunked into a grid, you will be given the additional option of switching to a chunk.
-   You are also given the option to import transformations (labeled as option 0).


<a id="orgaa65e7b"></a>

# Creating a New Local Crop around a Reconstruct Object

-   Select option 2 on the main menu (switch to set of images cropped around an object).
-   Enter the name of the object you would like to crop around. The program will confirm that this trace exists in the series.
-   If the uncropped image files are not in the working directory (i.e., your series is chunked), you will be prompted to locate all of the original image files.
    -   Do NOT select cropped images to make a new crop, even if the object exists within the crop.
-   Enter the number of microns to crop around the object.
    -   The crop is made around the bounds of the object, not its center. For example, entering 0 for this prompt will create a crop whose edges just touch the trace.


<a id="orgf93476a"></a>

# Switching to an Existing Crop

-   If switching to a crop made around an object, select option 2 on the main menu (switch to set of images cropped around an object).
    -   Enter the name of the object you would like to focus on.
-   If switching to a coordinate chunk, select option 3 on the main menu.
    -   Enter the coordinates you would like to focus on (ex. “0,0”).


<a id="org1161cac"></a>

# Backing Up Your Files

-   Backing up is NOT done through the program.
-   To back up your files, copy every file that is NOT an image file.
    -   This includes:
        -   Trace files (.###)
        -   Series file (.ser)
        -   Global transformations file (.txt)
        -   Local transformations files (.txt)
    -   This does NOT include:
        -   Uncropped image files
        -   The folders containing cropped image files


<a id="org9f5ef2b"></a>

# To be added

-   [ ] Creating a chunked series from scratch (including calibration), importing transformations


<a id="orgbc936b1"></a>

## Minor changes

-   [ ] On exit program, warn user if series is still focused on a crop, giving them the option to switch to uncropped series before exiting.

-   [ ] Give warning when switching crops for user to check if Reconstruct is actually closed.

-   [ ] Add option to open new series / working directory without having to exit and reopen program.

-   [ ] Show current series in menu at all times.

-   [ ] Change domain function to not search for "domain". (Sometimes domains aren't named "domain".)

-   [ ] Save most previously access series location and give option to set working dir to that


<a id="org663dd62"></a>

## More involved changes

-   [ ] Tool to extract trace data from all crops easily.

-   [ ] Tool to quickly backup traces from all crops and revert to previous backups.

-   [ ] Incorporate retro-reconstruct tools for dim 6 handling.

