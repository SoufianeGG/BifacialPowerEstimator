

""""Getting the Data From Solcast and Clean to 
Estimate the power productio of bifacial module using 
an empirical model with a view factor approach for estimating 
the total received irradiance. 
"""
from pvfactors.engine import PVEngine
from pvfactors.geometry import OrderedPVArray
#from  bifacial_radiance import RadianceObj

from scipy.interpolate import interp1d 
from datetime import datetime
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd  
import pytz  
import os
from bifacial import BifModule, PvConfigs, filepath


def solcastData(start_date: datetime = None  , end_date: datetime= None , timezone= None, data_file =  'data.csv' ): 
    # filetering the dataa
    data_file = os.path.join( os.path.dirname(filepath),"data", data_file) 
    # new solcast dataframe columns : air_temp, albedo,  dhi, dni , ghi, snow_depth, zenith, period_end  
    data_frame = pd.read_csv(data_file, delimiter =',')
    data_frame = pd.DataFrame(data  =  {'date' : data_frame['period_end'], 'temperature' :  data_frame['air_temp']
        , 'ghi' : data_frame['ghi'],'dhi': data_frame['dhi'],  'dni':data_frame['dni'], 'solarAzimuth': data_frame['azimuth'] ,  'solarZenith' : data_frame['zenith'], 
        'albedo' : data_frame['albedo'],  "snowDepth": data_frame['snow_depth']})
    data_frame.date  = pd.to_datetime(data_frame.date, utc = True )
    # timezone coversion
    if timezone is not None :  
        tz  = pytz.timezone(timezone)
        data_frame.date  =  data_frame.date.dt.tz_convert(tz) 
    # selet the date 
    if start_date  and end_date is not None :    
        newdata  = data_frame[(  start_date <= data_frame.date ) & (data_frame.date <=end_date) ]   
        return newdata.reset_index(drop = True )  
    else : return data_frame


"""Steps to compute the power production of a given module or system 

-------------        
STEP 1: Getting the datasheet and the tables 

STEP 2: Estimate the total irradiance 

STEP 3: Estimate the cell's temperature

STEP 4: Compute the power production using an empirical model d

STEP 5: Plot the power variation for a specific period  

"""


# step 1 reference values  

def ref_vals(bif_module : BifModule, gain  ) :
    power_ref  = bif_module.powerTable 
    gain_ref  = bif_module.gainTable
    irrad_ref = [1000*(x/bif_module.bifFactor +1) for x in gain_ref ] 
    fct_power  = interp1d(gain_ref, power_ref , fill_value='extrapolate')
    fct_phit  = interp1d(gain_ref, irrad_ref, fill_value='extrapolate')
    return fct_power(gain), fct_phit(gain)

# step 2 front and rear irradiance   

def irrad_frontRear( bif_module : BifModule,pv_config : PvConfigs  ,position, data):
   pvarray_parameters = {
    'n_pvrows': pv_config.nRows,            # number of pv rows
    'pvrow_height': pv_config.height,  # height of pvrows (measured at center / torque tube)
    'pvrow_width': bif_module.length   ,     # width of pvrows
    'axis_azimuth': 0,        # Azimuth angle of rotation axis 
    'surface_azimuth' : pv_config.azimuthAngle,
    'gcr':    pv_config.gcr } #s
   pvarray = OrderedPVArray.init_from_dict(pvarray_parameters)
   engine  = PVEngine(pvarray)
   engine.fit(data.date, data.dni, data.dhi, data.solarZenith, data.solarAzimuth, pv_config.tilt , pv_config.azimuthAngle,  data.albedo)
   report = engine.run_full_mode(fn_build_report  =   lambda pvarray: pvarray )
   front  =   float (report.ts_pvrows[position].front.list_segments[0].get_param_weighted('qinc'))
   rear   =   float( report.ts_pvrows[position].back.list_segments[0].get_param_weighted('qinc'))
   return front if (front >= 0 and  front <= 1e4)  else 0 , float(rear) if (rear >= 0 and rear <= 1e4) else 0  

# step 3 cell's temperature  

def  cell_temp(bif_module : BifModule, temperature , phit): 
    return (temperature  + (bif_module.tnoct - 20) * (phit/800) *(1 -   (bif_module.efficiency *(1-bif_module.maxPcoef*bif_module.tstc))/0.9 ))/(1+ (bif_module.tnoct - 20)* (phit/800)*(bif_module.maxPcoef*bif_module.efficiency/0.9))

# step 4 power production

def prod_power(bif_module: BifModule, pv_config , position, data,  snow_coef= 1):
    if data.solarZenith == 90: 
        return 0
    else :
        front, rear =  irrad_frontRear( bif_module, pv_config, position,data )
    phit   = snow_coef *front+  bif_module.bifFactor*rear    
    gain  =  rear/front *bif_module.bifFactor if front != 0.0 else  0.0
    pref =       ref_vals(bif_module,gain)[0] 
    if snow_coef == 0 : phit_ref =   1000
    else : phit_ref =  ref_vals(bif_module,gain)[1] 
    cell_temperature =  cell_temp( bif_module , data.temperature  , phit,) 
    return float (power_Est(bif_module,pref, cell_temperature, phit, phit_ref ))


# idea : compute the power production given the irradiances 

def prod_power_2(bif_module: BifModule, front , rear, data,  snow_coef= 1):
    if data.solarZenith == 90: 
        return 0
    # else :
    #     # front, rear =  irrad_frontRear( bif_module, pv_config, position,data )
    phit   = snow_coef *front+  bif_module.bifFactor*rear    
    gain  =  rear/front *bif_module.bifFactor if front != 0.0 else  0.0
    pref =       ref_vals(bif_module,gain)[0] 
    if snow_coef == 0 : phit_ref =   1000
    else : phit_ref =  ref_vals(bif_module,gain)[1] 
    cell_temperature =  cell_temp( bif_module , data.temperature  , phit,) 
    return float (power_Est(bif_module,pref, cell_temperature, phit, phit_ref ))



def power_Est(bif_module : BifModule, pref , cell_temp, phi_t, phit_ref) : 
    out_power  =  pref * (1+bif_module.maxPcoef*(cell_temp - 25) )*phi_t/phit_ref 
    return np.nan_to_num( out_power, nan=0)

# plotting the power variation 
# save the production as svg file 

def plot_data(data, title: str , save : bool , name : str):
    fig = px.line(template =  'plotly_white') 
    fig.add_trace((go.Scatter( x = data.date  ,  y = data.power ,  mode = 'lines', name =  title  , line=dict(color="orange") )))
    fig.update_layout(yaxis_title = "W" ,  xaxis_title = "Date",  font_family  =  'Times New Roman',font_color = 'black',font_size  =  18, )
    fig.show()  
    if save == True :  
        save_path =  os.path.join( os.path.dirname(filepath),name)
        fig.write_image( save_path +  ".svg")




