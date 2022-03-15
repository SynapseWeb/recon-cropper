

# Opening the Program

-   Python 3+ needs to be downloaded on your computer to run this program.
-   If you are running the recon-cropper for the first time, it will automatically install the necessary modules. 
    -   The program will ask you if you want to manually locate the site-packages folder. If you say no, the program will automatically find it for you.


# Choosing Your Working Directory

-   The program will ask you to select your “working directory,” which the folder that you will work in.
    -   If you have an existing series, this is the folder that contains the series file.
    -   If you are creating a new series, select or create an empty folder.


# Operating on an Existing Series

-   If you select a working directory with a series file, the program will open the main menu, giving you the following options:
    -   Option 1: Switch Reconstruct focus to the uncropped set of images.
    -   Option 2: Switch Reconstruct focus to a local crop (or create a new object crop).
    -   Option 3: If the series is chunked into a grid, you will be given the additional option of switching to a chunk.
-   You are also given the option to import transformations (labeled as option 0).


# Creating a New Local Crop around a Reconstruct Object

-   Select option 2 on the main menu (switch to set of images cropped around an object).
-   Enter the name of the object you would like to crop around. The program will confirm that this trace exists in the series.
-   If the uncropped image files are not in the working directory (i.e., your series is chunked), you will be prompted to locate all of the original image files.
    -   Do NOT select cropped images to make a new crop, even if the object exists within the crop.
-   Enter the number of microns to crop around the object.
    -   The crop is made around the bounds of the object, not its center. For example, entering 0 for this prompt will create a crop whose edges just touch the trace.


# Switching to an Existing Crop

-   If switching to a crop made around an object, select option 2 on the main menu (switch to set of images cropped around an object).
    -   Enter the name of the object you would like to focus on.
-   If switching to a coordinate chunk, select option 3 on the main menu.
    -   Enter the coordinates you would like to focus on (ex. “0,0”).


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


## To be added to tutorial

-   [ ] Creating a chunked series from scratch (including calibration), importing transformations

-   [ ] Make directory structure cleaner. (Currently a lot of folders are included with traces.)


## Minor changes

-   [ ] On exit program, warn user if series is still focused on a crop, giving them the option to switch to uncropped series before exiting.

-   [ ] Give warning when switching crops for user to check if Reconstruct is actually closed.

-   [ ] Add option to open new series / working directory without having to exit and reopen program.

-   [ ] Show current series in menu at all times.

-   [ ] Change domain function to not search for "domain". (Sometimes domains aren't named "domain".)

-   [ ] Save most previously access series location and give option to set working dir to that

-   [ ] Visual crops in menu? (Who knows how many crops exist in the series&#x2026;)


## More involved changes

-   [ ] Tool to extract trace data from all crops easily.

-   [ ] Tool to quickly backup traces from all crops and revert to previous backups.

-   [ ] Incorporate retro-reconstruct tools for dim 6 handling.

# Updating Transformation Text Files

-   LOCAL_TRANSFORMATION.txt files are now stored in the main working directory.
    -   Go into each of the folders containing a crop and rename the file to (crop name)_LOCAL_TRANSFORMATIONS.txt
        - Ex. 0,0_LOCAL_TRANSFORMATIONS.txt or d004_LOCAL_TRANSFORMATIONS.txt
    -   Move the text file outside the crop folder and into the main working directory
