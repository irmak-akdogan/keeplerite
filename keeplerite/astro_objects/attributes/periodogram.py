import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

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
            ax.set_ylabel("Signal to Noise Ratio") 
        
        ax.legend()
        ax.set_xlim(self.minf, self.maxf)
        ax.set_title(f"Periodogram of {self.name}")

        return fig , ax 
