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

from cancurve.parameters_matplotlib import font_size, cmap_default #set custom styles


#===============================================================================
# imports
#===============================================================================
import os, itertools, math
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
    """plot the cost items dataset as bar charts"""
    
    log = get_slog('plot_c00_costitems', log)
    
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
        
def plot_c00_DRF(df_raw,
                       figure=None,
                       fig_kwargs=dict(
                           figsize=(10,10),
                           tight_layout=True,
                           ),
                       
                       log=None):
    """matrix line plots"""
    
    log = get_slog('plot_c00_DRF', log)
    
    log.info(f'on {df_raw.shape}')
        
    
    """
    view(df_raw)
    ax.clear()
    """
    
    #===========================================================================
    # #data prep
    #===========================================================================
    
 
    #===========================================================================
    # plot
    #===========================================================================
    #figure default
    if figure is None:
        figure = plt.figure(**fig_kwargs)
        
    
    cat_l = df_raw.index.unique('cat')
    nrows = math.ceil(math.sqrt(len(cat_l)))  # Find smallest square layout accommodating the cats
    ncols = math.ceil(len(cat_l) / nrows)
    
    #create a figure with NxN subplots. each cat_l has a unique subplot (there will be some empty subplots)
    #return a dictionary keyed by 'cat' values
    ax_ar  = figure.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    #ax_d = dict(zip(cat_l, ax_ar.flat))
    ax_d = dict()
    for cat in cat_l:
        ax_d[cat] = dict(zip(cat_l, ax_ar.flat))[cat]
 
    
    #cmap = plt.cm.get_cmap('tab20')
    
    for i, (k0, gdf) in enumerate(df_raw.groupby(level='cat')):
        ax = ax_d[k0]
        #color = cmap(i*(1.0/len(cat_l)))
        #markers = itertools.cycle(plt.Line2D.filled_markers)
        
        #plot mean
        yar, xar = gdf.mean().values, gdf.mean().index.values
        ax.plot(xar, yar, color='black', linestyle='dashed', marker=None, linewidth=1.0,
                label=f'mean')
        
        #plot spagetti
        for j, (k1, row) in enumerate(gdf.iterrows()):
            xar, yar = row.index.values, row.values
            ax.plot(xar, yar, 
                    #color=color, marker=next(markers), 
                    linewidth=0.5, markersize=3, 
                    #alpha=0.5,
                    label=k1[1]
                    )
            
        #post
        ax.set_title(k0, y=0.8,
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=0.0,alpha=0.75 ),
                     )
        
        txt = f'sel count: {len(gdf)}'
        ax.text(.95, 0.05, txt, transform=ax.transAxes, 
                va='bottom', ha='right', 
                fontsize=6, color='black',
                #bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=0.0,alpha=0.5 ),
                )
        
        #ax.legend(fontsize=font_size-4)
            
        
 
    #===========================================================================
    # post
    #===========================================================================
    #hide empties
    for ax in ax_ar.flat:
        if not ax.has_data():  
            ax.set_visible(False)
        
 
    
 
    
    figure.suptitle('Depth-Replacement-Factors'+'\nby category')
    figure.supxlabel('depth (m)')
    figure.supylabel('replacement-factor')
    #figure.subplots_adjust(hspace=0, wspace=0)
 
 
        
        
    return figure
"""
plt.show()
"""

def plot_c01_depth_rcv(df_raw,
                       figure=None,
                       fig_kwargs=dict(
                           #figsize=(10,10),
                           tight_layout=True,
                           ),
                       
                       log=None):
    """plot the cost items dataset"""
    
    log = get_slog('plot_c01_depth_rcv', log)
    
    log.info(f'on {df_raw.shape}')
    
    
    #===========================================================================
    # #data prep
    #===========================================================================
    """
    view(df_raw)
    """
 
    #===========================================================================
    # setup figure
    #===========================================================================
    cmap = plt.cm.get_cmap('tab20')
    #figure default
    if figure is None:
        figure = plt.figure(**fig_kwargs)
    
    story_l = df_raw.index.unique('story').tolist()
    ax_ar  = figure.subplots(ncols=1, nrows=len(story_l), sharey=True, sharex=True)
    ax_d = dict(zip(story_l, ax_ar.flat))
    
    #===========================================================================
    # loop and plot
    #===========================================================================
    for k0, gdf in df_raw.groupby(level='story'):
        log.debug(k0)
        ax = ax_d[k0]
        
        #create stacked area plot (one polygon per cat.sum())
        gdf1 = gdf.groupby(level='cat').sum()
        
        """
             -0.9  -0.46  0.0        0.03  ...      1.22      1.52      1.83       2.7
        cat                                ...                                        
        CAB   0.0    0.0  0.0      0.0000  ...   9335.20   9335.20   9335.20   9335.20
        DOR   0.0    0.0  0.0      0.0000  ...   6161.00   6161.00   6161.00   6161.00
        DRY   0.0    0.0  0.0   8944.3525  ...  35777.41  35777.41  35777.41  35777.41
        
        ax.clear()
        """
        gdf1.T.plot.area(ax=ax, stacked=True, legend=False,
                         cmap=cmap)
        #
        
        #add legend
        ax.legend(ncols=6, title=f'story {k0}', fontsize=6, loc=2)
        
        #=======================================================================
        # ax.set_title(f'story {k0}', 
        #              #y=0.8,
        #              #bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=0.0,alpha=0.75 ),
        #              )
        #=======================================================================
        
        ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
        
    #===========================================================================
    # post
    #===========================================================================
    figure.suptitle('Depth-RCV'+'\nby story')
    figure.supxlabel('depth (m)')
    figure.supylabel('replacement cost value')
        
        
        
        
        
    return figure
"""
plt.show()
"""
        
def plot_c02_ddf(df_raw,
                       figure=None,
                       fig_kwargs=dict(
                           #figsize=(10,10),
                           tight_layout=True,
                           ),
                       
                       cmap=None,
                       
                       log=None):
    """plot the cost items dataset"""
    #===========================================================================
    # setup
    #===========================================================================
    log = get_slog('plot_c02_ddf', log)
    
    log.info(f'on {df_raw.shape}')  
    
    if cmap is None:
        cmap = cmap_default
    
    #===========================================================================
    # dataprep
    #===========================================================================
    df = df_raw.copy()
    bx = df.columns=='combined'
    assert bx.sum()==1
    
 
    
    #===========================================================================
    # setup figure
    #===========================================================================
 
    #figure default
    if figure is None:
        figure = plt.figure(**fig_kwargs)
        
    ax = figure.subplots()
    
    #===========================================================================
    # plot 
    #===========================================================================

    #stories
    df.loc[:, ~bx].plot.area(ax=ax, stacked=True, legend=False,cmap=cmap, xlabel='')
    
    #total
    xar, yar = df['combined'].index.values, df['combined'].values
    ax.plot(xar, yar, color='black', linestyle='dashed', linewidth=2, label='combined')
    
    #===========================================================================
    # post
    #===========================================================================
    ax.legend()
    
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:.2f}'))
    
    figure.suptitle('Depth-Damage-Function')
    figure.supxlabel('depth (m)')
    figure.supylabel('total replacement cost')
    
    
    return figure
"""
ax.clear()
plt.show()
"""

        
        