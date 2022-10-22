# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:29:05 2022

@author: luoyingying
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 14:45:58 2022

@author: luoyingying
"""
#%%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
#%%

#%%
ColorTable = pd.read_excel(r"C:\Users\luoyingying\AppData\Roaming\E-Mobile\Downloads\ColorTable.XLSX")
ColoRlist = np.array(ColorTable)
ColoRlist=ColoRlist.tolist()
new_blues=ColoRlist
    #%%
# 读取数据
#Sales = pd.read_excel(r"E:\1.0 YEandEDA\1.1 EDAProjectDevelop\CPOverlay\G0101.xlsx")
Sales = pd.read_excel(r"C:\Users\luoyingying\AppData\Roaming\E-Mobile\Downloads\G0113A.xlsx")
#%%
Summary = Sales.pivot_table(index = 'DIE_X', columns = 'DIE_Y', values = 'HARDBIN', aggfunc = np.sum)
#%%

ListMap = np.array(Summary)
ListMap=ListMap.tolist()
#%%
plt.figure(dpi=40,figsize=(15,15))
#%%
sns.set(style='white',rc = {'figure.figsize':(15,15)})
#%%
ax = sns.heatmap(ListMap,
                 cmap = new_blues, # 指定填充色
                 linewidths = 0.1, # 设置每个单元格边框的宽度
                 xticklabels=False,
                 yticklabels=False,
                 ax=None,
                 cbar=False,
                 cbar_ax=None)
#%%
filepath = "C:\\Users\\luoyingying\\AppData\\Roaming\\E-Mobile\\Downloads"
fig_name = 'scatterplotG0113A1test99.png'



fig_path = filepath + '/' + fig_name
heatmap = ax.get_figure()
heatmap.savefig(fig_path, bbox_inches='tight',dpi = 400)



#%%

