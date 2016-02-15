from numpy import real, imag, pi, where, loadtxt, sqrt, diag
from scipy.optimize import curve_fit
from os import path, listdir
import h5py

import plotly.plotly as py
from plotly.graph_objs import *
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
init_notebook_mode()

from plotlylayouts import *

# Resonator Analysis

def lorentz(x,*p):
#     p = amp, f0, kappa
    return (real(p[0]/(1-1j*(2*pi*x - 2*pi*p[1])/(p[2]/2)))**2 + imag(p[0]/(1-1j*(2*pi*x - 2*pi*p[1])/(p[2]/2)))**2)**.5

def analyze(filename, show=True):
    fig1, x,y = plotS21(filename, show=show)
#     Find Resonance
    f0 = x[where(y == y.max())][0]
    
# Convert db to Voltage
    yvolt = 10**(y/20.)
    trace1 = Scatter(
        x=x*1e-9,
        y=yvolt,
        name="Data",
        mode="markers")
    
    p, pcov = curve_fit(lorentz, x, yvolt, [yvolt.max(),f0,.01])

    f0 = round(p[1]*1e-9, 6)
    kappa = p[2]
    q = p[1]/(2*pi*kappa)
    
#     Calculate fit error

    perr = sqrt(diag(pcov))
    
    f0err = perr[1]*1e-9
    kappaerr = perr[2]
    qerr = perr[1]/(2*pi*perr[2])
    
    if show:
        print 'f0 = {}+/- {:.5f} ({:.2}%) GHz'.format(f0, f0err, (f0err/f0)*100)
        print 'kappa = {}+/- {:.5f} ({:.2}%)'.format(kappa, kappaerr, (kappaerr/kappa)*100)
        print 'Q = {:.3f}+/- {:.3f} ({:.2}%)'.format(q, qerr, (qerr/q)*100)


    line = Scatter(
        x=x*1e-9, 
        y=lorentz(x, *p),
        name="Fit",
        mode='lines'
    )

    data = [trace1, line]
    layout = dict(
        title=filename,
        xaxis=dict(title="Frequency (GHz)"),
        yaxis=dict(title="Volts (V)")
    )
    fig = Figure(data=data, layout=layout)
    if show:
        iplot(fig)

    #     Create results dict
    results = {
        'filename': filename,
        'freq': x,
        'dBm': y,
        'amp': yvolt,
        'f0': p[1],
        'kappa': p[2],
        'Q': p[1]/(2*pi*p[2]),
        'fig': fig,
        'f0err': f0err,
        'kappaerr': kappaerr,
        'qerr': qerr
    }
    return results

def getTrace(filename):
    x, y = loadtxt(filename, comments='!', skiprows=10, usecols=(0, 3), unpack=True)
    
    layout, trace = spectrumPlot(title=filename)
    trace['x'] = x*1e-9
    trace['y'] = y
    return layout, trace, x, y

def plotS21(filename, show=True, samplename="Sample"):
    data = []
    if type(filename) in (tuple, list):
        for f in filename:
            layout, trace, x, y = getTrace(f)
            data.append(trace)
    else:
        layout, trace, x, y = getTrace(filename)
        data.append(trace)

    layout['title']=samplename
    fig = Figure(data=data, layout=layout)
    if show:
        iplot(fig)
    return fig, x, y

def plotFluxDependence(datapath, samplename="Sample", param="f0"):
    files = listdir(path.join(datapath))

    volts = []
    freqs = []
    errors = []

    for f in files:
        if f.endswith('.s2p'):
            volt = float(path.splitext(f)[0])
            volts.append(volt)
            result = analyze(path.join(datapath,f), show=False)
            freqs.append(result[param])
    if param == "f0":
        yaxis = "Resonant Frequency (GHz)"
    elif param == "Q":
        yaxis = "Quality Factor (Q)"
    elif param == "kappa":
        yaxis = "$\kappa \\text{(MHz)}$"
        
    layout = dict(
            title="Flux Tuning of " + samplename,
            xaxis=dict(title="Volts (V)"),
            yaxis=dict(title=yaxis)
        )

    data = Scatter(
        x=volts,
        y=freqs,
        mode='markers',
        error_y=dict(
            type='data',
            visible=True
        )
    )

    fig = Figure(data=[data], layout=layout)
    iplot(fig)
    return fig

def plotDispersiveShift(datapath, show=False, samplename="Sample"):
    files = listdir(datapath)

    data = []
    layout, trace = spectrumPlot(title="Dispersive shift of " )

    for f in files:
        if f.endswith('.s2p'):
            result = analyze(path.join(datapath, f), show=show);
            
            descr = "$\\text{" + str(f.split('.')[0]) + "}\quad "
            descr = descr + "F_0 = " + str(round(result['f0']/1e9, 6)) + "\\text{GHz}\quad "
            descr = descr + "Q = " + str(round(result['Q'], 3)) + "\quad "
            descr = descr + "\kappa = " + str(round(result['kappa']/(2*pi*1e6), 3)) + "\\text{MHz}$"
            data.append(Scatter(
                x = result['freq'],
                y = result['dBm'],
                name = descr))
            
    layout['legend'] = dict(
        yanchor="bottom",
        xanchor="right",
        y=1.01,
        x=1
    )
    fig = Figure(data=data, layout=layout)
    iplot(fig)
    
def plotCounts(filename, show=True, samplename="Sample"):
    f = h5py.File(filename)
    data = []
    x = f['DataSet1']['xpoints'][:]
    y = None
    z = None
    if 'counts' in f['DataSet1'].keys():
        if 'ypoints' in f['DataSet1'].keys():
            y = f['DataSet1']['ypoints'][:]
            z = f['DataSet1']['counts'][:]
            layout, trace = countsPlot(title=samplename, dimension=2)
            trace['x'] = x
            trace['y'] = y
            trace['z'] = z
            data.append(trace)
        else:
            y = f['DataSet1']['counts'][:]
            layout, trace = countsPlot(title=samplename, dimension=1)
            trace['x'] = x
            trace['y'] = y
            data.append(trace)
            
    fig = Figure(data=data, layout=layout)
    if show:
        iplot(fig)
    
    return fig, x, y, z
#     else:
#         if 'ypoints' in f['DataSet1'].keys():
#             y = f['DataSet1']['ypoints'][:]
#             z = f['DataSet1']
#             z = np.sqrt(np.power(z['real'][:],2) + np.power(z['imag'][:],2))
#             extent = [min(x), max(x), min(y), max(y)]
#             plt.imshow(z, extent=extent)
#             return [x, y, z]   
#         else:
#             y = f['DataSet1']
#             y = np.sqrt(np.power(y['real'][:],2) + np.power(y['imag'][:],2))
#             plt.plot(x,y)
#             return [x, y]

def getH5Data(filename):
    f = h5py.File(filename)
    data = []
    x = f['DataSet1']['xpoints'][:]
    if 'counts' in f['DataSet1'].keys():
        if 'ypoints' in f['DataSet1'].keys():
            y = f['DataSet1']['ypoints'][:]
            z = f['DataSet1']['counts'][:]
            return x, y, z
        else:
            y = f['DataSet1']['counts'][:]
            return x, y
