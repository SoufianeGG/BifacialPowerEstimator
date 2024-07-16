# We estimate the power production of bifacial panels based on the datasheet prodvided
import json 

# Import the os module
import os

filepath = os.path.dirname(__file__) 
os.chdir(os.path.dirname(filepath))
# Get the absolute path of the datasheet file
datasheet_file = os.path.join( os.path.dirname(filepath),"data", "datasheet.json")
config_file  =   os.path.join(  os.path.dirname(filepath),"data", "config.json")

# Define the BifModule class
class BifModule:
    def __init__(self, datasheet_file= datasheet_file):
        with open(datasheet_file, 'r') as f:
            data = json.load(f)
            
        # Assign attributes
        self.name =  data["name"]
        self.efficiency  = data["efficiency"]
        self.powerRate = data["power_rate"]
        self.powerTable = data["power_table"]
        self.gainTable   = data["gain_table"]
        self.width = data["width"]
        self.length  = data["length"]
        self.orientation = data["orientation"]
        self.tnoct  = data["tnoct"]
        self.tstc =  data["tstc"]
        self.bifFactor = data["bifaciality_factor"]
        self.maxPcoef  = data["max_power_coef"]
        
        # check the orientation of the module
        if self.orientation == "landscape":
            self.length,  self.width   = self.width, self.length
 
# Class of the PV array 
class PvConfigs:
    def __init__(self, configs= config_file):
        with  open(configs , 'r') as f : 
            configs  = json.load (f)
        self.azimuthAngle  = configs['azimuth_angle']
        self.gcr = configs['ground_coverage_ratio']
        self.nModules  = configs['number_modules']
        self.nPanles   = configs['number_panels']
        self.nRows = configs['numbers_rows']
        self.height  = configs['center_height']
        self.tilt   = configs["tilt"]
        self.slideCoef  = configs["sliding_coefficient"]





