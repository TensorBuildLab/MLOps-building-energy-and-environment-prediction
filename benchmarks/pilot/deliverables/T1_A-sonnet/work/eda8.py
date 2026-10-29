import sys; sys.path.insert(0,'work')
from common import *
pd.set_option('display.width',250)
x = load2()
print(x.loc['2023-04-24 12:50':'2023-04-24 13:20',['Tout','SolS','ElVent','TSup','DH','CO2']].round(2).to_string())
print(x.loc['2023-04-24 15:25':'2023-04-24 15:45',['Tout','SolS','ElVent','TSup','DH','CO2']].round(2).to_string())
try:
    import zoneinfo; print(zoneinfo.ZoneInfo('Europe/Copenhagen'))
except Exception as e: print('no tz', e)
