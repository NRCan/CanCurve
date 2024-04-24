'''
Created on Apr. 24, 2024

@author: cef

default style parameters for plots
'''

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#set teh styles
plt.style.use('default')
font_size=8
dpi=300
cm = 1 / 2.54

matplotlib.rc('font', **{'family' : 'serif','weight' : 'normal','size': font_size})
matplotlib.rc('legend',fontsize=font_size)
 
matplotlib.rcParams.update({
    'axes.titlesize':font_size+2,
    'axes.labelsize':font_size,
    'xtick.labelsize':font_size,
    'ytick.labelsize':font_size,
    'figure.titlesize':font_size+4,
    'figure.autolayout':False,
    #'figure.figsize':(18*cm,18*cm),#typical full-page textsize for Copernicus and wiley (with 4cm for caption)
    'legend.title_fontsize':'large',
    'text.usetex':False,
    })


#NRCan colormap
colors_default = ['#99B7B3', '#2B403F', '#DFECEB']
cmap_default = mcolors.ListedColormap(colors_default, name='NRCan_cmap')