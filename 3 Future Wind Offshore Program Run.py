# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 20:36:46 2020

@author: Parag
"""
from oemof.tools import logger
from windpowerlib.wind_turbine import WindTurbine
from windpowerlib.turbine_cluster_modelchain import TurbineClusterModelChain
from windpowerlib import wind_farm
import pandas as pd
import logging
import os


try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None


logger.define_logging(logfile='wind_offshore.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

#[2]

logging.info("1.Read weather data")


filename = os.path.join(os.path.dirname(__file__), 'weather sample 1.csv')
weather = pd.read_csv(filename, index_col=0, header=[0, 1],
                      date_parser=lambda idx: pd.to_datetime(idx, utc=True))


weather.index = pd.to_datetime(weather.index).tz_convert('Europe/Copenhagen')


l0 = [_[0] for _ in weather.columns]
l1 = [int(_[1]) for _ in weather.columns]
weather.columns = [l0, l1]



logging.info("2.Initializing Wind Turbines ")


#Future Turbines
#12
siemens_gamesa_SG_8_167DD={

    'nominal_power': 8e6,
    'hub_height': 107,
    'rotor_diameter': 167,  
    'power_curve': pd.DataFrame(
        data={'value': [p * 1000 for p in [
                  0.0, 0.0, 650.0, 5600.0, 8000.0, 8000.0]],  
              'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]})  
}  


sg_8_167dd = WindTurbine(**bonus_b35)


logging.info("3.Creating Wind Farm ")


wind_turbine_fleet= pd.DataFrame(
        {'wind_turbine':[sg_8_167dd],
         'number_of_turbines':[213],
         })

offshore_wind_farm=wind_farm.WindFarm(wind_turbine_fleet, name='Offshore Wind Farm')

offshore_wind_farm.efficiency=0.9

offshore_wind_farm=TurbineClusterModelChain(offshore_wind_farm).run_model(weather)

offshore_wind_farm.power_output=offshore_wind_farm.power_output

print(offshore_wind_farm.power_output)


#Writing time series in csv file using pandas dataframe
logging.info("4.Write time series in CSV file")

df = pd.DataFrame(data=offshore_wind_farm.power_output)
s = df.to_csv('Wind Offshore.csv')
print(s)



logging.info("5.Plot time series data")

if plt:
    offshore_wind_farm.power_output.plot(legend=True, label='Offshore Wind Farms')
    
    plt.xlabel('Wind speed in m/s')
    plt.ylabel('Power in W')
    
    plt.show()
