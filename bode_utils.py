from scipy import log10, angle, squeeze, r_, where

def find_dB_mag_and_phase(Gjw):
    dB_mag = 20.0*log10(abs(Gjw))
    phase = angle(Gjw,1)
    return dB_mag, phase


def _get_fig(fig=None, fignum=1):
    if fig is None:
        import matplotlib.pyplot as plt
        fig = plt.figure(fignum)
    return fig

    
def bode_plot(freq, dB_mag, phase, fig=None, fignum=1, clear=True, xlim=None, \
              label=None, fmt='-', grid=True, **kwargs):
    """This function plots a very nice Bode plot.  freq is a vector in
    Hz.  dB_mag and phase are vectors with the same length as freq."""
    fig = _get_fig(fig, fignum)
    if clear:
        fig.clf()

    ax = fig.add_subplot(211)
    ax.semilogx(freq, dB_mag, fmt, label=label, **kwargs)
    ax.set_ylabel('dB Mag.')

    if grid:
        ax.grid(1)

    if xlim:
        ax.set_xlim(xlim)

    ax2 = fig.add_subplot(212)
    ax2.semilogx(freq, phase, fmt, label=label, **kwargs)
    ax2.set_ylabel('Phase (deg.)')
    ax2.set_xlabel('Freq. (Hz)')

    if grid:
        ax2.grid(1)

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


def calc_db_mag_and_phase(Gjw):
    dB = 20.0*log10(abs(Gjw))
    phase = angle(Gjw, 1)
    return dB, phase

def bode_plot_from_complex(freq, Gjw, fignum=1, clear=False, **kwargs):
    dB, phase = calc_db_mag_and_phase(Gjw)
    bode_plot(freq, dB, phase, fignum=fignum, clear=clear, **kwargs)
    


def crossover_freq(db, freq):
    #find where the current db value is greater than 0 and the next one is not
    t1=squeeze(db > 0.0)#vector of True and False elements for db > 0.0
    t2=r_[t1[1:],t1[0]]#vector t1 shifted by 1 index
    t3=(t1 & -t2)#current value is > 0.0 and the next is not
    myinds=where(t3)[0]
    if not myinds.any():
        return None, []
    maxind=max(myinds)
    return freq[maxind], maxind

