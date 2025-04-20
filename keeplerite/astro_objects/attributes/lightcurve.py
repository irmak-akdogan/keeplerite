import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

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

