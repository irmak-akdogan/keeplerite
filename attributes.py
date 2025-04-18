import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

class TPF(): 

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

    def __init__(self, data_list, name ):
        self.data = data_list 
        self.name = name 

    def filter_lcs(self, percentage): 

        # mediandan belli bi percentage 
        # altıysa ya da üstüyse silsin o data pointi 

        return None

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

    def __init__(self, data, fap, name, minf = 1 , maxf = 150  ):

        self.data = data 
        self.fap  = fap
        self.minf = minf
        self.maxf = maxf
        self.name = name 

    def plot_pd(self, smooth = 10, fap  = True, scale = "log"):
        fig, ax = plt.subplots()

        smoothed = self.data.smooth(method='boxkernel', filter_width = smooth)

        self.data.plot(linewidth=0.5, scale=scale, color= "black", ax = ax, alpha= 0.7, label = "Raw Periodogram" )
        smoothed.plot(linewidth=0.9,  scale=scale, color= "red",   ax = ax, label = "Smoothed")
        
        if fap: 

            plt.plot(self.fap,  c = 'green',  label = "FAP", linewidth=0.9)

        plt.legend()
        plt.xlim(self.minf, self.maxf)
        ax.set_title(f"Periodogram of {self.name}")

        return fig , ax 