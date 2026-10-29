p='work/verify.py'
s=open(p,encoding='utf-8').read()
s=s.replace("lim = (cut + pd.Timedelta(minutes=45)).tz_convert(None) + pd.Timedelta(hours=2 if 3 < cut.month < 11 else 1)","lim = M._local_naive(pd.DatetimeIndex([cut + pd.Timedelta(minutes=45)]))[0]")
open(p,'w',encoding='utf-8').write(s)
