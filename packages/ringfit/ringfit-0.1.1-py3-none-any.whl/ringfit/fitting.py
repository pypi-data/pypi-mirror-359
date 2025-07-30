import numpy as np
import ehtim as eh
from scipy.optimize import minimize
from ringfit import extraction as ex

RADPERUAS = eh.RADPERUAS   # rad / µas

# -----------------------------------------------------------1 basic fits
def fit_circle(P, xs, ys):
    """Return mean radius of best-fit circle."""
    return np.sqrt((P[:,0]-xs)**2 + (P[:,1]-ys)**2).mean()

def fit_ellipse(P, xs, ys):
    """Fit axis-aligned ellipse and return (width,height)."""
    x, y = P[:,0]-xs, P[:,1]-ys
    def cost(ab):
        a,b = ab
        if a<=1e-5 or b<=1e-5: return 1e12
        return np.sum(((x/a)**2+(y/b)**2-1)**2)
    a0,b0 = 0.5*x.ptp(), 0.5*y.ptp()
    res   = minimize(cost,[max(a0,1e-3),max(b0,1e-3)],method='Powell')
    a,b   = res.x if res.success else (a0,b0)
    return 2*a, 2*b

def fit_limacon(P, xs, ys):
    """Fit r(θ)=L1(1+L2 cos(θ-φ)), constrain |L2|≤0.5."""
    dx,dy   = P[:,0]-xs, P[:,1]-ys
    r_obs   = np.hypot(dx,dy)
    theta   = np.arctan2(dy,dx)
    def cost(p):
        L1,L2,phi = p
        if L1<=1e-6 or abs(L2)>0.5: return 1e12
        return np.sum((r_obs - L1*(1+L2*np.cos(theta-phi)))**2)
    res = minimize(cost,[r_obs.mean(),0.2,0.0],method='Powell')
    L1,L2,phi = res.x if res.success else (r_obs.mean(),0.2,0.0)
    return xs,ys,L1,np.clip(L2,-0.5,0.5),phi

# ------------------------------------------------------------ wrapper
def analyze_image(im="im1.jpg", threshold=0.02, radius=30, margin=15):
    """High-level convenience wrapper; prints fitted parameters."""
    arr = ex._to_array(im)
    pts = ex.rbp_find_bright_points(arr.copy(), threshold, radius, margin=margin)
    if not pts:
        print("no bright points found"); return
    xs, ys = ex.find_true_center(pts)
    P      = np.array([[p[1],p[0]] for p in pts])
    R      = fit_circle(P,xs,ys)
    ew,eh  = fit_ellipse(P,xs,ys)
    lima   = fit_limacon(P,xs,ys)
    print(f"pts={len(pts)} centre=({xs:.1f},{ys:.1f})")
    print(f"circle radius  : {R:.2f}")
    print(f"ellipse (w,h)  : ({ew:.2f}, {eh:.2f})")
    print(f"limaçon L1={lima[2]:.2f} L2={lima[3]:.2f} φ={lima[4]:.2f}")
