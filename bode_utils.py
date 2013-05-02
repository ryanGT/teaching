import matplotlib.pyplot as plt
from scipy import log10, angle, squeeze, r_, where

def find_dB_mag_and_phase(Gjw):
    dB_mag = 20.0*log10(abs(Gjw))
    phase = angle(Gjw,1)
    return dB_mag, phase

    
def bode_plot(freq, dB_mag, phase, fignum=1, clear=True, xlim=None, \
              label=None, fmt='-', grid=True, **kwargs):
    """This function plots a very nice Bode plot.  freq is a vector in
    Hz.  dB_mag and phase are vectors with the same length as freq."""
    plt.figure(fignum)
    if clear:
        plt.clf()

    plt.subplot(211)
    plt.semilogx(freq, dB_mag, fmt, label=label, **kwargs)
    plt.ylabel('dB Mag.')

    if grid:
        plt.grid(1)

    if xlim:
        plt.xlim(xlim)

    plt.subplot(212)
    plt.semilogx(freq, phase, fmt, label=label, **kwargs)
    plt.ylabel('Phase (deg.)')
    plt.xlabel('Freq. (Hz)')

    if grid:
        plt.grid(1)

    if xlim:
        plt.xlim(xlim)


def bode_plot2(freq, Gjw, *args, **kwargs):
    """calculate dB_mag and phase from Gjw and then plot a Bode plot
    using the bode_plot function, passing in
    bode_plot(freq,dB_mag,phase,*args,**kwargs)."""
    dB_mag, phase = find_dB_mag_and_phase(Gjw)
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

