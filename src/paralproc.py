
from bifacial import BifModule, PvConfigs
import bif_power 
import multiprocessing  
import psutil
from datetime import datetime 
from tqdm import tqdm 
import pandas as pd  

bif_module = BifModule()
pv_config =  PvConfigs()
steps = 24
position =  0

from zoneinfo import ZoneInfo 

eastern_timezone = ZoneInfo('US/Eastern')
time_zone  = 'US/Eastern'
start_date = datetime(2021, 1, 1, 0, tzinfo=eastern_timezone) 
end_date  = datetime(2021, 12, 31, 23,  tzinfo=eastern_timezone) 
start_date.astimezone(eastern_timezone) 
end_date.astimezone(eastern_timezone)
data = bif_power .solcastData(start_date= start_date,end_date= end_date, timezone=time_zone  )


def set_priority(pid):
    p = psutil.Process(pid)
    p.nice = psutil.HIGH_PRIORITY_CLASS 
    


class ParlFct(): 
    def __init__(self, bif_module: BifModule,pv_config :  PvConfigs,position, ): 
        self.bif_module  = bif_module 
        self.pv_config  = pv_config 
        self.position = position  
    def __call__(self, data): 
        return bif_power.prod_power(self.bif_module, self.pv_config, self.position, data)
         

if __name__ == "__main__" :
    result = []
    pool = multiprocessing.Pool(4, set_priority, (multiprocessing.current_process().pid,))
    processes  =  [ pool.apply_async( ParlFct(bif_module, pv_config, position), 
                                     args  = (data.iloc[i],) ) for i in tqdm(range(8760))]
    for p in processes: 
        result.append(p.get()) 
    # Register the output values as csv file 
    pd.DataFrame({'date':  data.date, 'power_prod': result}).to_csv(r'C:\Users\ghas2002\Desktop\codes_python\BifEstimator\bifacial-power-estimator\results\results.csv')