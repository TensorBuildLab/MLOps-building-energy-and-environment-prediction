from cvlib import *
import warnings; warnings.filterwarnings('ignore')
X,y,loc = get_data()
allf = list(X.columns)
def hgb(**kw):
    params = dict(max_iter=300, learning_rate=0.04, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, random_state=0)
    params.update(kw)
    return lambda: [HistGradientBoostingRegressor(**params)]
print('all features, residual HGB'); run_cv(X,y,loc,hgb(),allf,True)
print('all features, direct HGB'); run_cv(X,y,loc,hgb(),allf,False)
