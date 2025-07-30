from tkinter import filedialog
import pandas as pd
from opynfield.readin.track import Track
from xml.dom import minidom as md


def read_buridian(
    groups_with_file_type: list[str],
    verbose: bool,
    arena_radius_cm: float,
    running_window_length: int,
    window_step_size: int,
    sample_freq: int,
    time_bin_size: int,
    all_tracks: list[Track],
) -> list[Track]:
    """This function reads in all the tracks from the Buridian tracker format. The function extracts the x, y, and t
    information and smooths, centers, and converts the units of the track.

    :param groups_with_file_type: which groups have tracks recorded in this type
    :type groups_with_file_type: list[str]
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :param arena_radius_cm: the radius of the arena in which the track was recorded, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type arena_radius_cm: float
    :param running_window_length: a smoothing function parameter set to match ethovision, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type running_window_length: int
    :param window_step_size: a smoothing function parameter set to match ethovision, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type window_step_size: int
    :param sample_freq: the frame rate that the track was recorded with, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type sample_freq: int
    :param time_bin_size: how many seconds should be aggregated together, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type time_bin_size: int
    :param all_tracks: a list with all the Track objects from previously read-in datatypes
    :type all_tracks: list[Track]
    :return: a Track object with a consistent format for x y and t tracking points
    :rtype: list[Track]
    """
    for buridian_group in groups_with_file_type:
        if verbose:
            print(f"Running Buridian Tracker Files For Group: {buridian_group}")
        title1 = f"Select .dat files in folder for {buridian_group}"
        title2 = f"Select .xml files in folder for {buridian_group}"
        # select .dat and .xml buri files for the groups
        data_files = filedialog.askopenfilenames(
            filetypes=[("Dat files", "*.dat")], title=title1
        )
        meta_files = filedialog.askopenfilenames(
            filetypes=[("xml files", "*.xml")], title=title2
        )
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{buridian_group}, File {file_num + 1} Out Of {len(data_files)}")
            # read in each file's data
            file_data = pd.read_csv(data_files[file_num], sep="\t", lineterminator="\n")
            file_data = file_data.iloc[0:-2]
            file_meta = meta_files[file_num]  # match the data and metadata
            xypx = get_meta_info(
                file_meta, arena_radius_cm
            )  # extract the metadata information
            track = Track(
                buridian_group,
                file_data["x"].values,
                file_data["y"].values,
                file_data["time"].values,
                "Buridian Tracker",
                [xypx[0], xypx[1], xypx[2]],
                False,
            )  # create the track object
            # put track coordinates through standardization procedures
            track.buri_convert_units(arena_radius_cm, xypx[2], verbose)
            track.buri_convert_to_center(xypx[0], xypx[1], verbose)
            track.buri_running_line(running_window_length, window_step_size, verbose)
            track.buri_subsample(sample_freq, time_bin_size, verbose)
            track.buri_fill_missing(verbose)
            track.standardized = True
            all_tracks.append(track)
    return all_tracks


def get_meta_info(file: str, arena_radius_cm: float) -> pd.Series:
    """This function extracts center point information from the arena in which the animal was recorded

    :param file: the path to the metadata file for this track
    :type file: str
    :param arena_radius_cm: the radius of the arena in which the track was recorded, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type arena_radius_cm: float
    :return: the x and y coordinates of the center point in cm and the radius of the arena in pixels
    :rtype: pd.Series
    """
    doc = md.parse(file)  # creates the document object from the metadata file

    # pulls the arena radius from the metadata
    rad_pix = doc.getElementsByTagName("ARENA_RADIUS")  # gets the element list
    rad_pix = rad_pix.item(0)  # gets the element
    nodes = rad_pix.childNodes  # gets the list of element nodes
    node = nodes[0]  # gets the node
    arena_radius_px = int(
        node.data
    )  # node.data is a string of the arena radius in pixels

    # pulls the x coordinate of the arena center point
    x_cen = doc.getElementsByTagName("ARENA_CENTER_X")  # gets the element list
    x_cen = x_cen.item(0)  # gets the element
    nodes = x_cen.childNodes  # gets the list of element nodes
    node = nodes[0]  # gets the node
    x_coord = int(
        node.data
    )  # node.data is a string of the pixel position of the center point x coordinate
    x_coord = x_coord * (
        arena_radius_cm / arena_radius_px
    )  # convert the point units from pixels to cm

    # pulls the y coordinate of the arena center point
    y_cen = doc.getElementsByTagName("ARENA_CENTER_Y")  # gets the element list
    y_cen = y_cen.item(0)  # gets the element
    nodes = y_cen.childNodes  # gets the list of element nodes
    node = nodes[0]  # gets the node
    y_coord = int(
        node.data
    )  # node.data is a string of the pixel position of the center point y coordinate
    y_coord = y_coord * (
        arena_radius_cm / arena_radius_px
    )  # convert the point units from pixels to cm

    # format the needed metadata into a list
    xy = pd.Series([x_coord, y_coord, arena_radius_px])
    return xy
