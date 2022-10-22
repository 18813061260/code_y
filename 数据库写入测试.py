# -*- coding: utf-8 -*-
"""
Created on Wed May 11 19:48:02 2022

@author: luoyingying
"""


import numpy as np
from scipy import signal
import xlrd
import pandas as pd 
import cv2
import operator
import math
import random

from matplotlib import pyplot as plt
import time
import cx_Oracle #连接DB
import re  #正则表达式
import os #与文件夹相关
import datetime
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
from keras.models import load_model
#%%

SQL_GET_CP_WAFER_SUM_DATA = """
SELECT 
PRODUCT,     
LOT,       
WAFER,                
CP_TYPE,              
CP_TEST_PROG,             
to_char(MEAS_TIME,'YYYY-MM-DD HH:mm:ss') MEAS_TIME,  
to_char(MEAS_TIME,'YYYYMMDD-HHmmss')TIME,    
GOOD_DIE_COUNT,   
TOTAL_DIE_COUNT,  
ORIGINAL_WAFER_NOTCH,     
YIELD，                  
GROSS_DIE_COUNT,          
MAP_DATA,
WAFER_NO,
CORR_LOT,
SCRIBE_ID             
FROM CP_WAFER_SUM 
WHERE 1 = 1
AND meas_time >=to_date(:TIME_START,'yyyyMMddHH24MISS')
AND meas_time <=to_date(:TIME_END,'yyyyMMddHH24MISS')
and YIELD >= :YIELD_MIN
and YIELD <= :YIELD_MAX
and TOTAL_DIE_COUNT>=GROSS_DIE_COUNT 
"""

#%%
# recordsDB = {}
# # for i in range(len(OutPut["uint_key"])):
#     # recordsDB["product"] = None
#     # recordsDB["lot"] = None
#     # recordsDB["wafer"] = None
#     # recordsDB["cp_type"] = None
#     # recordsDB["cp_test_prog"] = None
#     # recordsDB["pattern_name"] = None
#     # recordsDB["reliability"] = None  
    
# recordsDB["product"] = 'Y0099A'
# recordsDB["lot"] = 'A220667.004'
# recordsDB["wafer"] = 'A220667.004#01'
# recordsDB["cp_type"] = 'Y0099A-TK-01'
# recordsDB["cp_test_prog"] = 'Y0099A-TK-01'
# recordsDB["pattern_name"] = 'CenterRadio'
# recordsDB["reliability"] = '0.9'
# recordsDB["update_time"] =  datetime.datetime.now()
# recordsDB["wafer_no"] = '03'
# recordsDB["corr_lot"] = 'A220667'
# recordsDB["scribe_id"] ='A220667_25'
# recordsDB["meas_time"] = '2022-04-13 08:04:47'
#%%
SQL_CP_MAP_SSA= """
insert into CP_MAP_SSA
(PRODUCT,LOT,WAFER, CP_TYPE,CP_TEST_PROG,PATTERN_NAME,RELIABILITY,UPDATE_TIME,WAFER_NO,CORR_LOT,SCRIBE_ID,MEAS_TIME)
VALUES
(
:PRODUCT, 
:LOT, 
:WAFER, 
:CP_TYPE,
:CP_TEST_PROG,
:PATTERN_NAME,
:RELIABILITY,
:UPDATE_TIME,
:WAFER_NO,
:CORR_LOT,
:SCRIBE_ID,
:MEAS_TIME
)
"""

#%%
SQL_GET_CP_BIN_INFO_DATA = """
select 
distinct PRODUCT,
BIN_NAME，
BIN_TYPE 
from CP_WAFER_BIN_SUM
"""

#%%
    #连接DB    
conn = cx_Oracle.connect('EDA/JkEdaTest#2022@192.168.6.149/jktedadb')#这里的顺序是用户名/密码@oracleserver的ip地址/数据库名字
cur = conn.cursor()

#data = sourcedb.execute(config_sql.SQL_GET_CP_WAFER_SUM_DATA,YIELD_MIN=config.yield_min,YIELD_MAX=config.yield_max,TIME_START=sLastDataTime,TIME_END=sMaxDataTime)
data = cur.execute(SQL_GET_CP_WAFER_SUM_DATA,YIELD_MIN=0,YIELD_MAX=100,TIME_START='20220413000000',TIME_END='20220414000000')

records = {}#存图的路径
records["uint_key"] = []
records["map_data"] = []

OutPut = {}#存图的路径
OutPut["uint_key"] = []
OutPut["Value"] = []
for row in data:
    print(row)
    records["uint_key"].append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]])
    
    OutPut["uint_key"].append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[13],row[14],row[15]])
    # #text  =  json.loads(row[12])
    # #records["map_data"].append(row[10].read())
    text = row[12].read()   #'str' object has no attribute 'read'
    records["map_data"].append(text)

bin_info = cur.execute(SQL_GET_CP_BIN_INFO_DATA).fetchall()   #获取每片wafer bin info

waferbin_records = []
for row in bin_info:
    waferbin_records.append([row[0],row[1],row[2]])
   # cur.close()
   # conn.commit()
   # conn.close()
#print(len(waferbin_records))

###############################################################################
waferbin_records = np.array(waferbin_records) #转成numpy，方便拿出某一行


bin_need = waferbin_records[waferbin_records[:,0]==records["uint_key"][0][0]]
#取出所有的Goodbin,画图呈现绿色
good_bin = bin_need[bin_need[:,2]=='G'][:,[1,2]]
MAP_data_str = records["map_data"]
# 处理数据
cur.close()
conn.commit()
conn.close()
#%%    
for map_index in range(len(records["uint_key"])):
    MAP_data_list = MAP_data_str[map_index].replace('\n', ',').replace('\r', ',')  #将换行符替换成逗号
    MAP_data_list = MAP_data_list[0:-1]#去掉最后一个逗号
    MAP_data_list = re.split(r'[\s\,]+', MAP_data_list)
    MAP_data_board = list(map(lambda x:int(x),MAP_data_list)) #将str变成int
    #获取需要的map数据
    #MAP_data   # ['diex','diey','ini_diex','ini_diey','value','hardbin','softbin','sitenum']
    if len(MAP_data_board)%8 == 0:
        MAP_data = np.array(MAP_data_board).reshape(int(len(MAP_data_board)/8),8)
    elif len(MAP_data_board)%7 == 0:
        MAP_data = np.array(MAP_data_board).reshape(int(len(MAP_data_board)/7),7)
    else:
        print("MAP_data in CP_WAFER_SUM info not correct")  #后期换成log写入文档
    bin_sort = sorted([(np.sum(MAP_data[:,6]==i),i) for i in set(MAP_data[:,6])])  #(count,bin_name)
    bin_max = bin_sort[-1][-1]  
    MAP_data_need = MAP_data[:,[0,1,6]]
    #转化成map
    max_x = max(MAP_data[:,0])
    max_y = max(MAP_data[:,1]) 
    cp_pattern = np.zeros((max_x,max_y,3))
    #将cp map 单个bin 呈现出来
    for (bin_count,bin_name) in bin_sort:
        #if bin_count>30: bin的个数大于这个数才会要
        cp_pattern_bin = np.array(MAP_data_need[MAP_data_need[:,2]==bin_name])
        #将cp map呈现出来
        if str(bin_name) in good_bin[:,0]:
            cp_pattern[cp_pattern_bin[:,0]-1,cp_pattern_bin[:,1]-1]+=np.array([0,255,0])
        else:
            cp_pattern[cp_pattern_bin[:,0]-1,cp_pattern_bin[:,1]-1]+=np.random.randint(0,256,3)
    cp_map2 = np.rot90(cp_pattern,k=1)
    cp_map2 = cp_map2.astype(np.uint8)
    #%

# 存图

    # cp_map_path =config.new_dir  #存放cp map的路径config.new_dir
   
    # new_model = load_model(config.model_path)
    
    cp_map_path = 'E:/1.0 YEandEDA/7.0 ProjectPlan/12 WaferCrack/Test/'   #存放cp map的路径
    new_model = load_model('F:/CP special map classes project/My_Xception_Model/My_Xception_Model_15-0.11-0.97.hdf5')
    
    filename_bin = cp_map_path+str(records["uint_key"][map_index][10])[:5]+'_'+records["uint_key"][map_index][0]+'_'+records["uint_key"][map_index][2]+'_'+records["uint_key"][map_index][6]+".jpg"#
   # cv2.imwrite(filename_bin, cp_map2)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    img=cp_map2
    img=Image.fromarray(np.uint8(img))
#         img =  Image.open("F:/test/82.78_Y0120A_A1A1145#18_20220201-090248.jpg")
#         plt.imshow(img)
    target_size=(224, 224)
    img = img.resize(target_size)
    img = image.img_to_array(img)/255
    img=np.expand_dims(img,axis=0)
    out=np.argmax(new_model.predict(img))
    
    writePathandName= "E:/CP_special_Map/PredictImgResult/"#config.writePathandName
    TEST={'CenterFull': 0, 'CenterOther': 1, 'CenterRadio': 2, 'CenterScatter': 3, 'CornerLarge': 4, 'CornerLitter': 5, 'DonutOther': 6, 'DonutReal': 7, 'EdgeFat': 8, 'EdgeSlim': 9, 'Line_Litter': 10, 'Line_Long': 11, 'Moon': 12, 'Others': 13, 'Random': 14, 'Scrath': 15}
    Possibility=np.max(new_model.predict(img))
    #print(Possibility)

    Code_name=list(TEST.keys())[list(TEST.values()).index(out)]
    imgename=str(records["uint_key"][map_index][10])[:5]+'_'+records["uint_key"][map_index][0]+'_'+records["uint_key"][map_index][2]+'_'+records["uint_key"][map_index][6]+".jpg"
#     print(Code_name)
    if Possibility>-9:
#             mapsave(writePathandName,Code_name,(img[0]*255),str(Possibility)+'_'+file_names[i])
        # mapsave(writePathandName,Code_name,(img[0]*255),imgename)
        print(imgename)
    else:
        print(imgename)
        # mapsave(writePathandName,'NeednewPattern',(img[0]*255),imgename)
        
    

#         OutPut["uint_key"].append([records["uint_key"]])
    OutPut["Value"].append([Code_name,Possibility])

#%%

##########################################参考代码
conn = cx_Oracle.connect('EDA/JkEdaTest#2022@192.168.6.149/jktedadb')#这里的顺序是用户名/密码@oracleserver的ip地址/数据库名字
cur = conn.cursor()
if len(OutPut["uint_key"]) > 0:
    
    recordsDB = {}
    for i in range(len(OutPut["uint_key"])):
        print(i)
        # recordsDB["product"] = None
        # recordsDB["lot"] = None
        # recordsDB["wafer"] = None
        # recordsDB["cp_type"] = None
        # recordsDB["cp_test_prog"] = None
        # recordsDB["pattern_name"] = None
        # recordsDB["reliability"] = None  
        
        recordsDB["product"] = OutPut['uint_key'][i][0]
        recordsDB["lot"] = OutPut['uint_key'][i][1]
        recordsDB["wafer"] = OutPut['uint_key'][i][2]
        recordsDB["cp_type"] = OutPut['uint_key'][i][3]
        recordsDB["cp_test_prog"] = OutPut['uint_key'][i][4]
        recordsDB["pattern_name"] = OutPut["Value"][i][0]
        recordsDB["reliability"] = str(round(OutPut["Value"][i][1],4))
        recordsDB["update_time"] =  datetime.datetime.now()
        recordsDB["wafer_no"] = OutPut['uint_key'][i][7]
        recordsDB["corr_lot"] = OutPut['uint_key'][i][8]
        # recordsDB["scribe_id"] = OutPut['uint_key'][i][9]
        recordsDB["scribe_id"] = "A1A1111_01"
        recordsDB["meas_time"] = str(OutPut['uint_key'][i][5])
        print('ok')

        # targetdb.execute(config_sql.SQL_CP_MAP_SSA,
        cur.execute(SQL_CP_MAP_SSA,
                    PRODUCT = recordsDB["product"],
                    LOT = recordsDB["lot"],
                    WAFER = recordsDB["wafer"],
                    CP_TYPE = recordsDB["cp_type"],
                    CP_TEST_PROG = recordsDB["cp_test_prog"],
                    PATTERN_NAME = recordsDB["pattern_name"],
                    RELIABILITY = recordsDB["reliability"],
                    UPDATE_TIME = recordsDB["update_time"],
                    WAFER_NO = recordsDB["wafer_no"],
                    CORR_LOT = recordsDB["corr_lot"],
                    SCRIBE_ID = recordsDB["scribe_id"],
                    MEAS_TIME = recordsDB["meas_time"]
                    )


cur.close()
conn.commit()
conn.close()


#%%


# data = cur.execute(SQL_GET_CP_WAFER_SUM_DATA,YIELD_MIN=0,YIELD_MAX=100,TIME_START=20220314000000,TIME_END=20220315000000)
data = cur.execute(SQL_CP_MAP_SSA,
                   PRODUCT = recordsDB["product"],
                   LOT = recordsDB["lot"],
                   WAFER = recordsDB["wafer"],
                   CP_TYPE = recordsDB["cp_type"],
                   CP_TEST_PROG = recordsDB["cp_test_prog"],
                   PATTERN_NAME = recordsDB["pattern_name"],
                   RELIABILITY = recordsDB["reliability"],
                   UPDATE_TIME = recordsDB["update_time"],
                   WAFER_NO = recordsDB["wafer_no"],
                   CORR_LOT = recordsDB["corr_lot"],
                   SCRIBE_ID = recordsDB["scribe_id"],
                   MEAS_TIME = recordsDB["meas_time"]
                   )
    #%%
records = {}#存图的路径
records["uint_key"] = []
records["map_data"] = []
for row in data:
    records["uint_key"].append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]])
    #records["map_data"].append(row[10].read())
    text = row[12]#.read()
    records["map_data"].append(text)
        #%%
#%%


# 获取大量彩色cp map封装
def get_color_map(time_start,time_end,yield_min,yield_max):
    SQL_GET_CP_WAFER_SUM_DATA = """
    SELECT 
    PRODUCT,      
    LOT,
    WAFER,
    CP_TYPE,
    CP_TEST_PROG,
    to_char(MEAS_TIME,'YYYY-MM-DD HH:mm:ss') MEAS_TIME,
    to_char(MEAS_TIME,'YYYYMMDD-HHmmss')TIME,
    GOOD_DIE_COUNT,
    TOTAL_DIE_COUNT,
    ORIGINAL_WAFER_NOTCH,
    YIELD，
    GROSS_DIE_COUNT,
    MAP_DATA
    FROM CP_WAFER_SUM 
    WHERE 1 = 1
    AND meas_time >=to_date(:TIME_START,'yyyyMMddHH24MISS')
    AND meas_time <=to_date(:TIME_END,'yyyyMMddHH24MISS')
    and YIELD >= :YIELD_MIN
    and YIELD <= :YIELD_MAX
    and TOTAL_DIE_COUNT>=GROSS_DIE_COUNT 
    """
    #获取每片wafer bin info
    SQL_GET_CP_BIN_INFO_DATA = """
    select 
    distinct PRODUCT,
    BIN_NAME，
    BIN_TYPE 
    from CP_WAFER_BIN_SUM
    """


    #连接DB    
    # conn = cx_Oracle.connect('EDA/JkEdaTest#2022@192.168.6.149/jktedadb')#这里的顺序是用户名/密码@oracleserver的ip地址/数据库名字
    # cur = conn.cursor()
    # data = cur.execute(SQL_GET_CP_WAFER_SUM_DATA,YIELD_MIN=yield_min,YIELD_MAX=yield_max,TIME_START=time_start,TIME_END=time_end)