from numpy import real, imag, pi, where, loadtxt
from scipy.optimize import curve_fit
from bokeh.plotting import figure, output_notebook, show, gridplot


# Resonator Analysis

def lorentz(x,*p):
#     p = amp, f0, kappa
    return (real(p[0]/(1-1j*(2*pi*x - 2*pi*p[1])/(p[2]/2)))**2 + imag(p[0]/(1-1j*(2*pi*x - 2*pi*p[1])/(p[2]/2)))**2)**.5

def analyze(filename):
    fig1, x,y = plotS21(filename)
#     Find Resonance
    f0 = x[where(y == y.max())][0]
    
# Convert db to Voltage
    yvolt = 10**(y/20.)
    fig=figure(
        x_axis_label="Frequency (GHz)",
        y_axis_label="Amplitude (V)",
        width=450)
    fig.circle(x*1e-9,yvolt, fill_color=None)
    p, res = curve_fit(lorentz, x, yvolt, [yvolt.max(),f0,.01])
    print("f0 = " + str(round(p[1]*1e-9, 6)) + " GHz")
    print("kappa = " + str(p[2]))
    print("Q = " + str(p[1]/(2*pi*p[2])))
    fig.line(x*1e-9,lorentz(x,*p))
    grid = gridplot([[fig1, fig]], title=filename)
    show(grid)

    #     Create results dict
    results = {
        'filename': filename,
        'freq': x,
        'dBm': y,
        'amp': yvolt,
        'f0': p[1],
        'kappa': p[2],
        'Q': p[1]/(2*pi*p[2]),
        'fig': grid
    }
    return results

def plotS21(filename):
    print(filename)
    x, y = loadtxt(filename, comments='!', skiprows=10, usecols=(0, 3), unpack=True)
    fig = figure(
        x_axis_label="Frequency (GHz)",
        y_axis_label="|S21| (dBm)" ,
        width=450)
    fig.circle(x*1e-9,y, fill_color=None)
    return fig,x,y