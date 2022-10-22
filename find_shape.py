from gettext import find
import pandas
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os



# Line search
dict_direction = {}
dict_direction[0] = [[j,0] for j in range(10)]
dict_direction[1] = [[-j,0] for j in range(10)]
dict_direction[2] = [[0,j] for j in range(10)]
dict_direction[3] = [[0,-j] for j in range(10)]
dict_direction[4] = [[j,j] for j in range(10)]
dict_direction[5] = [[j,-j] for j in range(10)]
dict_direction[6] = [[-j,-j] for j in range(10)]
dict_direction[7] = [[-j,j] for j in range(10)]

def find_line(data_defect):
    list_coor = []
    for index,i in data_defect.iterrows():
        list_coor.append([i['INITIAL_DIE_X'],i['INITIAL_DIE_Y']])
    list_result = []
    for i in list_coor:
        list_temp = [[i[0]+1,i[1]],[i[0]-1,i[1]],[i[0],i[1]+1],[i[0],i[1]-1],[i[0]+1,i[1]+1],[i[0]+1,i[1]-1],[i[0]-1,i[1]-1],[i[0]-1,i[1]+1]]
        for j in range(len(list_temp)):
            if list_temp[j] in list_coor:
                list_line = [[x[0]+i[0],x[1]+i[1]] for x in dict_direction[j]]
                list_join = [k for k in list_line if k in list_coor]
                if len(list_join)>=10:
                    int_side = 0
                    for i in list_join:
                        list_side = [[i[0]+1,i[1]],[i[0]-1,i[1]],[i[0],i[1]+1],[i[0],i[1]-1],[i[0]+1,i[1]+1],[i[0]+1,i[1]-1],[i[0]-1,i[1]-1],[i[0]-1,i[1]+1]]
                        int_side += len([x for x in list_side if x in list_coor])
                    if int_side <= 40:
                        print(list_join)
                        list_result.append(list_join)
    return list_result


# Fixed site
def find_site(data_defect):
    data_group = data_defect.groupby(['SITENUM','INITIAL_DIE_Y']).agg({'PRODUCT':'count'})
    data_result = data_group[data_group['PRODUCT']>3]
    list_result = []
    
    for i in data_result.index:
        for index,row in data_defect[(data_defect['SITENUM']==i[0]) and (data_defect['INITIAL_DIE_Y']==i[1])]:
            list_result.append[row['INITIAL_DIE_X'],row['INITIAL_DIE_Y']]
    return list_result


# Find square
dict_fail = {}
dict_fail[0] = [[0,0],[1,0],[1,1],[0,1]]
dict_fail[1] = [[0,0],[1,0],[1,-1],[0,-1]]
dict_fail[2] = [[0,0],[0,-1],[-1,-1],[-1,0]]
dict_fail[3] = [[0,0],[0,1],[-1,1],[-1,0]]
def find_square(data_defect):
    list_fail = []
    list_defect = []
    list_return = []
    for index,i in data_defect.iterrows():
        list_fail.append([i['INITIAL_DIE_X'],i['INITIAL_DIE_Y']])
        list_defect.append([i['INITIAL_DIE_X'],i['INITIAL_DIE_Y'],i['SOFTBIN']])
    # Find four square matrix shape.
    for i in list_defect:
        if i[2] == 11 or i[2] == 12:
            list_temp = [[i[0]+1,i[1]+1],[i[0]+1,i[1]-1],[i[0]-1,i[1]-1],[i[0]-1,i[1]+1]]
            for j in range(len(list_temp)):
                if list_temp[j] in list_fail:
                    list_dict = [[i[0]+m[0],i[1]+m[1]] for m in dict_fail[j]]
                    list_result = []
                    int_count = 0
                    for x in list_defect:
                        if [x[0],x[1]] in list_dict:
                            list_result.append(x)
                            if x[2] == 11 or x[2] == 12:
                                int_count = int_count + 1
                    if len(list_result) == 4 and int_count >= 3:
                        list_return.append(list_dict)
    return list_return


# Find edge shaped wafer.
def find_edge(data_defect):
    list_input = []
    list_cont = []
    list_result = []
    for index,row in data_defect.iterrows():
        list_input.append([row['INITIAL_DIE_X'],row['INITIAL_DIE_Y']])
        if row['SOFTBIN'] == 10:
            list_cont.append([row['INITIAL_DIE_X'],row['INITIAL_DIE_Y']])
        # symmetric judgement.
    list_cont_x = []
    for i in list_cont:
        if ([i[0]-1,i[1]] not in list_input) or ([i[0]+1,i[1]] not in list_input):
            list_cont_x.append(i[0])
    for i in list_cont:
        if list_cont_x.count(i[0]) >= 4:
            list_result.append(i)
    return list_result

# Paint color
def paint_color(data_wafer, str_text):
    ColorTable = pd.read_excel(r"C:\Users\luoyingying\AppData\Roaming\E-Mobile\Downloads\ColorTable.XLSX")
    ColoRlist = np.array(ColorTable)
    ColoRlist=ColoRlist.tolist()
    new_blues=ColoRlist
    # 读取数据
    #Sales = pd.read_excel(r"E:\1.0 YEandEDA\1.1 EDAProjectDevelop\CPOverlay\G0101.xlsx")
    #list_path = ['wafer_radio/A150437_14']
    #for i in list_path: 
    Sales = data_wafer

    Summary = Sales.pivot_table(index = 'DIE_X', columns = 'DIE_Y', values = 'SOFTBIN', aggfunc = np.sum)
    

    ListMap = np.array(Summary)
    ListMap=ListMap.tolist()
    
    plt.figure(dpi=40,figsize=(15,15))
    
    sns.set(style='white',rc = {'figure.figsize':(15,15)})
    
    ax = sns.heatmap(ListMap,
                    cmap = new_blues, # 指定填充色
                    linewidths = 0.1, # 设置每个单元格边框的宽度
                    xticklabels=False,
                    yticklabels=False,
                    ax=None,
                    cbar=False,
                    cbar_ax=None)
    plt.text(str_text)
    filepath = "D:/special_shape"
    fig_name = str_file+'.png'
    fig_path = filepath + '/' + fig_name
    heatmap = ax.get_figure()
    
    heatmap.savefig(fig_path, bbox_inches='tight',dpi = 400)
    plt.clf()
    plt.close()


if __name__ == '__main__':
    os.chdir(r'D:\0905')
    list_file = os.listdir()[0:50]
    for str_file in list_file:
        data_wafer = pandas.read_csv(str_file)
        data_defect = data_wafer[data_wafer['SOFTBIN']!=1]
        dict_shape = {
            'line': find_line(data_defect),
            'site': find_site(data_defect),
            'square': find_square(data_defect),
            'edge': find_edge(data_defect)
        }
        for i in dict_shape:
            if dict_shape[i]:
                paint_color(data_wafer,str(i)+':'+str(dict_shape[i]))