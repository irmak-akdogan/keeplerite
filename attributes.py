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
    
class LC():

    """
    A class for managing and visualizing lightcurves obtained from Kepler Target Pixel Files.

    This class normalizes and filters the lightcurve data,
    calculates false alarm probability (FAP) estimates by applying 
    the given uncertainties to a hypothetical constant flux,
    and plots the lightcurve.

    Parameters
    ----------
    data : lightkurve.LightCurve
        The lightcurve data for a given astronomical object.
    name : str
        The name of the astronomical object.

    Attributes
    ----------
    data : lightkurve.LightCurve
        The lightcurve data
    name : str
        The name of the object the lightcurve belongs to.

    Methods
    -------
    filter_lcs(percentage)
        Removes data points whose flux falls outside a specified percentage range 
        around the normalized median flux (e.g., 30% removes points < 0.7 or > 1.3 
        of the median in a normalized lightcurve).

    get_err(num)
        Performs constant flux simulations by generating lightcurves with normally 
        distributed noise and computing a median power spectrum to be used as a 
        False Alarm Probability (FAP) estimate. `num` specifies the number of simulations.

    plot_lc()
        Plots the current lightcurve and returns the matplotlib figure and axes.
        The plot is titled using the object's name.
    """


    def __init__(self, data, name ):
        self.data = data 
        self.name = name 

    def filter_lcs(self, percentage): 
        flux = self.data.flux / np.nanmedian(self.data.flux)
    
        lower = 1 - (percentage / 100)
        upper = 1 + (percentage / 100)

        mask = (flux >= lower) & (flux <= upper)

        self.data = self.data[mask]

    def get_err(self, num): 

        valid = np.isfinite(self.data.flux_err) & (self.data.flux_err > 0)

        f = self.data[valid].flux
        t = self.data[valid].time.to_value('jd')
        e = self.data[valid].flux_err

        median = np.median(f)
        meanflux_per = []
        to_be_stacked = [] 
        
        for ii in range(num):
            rand_flux = np.random.normal(median, e)
            rand_lk = lk.LightCurve(time = t, flux = rand_flux )
            rand_per = rand_lk.to_periodogram(normalization='psd')
            meanflux_per.append(rand_per)

            powers = rand_per.power.to_value()
            to_be_stacked.append(powers)
            
        medians = np.median( np.array(to_be_stacked) , axis = 0)
            
        return medians
    
    def plot_lc(self):

        ax = self.data.plot()
        fig = ax.figure
        ax.set_title(f"Lightcurve of {self.name}")

        return fig, ax 


class PD(): 

    """
    A class for analyzing and plotting periodograms of the lightcurves.

    This class stores the periodogram data, an estimate of the false alarm probability (FAP),
    and provides a plotting function with options for smoothing and signal-to-noise visualization.

    Parameters
    ----------
    data : lightkurve.periodogram.Periodogram
        The raw periodogram data derived from a lightcurve.
    fap : np.ndarray
        An array representing the False Alarm Probability (FAP) across frequencies,
        typically estimated via noise simulations.
    name : str
        The name of the astronomical object.
    minf : float, optional
        Minimum frequency for the x-axis range in the plot (default is 1).
    maxf : float, optional
        Maximum frequency for the x-axis range in the plot (default is 150).

    Attributes
    ----------
    data : lightkurve.periodogram.Periodogram
        The original periodogram data.
    fap : np.ndarray
        Estimated FAP values across the frequency domain.
    minf : float
        Minimum frequency to be plotted.
    maxf : float
        Maximum frequency to be plotted.
    name : str
        The name of the object the periodogram belongs to.

    Methods
    -------
    plot_pd(smooth=10, scale="log", sn=False)
        Plots the periodogram with optional smoothing and scale.
        If `sn` is True, the plot will show the signal-to-noise ratio (S/N) instead of power.
        The smoothed and raw periodogram are plotted together, and the plot is labeled with
        the object's name and frequency range.
    """


    def __init__(self, data, fap, name, minf = 1 , maxf = 150  ):

        self.data = data 
        self.fap  = fap
        self.minf = minf
        self.maxf = maxf
        self.name = name 

    def plot_pd(self, smooth = 10, scale = "log", sn = False):
        
        fig, ax = plt.subplots()

        smoothed = self.data.smooth(method='boxkernel', filter_width = smooth)

        if sn: 
            fap_value = np.median(self.fap)
            per = self.data / fap_value 
            sm = smoothed / fap_value
            
        else: 
            per = self.data
            sm  = smoothed
            ax.plot(self.fap,  c = 'green',  label = "FAP", linewidth=0.9)

        per.plot(linewidth=0.5, scale=scale, color= "black", ax = ax, alpha= 0.7, label = "Raw Periodogram" )
        sm.plot(linewidth=0.9,  scale=scale, color= "red",   ax = ax, label = "Smoothed")

        if sn : 
            ax.set_ylabel("Signal to Noise Ratio") #this does not work lmao
        
        ax.legend()
        ax.set_xlim(self.minf, self.maxf)
        ax.set_title(f"Periodogram of {self.name}")

        return fig , ax 