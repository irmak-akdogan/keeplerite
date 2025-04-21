# Welcome to Keeplerite

### A light way to keep all your Kepler stuff! 

This is package for easy visualization of Kepler data. It can be either imported to a jupyter notebook or used on streamlit with interactive tools. 

## What does it do? 

`keeplerite` simplifies working with Kepler space telescope data by providing a convenient interface to visualize and analyze light curves, target pixel files (TPFs), and periodograms by using the `lightkurve` library under the hood.

By few lines of code or using the Streamlit app, you can:

- Search and retrieve Kepler TPFs and light curves for a given target  
- Explore the effect of different apertures on the lightcurve
- Compute and visualize periodograms to study periodic signals  
- Propagate flux uncertainties using simulations  

## Installation

This package is not on pyPI yet, so it is not installable by pip. However, you can download the package from this github page, go to "Code" button and choose "Download ZIP". After that, open up the ZIP file. Use the block below to import it in a jupyter notebook. For more guide on how to use keeplerite on jupyter, check out tutorial.ipynb ! 

    $ import sys
    $ from pathlib import Path

    $ sys.path.append("the/path/to/where/you/keep/keeplerite")

    $ from keeplerite.astro_objects import Astro_Objects , TPF , LC , PD 


## Streamlit App 

### Online 

You can also access an online streamlit app version of keeplerite by the link below. If the app hasn't been used for a while, it might be asleep, and you'll need to wait a bit for it to wake up. Here, you can use the dropdown menus, textboxes, sliders, and checkboxes to adjust the settings of your tpf, lightcurve, and periodogram quickly.  

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://keeplerite.streamlit.app/)

### Local 

There are some advantages to running the app locally instead of online. There might be runtime errors on streamlit servers if the files have been downloading for too long, and the app tends to be slower due to limited computing in streamlit. 

To be able to save the fits files retrieved from keeplerite, run the app faster, and to avoid runtime errors, you can also use the streamlit app locally on your own machine. If you run these commands on your terminal, it will automatically take you to a web page where keeplerite is run locally. 

    $ cd /path/to/where/you/keep/keeplerite
    $ streamlit run webapp.py 

## Dependencies 

This package relies on:

* lightkurve
* numpy
* matplotlib
* streamlit