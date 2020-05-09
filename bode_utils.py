from scipy import log10, angle, squeeze, r_, where
import matplotlib
import numpy as np
from numpy import pi
import matplotlib.ticker
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


def find_freq_vect(t):
    dt = t[2] - t[1]
    T = t.max()+dt
    df = 1/T
    N = len(t)
    nvect = np.arange(N)
    freq = df*nvect
    return freq

def unwrap_deg(phase):
    phaser = phase*pi/180
    phaseru = np.unwrap(phaser)
    phase_uw = phaseru*180/pi
    return phase_uw


def find_dB_mag_and_phase(Gjw):
    dB_mag = 20.0*log10(abs(Gjw))
    phase = angle(Gjw,1)
    return dB_mag, phase


def _get_fig(fig=None, fignum=1, figsize=None):
    if fig is None:
        import matplotlib.pyplot as plt
        fig = plt.figure(fignum, figsize=figsize)
    return fig

def mygrid(ax):
    ax.grid(1, which="both",ls=":", color='0.75')

    
def set_log_ticks(ax,nullx=False):
    locmaj = matplotlib.ticker.LogLocator(base=10,numticks=12) 
    ax.xaxis.set_major_locator(locmaj)
    if nullx:
        ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())

    mysubs = np.arange(0.1,0.99,0.1)
    locmin = matplotlib.ticker.LogLocator(base=10.0,subs=mysubs,numticks=12)
    ax.xaxis.set_minor_locator(locmin)
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())


def set_db_ticks(ax, db):
    dbmin = db.min()
    dbmax = db.max()
    # aim for less than 6 ticks in muliples of 10, 20, 40 , ...
    myspan = dbmax-dbmin
    maxticks = 6

    ticklist = [10,20,40,60,80]

    N = None

    for tick in ticklist:
        if myspan/tick < maxticks:
            N = tick
            break

    if N is None:
        N = 100

    majorLocator = MultipleLocator(N)
    majorFormatter = FormatStrFormatter('%d')

    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)

    
def set_phase_ticks(ax, phase):
    phmin = phase.min()
    phmax = phase.max()
    # if 4 or 5 multiples of 45 is enough, use 45 as the base
    mul45 = (phmax-phmin)/45
    if mul45 < 6:
        N = 45
    elif mul45 < 12:
        N = 90
    else:
        N = 180
    majorLocator = MultipleLocator(N)
    majorFormatter = FormatStrFormatter('%d')

    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)

    
def bode_plot(freq, dB_mag, phase, fig=None, fignum=1, clear=True, xlim=None, \
              label=None, fmt='-', grid=True, figsize=None, unwrap=False, \
              **kwargs):
    """This function plots a very nice Bode plot.  freq is a vector in
    Hz.  dB_mag and phase are vectors with the same length as freq."""
    fig = _get_fig(fig, fignum, figsize=figsize)
    if clear:
        fig.clf()

    if len(fig.axes) > 1:
        ax = fig.axes[0]
    else:
        ax = fig.add_subplot(211)

    if unwrap:
        phase = unwrap_deg(phase)
        
    ax.semilogx(freq, dB_mag, fmt, label=label, **kwargs)
    ax.set_ylabel('dB Mag.')

    set_log_ticks(ax,nullx=True)
    set_db_ticks(ax, dB_mag)

    if grid:
        mygrid(ax)
        #ax.grid(1)

    if xlim:
        ax.set_xlim(xlim)


    if len(fig.axes) > 1:
        ax2 = fig.axes[1]
    else:
        ax2 = fig.add_subplot(212)

    ax2.semilogx(freq, phase, fmt, label=label, **kwargs)
    ax2.set_ylabel('Phase (deg.)')
    ax2.set_xlabel('Freq. (Hz)')

    set_log_ticks(ax2)
    set_phase_ticks(ax2, phase)

    if grid:
        #ax2.grid(1)
        mygrid(ax2)

    if xlim:
        ax2.set_xlim(xlim)


def bode_plot2(freq, Gjw, *args, **kwargs):
    """calculate dB_mag and phase from Gjw and then plot a Bode plot
    using the bode_plot function, passing in
    bode_plot(freq,dB_mag,phase,*args,**kwargs)."""
    dB_mag, phase = find_dB_mag_and_phase(Gjw)
    bode_plot(freq,dB_mag,phase,*args,**kwargs)
    return dB_mag, phase


def bode_plot3(freq, inst, *args, **kwargs):
    """call bode_plot after extracting dBmag and phase from inst.  In
    theory, any instance that has a dBmag and phase property would
    work, but this was created to make it easy to pass in an rwkbode
    instance to bode_plot."""
    if callable(inst.dBmag):
        dB_mag = inst.dBmag()
    else:
        dB_mag = inst.dBmag
    phase = inst.phase
    bode_plot(freq,dB_mag,phase,*args,**kwargs)
    return dB_mag, phase


def calc_db_mag_and_phase(Gjw, unwrap=False):
    dB = 20.0*log10(abs(Gjw))
    phase = angle(Gjw, 1)
    if unwrap:
        phase = unwrap_deg(phase)
    return dB, phase


def bode_plot_from_complex(freq, Gjw, fignum=1, clear=False, unwrap=False, \
                           **kwargs):
    dB, phase = calc_db_mag_and_phase(Gjw, unwrap=unwrap)
    bode_plot(freq, dB, phase, fignum=fignum, clear=clear, **kwargs)
    


def crossover_freq(db, freq):
    #find where the current db value is greater than 0 and the next one is not
    t1=squeeze(db > 0.0)#vector of True and False elements for db > 0.0
    t2=r_[t1[1:],t1[0]]#vector t1 shifted by 1 index
    t3=(t1 & ~t2)#current value is > 0.0 and the next is not
    ind = t3.argmax()
    return freq[ind], ind

