import lightkurve as lk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize 
from sectors import*

def get_values(name, sector = -1):
    
    search = search_result(name)
    
    if sector == -1:
        lc = search[len(search)-1].download()
        sector = lc.sector
    else:
        lc = lk.search_lightcurve(name, author = 'SPOC', sector = sector, cadence = 120).download()
    
    time = np.array(lc.time.value)
    flux = np.array(lc.flux.value)
    flux_err = np.array(lc.flux_err.value)

    full = np.stack((time, flux, flux_err), axis =-1)

    df = pd.DataFrame(full, columns = ['Time','Flux', 'Flux_err'])
    df = df.dropna(subset=['Flux'])
    
    time = df['Time']
    flux = df['Flux']
    flux_err = df['Flux_err']
    
    return time, flux, flux_err

def sin_func(t, amp, freq, phase, offset):
    return amp * np.sin(t * freq + phase)  + offset

def fit_sin(time, flux):

    time = np.array(time)
    flux = np.array(flux)
    ff = np.fft.fftfreq(len(time), (time[1]-time[0])) # Discrete Fourier Transform sample frequencies
    Fyy = abs(np.fft.fft(flux)) #Compute the one-dimensional discrete Fourier Transform.
    guess_amp = np.std(flux) #* 2.**0.5
    guess_freq = abs(ff[np.argmax(Fyy[1:])+1]) # excluding the zero frequency "peak", which is related to offset
    guess_freq = 2.*np.pi*guess_freq
    guess_phase = 0.
    guess_offset = np.mean(flux)
    guess = np.array([guess_amp, guess_freq, guess_phase, guess_offset])

   
    popt, pcov = scipy.optimize.curve_fit(sin_func, time, flux, p0=guess)
    A, w, p, c = popt
    f = w/(2.*np.pi)
    fitfunc = lambda t: A * np.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc }

def freq_errors(time, flux, flux_err, result):
    
    time = np.array(time)
    flux = np.array(flux)
    flux_err = np.array(flux_err)
    N = len(time)
    T = time[-1] - time[0]
    
    A = result['amp']
    w = result['omega']
    p = result['phase']
    c = result['offset']
    f = result['freq']
    
    sigma_m = 1.08574 * (flux_err/flux)
    a = np.sqrt((2/N)) * sigma_m

#     function = lambda t: A * np.sin(w*t + p) + c
#     pred_flux = function(time)
#     act_flux = np.copy(flux)

#     rmsd = RMSD(act_flux, pred_flux)
    
#     error = (np.sqrt(6/N)) * (1/((np.pi)*T)) * rmsd

    freq_err = (np.sqrt(6/N)) * 1/(np.pi*T) * (sigma_m/a)
#     per_err = 1 / freq_err
    per_err = freq_err / ((f**2))
    
    return freq_err, per_err
    
def least_square_fit(TIC, sector = -1):
  
  t,f, f_err = get_values(TIC, sector)
  result = fit_sin(t, f)

  print('Amplitude: ' +str(result['amp']))
  print('Angular freq: ' +str(result['omega']))
  print('Phase: ' +str(result['phase']))
  print('Offset: ' +str(result['offset']))
  print('Freq: ' +str(result['freq']))
  print('Period: ' +str(result['period']))
  
  plt.plot(t, f,"-k", label=TIC, linewidth=2)
  plt.plot(t, result["fitfunc"](t), "r-", label="sin fit curve", linewidth=2)
  plt.legend(loc="best")
  plt.show()

  freq_err, per_err = freq_errors(t,f, f_err, result)
  print(freq_err)
  print(per_err)
  
