import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

#from pathlib import Path
#tmp_dir = Path("/tmp")

from attributes import TPF, LC, PD


class Astro_Objects(): 

    """
    A class for handling Kepler target pixel files, lightcurves, and periodograms
    associated with a specific astronomical object.

    Attributes
    ----------
    search : lightkurve.search.SearchResult
        The search result object containing TPF files across quarters.
    name : str
        Name of the target object.
    tpf : TPF or None
        TPF object containing pixel file data and aperture information.
    lc : LC or None
        LC object containing the processed lightcurve.
    pd : PD or None
        PD object containing the periodogram and FAP.
    quarters : ndarray
        Array of available quarter numbers.

    Methods
    -------
    get_quarters()
        Extracts and returns a list of available quarters from the search result.

    filter_quarter(quarter_number)
        Returns the subset of the search result corresponding to a specific quarter.

    set_tpf(quarter=0)
        Downloads and sets the TPF object for a given quarter.

    set_lc(stitch, aperture_type="pipeline", threshold=1)
        Constructs and sets the LC object from the TPF data.
        If stitch is True, it stitches data from all available quarters.
        
    set_pd(minf=1, maxf=150, num=10)
        Generates and sets the PD object using the lightcurve and simulated FAP.
    """

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
            tpf = filtered.download()
            self.tpf = TPF(tpf, self.name , quarter) 

    def set_lc(self, stitch, aperture_type = "pipeline", threshold = 1 ): 

        if self.tpf == None:
            self.set_tpf()
   
        if stitch:

            all_tpfs = self.search.download_all()

            lcs = []

            for tpf in all_tpfs:
                if aperture_type == "custom":
                    aperture_mask = tpf.create_threshold_mask(threshold=threshold)
                else:
                    aperture_mask = aperture_type 

                lc = tpf.to_lightcurve(aperture_mask=aperture_mask)
                lcs.append(lc)
            
            collection = lk.LightCurveCollection(lcs)
            stithced_lk = collection.stitch()

            self.lc = LC(stithced_lk, name = self.name)
            
        else: 
            lc = self.tpf.data.to_lightcurve(aperture_mask = self.tpf.aperture).normalize()
            self.lc = LC(lc, self.name )

    
    def set_pd(self, minf = 1 , maxf = 150, num = 10 ):

        if self.lc == None:
            self.set_lc()
        
        fap = self.lc.get_err(num = num)

        pd = self.lc.data.to_periodogram(normalization = 'psd', minimum_frequency = minf, maximum_frequency = maxf)
        self.pd = PD(pd, fap, self.name,  minf, maxf)