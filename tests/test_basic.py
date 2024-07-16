import unittest 
import bif_power 
import marion_model 
from bifacial import BifModule, PvConfigs

bif_module  = BifModule()
pv_configs =   PvConfigs()


class TestBif(unittest.TestCase):
    # testing the celle's temperautre
    def  test_cell_temp(self) : 
        self.assertAlmostEquals(bif_power.cell_temp(bif_module, 30,1000),   55.5144, delta = 0.2)
    
    def test_sliding_coef(self):
        self.assertAlmostEquals(marion_model.sliding_coef(30), 0.3, delta = 0.01)  
if __name__ == '__main__': 
    unittest.main() 