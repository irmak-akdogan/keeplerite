import streamlit as st

import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

from astro_objects import Astro_Objects
    
st.set_page_config(page_title="Keeplerite", page_icon=":sunny:")

st.title('Kepler Data Visualizer')

st.markdown("""
 * Use the menu on the left to search an object and adjust plotting settings.
 * Your plots will appear below! 
""")

st.sidebar.markdown("## Object Settings")

name = st.sidebar.text_input('Object Name', "Kepler-8") 
exp_time = st.sidebar.selectbox('Exposure Time', ["long", "short", "fast"])

search_state = st.text('Searching your object... this may take a minute.')

@st.cache_data
def search_object(t_name, exptime):

    search = lk.search_targetpixelfile(t_name, mission = "Kepler", exptime = exptime )
    
    return search

if "astro_obj" not in st.session_state or st.session_state["name"] != name:

    search = search_object(name, exp_time)
    object = Astro_Objects(search, target_name=name)
    st.session_state["astro_obj"] = object
    st.session_state["name"] = name

else:
    object = st.session_state["astro_obj"]



search_state.text('Object found!')

st.sidebar.markdown("## Target Pixel File Settings")

quarter_to_display = st.sidebar.selectbox('Quarter', object.quarters)

try:
    object.set_tpf(quarter = quarter_to_display)

except:
    st.warning('There was a problem creating your Target Pixel File. Try a different setting.')
    st.stop()

aperture_option    = st.sidebar.selectbox('Aperture', ["pipeline", "threshold", "all", "custom"])

if aperture_option == "custom": 
    std = st.sidebar.number_input("Standard Deviations From Mean", 
                                  min_value=1, max_value=5, value=1, step=1)
else:
    std = 1 

object.tpf.set_aperture(aperture_option, std)

show_aperture      = st.sidebar.checkbox('Show Aperture', value = False)

st.header("Target Pixel File")
fig1, _ = object.tpf.plot_tpf(show_aperture = show_aperture)
st.pyplot(fig1)

st.sidebar.markdown("## Lightcurve Settings")

stitch_all_q     = st.sidebar.checkbox('Stitch All Quarters', value = False)

filter_percent   = st.sidebar.number_input('Outlier Filter Percentage', min_value=1, max_value=100, value=20, step=10)

st.header("Lightcurve")

try:
    object.set_lc(stitch = stitch_all_q, 
                aperture_type = aperture_option,
                threshold = std)
    object.lc.filter_lcs(filter_percent)
    fig2, _ = object.lc.plot_lc()
    st.pyplot(fig2)

except:
    st.warning('There was a problem creating your Lightcurve. Try a different setting.')
    st.stop()

st.sidebar.markdown("## Periodogram Settings")

scales = ['log', 'linear', 'symlog', 'asinh', 'logit', 'function', 'functionlog']

freq_range = st.sidebar.slider('Frequency Range', min_value=1, max_value=1000, value=(1,150))
scale  = st.sidebar.selectbox('Select Scale', scales)
smoothing = st.sidebar.slider('Smoothing', min_value=0.1, max_value=50.0, value=10.0)
s_to_n  = st.sidebar.checkbox('Plot S/N', value = False)
fap = st.sidebar.slider('Error Refinement - Will take longer to compute', min_value=1, max_value=1000, value=10)

st.header("Periodogram")

try: 
    object.set_pd( minf = freq_range[0], maxf= freq_range[1], num = fap)
    fig3, _ = object.pd.plot_pd(smooth = smoothing, scale = scale, sn  = s_to_n)
    st.pyplot(fig3)

except:
    st.warning('There was a problem creating your Periodogram. Try a different setting.')
    st.stop()


#tpf.interact_sky  - gaia targetlerını üzerine eklicek
#TGLC  <333333
 
# to do acil: 
#   make a jupyter notebook about it :/ 

#   sort by time value or quarter before you stitch - find np.arg_sort 