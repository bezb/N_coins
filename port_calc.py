# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:54:17 2023

@author: KBezborodov
"""

import pandas as pd
import numpy as np

init_val = 100      # initial investment in fiat
fee4swap = 0.01     # One percent
fee4swap_fix = 1    # One dollar
min_balance = 5     # minimal balance to donate
 
def port_calc (hi_res, low_res, dolya, curs_w):

    global port_0
    global zeros
    
    weekz = curs_w.date.count() 
    Ncol = curs_w.shape[1] - 1
    
    port_0 = pd.DataFrame(columns=curs_w.columns, index=curs_w.index)
    port_0['date'] = curs_w['date']
    
    port_0.iloc[0,1:Ncol+1] = init_val
    # port_0.iloc[0,2:Ncol] = 0     # all 0 but BTC & USD
    zeros = curs_w.iloc[0, : ] == 0
    port_0.loc[:, zeros ] = 0

    #print( port_0.iloc[0:1,0:Ncol+1] )
    port_0.insert(port_0.shape[1], 'itogo', 0, allow_duplicates = False)

    pd.set_option('display.float_format', '{:.4f}'.format)

    curs_now = curs_w.iloc[1,1:Ncol+1]
    curs_before = curs_w.iloc[0,1:Ncol+1]
    curs_d0 = curs_now / curs_before
    curs_d0 = curs_d0.fillna(0)
    curs_d0.replace( np.inf, 0, inplace=True)
    port_0.iloc[1,1:Ncol+1] = port_0.iloc[0,1:Ncol+1] * curs_d0
    
    # print( port_0.iloc[1,0:Ncol+1] )
    
    for i in range(2, weekz): 
        curs_now = curs_w.iloc[i,1:Ncol+1]
        curs_before = curs_w.iloc[i-1,1:Ncol+1]
        curs_early = curs_w.iloc[i-2,1:Ncol+1]
    
    # дельта к прошлой неделе
        curs_d = curs_now / curs_before - 1 
        curs_d = curs_d.fillna(0)
        curs_d.replace( np.inf, 0, inplace=True)

        port_0.iloc[i,1:Ncol+1] = port_0.iloc[i-1,1:Ncol+1] * (1 + curs_d)
    
    # дельта к позапрошлой неделе
        curs_d2 = curs_before / curs_early - 1 
        curs_d2 = curs_d2.fillna(0)
        curs_d2.replace( np.inf, 0, inplace=True)
        curs_d3 = curs_d + curs_d2
    
    # критерии добавления - вычитания
        crit_plus = curs_d > hi_res    # выросли сильно
        crit_minus1 = curs_d < low_res  # упали сильно сейчас
        crit_minus2 = (curs_d3 < low_res) & (curs_d < 0) # падают 2 недели подряд
        crit_minus12 = crit_minus1 | crit_minus2      # упали сильно за 1 ИЛИ 2 недели
        crit_minus3 = (port_0.iloc[i,1:Ncol+1] >= min_balance)
        crit_minus = crit_minus12 & crit_minus3      # упали И баланс не маленький
        
        port_0.iloc[i,1:Ncol+1] = port_0.iloc[i-1,1:Ncol+1] * (1 + curs_d)
    
        num_plus = sum(crit_plus)
        num_minus = sum(crit_minus)
        num_sigma = num_plus - num_minus
        if num_plus == 0 and num_minus == 0 : 
            continue
    
        if num_sigma > 0 : crit_minus['USD'] = True
        if num_sigma < 0 : 
            crit_plus['USD'] = True
            num_plus = num_plus + 1
    
        crit_any = crit_minus + crit_plus   # с кем что-то делаем 
        crit_none = ~crit_any               # с кем ничего не делаем
        
        port_sub = port_0.iloc[i,1:Ncol+1]
        port_sub_minus = dolya * port_sub[crit_minus]
        obshak_sum = sum(port_sub_minus)
        fee_fix = fee4swap_fix * 0.5 * (num_minus + num_plus)
        dobavka = (obshak_sum*(1.0 - fee4swap) / num_plus) - fee_fix
        if dobavka < 0 : 
            continue
    
        port_sub_first = (port_sub - port_sub_minus).fillna(port_sub)
        
        port_sub_plus = port_sub[crit_plus] + dobavka

        a1 = port_sub[crit_none]
        a2 = port_sub_first[crit_minus]
        a3 = port_sub_plus[crit_plus]
        port_super = pd.concat( [a1, a2, a3] )      #, join='inner')
        port_super['date'] = port_0.iloc[i,0]
        
        port_0.loc[ i , : ] = port_super
    
    port_0['itogo'] = port_0.loc[:, 'BTC':'USD'].sum(axis=1)
    return port_0 #ret_MAX_LAST
