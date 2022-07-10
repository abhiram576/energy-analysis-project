# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 21:29:22 2020

@author: Kaustubh Dhamale
"""

# built-in python modules
import datetime
import inspect
import os

# scientific python add-ons
import numpy as np
import pandas as pd

# plotting stuff
# first line makes the plots appear in the notebook
#matplotlib inline 
import matplotlib.pyplot as plt
import matplotlib as mpl

# finally, we import the pvlib library
from pvlib import solarposition,irradiance,atmosphere,pvsystem
from pvlib.forecast import GFS, NAM, NDFD, RAP, HRRR

# Choose a location.
# Denmark
latitude = 56.56
longitude = 9.0309
tz = 'Etc/GMT+1'
surface_tilt = 30
surface_azimuth = 180 # pvlib uses 0=North, 90=East, 180=South, 270=West convention
albedo = 0.2
start = pd.Timestamp(datetime.date.today(), tz=tz) # today's date
end = start + pd.Timedelta(days=360) # 10 days from today


# Define forecast model
fm = GFS()
#fm = NAM()
#fm = NDFD()
#fm = RAP()
#fm = HRRR()
# Retrieve data
forecast_data = fm.get_processed_data(latitude, longitude, start, end)
forecast_data.head()
forecast_data['temp_air'].plot()
ghi = forecast_data['ghi']
ghi.plot()
plt.ylabel('Irradiance ($W/m^{-2}$)')

# retrieve time and location parameters
time = forecast_data.index
a_point = fm.location
solpos = a_point.get_solarposition(time)
#solpos.plot()
dni_extra = irradiance.get_extra_radiation(fm.time)

#dni_extra.plot()
#plt.ylabel('Extra terrestrial radiation ($W/m^{-2}$)')
airmass = atmosphere.get_relative_airmass(solpos['apparent_zenith'])

#airmass.plot()
#plt.ylabel('Airmass')
poa_sky_diffuse = irradiance.haydavies(surface_tilt, surface_azimuth,
                                       forecast_data['dhi'], forecast_data['dni'], dni_extra,
                                       solpos['apparent_zenith'], solpos['azimuth'])
#poa_sky_diffuse.plot()
#plt.ylabel('Irradiance ($W/m^{-2}$)')
poa_ground_diffuse = irradiance.get_ground_diffuse(surface_tilt, ghi, albedo=albedo)

#poa_ground_diffuse.plot()
#plt.ylabel('Irradiance ($W/m^{-2}$)')
aoi = irradiance.aoi(surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])

#aoi.plot()
#plt.ylabel('Angle of incidence (deg)')
poa_irrad = irradiance.poa_components(aoi, forecast_data['dni'], poa_sky_diffuse, poa_ground_diffuse)

poa_irrad.plot()
plt.ylabel('Irradiance ($W/m^{-2}$)')
plt.title('POA Irradiance')
temperature = forecast_data['temp_air']
wnd_spd = forecast_data['wind_speed']
pvtemps = pvsystem.sapm_celltemp(poa_irrad['poa_global'], wnd_spd, temperature)

pvtemps.plot()
plt.ylabel('Temperature (C)')
sandia_modules = pvsystem.retrieve_sam('SandiaMod')
sandia_module = sandia_modules.Canadian_Solar_CS5P_220M___2009_
sandia_module
effective_irradiance = pvsystem.sapm_effective_irradiance(poa_irrad.poa_direct, poa_irrad.poa_diffuse, 
                                                          airmass, aoi, sandia_module)

sapm_out = pvsystem.sapm(effective_irradiance, pvtemps, sandia_module)
#print(sapm_out.head())

sapm_out[['p_mp']].plot()
plt.ylabel('DC Power (W)')
plt.xlabel('10 days of Denamrk')
