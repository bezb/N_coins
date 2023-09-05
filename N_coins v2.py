# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 18:47:35 2023

@author: KBezborodov
"""

import pandas as pd
from datetime import date, datetime
#import plotly.graph_objects as go

from port_calc import port_calc 

# ------ Globals 

# bull_1 = 2017-3-27 ... 2017-12-17
# bull_2 = 2019-1-21 ... 2019-7-7
# bull_3 = 2020-3-23 ... 2021-3-21
# bull_4 = 2021-7-26 ... 2021-11-21
# bull_5 = 2022-11-28 ... 2023-8-31

# bear_1 = 2018-1-8 ... 2018-12-16
# bear_2 = 2019-8-12 ... 2020-3-22
# bear_3 = 2021-4-19 ... 2021-7-25
# bear_4 = 2021-11-22 ... 2023-1-8

# 7 years = 2016-3-14 ... 2023-7-31
# 6 years = 2017-3-27 ... 2023-7-31
# 4 years = 2019-1-21 ... 2023-7-31
# 3 years = 2020-3-23 ... 2023-7-31
# 2 years = 2021-5-31 ... 2023-7-31

date_start = date(2016, 3, 14) 
date_stop = date(2023, 8, 31) 

outfile3 = 'res_N_coins_3D 7yrs_full_MAX.xlsx'

infile = '17_coins_usd.csv'

hi_res_min = 0.40
hi_res_max = 0.60
hi_res_steps = 10 # 44

lo_res_min = -0.12
lo_res_max = -0.18
lo_res_steps = 6 # 34

dolya_min = 0
dolya_max = 1
dolya_steps = 10 # 10


#used_c = [1, 1, 1, 1, 1, 1, 0, 0, 1, 1]
#used_coins = pd.Series(used_c)

# ---- Reading source

curs = pd.read_csv( infile, encoding='ansi', parse_dates=[0], dayfirst=True, sep=';', decimal=',' )
#curs = curs.rename(columns={'дата':'date'} )
curs['date'] = pd.to_datetime(curs['date']).dt.date

Ncoins = curs.shape[1] - 1        # Number of Coins
Ncol = Ncoins + 1                 # Number of Columns

curs2 = curs[curs.date >= date_start]
curs2 = curs2[curs2.date <= date_stop]

# ---- convert days to weeks 

w1 =  curs2['date'].sub(date_start).astype('int64')
w2 = w1.div(86400000000000).astype('int64')
w3 = w2.div(7).astype('int')
curs2['week'] = w3
del w1, w2, w3
# days = curs2.date.count() 

curs_w = pd.DataFrame(columns=curs2.columns)
curs_w['date'] = curs2['date'].groupby(curs2.week).max()
curs_w.iloc[:,1:Ncol] = curs2.iloc[:,1:Ncol].groupby(curs2.week).mean()
curs_w = curs_w.drop(columns='week', axis=1)

# ---- remove columns containing zeros only

curs_w = curs_w.drop(columns = curs_w.columns[curs_w.iloc[:,0:Ncol].max() == 0])

# ---- adding fiat

curs_w['USD'] = 1.0

pd.set_option('display.float_format', '{:.4f}'.format)

# -------- Main cycle -------

hi_res_delta = (hi_res_max - hi_res_min) / hi_res_steps

lo_res_delta = (lo_res_max - lo_res_min) / lo_res_steps

dolya_delta = (dolya_max - dolya_min) / dolya_steps

res = pd.DataFrame(columns=['hi_res', 'low_res', 'dolya', 'port_MAX', 'port_LAST'])

time_start = datetime.now()
print (' Started at ' + str(time_start))
#time_1perc = 100 / ((hi_res_steps+1) * (lo_res_steps+1))

for a_ind in range (0, hi_res_steps+1):
    hi_res = hi_res_min + (a_ind * hi_res_delta)
    hi_res = float(f'{hi_res:4f}')

    for b_ind in range (0, lo_res_steps+1):
        low_res = lo_res_min + (b_ind * lo_res_delta)
        low_res = float(f'{low_res:4f}')

        if b_ind > 0 :
            time_cur = datetime.now()
            time_work = time_cur - time_start
            time_perc = (a_ind * (lo_res_steps + 1) + b_ind) / ((hi_res_steps+1) * (lo_res_steps+1))
            time_perc_100 = 0.01 * int( time_perc * 10000)
            time_perc_100 = float(f'{time_perc_100:2f}')
            time_estim = time_work * (1 / time_perc)
            time_end = time_start + time_estim

            print("\r[+] Done: " + str(time_perc_100) + str('% - est ') + str(time_end), end="")

        for d_ind in range (0, dolya_steps+1):
            dolya = dolya_min + (d_ind * dolya_delta)
            dolya = float(f'{dolya:4f}')

            port_0 = port_calc(hi_res, low_res, dolya, curs_w)

            ret_MAX = port_0['itogo'].max() 
            ret_LAST = port_0['itogo'].iloc[-1] 
            
            ret_MAX = float(f'{ret_MAX:4f}')
            ret_LAST = float(f'{ret_LAST:4f}')

            #print (hi_res, low_res, dolya, ret_MAX, ret_LAST )
            appe = [hi_res, low_res, dolya, ret_MAX, ret_LAST]
            res.loc[ len(res.index )] = appe

time_end = datetime.now()
print ('\n Main cycle done at ' + str(time_end))


# ----- Widening dataframes & reporting

writer = pd.ExcelWriter(outfile3)
res.to_excel(writer, 'Sheet1', index=False)

for d_ind in range (0, dolya_steps+1):
    dolya = dolya_min + (d_ind * dolya_delta)
    dolya = float(f'{dolya:4f}')
    res_tmp = res[res['dolya'] == dolya]
    res_tmp = res_tmp.drop(columns='dolya', axis=1)
    wide_tmp = res_tmp.pivot(index='hi_res', columns='low_res', values='port_LAST')
    wide_tmp.to_excel(writer, str(dolya), index=True)
writer.save()
del writer


''' 

fig = go.Figure(data=[go.Surface(z=res_wide_M.values)])

fig.update_layout(title='Mt Bruno Elevation', autosize=True,
                  width=500, height=500,
                  margin=dict(l=65, r=50, b=65, t=90))
fig.show()
    
# ----- Counting potfolios in BTC

#port_0['date'] = pd.to_datetime(port_0['date']).dt.date
port_0_btc = port_0.copy()
port_0_btc.iloc[:,1:Ncol] = port_0.iloc[:,1:Ncol].div(curs_w.iloc[:,1], axis=0)
# port_0.iloc[:,1:9] = port_0.iloc[:,1:9].round(4)

'''

print( ' End' )
