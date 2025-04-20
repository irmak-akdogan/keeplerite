# keeplerite

Welcome to keeplerite, a package for easy visualization of Kepler data. 

## What does it do? 



## Installation 

This package is not on pyPI yet. However, you can install the package from this github page, go to "Code" button and choose "Download ZIP". After that, open up the ZIP file.

    $ from /path/to/keeplerite import Astro_Objects 


## Streamlit App 

### Online 

You can also access an online streamlit app version of keeplerite right [here!](https://keeplerite.streamlit.app/) If the app hasn't been used for a while, it might be asleep, and you'll need to wait a bit for it to wake up. Here, you can use the dropdown menus, textboxes, sliders, and checkboxes to adjust the settings of your tpf, lightcurve, and periodogram quickly.  

### Local 

There are some advantages to running the app locally instead of online. There might be runtime errors on streamlit servers if the files have been downloading for too long, and the app tends to be slower due to limited computing in streamlit. 

To be able to save the fits files retrieved from keeplerite, run the app faster, and to avoid runtime errors, you can also use the streamlit app locally on your own machine. If you run these commands on your terminal, it will automatically take you to a web page where keeplerite is run locally. 

    $ cd /path/to/keeplerite
    $ streamlit run webapp.py 




