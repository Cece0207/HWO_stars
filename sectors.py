def search_result(name):
    search_result = lk.search_lightcurve(name, author = 'SPOC', cadence = 120)
    return search_result

def plot_all_sectors(search_result):
    for i in range(len(search_result)):
        lc = search_result[i].download()
#         lc.normalize().scatter() 

        pg = lc.to_periodogram(maximum_period=30)
        pg.plot(view='period', title = '$' + 'Sector: ' + str(lc.sector)+ '$')


        # Create a model light curve for the highest peak in the periodogram
        lc_model = pg.model(time=lc.time, frequency=pg.frequency_at_max_power)
        ax = lc.normalize().scatter()
        lc_model.scatter(ax=ax, lw=3, ls='--', c='red', label = '$' + 'Sector: ' + str(lc.sector)+ '$')

def all_per(search):
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
