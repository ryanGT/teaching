import matplotlib.pyplot as plt
from scipy import log10, angle

def find_dB_mag_and_phase(Gjw):
    dB_mag = 20.0*log10(abs(Gjw))
    phase = angle(Gjw,1)
    return dB_mag, phase

    
def bode_plot(freq, dB_mag, phase, fignum=1, clear=True, xlim=None, \
              label=None, fmt='-'):
    """This function plots a very nice Bode plot.  freq is a vector in
    Hz.  dB_mag and phase are vectors with the same length as freq."""
    plt.figure(fignum)
    if clear:
        plt.clf()

    plt.subplot(211)
    plt.semilogx(freq, dB_mag, fmt, label=label)
    plt.ylabel('dB Mag.')

    if xlim:
        plt.xlim(xlim)

    plt.subplot(212)
    plt.semilogx(freq, phase, fmt, label=label)
    plt.ylabel('Phase (deg.')
    plt.xlabel('Freq. (Hz)')

    if xlim:
        plt.xlim(xlim)


def bode_plot2(freq, Gjw, *args, **kwargs):
    """calculate dB_mag and phase from Gjw and then plot a Bode plot
    using the bode_plot function, passing in
    bode_plot(freq,dB_mag,phase,*args,**kwargs)."""
    dB_mag, phase = find_dB_mag_and_phase(Gjw)
    bode_plot(freq,dB_mag,phase,*args,**kwargs)
    return dB_mag, phase

