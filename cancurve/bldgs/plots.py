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
 
import matplotlib.colors as mcolors
import matplotlib.patches as patches


import os, itertools, math
import pandas as pd
import numpy as np

from cancurve.hp.logr import get_log_stream
from cancurve.hp.basic import view_web_df as view

#===============================================================================
# helper funcs----------
#===============================================================================


def get_large_cmap():
        #setup colors
    bcolors = list(mcolors.CSS4_COLORS.values())
    np.random.shuffle(bcolors)
    return mcolors.ListedColormap(bcolors)
    
    

def get_slog(name, log):
    if log is None:
        log = get_log_stream()
        
    return log.getChild(name)


def plot_c00_costitems(df_raw,
                       figure=None,
                       fig_kwargs=dict(
                           figsize=(6,10)),
                       ylabel='cost ($)',
                       
                       log=None):
    """plot the cost items dataset as bar charts
    
    params
    --------
    pd.DataFrame
        cost-items dataframe
    
    """
    
    log = get_slog('plot_c00_costitems', log)
    
    log.info(f'on {df_raw.shape}')
    
    """
    view(df_raw)
    """
    
    #===========================================================================
    # #data prep
    #===========================================================================
    ser = df_raw.drop('desc', axis=1).set_index(['group_code', 'story', 'drf_intersect'], append=True).iloc[:, 0]
    
    #sum and pivot
    ser1 = ser.groupby(['group_code', 'story', 'drf_intersect']).sum() #.unstack('group_code')
 
    log.debug(f'groupby.sum to {len(ser1)}')
    
    #===========================================================================
    # plot
    #===========================================================================
    #figure default
    if figure is None:
        figure = plt.figure('c00_costitems', **fig_kwargs)
        
    

    
    cmap = matplotlib.colormaps.get_cmap('tab20')
    #cmap = get_large_cmap()
    gc_l = ser1.index.unique('group_code').tolist()
    color_v = [cmap(i * (1.0 / len(gc_l))) for i,k in enumerate(gc_l)]
    np.random.shuffle(color_v)
    color_d = dict(zip(gc_l, color_v))
    log.debug(f'built colors for {len(color_d)} \'group_code\'')
    
    #iterator for small labels
    ha_offset=itertools.cycle([+20, -20])
    ha_l = itertools.cycle(['left', 'right'])
 
                
    #create two axijs side by side 
    story_l = ser1.index.unique('story').to_list()
    log.debug(f'on storys: {story_l}')
    
    # Create subplots based on the number of stories
    if len(story_l) == 1:
        # When there's only one story, subplots returns a single Axes object
        ax_d = {story_l[0]: figure.subplots(nrows=1, ncols=1, sharey=True)}
    else:
        # When there are multiple stories, subplots returns a list of Axes
        ax_list = figure.subplots(nrows=1, ncols=len(story_l), sharey=True)
        # Ensure ax_list is iterable, even if it contains just one element
        ax_d = dict(zip(story_l, ax_list))
    
    
    ymax = max(ser1.groupby('story').sum())
    
    log.debug(f'plotting on {len(ax_d)}')
    for k0, ax in ax_d.items():
        gser = ser1.xs(k0, level='story') 
 
        jval=0
 
        #=======================================================================
        # loop and plot each rectangle bar
        #=======================================================================
        for i, ((k1,present), val) in enumerate(gser.items()):
             
            #===================================================================
            # plot the bar
            #===================================================================
            pkwargs = dict(
                align='center', bottom=jval, width=0.75,
                color=color_d[k1], hatch=None, edgecolor=None,
                alpha=0.9)
            
            #missing hatch
            if not present:
                pkwargs.update(dict(hatch='/', edgecolor='red', alpha=1.0))
                
 
            container = ax.bar(0.5,val, **pkwargs)            
            jval = val + jval
            
            
                
            #===================================================================
            # #add the label
            #===================================================================
            
            if not present: group_name=f'{k1} (miss)'
            else: group_name=k1
            
            """hiding labels on skinny bars""" 
            for rect in container:height=rect.get_height() #pull out first rectangle                
                
            #offset tiny bars
            if height < ymax*0.005:
                log.warning(f'no label added for {group_name} (too small)')
            elif height < ymax*0.02:
                xy = (rect.get_x() + rect.get_width() / 2, rect.get_y()+height/2)
                ax.annotate(group_name,
                    #f'{k1} {100*(val/gser.sum()):.2f}% ({val:,.0f})',
                    xy=xy,
                    xytext=(next(ha_offset), 0),  # Use offset for popping out
                    textcoords="offset points",
                    #fontsize=6,
                    xycoords='data',
                    ha=next(ha_l), va='bottom',
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
            else:
                ax.bar_label(container, labels = [f'{group_name}: {100*(val/gser.sum()):.0f}% ({val:,.0f})'], label_type='center')
                
 
            
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
        txt = f'storey \'{k0}\''+f'\ncost sum: {gser.sum():,.0f}'
        if np.any(np.invert(gser.index.get_level_values('drf_intersect'))):
            txt+=f'\nmissing cost sum: {gser.xs(False, level=1).sum():,.0f}'                    
            
        ax.set_title(txt)
            
        
    #===========================================================================
    # post
    #===========================================================================
    # Clean up x-axis labels so only the 'k0' is shown
    for k0, ax in ax_d.items():
        ax.set_xticks([])  # Set a single tick at the center of the bars
        ax.set_xticklabels([])  # Set the label to the 'story' name
 
        
        #left-most
        if k0==story_l[0]:
            ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
            ax.set_ylabel(ylabel)
            
        else:
            ax.spines['left'].set_visible(False)
            ax.set_yticks([])
    
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
    #===========================================================================
    # legend
    #===========================================================================
    hatch_patch = patches.Patch(facecolor='white', linewidth=2, edgecolor='red',hatch='/',  label='missing in DRF')
    
    figure.legend(handles=[hatch_patch], labels=['missing in DRF'], loc=4)
            
 


    figure.suptitle('Cost-Item Totals')
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
                       
                       log=None, 
                       ylabel='replacement-factor',
                       ):
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
        figure = plt.figure('c00_DRF', **fig_kwargs)
        
    
    cat_l = df_raw.index.unique('category')
    nrows = math.ceil(math.sqrt(len(cat_l)))  # Find smallest square layout accommodating the cats
    ncols = math.ceil(len(cat_l) / nrows)
    
    #create a figure with NxN subplots. each cat_l has a unique subplot (there will be some empty subplots)
    #return a dictionary keyed by 'category' values
    ax_ar  = figure.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    #ax_d = dict(zip(cat_l, ax_ar.flat))
    ax_d = dict()
    for cat in cat_l:
        ax_d[cat] = dict(zip(cat_l, ax_ar.flat))[cat]
 
    
    #cmap = matplotlib.colormaps.get_cmap('tab20')
    
    for i, (k0, gdf) in enumerate(df_raw.groupby(level='category')):
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
        
 
    
 
    
    figure.suptitle('Depth-Replacement-Factors'+'\nby Category')
    figure.supxlabel('depth (%s)'%df_raw.columns.name)
    figure.supylabel(ylabel)
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
                       expo_units=None, 
                       ylabel='cost ($)',
                       
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
 
    
    cmap = matplotlib.colormaps.get_cmap('tab20')
    #figure default
    if figure is None:
        figure = plt.figure('c01_depth_rcv', **fig_kwargs)
    
    story_l = df_raw.index.unique('story').tolist()
    ax_ar  = figure.subplots(ncols=1, nrows=len(story_l), sharey=True, sharex=True)
    
    #convert to dictionary
    if isinstance(ax_ar, np.ndarray):
        ax_d = dict(zip(story_l, ax_ar.flat))
    else:
        ax_d = {story_l[0]:ax_ar}
 
    
    #===========================================================================
    # loop and plot
    #===========================================================================
    for k0, gdf in df_raw.groupby(level='story'):
        log.debug(f'plotting storey {k0}')
        ax = ax_d[k0]
        
        #create stacked area plot (one polygon per cat.sum())
        gdf1 = gdf.groupby(level='category').sum()
        
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
        ax.legend(ncols=6, title=f'storey {k0}', fontsize=6, loc=2)
        
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
    ax.xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:.1f}'))
    
    figure.suptitle('Depth-Cost'+'\nby Storey')
    
    xlab = 'depth'
    if not expo_units is None:
        xlab = xlab+' (%s)'%expo_units
    figure.supxlabel(xlab)
    
    figure.supylabel(ylabel)
    
    log.debug(f'finished')
        
        
        
        
        
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
                       ylabel='damage',
                       expo_units=None,
                       
                       log=None):
    """plot depth-damage per-story"""
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
    
 
    #try ane rename columns (probably a better way to do this)
    try:
        df = df.rename(columns={'main':'storey: 0', 'base':'storey: -1'})
    except Exception as e:
        log.error(f'failed to rename columns w/\n    {e}')
    
    #===========================================================================
    # setup figure
    #===========================================================================
 
    #figure default
    if figure is None:
        figure = plt.figure('c02_ddf', **fig_kwargs)
        
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
    
    figure.suptitle('Depth-Damage Function')
    
    xlab = 'depth'
    if not expo_units is None:
        xlab = xlab+' (%s)'%expo_units
    figure.supxlabel(xlab)

    figure.supylabel(ylabel)
    
    
    return figure
"""
ax.clear()
plt.show()
"""

        
        