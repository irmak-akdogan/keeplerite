import streamlit as st

import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

#from .astronomyobject import Astro_Objects

class Astro_Objects(): 

    def __init__(self, search, target_name = None, location = None ):

        self.name = target_name
        self.location = location

        self.tpf = None
        self.lc  = None 
        self.pd = None

        self.search = search
        self.quarters = self.get_quarters()


    def get_quarters(self):

        #add some filtering here to get rid of bad quarters. 

        descriptions = self.search.table['description']
        quarters = []

        for desc in descriptions:
            if 'Q' in desc:
                q_index = desc.find('Q')
                number = ''
                i = q_index + 1

                while i < len(desc) and desc[i].isdigit():
                    number += desc[i]
                    i += 1
                if number:
                    quarters.append(int(number))

        return np.unique(quarters)
    
    def filter_quarter(self, quarter_number):

        filtered = self.search[[f"Q{quarter_number}" in desc for desc in self.search.table['description']]]

        return filtered


    def set_tpf(self, quarter = 0):

        filtered = self.filter_quarter(quarter_number = quarter)
        
        results = len(filtered)

        if results == 0:
            print("No target pixel file found. Try a different quarter.")
        elif results == 1:
            tpf = filtered.download(download_dir="/Users/student/Desktop/lightkurve")
            self.tpf = TPF(tpf) 
        else: 
            print(f"Multiple results found ({results}). Please refine your search.")
            # Optionally, you could pick the first or let the user choose
            # self.tpf = TPF(search[0].download(download_dir="..."))

    def set_lc(self): 

        if self.tpf == None:
            self.set_tpf()

        lc = self.tpf.data.to_lightcurve(aperture_mask = self.tpf.aperture)
        self.lc = LC(lc)
    
    def set_pd(self, minf = 1 , maxf = 150, num = 10 ):

        if self.lc == None:
            self.set_lc()
        
        fap = self.lc.get_err(num = num)

        pd = self.lc.data.to_periodogram(normalization = 'psd', minimum_frequency = minf, maximum_frequency = maxf)
        self.pd = PD(pd, fap, minf, maxf)

class TPF(): 

    def __init__(self, data):
        self.data = data
        self.aperture = "pipeline"
        
    def plot_tpf(self, show_aperture = False): 

        if show_aperture: 
            ax = self.data.plot(aperture_mask = self.aperture)  
        else: 
            ax = self.data.plot()

        fig = ax.figure
        
        return fig, ax  

    def set_aperture():
        #no idea how I'll do this yet 
        #will have some sort of user input 

        return None
    
class LC():

    def __init__(self, data_list):
        self.data = data_list 

    def filter_lcs(self, percentage): 

        # mediandan belli bi percentage 
        # altıysa ya da üstüyse silsin o data pointi 

        return None

    def stitch(self): 

        #make a collection and then stitch em' up

        return None

    def get_err(self, num): 

        f = self.data.flux
        t = self.data.time.to_value('jd')
        e = self.data.flux_err

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

        return fig, ax 


class PD(): 

    def __init__(self, data, fap, minf = 1 , maxf = 150 ):

        self.data = data 
        self.fap  = fap
        self.minf = minf
        self.maxf = maxf

    def plot_pd(self, smooth = 10, fap  = False):
        fig, ax = plt.subplots()

        smoothed = self.data.smooth(method='boxkernel', filter_width = smooth)

        self.data.plot(linewidth=0.5, scale='log', color= "black", ax = ax, alpha= 0.7, label = "Raw Periodogram" )
        smoothed.plot(linewidth=0.9, color= "red", scale='log', ax = ax, label = "Smoothed")
        
        if fap: 

            plt.plot(self.fap,  c = 'green',  label = "FAP", linewidth=0.9)

        plt.legend()
        plt.xlim(self.minf, self.maxf)

        return fig , ax 
    



st.title('Kepler Data Visualizer')

st.sidebar.markdown("## Object Settings")

name = st.sidebar.text_input('Object Name', 'Kepler-8') 
exp_time = st.sidebar.selectbox('Exposure Time', ["long", "short", "fast"])

@st.cache_data
def search_object(t_name, exptime):

    search = lk.search_targetpixelfile(t_name, mission = "Kepler", exptime = exptime )
    
    return search

search = search_object(name, exp_time)
object = Astro_Objects(search , target_name = name )

# print the name of the object and the location from WCS maybe 

st.sidebar.markdown("## Target Pixel File Settings")

quarter_to_display = st.sidebar.selectbox('Quarter', object.quarters)
aperture_option    = st.sidebar.selectbox('Aperture', ["pipeline", "threshold", "all", "custom"])

if aperture_option == "custom": 
    std = st.sidebar.number_input("Standard Deviations From Mean", min_value=1, max_value=5, value=1, step=1)

show_aperture      = st.sidebar.checkbox('Show Aperture', value = False)

object.set_tpf(quarter = quarter_to_display)

st.header("Target Pixel File")
fig1, _ = object.tpf.plot_tpf( show_aperture = show_aperture)
st.pyplot(fig1)

st.sidebar.markdown("## Lightcurve Settings")

stitch_all_q     = st.sidebar.checkbox('Stitch All Quarters', value = False)

if stitch_all_q: 
    color_by_quarter = st.sidebar.checkbox('Color By Quarter', value = False)

remove_percent   = st.sidebar.number_input('Outlier Filter Percentage', min_value=1, max_value=100, value=20, step=10)

st.sidebar.markdown("## Periodogram Settings")

freq_range = st.sidebar.slider('Frequency Range', min_value=1, max_value=1000, value=(1,150))
log_scale  = st.sidebar.checkbox('Use Logarithmic Scale', value = True)
smoothing = st.sidebar.slider('Smoothing', min_value=0.1, max_value=50.0, value=10.0)
s_to_n  = st.sidebar.checkbox('Plot S/N', value = False)
fap = st.sidebar.slider('Error Refinement', min_value=1, max_value=1000, value=10)


# to do : 
#   add error handling  
#   also bad data filtering / outlier removal 
#   aperture stuff 
#   periodogram freq range doesnt work idk why - fap da sanki çalışmıyo ama emin olamadım 

st.header("Lightcurve")
object.set_lc()
fig2, _ = object.lc.plot_lc()
st.pyplot(fig2)

st.header("Periodogram")
object.set_pd( minf = freq_range[0], maxf= freq_range[1], num = fap)
fig3, _ = object.pd.plot_pd(smooth = smoothing)
st.pyplot(fig3)


#tpf.interact_sky  - gaia targetlerını üzerine eklicek
#TGLC  <333333