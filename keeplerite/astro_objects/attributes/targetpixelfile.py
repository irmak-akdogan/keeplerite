import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

class TPF(): 

    """
    A wrapper class for handling and visualizing 
    Target Pixel Files (TPFs) from the Kepler mission.

    This class stores a single TPF and provides methods for 
    setting the aperture for lightcurve extraction and plotting the pixel data with optional 
    aperture overlays. It also stores the object's name and the quarter 
    for use in labeling.

    Parameters
    ----------
    data : lightkurve.TargetPixelFile 
        The downloaded TPF data for a given object and quarter.
    name : str
        The name of the astronomical object. Used for titling the plot.
    quarter : int
        The Kepler observing quarter. Also used for titling.

    Attributes
    ----------
    data : lightkurve.TargetPixelFile
        The raw TPF data object.
    aperture : str or ndarray
        The aperture mask to be used for photometry; can be a string ("pipeline", etc.)
        or a custom boolean mask.
    name : str
        The name of the astronomical object.
    quarter : int
        The observing quarter.

    Methods
    -------
    set_aperture(aperture_type="pipeline", threshold=1)
        Sets the aperture mask to be used. Can be "pipeline", "threshold", "all", or "custom" 
        (using a threshold mask).
    
    plot_tpf(show_aperture=False)
        Plots the TPF data. Optionally overlays the selected aperture mask. 
        Returns the matplotlib figure and axes.
    """


    def __init__(self, data, name, quarter):
        self.data = data
        self.aperture = "pipeline"
        self. name = name 
        self.quarter = quarter 

    def set_aperture(self, aperture_type = "pipeline", threshold = 1 ):

        if aperture_type == "custom":
            self.aperture = self.data.create_threshold_mask(threshold=threshold)
        else: 
            self.aperture = aperture_type

    def plot_tpf(self, show_aperture = False): 

        if show_aperture: 
            ax = self.data.plot(aperture_mask = self.aperture)  
        else: 
            ax = self.data.plot()

        fig = ax.figure
        ax.set_title(f"Target Pixel File of {self.name}, Quarter {self.quarter}")
        
        return fig, ax  