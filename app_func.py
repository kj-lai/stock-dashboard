import numpy as np, pandas as pd, re, time
from datetime import datetime
from time import time
from tqdm import tqdm
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

chromedriver = '../selenium_driver/bin/chromedriver'
out_dir = './data/'

# KLSE
klse = pd.read_csv(out_dir+'klse_06_final_table.csv')
klse['code'] = klse['code'].astype(str).apply(lambda x: x.zfill(4))
klse2 = pd.read_csv(out_dir+'klse_02_10yr_data.csv')
klse2['code'] = klse2['code'].astype(str).apply(lambda x: x.zfill(4))

# NASDAQ & NYSE
nyse = pd.read_csv(out_dir+'nasdaq_nyse_06_final_table.csv')
nyse2 = pd.read_csv(out_dir+'nasdaq_nyse_02_10yr_data.csv')

def show_tables(input_code, market):
    symbol = ['—','\xa0-\xa0']
    if market == 'klse':
        table1 = klse[klse.code == str(input_code)]
    elif market == 'nyse':
        table1 = nyse[nyse.ticker == str(input_code)] 
    if len(table1) == 0:
        # print('ERROR - Unidentified stock code/ticker.')
        return '_', '_', '_', '_', '_', '_', '_', '_'
    else:
        temp = table1.columns.tolist()
        table1_1 = table1[temp[:15]]
        table1_2 = table1[temp[15:-18]]
        table1_3 = table1[temp[-18:-11]]
        table1_4 = table1[temp[-5:]]

        if market == 'klse':
            table2 = klse2[klse2.code == str(input_code)].T.reset_index()
        elif market == 'nyse':
            table2 = nyse2[nyse2.ticker == str(input_code)].T.reset_index()
        table2.columns = ['Year'] + table2.iloc[1].tolist()[1:]
        table2.drop(index=[0,1], inplace=True)
        table_show = table2.copy()
        for cols in ['Revenue','NP','OCF','Shares']:
            table2[cols] = table2[cols].apply(lambda x: int(x.replace(',','')) if x not in symbol else 0)
        for cols in ['EPS', 'DPS', 'Div Payout','BVPS','NP Margin','ROE','Revenue GR','Revenue GR 3Y avg','Revenue GR 5Y avg', 
                     'Revenue GR 10Y avg','EPS GR','EPS GR 3Y avg','EPS GR 5Y avg','EPS GR 10Y avg','OCF GR','D/E','Price']:
            table2[cols] = table2[cols].apply(lambda x: float(x.replace(',','')) if x not in symbol else 0.0)
        table2['P/E'] = table2.apply(lambda x: np.around(x['Price']/x['EPS'], 2) if x['EPS'] != 0 else 0.0, axis=1)
        table2['EY'] = table2.apply(lambda x: np.around(x['EPS']/x['Price']*100, 2) if x['Price'] != 0 else 0.0, axis=1)
        table2['DY'] = table2.apply(lambda x: np.around(x['DPS']/x['Price']*100, 2) if x['Price'] != 0 else 0.0, axis=1)
        table_show['P/E'] = table2['P/E']
        table_show['EY'] = table2['EY']
        table_show['DY'] = table2['DY']
        temp = table2.columns.tolist()
        col_list = ['Year','Year End','Shares','BVPS','Price','P/E','EPS','EY','DPS','DY','Div Payout',
                    'ROE','D/E','Revenue','NP','NP Margin','OCF',
                    'EPS GR','EPS GR 3Y avg','EPS GR 5Y avg','EPS GR 10Y avg',
                    'Revenue GR','Revenue GR 3Y avg','Revenue GR 5Y avg','Revenue GR 10Y avg','OCF GR']
        table2 = table2[col_list]
        table_show = table_show[col_list]
        # try:
        #     title = table1.name.values[0]
        # except:
        #     title = ''
        # print('----- Stock Details for '+str(input_code)+': '+title+' -----')
        # display(table1_1)
        # display(table1_2.iloc[:, :18])
        # display(table1_2.iloc[:, 18:33])
        # display(table1_3)
        # display(table1_4)

        # print('\n----- Past 10 Year Financials -----')
        # display(table_show.iloc[:,:17])
        # display(table_show.iloc[:,17:])

        # print('\n----- Plot Graphs -----')
        fig1, fig2, fig3 = plot_tables(table2[::-1])

        return table1_1, table1_2, table1_3, table1_4, table2, fig1, fig2, fig3

def add_trendline(x, y):
    z = np.polyfit(x, y, 1)
    return z, np.poly1d(z)(x)

def plot_tables(table):
    nYear = len([x for x in table['NP'].tolist() if x != 0])
    
    fig1, ax = plt.subplots(1, 2, figsize=(20,6))
    fig1.patch.set_facecolor('white')
    ax0 = ax[0].twinx()
    ax[0].bar(np.arange(10)-0.2, table['NP'], color='black', width=0.4, alpha=0.7)
    ax0.bar(np.arange(10)+0.2, table['NP Margin'], color='red', width=0.4, alpha=0.7)
    ax[0].set_xticks(np.arange(0,10,1))
    ax[0].set_xticklabels(table.Year)
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Net Profit')
    ax0.set_ylabel('NP Margin (%)')
    ax[0].set_title('Net Profit vs NP Margin')
    coeff1, line1 = add_trendline(np.arange(nYear)-0.2, table['NP'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear)+0.2, table['NP Margin'][-nYear:])
    ax[0].legend(['NP : '+str(np.around(coeff1[0],2))] ,loc="upper left")
    ax0.legend(['Margin : '+str(np.around(coeff2[0],2))] ,loc="upper left", bbox_to_anchor=(0, 0.94))
    ax[0].plot(np.arange((10-nYear),10)-0.2, line1, '--', color='black', linewidth=3)
    ax0.plot(np.arange((10-nYear),10)+0.2, line2, '--', color='red', linewidth=3)

    
    ax0 = ax[1].twinx()
    ax[1].bar(np.arange(10)-0.3, table['Revenue'], color='black', width=0.3, alpha=0.7)
    ax0.bar(np.arange(10), table['OCF'], color='red', width=0.3, alpha=0.7)
    ax0.bar(np.arange(10)+0.3, table['NP'], color='blue', width=0.3, alpha=0.7)
    ax[1].set_xticks(np.arange(0,10,1))
    ax[1].set_xticklabels(table.Year)
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('MYR Mil')
    ax[1].set_title('Revenue vs Operating Cash Flow vs Net Profit')
    coeff1, line1 = add_trendline(np.arange(nYear)-0.3, table['Revenue'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear), table['OCF'][-nYear:])
    coeff3, line3 = add_trendline(np.arange(nYear)+0.3, table['NP'][-nYear:])
    ax[1].legend(['Revenue : '+str(np.around(coeff1[0],2))], loc="upper left")
    ax0.legend(['OCF : '+str(np.around(coeff2[0],2)),
                'NP : '+str(np.around(coeff3[0],2))], loc="upper left",bbox_to_anchor=(0, 0.94))
    ax[1].plot(np.arange((10-nYear),10)-0.3, line1, '--', color='black', linewidth=3)
    ax0.plot(np.arange((10-nYear),10), line2, '--', color='red', linewidth=3)
    ax0.plot(np.arange((10-nYear),10)+0.3, line3, '--', color='blue', linewidth=3)
    
    
    fig2, ax = plt.subplots(1, 2, figsize=(20,6))
    fig2.patch.set_facecolor('white')
    ax0 = ax[0].twinx()
    ax[0].bar(np.arange(10)-0.2, table['EY'], color='black', width=0.4, alpha=0.7)
    ax0.bar(np.arange(10)+0.2, table['DY'], color='red', width=0.4, alpha=0.7)
    ax[0].set_xticks(np.arange(0,10,1))
    ax[0].set_xticklabels(table.Year)
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Earning Yield (%)')
    ax0.set_ylabel('Dividend Yield (%)')
    ax[0].set_title('Earning Yield vs Dividend Yield') 
    coeff1, line1 = add_trendline(np.arange(nYear)-0.2, table['EY'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear)+0.2, table['DY'][-nYear:])
    ax[0].legend(['EY : '+str(np.around(coeff1[0],2))] ,loc="upper left")
    ax0.legend(['DY : '+str(np.around(coeff2[0],2))] ,loc="upper left", bbox_to_anchor=(0, 0.94))
    ax[0].plot(np.arange((10-nYear),10)-0.2, line1, '--', color='black', linewidth=3)
    ax0.plot(np.arange((10-nYear),10)+0.2, line2, '--', color='red', linewidth=3)
    
    
    ax[1].bar(np.arange(10)-0.2, table['EPS'], color='black', width=0.4, alpha=0.7)
    ax[1].bar(np.arange(10)+0.2, table['DPS'], color='red', width=0.4, alpha=0.7)
    ax[1].set_xticks(np.arange(0,10,1))
    ax[1].set_xticklabels(table.Year)
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('Amount per Share (Sen)')
    ax[1].set_title('Earning per Share vs Dividend per Share')
    coeff1, line1 = add_trendline(np.arange(nYear)-0.2, table['EPS'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear)+0.2, table['DPS'][-nYear:])
    ax[1].legend(['EPS : '+str(np.around(coeff1[0],2)),
                  'DPS : '+str(np.around(coeff2[0],2))],loc="upper left")
    ax[1].plot(np.arange((10-nYear),10)-0.2, line1, '--', color='black', linewidth=3)
    ax[1].plot(np.arange((10-nYear),10)+0.2, line2, '--', color='red', linewidth=3)
    
    
    fig3, ax = plt.subplots(1, 2, figsize=(20,6))
    fig3.patch.set_facecolor('white')
    ax0 = ax[0].twinx()
    ax[0].bar(np.arange(10)-0.2, table['Price'], color='black', width=0.4, alpha=0.7)
    ax0.bar(np.arange(10)+0.2, table['P/E'], color='red', width=0.4, alpha=0.7)
    ax[0].set_xticks(np.arange(0,10,1))
    ax[0].set_xticklabels(table.Year)
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Share Price (RM)')
    ax0.set_ylabel('Ratio')
    ax[0].set_title('Price vs P/E Ratio')
    coeff1, line1 = add_trendline(np.arange(nYear)-0.2, table['Price'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear)+0.2, table['P/E'][-nYear:])
    ax[0].legend(['Price : '+str(np.around(coeff1[0],2))] ,loc="upper left")
    ax0.legend(['P/E : '+str(np.around(coeff2[0],2))] ,loc="upper left", bbox_to_anchor=(0, 0.94))
    ax[0].plot(np.arange((10-nYear),10)-0.2, line1, '--', color='black', linewidth=3)
    ax0.plot(np.arange((10-nYear),10)+0.2, line2, '--', color='red', linewidth=3)
    
    
    ax1 = ax[1].twinx()
    ax[1].bar(np.arange(10)-0.2, table['ROE'], color='black', width=0.4, alpha=0.7)
    ax1.bar(np.arange(10)+0.2, table['D/E'], color='red', width=0.4, alpha=0.7)
    ax[1].set_xticks(np.arange(0,10,1))
    ax[1].set_xticklabels(table.Year)
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('Percentage (%)')
    ax1.set_ylabel('Ratio')
    ax[1].set_title('Return on Equity & D/E Ratio')
    coeff1, line1 = add_trendline(np.arange(nYear)-0.2, table['ROE'][-nYear:])
    coeff2, line2 = add_trendline(np.arange(nYear)+0.2, table['D/E'][-nYear:])
    ax[1].legend(['ROE : '+str(np.around(coeff1[0],2))] ,loc="upper left")
    ax1.legend(['D/E : '+str(np.around(coeff2[0],2))] ,loc="upper left", bbox_to_anchor=(0, 0.94))
    ax[1].plot(np.arange((10-nYear),10)-0.2, line1, '--', color='black', linewidth=3)
    ax1.plot(np.arange((10-nYear),10)+0.2, line2, '--', color='red', linewidth=3)
    
    
    return fig1, fig2, fig3