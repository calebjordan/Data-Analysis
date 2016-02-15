from plotly.graph_objs import *

def spectrumPlot(title=""):
    layout = Layout(
        title=title,
        yaxis=dict(
            titlefont=dict(size=22),
            title="S21 (dB)",
            tickfont= dict(size= 16),
            ticks="inside",
            mirror="ticks",
            zeroline=False,
            showline=True,
            ),
        xaxis=dict(
            titlefont=dict(size=22),
            title="Frequency (GHz)",
            tickfont= dict(size= 16),
            ticks="inside",
            mirror="ticks",
            zeroline=False,
            showline=True,
            )
    )
    trace = Scatter(
        line=dict(width=1),
        mode="lines"
        )
    return layout, trace

def countsPlot(title="", dimension=1):
    layout = Layout(
        title=title,
        yaxis=dict(
            titlefont=dict(size=22),
            title="Switching Probability",
            tickfont= dict(size= 16),
            ticks="inside",
            mirror="ticks",
            zeroline=False,
            showline=True,
        ),
         xaxis=dict(
            titlefont=dict(size=22),
            title="",
            tickfont= dict(size= 16),
            ticks="inside",
            mirror="ticks",
            zeroline=False,
            showline=True,
            )       
    )
    trace = Scatter(
        line=dict(width=1),
        mode="markers"
    )
    return layout, trace