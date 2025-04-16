import streamlit as st

import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

#from .astronomyobject import Astro_Objects

class Astro_Objects(): 

    def __init__(self, search, target_name = None, ):

        self.name = target_name

        self.tpf  = None
        self.lc  = None
        self.pd   = None

        self.search = search
        self.quarters = self.get_quarters()
    
    def get_quarters(self):

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

        if len(filtered) == 0:
            print("No target pixel file found. Try a different quarter.")
        else: 
            tpf = filtered.download(download_dir="/Users/student/Desktop/lightkurve")
            self.tpf = TPF(tpf) 

    def set_lc(self, stitch): 

        if self.tpf == None:
            self.set_tpf()
   
        if stitch:

            all_tpfs = self.search.download_all(download_dir="/Users/student/Desktop/lightkurve")

            lcs = []

            for tpf in all_tpfs:
                lc = tpf.to_lightcurve(aperture_mask = self.tpf.aperture)
                lcs.append(lc)
            
            collection = lk.LightCurveCollection(lcs)
            stithced_lk = collection.stitch()

            self.lc = LC(stithced_lk)
            
        else: 
            lc = self.tpf.data.to_lightcurve(aperture_mask = self.tpf.aperture).normalize()
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

    def set_aperture(self, aperture, threshold = 1 ):

        if aperture == "custom": 
            custom_threshold_mask = self.data.create_threshold_mask(threshold= threshold)
            self.aperture = custom_threshold_mask
        else: 
            self.aperture = aperture
    
class LC():

    def __init__(self, data_list):
        self.data = data_list 

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

        return fig, ax 


class PD(): 

    def __init__(self, data, fap, minf = 1 , maxf = 150 ):

        self.data = data 
        self.fap  = fap
        self.minf = minf
        self.maxf = maxf

    def plot_pd(self, smooth = 10, fap  = True, scale = "log"):
        fig, ax = plt.subplots()

        smoothed = self.data.smooth(method='boxkernel', filter_width = smooth)

        self.data.plot(linewidth=0.5, scale=scale, color= "black", ax = ax, alpha= 0.7, label = "Raw Periodogram" )
        smoothed.plot(linewidth=0.9,  scale=scale, color= "red",   ax = ax, label = "Smoothed")
        
        if fap: 

            plt.plot(self.fap,  c = 'green',  label = "FAP", linewidth=0.9)

        plt.legend()
        plt.xlim(self.minf, self.maxf)

        return fig , ax 
    

st.title('Kepler Data Visualizer')

st.markdown("""
 * Use the menu at left to search an object and adjust plotting settings
 * Your plots will appear below
""")

st.sidebar.markdown("## Object Settings")

name = st.sidebar.text_input('Object Name') 
exp_time = st.sidebar.selectbox('Exposure Time', ["long", "short", "fast"])

search_state = st.text('Searching your object... this may take a minute.')

@st.cache_data
def search_object(t_name, exptime):

    search = lk.search_targetpixelfile(t_name, mission = "Kepler", exptime = exptime )
    
    return search

search = search_object(name, exp_time)
object = Astro_Objects(search , target_name = name )

search_state = st.text('Object found!')

st.sidebar.markdown("## Target Pixel File Settings")

quarter_to_display = st.sidebar.selectbox('Quarter', object.quarters)

try:
    object.set_tpf(quarter = quarter_to_display)
except:
    st.warning('no tpf :(')
    st.stop()

aperture_option    = st.sidebar.selectbox('Aperture', ["pipeline", "threshold", "all", "custom"])

if aperture_option == "custom": 
    std = st.sidebar.number_input("Standard Deviations From Mean", 
                                  min_value=1, max_value=5, value=1, step=1)
    object.tpf.set_aperture(aperture_option, std)
else:
    object.tpf.set_aperture(aperture_option)

show_aperture      = st.sidebar.checkbox('Show Aperture', value = False)

st.header("Target Pixel File")
fig1, _ = object.tpf.plot_tpf( show_aperture = show_aperture)
st.pyplot(fig1)

st.sidebar.markdown("## Lightcurve Settings")

stitch_all_q     = st.sidebar.checkbox('Stitch All Quarters', value = False)

filter_percent   = st.sidebar.number_input('Outlier Filter Percentage', min_value=1, max_value=100, value=20, step=10)

st.header("Lightcurve")

try:
    object.set_lc(stitch_all_q)
    fig2, _ = object.lc.plot_lc()
    st.pyplot(fig2)
except:
    st.warning('light aint curvin')
    st.stop()

st.sidebar.markdown("## Periodogram Settings")

scales = ['linear', 'log', 'symlog', 'asinh', 'logit', 'function', 'functionlog']

freq_range = st.sidebar.slider('Frequency Range', min_value=1, max_value=1000, value=(1,150))
scale  = st.sidebar.selectbox('Select Scale', scales)
smoothing = st.sidebar.slider('Smoothing', min_value=0.1, max_value=50.0, value=10.0)
s_to_n  = st.sidebar.checkbox('Plot S/N', value = False)
fap = st.sidebar.slider('Error Refinement', min_value=1, max_value=1000, value=10)

st.header("Periodogram")

try: 
    object.set_pd( minf = freq_range[0], maxf= freq_range[1], num = fap)
    fig3, _ = object.pd.plot_pd(smooth = smoothing, scale = scale)
    st.pyplot(fig3)
except:
    st.warning('Cant periodogram today')
    st.stop()


#tpf.interact_sky  - gaia targetlerını üzerine eklicek
#TGLC  <333333


# where will i save the files...  
# to do : 
#   add error handling  
#   outlier removal 
