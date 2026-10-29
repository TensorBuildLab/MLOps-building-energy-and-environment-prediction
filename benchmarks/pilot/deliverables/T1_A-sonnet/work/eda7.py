import sys; sys.path.insert(0,'work')
from common import *
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',300)
x = load2()
print(x['Troom']['2023-05-11 08:00':'2023-05-12 14:00'].iloc[::12].round(2).to_string())
print(x['Troom'].resample('D').agg(['min','median','max']).iloc[60:].round(1).to_string())
print(x['Tout'][x['Tout']>30])
for c in ['Tout','Wind','SolE','SolS','SolW','ElVent','Flow','TSup','DH','HC','LightLvl']:
    s=x[c]; print(c, s.quantile([0,.001,.5,.999,1]).round(1).tolist())
