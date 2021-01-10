from sklearn.linear_model import LinearRegression
import numpy as np

class Simulator:

    __slots__ = ('X', 'Y', 'linreg')

    def __init__(self, datas, ts):
        self.X, self.Y = X, Y = self.get_XY(datas, ts)
        self.linreg = LinearRegression().fit(X, Y)

    @staticmethod
    def get_XY(datas, ts):

        n = sum(len(v[0]) - 1 for v in datas.values())
        ps = sorted(set(len(ds) for ds in datas.values()))
        if len(ps) > 1:
            raise ValueError
        p = q = ps[0]

        X, Y = np.empty((n, p)), np.empty((n, q))

        ni = 0
        for i, (k, subdatas) in enumerate(sorted(datas.items())):
            t = ts[k]
            dt = np.diff(t)
            assert (dt > 0).all()
            lengths = sorted(set(len(d) for d in subdatas))
            if len(lengths) > 1: continue
            length = max(lengths[0] - 1, 0)
            for ii, d in enumerate(subdatas):
                indices = slice(ni, ni + length), ii
                X[indices] = (Xi := d[: -1])
                Y[indices] = (d[1 :] - Xi) / dt
            ni += length

        return X, Y

    def simulate(self, x, niterations, dt = 1e-5):
        X = self.X
        linreg = self.linreg
        vals = np.empty((niterations, X.shape[-1]))
        vals[0] = x
        ts = np.linspace(0, dt * niterations, niterations)
        for ni in range(1, niterations):
            pds = linreg.predict([x])[0]
            vals[ni] = x = x + pds * dt
        return ts, vals