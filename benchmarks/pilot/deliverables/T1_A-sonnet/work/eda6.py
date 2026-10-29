import sys; sys.path.insert(0,'work')
from common import *
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',200)
df = load().drop(columns='timestamp')
names = ['Tout','Wind','SolE','SolS','SolW','ElVent','Flow','TSup','DH','HC','CO2','Troom','People','Active','Damper','Rad','LightLvl','LightOn','Window','Tset','Hlim','Clim']
assert len(names)==df.shape[1]-0, (len(names), df.shape)
df.columns=names
x=df
x['CO2']=x['CO2'].where(x['CO2']>0)
t = x['Troom']; print('Troom>35', (t>35).sum(), t[t>35].index.min(), t[t>35].index.max())
print(t[t>35].resample('D').count()[lambda s:s>0])
o = x['Tout']; print('Tout>40', (o>40).sum(), o[o>40].index[:5].tolist())
h = x.groupby([x.index.hour])[['CO2','Active','Damper','Window','LightOn','Flow','People']].mean().round(2)
print(h)
wd = x.index.dayofweek
print(x.groupby(wd)[['CO2','Active','Damper']].mean().round(1))
print(x.corr().round(2)['CO2'])
# active vs CO2
print(x.groupby('Active')['CO2'].describe())
print(x.groupby('Damper')['CO2'].describe().head(10))
