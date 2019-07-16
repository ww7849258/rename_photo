#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
批量修改照片文件名称的Python脚本程序。
遍历指定目录（含子目录）的照片文件，根据拍照时间将照片文件名修改为以下格式：
WWU_190715_091230.jpg (WW_%Y%m%d_%H%M%S)

由于文件名已经精确到秒，理论上重名的概率非常小。
如果需要考虑到重名的问题，可以对本程序进行进一步的优化。

！该程序需要安装exifread模块，否则无法使用。
例如，Linux/Mac OS X下命令行安装该模块：sudo pip install exifread
'''

import os
import stat
import time
import exifread
import sys
MY_DATE_FORMAT = 'WWU_%y%m%d_%H%M%S'

SUFFIX_FILTER = [ '.jpg' , '.png' , '.mpg' , '.mp4' , '.thm' , '.bmp' , '.jpeg' , '.avi' , '.mov', '.m4v']
DELETE_FILES = [ 'thumbs.db' , 'sample.dat' ]

def isFormatedFileName(filename):
     #判断是否已经是格式化过的文件名
     try:
         filename_nopath = os.path.basename(filename)
         f , e = os.path.splitext(filename_nopath)
         time.strptime(f, MY_DATE_FORMAT)
         return True
     except ValueError:
         return False

def isTargetedFileType(filename):
     #根据文件扩展名，判断是否是需要处理的文件类型
     filename_nopath = os.path.basename(filename)
     f , e = os.path.splitext(filename_nopath)
     if e.lower() in SUFFIX_FILTER:
         return True
     else:
         return False

def isDeleteFile(filename):
     #判断是否是指定要删除的文件
     filename_nopath = os.path.basename(filename)
     if filename_nopath.lower() in DELETE_FILES:
         return True
     else:
         return False

def generateNewFileName(filename):
     #根据照片的拍照时间生成新的文件名（如果获取不到拍照时间，则使用文件的创建时间）
     try:
         if os.path.isfile(filename):
             fd = open(filename, 'rb')
         else:
             raise "[%s] is not a file!\n"%filename
     except :
         raise "unopen file[%s]\n"%filename

     data = exifread.process_file(fd)
     dateStr = "" 
     if data:
         #取得照片的拍摄日期
         try:
             t = data['EXIF DateTimeOriginal']
             #转换成 yyyymmdd_hhmmss的格式
             dateStr = 'WWU_' + str(t).replace(":","")[2:8] + "_" + str(t).replace(":","")[9:]
             print(dateStr)
         except:
             pass

     #如果没有取得exif信息，则用图像文件的创建日期作为拍摄日期
     state = os.stat(filename)
     if len(dateStr) == 0:
       dateStr = time.strftime(MY_DATE_FORMAT, time.localtime(state[-2]))
       print(dateStr)
     dirname = os.path.dirname(filename)
     filename_nopath = os.path.basename(filename)
     f , e = os.path.splitext(filename_nopath)
     newFileName = os.path.join(dirname ,dateStr + e )
     return newFileName

def scandir(startdir):
     #遍历指定目录以及子目录，对满足条件的文件进行改名或删除处理
     os.chdir(startdir)
     for obj in os.listdir(os.curdir):
         if os.path.isfile(obj):
             if isTargetedFileType(obj) and isFormatedFileName(obj) == False:
                 #对满足过滤条件的文件进行改名处理
                 newFileName = generateNewFileName(obj)
                 print("rename [%s] => [%s]"%(obj,newFileName))
                 os.rename(obj ,newFileName)
             elif isDeleteFile(obj):
                 #删除制定的文件
                 print("delete [%s]: "%obj)
                 os.remove(obj)
             else:
                 pass
         if os.path.isdir(obj):
             scandir(obj)
             os.chdir(os.pardir)

if __name__ == "__main__" :
    if len(sys.argv) > 1:
      path = sys.argv[1]
      scandir(path)
    else:
      print("请输入要处理的文件路径(绝对路径)")
      print("eg: Python3 batch_rename_jpg.py '/Users/wuwei/2019-05' ")
