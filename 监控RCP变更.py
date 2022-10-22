# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 10:37:35 2022

@author: tanquanlu
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:17:36 2022

@author: tanquanlu
"""

import os
import time
import datetime
import pandas as pd
#import xlwt
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
#import schedule
import configparser


modify_file=[]
modify_file.append('Recipe_Property,Recipe_name,创建时间,修改时间,Comment,Checker,Modified_File_link')
def open_file(path,gap_time=None):
    #alarm_path="E:/Vidas工作相关/RECIPE/2022/0513林道斌/alarm_path/预警全记录.xlsx"
    alarm_path=config.get("path", "all")
    alarm_df=pd.DataFrame(pd.read_excel(alarm_path))
    if gap_time is None:
        gap_time=-2
    
    files= os.listdir(path) #得到文件夹下的所有文件名称
    t1=datetime.datetime.now()
    t11=t1.strftime("%Y-%m-%d %H:%M:%S")
    t0=t1+datetime.timedelta(hours=gap_time)
    t00=t0.strftime("%Y-%m-%d %H:%M:%S")   
    for i in range(len(files)):
        file=files[i]
        suffix=file.split('.')[-1]
        file_path=path+'/'+file
        if os.path.isfile(file_path):
            atime = time.localtime(os.path.getatime(file_path))
            atime=time.strftime("%Y-%m-%d %H:%M:%S", atime)
            ctime = time.localtime(os.path.getctime(file_path))
            ctime=time.strftime("%Y-%m-%d %H:%M:%S", ctime)
            mtime = time.localtime(os.path.getmtime(file_path))
            mtime=time.strftime("%Y-%m-%d %H:%M:%S", mtime)
            
            if t00<ctime<t11 or t00<mtime<t11:
                med=suffix+','+file+','+ctime+','+mtime+',,,'+file_path
                modify_file.append(med)                
                
        else:
            open_file(file_path)
    df_new=pd.DataFrame(modify_file)
    df_new=df_new[0].str.split(',',expand=True)
    df_new.columns=df_new.iloc[0,:]
    df_new=df_new.drop(index=0)
    alarm_df=alarm_df.append(df_new)
    alarm_df=alarm_df.drop_duplicates(['Recipe_Property','Recipe_name','创建时间','修改时间','Modified_File_link'],keep='first')
    alarm_df.to_excel(alarm_path,index=False,header=True)
    return(modify_file)
def concat_content(new_tb,old_tb,backup_path):    
    df=pd.read_excel(old_tb)
    df=pd.DataFrame(df)
    df1=df[df[['Comment','Checker']].isnull().any(axis=1)]
    df_comment=pd.merge(df,df1,how='left', indicator=True).query(
                "_merge=='left_only'").drop('_merge', 1)
    df_new=pd.DataFrame(new_tb)
    df_new=df_new[0].str.split(',',expand=True)
    df_new.columns=df_new.iloc[0,:]
    df_new=df_new.drop(index=0) 
    df3=pd.concat([df1,df_new], ignore_index=True)
    df3=df3.drop_duplicates(subset=None, keep='first', inplace=False)
    beifen=pd.read_excel(backup_path)
    beifen=pd.DataFrame(beifen)
    df4=beifen.append(df_comment)
    df3.to_excel(old_tb,index=False)
    df4.to_excel(backup_path,index=False)
    return(df3)
def save_mail_inform(file,save_path):
    df=pd.DataFrame(file)
    df=df[0].str.split(',',expand=True)
    df.to_excel(save_path,index=False,header=False)
    save_path2=('/').join(save_path.split('/')[0:-1])+'/another.xlsx'
    df.to_excel(save_path2,index=False,header=False)
def send_mail(mail_body,receiver):
    BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
    cred = Credentials(r'smmc-testpe@silanic.cn', '*****')
    config = Configuration(server='JKMailCAS.silanic.cn', credentials=cred, auth_type=NTLM)
    a = Account(
    primary_smtp_address='smmc-testpe@silanic.cn', config=config, autodiscover=False, access_type=DELEGATE)
    #print('\n',mail_body)
    html='<!DOCTYPE html><html><h2><font size="3" color="black">Dear all:</font></h2><style>p {text-indent:2em;}</style><p>请打开<a href="E:/Vidas工作相关/RECIPE/2022/0513林道斌/output/inform_content.xlsx">此链接</a>查看添加文件变更Common</p></html>'
    m = Message(
    account=a,
    folder=a.sent,
    subject=u'测试邮件: '+str(datetime.datetime.now())[0:19]+' 文件新增/变更预警',
    body=HTMLBody(html)+HTMLBody(mail_body),
    to_recipients=receiver)
    m.send_and_save()
    return(m)
    
def send_mail_succ_flag(path2):
    BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
    cred = Credentials(r'smmc-testpe@silanic.cn', '*****')
    config = Configuration(server='JKMailCAS.silanic.cn', credentials=cred, auth_type=NTLM)
    a = Account(
    primary_smtp_address='smmc-testpe@silanic.cn', config=config, autodiscover=False, access_type=DELEGATE)
    #print('\n',mail_body)
    html='<!DOCTYPE html><html><h2><font size="3" color="black">备份成功啦！！！</font></h2></html>'
    m = Message(
    account=a,
    folder=a.sent,
    subject=u'总记录备份成功通知，备份时间为：'+str(datetime.datetime.now())[0:19],
    body=HTMLBody(html)+path2,
    to_recipients=['lindaobin@silanic.cn','tanquanlu@silanic.cn'])
    m.send_and_save()
    return(m)

def super_backup(bp_path):
    df0=pd.DataFrame(pd.read_excel(bp_path))
    #path='E:/Vidas工作相关/RECIPE/2022/0513林道斌/备份/TEST文件变更记录总log_all.xlsx'
    path=config.get("path", "super_backup_file_path")
    df=pd.DataFrame(pd.read_excel(path))
    df=df.append(df0)
    df=df.drop_duplicates()
    df.to_excel(path,index=False)   
    return(df)  

def super_backup_feather(bp_path):
    path=config.get("path", "super_backup_file_path")
    df=pd.DataFrame(pd.read_excel(path))
    df=df.append(df0)
    df=df.drop_duplicates()
    df.to_excel(path,index=False)
    
    path2='/'.join(path.split('/')[0:-1])+'/总log_all.feather'    
    df2=pd.read_feather(path2, columns=None, use_threads=True)
    df0=pd.DataFrame(pd.read_excel(bp_path))    
    df0=df0.astype(str)
    df2=df2.append(df0)   
    df2=df2.drop_duplicates()    
    df2.to_feather(path2)
    #x_feather=pd.read_feather(r"E:\Vidas工作相关\RECIPE\2022\0513林道斌\备份\TEST文件变更记录总log_all.feather", columns=None, use_threads=True)
    
    save_path=path2+';\n'+path
    send_mail_succ_flag(save_path)
    print('备份成功！')
    return(df2) 
if __name__=="__main__":
    config = configparser.ConfigParser()
    config.read("./Config.ini", encoding="utf-8")    
    a0=config.sections()  # 获取section节点
    a1=config.options('path')  # 获取指定section 的options即该节点的所有键
    #path='E:/Vidas工作相关/RECIPE/2022/0513林道斌/data'
    path=config.get("path", "RECIPE_PATH")
    #save_path0='E:/Vidas工作相关/RECIPE/2022/0513林道斌/output/inform_content.xlsx'
    save_path0=config.get("path", "alarm_file_path")
    #backup_path='E:/Vidas工作相关/RECIPE/2022/0513林道斌/备份/TEST文件变更记录总log.xlsx'
    backup_path=config.get("path", "backup_file_path")
    beifen=pd.read_excel(backup_path)
    beifen=pd.DataFrame(beifen)
    new_file=open_file(path)
    final_alarm=concat_content(new_file,save_path0,backup_path)
    alarm_count=len(final_alarm)
    alarm_files=str(list(final_alarm.loc[:,'Recipe_name']))[1:-1]
    beifen_latest=pd.DataFrame(pd.read_excel(backup_path))
    i=0
    if alarm_count>0:
        i+=1
        #mail_to=['lindaobin@silanic.cn','tanquanlu@silanic.cn']
        #mail_to=['tanquanlu@silanic.cn']
        mail_to=list(config.get("mail", "cc").split(';'))
        #print(mail_to,type(mail_to))
        main_body='注：有'+str(alarm_count)+'个文件新增OR变更，具体是：'+alarm_files
        send_mail(main_body,mail_to)
    now=datetime.datetime.now()
    if now.day in (8,18,28) and 0<=now.hour<2:
        final_beifen=super_backup_feather(backup_path)
