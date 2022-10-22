'''
@File: CP TO CP
@Author: yezhongsheng
@Email: yezhongsheng@silanic.cn
@Time: 2022/09/03
@Decribe: Find similar defect shaped wafers.
'''

import numpy
import pandas
import seaborn as sns
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk


def calc_corr(a, b):
    # Correlation efficient calculas
    if len(a)*len(b) == 0:
        return 0
    else:
        a_avg = sum(a)/len(a)
        b_avg = sum(b)/len(b)
        cov_ab =  sum([(x-a_avg)*(y-b_avg) for x,y in zip(a,b)])
        sq = sum([(x-a_avg)**2 for x in a])*sum([(x-b_avg)**2 for x in b])
    if sq == 0:
        return 0
    else:
        return cov_ab/(sq**0.5)


def find_result(dict_hash, str_scribe, float_limit):
    # Find correlated result to dictionary
    dict_result = {}
    list_input = dict_hash[str_scribe]
    if len(list_input)==0:
        float_ratio = 0
    else:
        float_ratio = sum(list_input)/len(list_input)
    def func_sub(list_row):
        if len(list_row)<=len(list_input):
            list_temp = list_input[:len(list_row)]
            float_corr = calc_corr(list_temp,list_row)
        else:
            list_temp = list_row[:len(list_input)]
            float_corr = calc_corr(list_temp,list_input)
        return float_corr
    for i in dict_hash:
        list_row = dict_hash[i]
        if len(list_row) > 0:
            float_diff = abs((sum(list_row)/len(list_row)) - float_ratio)
            float_corr = func_sub(list_row)
            if (float_corr > float_limit)  & (float_diff<0.1):
                dict_result[i] = [float_corr, float_diff]
    return dict_result


def paint_result(dict_result, str_save):
    # Paint wafer color in dict hash.
    # Color config file
    ColorTable = pandas.read_excel(r"\\Jkfs\营运系统\器件与电性测试工程部\系统内跨部门工作区\项目类\EDA\以图搜图\ColorTable.XLSX")
    ColoRlist = numpy.array(ColorTable)
    ColoRlist=ColoRlist.tolist()
    new_blues=ColoRlist
    os.chdir(r'\\Jkfs\营运系统\器件与电性测试工程部\系统内跨部门工作区\项目类\EDA\以图搜图')
    for i in dict_result: 
        Sales = pandas.read_csv(i)
        Summary = Sales.pivot_table(index = 'DIE_X', columns = 'DIE_Y', values = 'SOFTBIN', aggfunc = np.sum)
        ListMap = numpy.array(Summary)
        ListMap = ListMap.tolist()
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
        fig_name = i+'.png'
        fig_path = str_save + '/' + fig_name
        heatmap = ax.get_figure()
        heatmap.savefig(fig_path, bbox_inches='tight',dpi = 400)
        plt.clf()
        plt.close()


if __name__ == '__main__':
    window = Tk()
    window.title("以图搜图 v1.0")
    window.geometry('1000x600')

    # 第一行
    label_1 = Label(window, text='输入硅圆SCRIBE_ID编号，搜索相似缺陷纹理硅圆图片：')
    label_1.grid(column=0,row=0)
    entry_scribe = Entry(window, width=25)
    entry_scribe.grid(column=1,row=0)

    # 第二行
    label_2 = Label(window, text='搜索范围时限长度设置：')
    label_2.grid(column=0,row=1)
    combo_month = Combobox(window, width=23)
    combo_month['values'] = ('一个月内','三个月内','六个月内','九个月内','十二个月内')
    combo_month.current(1)
    combo_month.grid(column=1, row=1)

    # 搜索按钮
    def func_click():
        str_click = Label(window, text='正在搜索' + combo_month.get() + entry_scribe.get() + '的相似图片......', cursor='circle')
        str_click.grid(column=0,row=5)

    button_search = Button(window, text='搜索', command=func_click)
    button_search.grid(column=2,row=0)

    #保存按钮
    def func_save():
        str_click_save = Label(window, text='保存路径：', cursor='circle')
        str_click_save.grid(column=0,row=4)
        entry_value = StringVar()
        entry_save = Entry(window, textvariable=entry_value, width=25)
        entry_save.grid(column=1,row=4)
        def func_file():
            str_file = filedialog.askdirectory()
            entry_value.set(str_file)
        button_search = Button(window, text='选择路径', command=func_file)
        button_search.grid(column=2,row=4)
        global str_save
        str_save = entry_save.get()

    chk_state = BooleanVar()
    chk_state.set(False) # Set check state
    chk = Checkbutton(window, text="是否保存搜索结果图片", cursor='circle', var=chk_state, command=func_save)
    
    chk.grid(column=0, row=3)

    window.mainloop()
    
    dict_hash = numpy.load(r'\\Jkfs\营运系统\器件与电性测试工程部\系统内跨部门工作区\项目类\EDA\以图搜图\dict_hash.npy',allow_pickle=True).item()
    dict_result = find_result(dict_hash, entry_scribe.get())
    paint_result(dict_result, str_save)
    for png in os.listdir(str_save):
        img_temp = Image.open(png)
        img_png = ImageTk.PhotoImage(img_temp)
        label_img = Label(window, image=img_png)
        label_img.pack()
