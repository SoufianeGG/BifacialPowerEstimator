import pandas as pd 
import numpy as np  
from bifacial import BifModule, PvConfigs
import calplot
from tqdm import tqdm 
import bif_power 

# Here we use the Marion's model for ground mounted system 
# reference :  https://www.sciencedirect.com/science/article/pii/S0038092X13003034?via%3Dihub

def sliding_coef(tilt_angle) : 
    return 0.6*np.sin(tilt_angle *np.pi /180)  
 
# function to find the days where S_today > S_yesterday 

def marion_model_days(input_data: pd.DataFrame,pv_config : PvConfigs ):  
    # compute the daily snowDepth 
    daily_snow =  [input_data.snowDepth[i*24-1] for i in range(1,round(len(input_data)/24))] 
    daily_df  = pd.DataFrame({'date': input_data.date , 'snowDepth': daily_snow , 'condition': [0]* len(input_data)}) 
    for i in range(1,len(input_data)):
    # check if there is a new snowfall
        if  1 < (daily_df.snowDepth[i] - daily_df.snowDepth[i-1])* np.cos(pv_config.titl*np.pi/180):
            daily_df.condition[i] = 1 
    # Highlight the days where we have snowDepth 
    return daily_df 

# we assume that we've the same configuration as Marion model
# 3 modules in vertical direction  


def covered_modules(pv_config : PvConfigs, input_data : pd.DataFrame ):  
    slidingCoefficient = sliding_coef(pv_config.tilt)
    activation_coefficient  = pv_config.slideCoef 
    daily_snow =  [input_data.snowDepth[i*24-1] for i in range(1,int(len(input_data)/24))] 
    covered_height  =  [0]* len(input_data)
    for i in range(1,int(len(input_data)/24)-1):  
    # idea: condition of the snow coverage
        if 1 < (daily_snow[i]-daily_snow [i-1])* np.cos(pv_config.tilt*np.pi/180) :   
            covered_height[i*24 : (i+1)*24] =  [1]* 24
            for j in range(i*24+1, (i+1)*24): 
                if (input_data.temperature[j] - input_data.totalIrrad[j]/activation_coefficient > 0.0) and (covered_height[j]> 0.0) :
                    covered_height[j] = covered_height[j]-slidingCoefficient 
                else :   covered_height[j] = covered_height[j-1]
                if covered_height[j] < 0 : covered_height[j] = 0 
        else :
            covered_height[i*24 : (i+1)*24]  = [covered_height[i*24-1]] * 24 
            for k in range(i*24+1, (i+1)*24): 
                if (input_data.temperature[k] - input_data.totalIrrad[k]/activation_coefficient > 0.0) and (covered_height[k]> 0.0):
                    covered_height[k] = covered_height[k]-slidingCoefficient
                else :   covered_height[k] = covered_height[k-1]  
                if covered_height[k] < 0 : covered_height[k] = 0
    input_data['covered_height'] = covered_height            
    return input_data


# power production of the modules
# snow strings covered or partially covered are considered to produce no electricity 
# we assume that we've the same configuration as Marion's model  

def snow_power( bif_module : BifModule, pv_config: PvConfigs, inputData:pd.DataFrame):
   # module1, module2, module3  = [[1]*len(inputData)] * 3
    module1  =  [1]*len(inputData)
    module2  =  [1]*len(inputData)
    module3  =  [1]*len(inputData)
    power_m1 = [1]*len(inputData)
    power_m2 = [1]*len(inputData)
    power_m3 = [1]*len(inputData)
    for i in tqdm(range(len(inputData))): 
        if ( 0 < inputData.covered_height[i] <= 1/3): 
            module1[i] =0
        elif ( 1/3 < inputData.covered_height[i] <= 2/3):
            module1[i] =0
            module2[i]= 0
        elif  ( 2/3 < inputData.covered_height[i] <=1) :
            module1[i] = 0 
            module2[i] = 0
            module3[i] = 0 
        power_m1[i] = bif_power.prod_power(bif_module, pv_config , 0, inputData.iloc[i], module1[i])
        power_m2[i] = bif_power.prod_power(bif_module, pv_config , 0, inputData.iloc[i], module2[i])
        power_m3[i] = bif_power.prod_power(bif_module, pv_config , 0, inputData.iloc[i], module3[i])
    inputData['module1'], inputData['module2'], inputData['module3'] = [power_m1, power_m2, power_m3]
    inputData['m1'], inputData['m2'], inputData['m3'] =  [module1, module2, module3]
    return inputData 

# Show the day of the 

def cal_marionDays( data : pd.DataFrame ): 
    events = pd.Series( data.covered_height , index = data.date )
    calplot.calplot( events, yearlabel_kws ={'color': 'black'} )