
#Defect history integrated ratio


import pandas

#Migrate x,y to real center
# 
data_merge['index_2_x'] = data_merge['WAFER_X'] + data_merge['CENTER_X']
data_merge['index_2_y'] = data_merge['WAFER_Y'] + data_merge['CENTER_Y']
data_merge['index_2_x'] = data_merge['index_2_x']/data_merge['DIE_SIZE_X']
data_merge['index_2_y'] = data_merge['index_2_y']/data_merge['DIE_SIZE_Y']
data_merge['index_int_x'] = data_merge['index_2_x'].apply(lambda x: int(x) if x>=0 else int(x)-1)
data_merge['index_int_y'] = data_merge['index_2_y'].apply(lambda x: int(x) if x>=0 else int(x)-1)

#Select process required
list_process = data_min['USER_LAYER'].tolist()
data_y['in_process'] = data_y['LAYER_ID'].apply(lambda x: x in list_process]
data_y = data_y[data_y['in_process']==1]

#Select size-enough defects
data_y = data_merge[data_merge['PRODUCT']=='G0101A']
data_min = data_min[['USER_LAYER','USER_SIZE_OOC','USER_SIZE','PRODUCT']]
data_min.columns = ['LAYER_ID', 'USER_SIZE_OOC', 'USER_SIZE', 'PRODUCT']
data_y = pandas.merge(data_y,data_min,on=['PRODUCT', 'LAYER_ID'])
data_y['defect_limit'] = data_y['SIZE_D'] > data_y['USER_SIZE']*1000
data_y = data_y[data_y['defect_limit'] == 1]

# Default effective area matrix
data_default = pandas.read_csv('D:\data_defect\G0101A.csv',header=0)
data_default['list_default'] = data_default['default'].apply(lambda x:x.split(','))
list_matrix = [[ [] for i in range(-100,100)] for i in range(-100,100)]
int_sum = 0
for i in data_default['list_default']:
    list_matrix[int(i[0])][int(i[1])] = int(i[2])
    if int(i[2]) == 0:
        int_sum += 1


# Effective defect earlier than present layer.
list_layer = data_y['WAFER_KEY'].unique()
dict_result = {}
for i in list_layer:
    # Dataframe earlier than present layer.
    str_time = data_y[data_y['WAFER_KEY'] == i]['MEASURE_TIME'].unique()[0]
    str_lot = data_y[data_y['WAFER_KEY'] == i]['LOT'].unique()[0]
    str_wafer = data_y[data_y['WAFER_KEY'] == i]['WAFER'].unique()[0]
    data_temp = data_y[data_y['LOT'] == str_lot]
    data_temp = data_temp[data_temp['WAFER'] == str_wafer]
    data_temp = data_temp[data_temp['MEASURE_TIME'] <= str_time]
    # Judge whether defect is effective.
    list_matrix_temp = [[ [] for i in range(-100,100)] for i in range(-100,100)]
    int_sum = 0
    for index,j in data_temp.iterrows():
        int_default = list_matrix[int(j['index_int_x'])][int(j['index_int_y'])]
        if int_default == 0:
            if list_matrix_temp[int(j['index_int_x'])][int(j['index_int_y'])] != 1:
                int_sum += 1
                list_matrix_temp[int(j['index_int_x'])][int(j['index_int_y'])] = 1
    dict_result[i] = int_sum

data_group = data_y.groupby('WAFER_KEY').agg({'WAFER_KEY': 'first', 'PRODUCT':'first','LOT':'first', 'WAFER':'first',  'LAYER_ID':'first','USER_SIZE_OOC':'first'})
data_group['defect_history'] = data_group['WAFER_KEY'].map(dict_result)
data_group['defect_ratio'] = data_group['defect_history']/int_sum
data_group['over_limit'] = data_group['defect_history'] > data_group['USER_SIZE_OOC']


print('Result over minimum limit",data_group)

























