'''
Created on Apr. 24, 2024

@author: cef

plotting functions
'''

#===============================================================================
# setup matplotlib
#===============================================================================
import matplotlib
#matplotlib.use('Qt5Agg') #sets the backend (case sensitive)
matplotlib.set_loglevel("info") #reduce logging level
import matplotlib.pyplot as plt

from cancurve.parameters_matplotlib import font_size #set custom styles


#===============================================================================
# imports
#===============================================================================
import os
import pandas as pd
import numpy as np

from .hp.logr import get_log_stream
from .hp.basic import view_web_df as view

#===============================================================================
# helper funcs----------
#===============================================================================
 

def get_slog(name, log):
    if log is None:
        log = get_log_stream()
        
    return log.getChild(name)


def plot_c00_costitems(df_raw,
                       figure=None,
                       fig_kwargs=dict(
                           figsize=(6,10)),
                       
                       log=None):
    """plot the cost items dataset"""
    
    log = get_slog('plot_c00', log)
    
    log.info(f'on {df_raw.shape}')
    
    """
    view(df_raw)
    """
    
    #===========================================================================
    # #data prep
    #===========================================================================
    ser = df_raw.drop('desc', axis=1).set_index(['group_code', 'story'], append=True).iloc[:, 0]
    
    #sum and pivot
    ser1 = ser.groupby(['group_code', 'story']).sum() #.unstack('group_code')
 
    
    
    #===========================================================================
    # plot
    #===========================================================================
    #figure default
    if figure is None:
        figure = plt.figure(**fig_kwargs)
        
    cmap = plt.cm.get_cmap('tab20')
    
                
    #create two axijs side by side 
    stories_l = ser1.index.unique('story').to_list()
    ax_d = dict(zip(stories_l, figure.subplots(nrows=1, ncols=len(stories_l), sharey=True)))
    
    for k0, ax in ax_d.items():
        gser = ser1.xs(k0, level='story') 
 
        jval=0
 
        for i, (k1, val) in enumerate(gser.items()):
             
            color=cmap(i * (1.0 / len(gser)))
            container = ax.bar(0.5,val, align='center', bottom=jval, width=0.75,color=color)            
            jval = val + jval
            
            #add the label
            ax.bar_label(container, labels = [f'{k1} ({val:,.0f})'], label_type='center')
            
        #add the meta
        ax.set_xlim(0, 1)

        #=======================================================================
        # txt = f'RCV sum: {gser.sum():,.0f}'
        # ax.text(0.5, 1.0, txt, transform=ax.transAxes, 
        #         va='top', ha='center', 
        #         #fontsize=8, color='black',
        #         bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=0.0,alpha=0.5 ),
        #         )
        #=======================================================================
        ax.set_title(f'story \'{k0}\''+f'\nRCV sum: {gser.sum():,.0f}')
            
    #===========================================================================
    # post
    #===========================================================================
    # Clean up x-axis labels so only the 'k0' is shown
    for k0, ax in ax_d.items():
        ax.set_xticks([])  # Set a single tick at the center of the bars
        ax.set_xticklabels([])  # Set the label to the 'story' name
        #ax.set_xlabel(f'story \'{k0}\'')
        
        #left-most
        if k0==stories_l[0]:
            ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
            ax.set_ylabel('Replacement Cost (Sum)')
            
        else:
            ax.spines['left'].set_visible(False)
            ax.set_yticks([])
    
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
            
 


    figure.suptitle('Cost-item totals')
    figure.subplots_adjust(hspace=0, wspace=0)
 
 
        
        
    return figure
"""
plt.show()
"""
        
        
        
        
        
        
        
        
        