import lightkurve as lk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def search_result(TIC):
    search_result = lk.search_lightcurve(TIC, author = 'SPOC', cadence = 120)
    return search_result
    
def single_sector(TIC, sector = -1):
    
    # layout of the figure
    fig, axes = plt.subplots(3, 1)
    fig.set_figheight(15)
    fig.set_figwidth(10)
    fig.tight_layout(pad=5.0)
    
    # Gathering data from specific sector
    search = search_result(TIC)
    
    if sector == -1:
        lc = search[len(search)-1].download()
    else:
        lc = lk.search_lightcurve(TIC, author = 'SPOC', sector = sector, cadence = 120).download()

    # Creating plots    
    lc.normalize().scatter(ax=axes[0], c='k', label = 'Light Curve') 

    pg = lc.to_periodogram(maximum_period=30)
    pg.plot(ax = axes[1], view='period', c='k', label = 'Periodogram')

    lc_model = pg.model(time=lc.time, frequency=pg.frequency_at_max_power)
    lc.normalize().scatter(ax=axes[2], c='k', label = 'Light Curve') 
    lc_model.plot(ax=axes[2], lw=3, ls='--', c='red', title = 'Model')
    
    # More figure layouts
    title = str(TIC) + ', Sector: ' + str(lc.sector)
    fig.suptitle(title, fontsize=16)
    
def plot_all_sectors(TIC):
    search_result = search_result(TIC)
    
    for i in range(len(search_result)):
        lc = search_result[i].download()
#         lc.normalize().scatter() 

        pg = lc.to_periodogram(maximum_period=30)
        pg.plot(view='period', title = '$' + 'Sector: ' + str(lc.sector)+ '$')

        # Create a model light curve for the highest peak in the periodogram
        lc_model = pg.model(time=lc.time, frequency=pg.frequency_at_max_power)
        ax = lc.normalize().scatter()
        lc_model.scatter(ax=ax, lw=3, ls='--', c='red', label = '$' + 'Sector: ' + str(lc.sector)+ '$')

def all_per(TIC):
    search = search_result(TIC)
    periods = []
    avg = 0
    std = 0

    for i in range(len(search)):
        lc = search[i].download()
        pg = lc.to_periodogram(maximum_period=30)
        per = pg.period_at_max_power.value
        print('Period in Sector', lc.sector,':', per)
        periods.append(per)
    std = np.std(periods)
    avg = np.average(periods)
    print('The avgerage is', avg, 'with a std of ', std)

def momentum_dumps(TIC):
    search = search_result(TIC)
    
    sectors = []
    for i in range(len(search)):
        sector_num = str(search[i].mission)
        sector_num = sector_num.split(' ')[2]
        sector_num = int(sector_num[:2])
        sectors.append(sector_num)
    
    
    for i in sectors:

        tpf = lk.search_targetpixelfile(TIC, mission='TESS',sector = i, author = 'SPOC', cadence = 120 ).download(quality_bitmask = 'none')
        
        plt.figure(figsize=(20,10))
    
        lc = lk.search_lightcurve(TIC, mission='TESS',sector = i, author = 'SPOC', cadence = 120 ).download(quality_bitmask = 'hard')
        lc.normalize().scatter()
 
        plt.vlines(tpf.time.value[np.bitwise_and(lc.hdu[1].data['QUALITY'],32) == 32], ymin=0, ymax=2, color = 'mediumseagreen', label = 'Momentum Dumps')
        
        f = lc.normalize()
        f = f[~np.isnan(f['flux'])]
        min_f = min(f['flux']) - 0.001
        max_f = max(f['flux']) + 0.001
        plt.ylim(min_f,max_f)
  
        plt.xlabel('Time (TJD)',fontsize = 16)
        plt.ylabel('Relative Flux', fontsize = 16)
        plt.title('$'+'Momentum Dump  Check,  Sector  '+ str(i) + '$', fontsize = 20)
        plt.legend(loc='best', fontsize = 12)
    
        plt.show()

def stitch(TIC):
    # want to add code that allows to change the range of stiched light curve, ie if data in sec 1-13 & 27-37 just want to show 27-37
    lc_full = lk.search_lightcurve(TIC, author = 'SPOC', cadence = 120).download_all()
    stitch = lc_full.stitch()
    
    stitch.scatter()
    
    pg = stitch.to_periodogram(maximum_period=30)
    pg.plot()
    print('The period at max power: ', pg.period_at_max_power)
  

    
    
