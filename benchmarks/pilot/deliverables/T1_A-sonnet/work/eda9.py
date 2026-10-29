import sys; sys.path.insert(0,'work')
from common import *
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
x = load2()
x['CO2']=x['CO2'].where(x['CO2']>0)
d = x['2023-05-10 06:00':'2023-05-10 20:00'][['CO2','Active','Damper','Window','LightOn','LightLvl','Flow','Troom']]
print(d.iloc[::3].round(1).to_string())
