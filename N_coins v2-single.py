# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 18:47:35 2023

@author: KBezborodov
"""

import pandas as pd
from datetime import date

from port_calc import port_calc


infile = '17_coins_usd.csv'

# Globals 

global port_0, curs_w

# bull_1 = 2017-3-27 ... 2017-12-17
# bull_2 = 2019-1-21 ... 2019-7-7
# bull_3 = 2020-3-23 ... 2021-3-21
# bull_4 = 2021-7-26 ... 2021-11-21
# bull_5 = 2022-11-28 ... 2023-8-31

# bear_1 = 2018-1-8 ... 2018-12-16
# bear_2 = 2019-8-12 ... 2020-3-22
# bear_3 = 2021-4-19 ... 2021-7-25
# bear_4 = 2021-11-22 ... 2023-1-8

# 7 years = 2016-3-14 ... 2023-8-31
# 6 years = 2017-3-27 ... 2023-8-31
# 5 years = 2018-6-11 ... 2023-8-31
# 4 years = 2019-1-21 ... 2023-8-31
# 3 years = 2020-3-23 ... 2023-8-31
# 2 years = 2021-5-31 ... 2023-8-31

date_start = date(2016, 3, 14) 
date_stop = date(2023, 8, 31) 

hi_res = 0.46
low_res = -0.14
dolya = 0.9

outfile2 = 'res_N_coins_usd 7yrs 046_014_09 tst.xlsx'


# init_c = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# init_coins = pd.Series(init_c)

# ---- Reading source

curs = pd.read_csv( infile, encoding='ansi', parse_dates=[0], dayfirst=True, sep=';', decimal=',' )
#curs = curs.rename(columns={'дата':'date'} )
curs['date'] = pd.to_datetime(curs['date']).dt.date

Ncoins = curs.shape[1] - 1        # Number of Coins
Ncol = Ncoins + 1                 # Number of Columns

curs2 = curs[curs.date >= date_start]
curs2 = curs2[curs2.date <= date_stop]

# --- convert days to weeks 

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

# ----- remove columns containing zeros only

curs_w = curs_w.drop(columns = curs_w.columns[curs_w.iloc[:,0:Ncol].max() == 0])

# ---- adding fiat

curs_w['USD'] = 1.0


# -------- Main cycle -------

port_0 = port_calc(hi_res, low_res, dolya, curs_w)
ret_MAX = port_0['itogo'].max() 
ret_LAST = port_0['itogo'].iloc[-1] 

port_0['date'] = pd.to_datetime(port_0['date']).dt.date
port_0.iloc[:,1:Ncol+2] = port_0.iloc[:,1:Ncol+2].round(2)
port_0.to_excel(outfile2, 'port_0', index=False)

'''   
# ----- Counting potfolios in BTC

#port_0_btc = port_0.copy()
#port_0_btc.iloc[:,1:Ncol] = port_0.iloc[:,1:Ncol].div(curs_w.iloc[:,1], axis=0)
'''

print( ' End' )
