import numpy as np
import matplotlib.pyplot as plt
import ehtim as eh

from . import extraction as ex        # rbp + profile code :contentReference[oaicite:0]{index=0}
from . import fitting    as fit       # circle / ellipse / limacon  :contentReference[oaicite:1]{index=1}


class AnalysisObject:
    def __init__(self, im, *, bp_th=0.005, bp_rad=30, margin=15, halfwin=40):
        if not isinstance(im, eh.image.Image):
            raise TypeError("expect ehtim.image.Image")
        self._im = im.copy()

        # grab all four quantities from the helper in extraction.py
        (self.angle,
         self.radius,
         self.brightness,
         self.width) = ex.get_quantities(
             im, ('angle', 'radius', 'brightness', 'width'),
             bp_th=bp_th, bp_rad=bp_rad, margin=margin, halfwin=halfwin
         )                                             # :contentReference[oaicite:2]{index=2}

        # one-shot geometric fits on the bright-point cloud
        pts = ex.rbp_find_bright_points(
            ex._to_array(im).copy(), bp_th, bp_rad, margin=margin
        )                                              # :contentReference[oaicite:3]{index=3}
        P  = np.array([[p[1], p[0]] for p in pts])
        xs, ys = ex.find_true_center(pts)              # :contentReference[oaicite:4]{index=4}
        self.circle_r     = fit.fit_circle(P, xs, ys)
        self.ellipse_wh   = fit.fit_ellipse(P, xs, ys)
        self.limacon      = fit.fit_limacon(P, xs, ys)

    # ------------------------------------------------------------------ #

    def plot(self, x, y, *, plot=True, **kw):
        data = {
            'angle':       self.angle,
            'radius':      self.radius,
            'brightness':  self.brightness,
            'width':       self.width,
        }
        if x not in data or y not in data:
            raise ValueError("x and y must be one of angle/radius/brightness/width")
        xdata, ydata = data[x], data[y]

        if plot:
            plt.figure(figsize=kw.pop('figsize', (6, 4)))
            plt.plot(xdata, ydata, **kw)
            plt.xlabel(x.capitalize())
            plt.ylabel(y.capitalize())
            plt.tight_layout()
            plt.show()

        return xdata, ydata
