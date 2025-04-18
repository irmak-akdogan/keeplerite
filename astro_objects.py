import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

from attributes import TPF, LC, PD


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
            #tpf = filtered.download(download_dir="/Users/student/Desktop/lightkurve")
            tpf = filtered.download(download_dir="./lightkurve")
            self.tpf = TPF(tpf, self.name , quarter) 

    def set_lc(self, stitch, aperture_type = "pipeline", threshold = 1 ): 

        if self.tpf == None:
            self.set_tpf()
   
        if stitch:

            all_tpfs = self.search.download_all(download_dir="./lightkurve")

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