import sys; sys.path.insert(0,'work')
from common import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_rows',200)
df = load()
co2='RoomB:Sensor__CO2'
s = df[co2]
print(s.describe())
print((s<0).sum(), (s==-999).sum())
print(s[s>0].quantile([.001,.01,.05,.25,.5,.75,.95,.99,.999]))
vc = s[s>0].round().value_counts().head(20); print(vc)
# unique values count
print('nunique', s[s>0].nunique())
# step sizes
d = s[s>0].diff().dropna(); d=d[d!=0]; print(d.abs().describe()); print(d.abs().round().value_counts().head(15))
# fraction of consecutive equal
print('frac equal consecutive', (s.diff()==0).mean())
fig,axs=plt.subplots(4,1,figsize=(18,14))
s2 = s.where(s>0)
for i,(a,b) in enumerate([('2023-02-27','2023-03-20'),('2023-03-20','2023-04-10'),('2023-04-10','2023-05-01'),('2023-05-01','2023-06-01')]):
    s2[a:b].plot(ax=axs[i])
plt.tight_layout(); plt.savefig('work/co2.png', dpi=60)
