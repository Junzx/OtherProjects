# -*- coding: UTF-8 –*-
from __future__ import division
import xlwt

def Run():

    # 初始化
    lst_all_data = []
    
    # 读取文件
    with open('data.txt','r') as fhandle:
        for line in fhandle:
            line = line.strip('\n')
            lst_line_data = [item for item in line.split(' ') if item != '']
            
            tmp = []
            tmp.append(lst_line_data[2])
            tmp.append(lst_line_data[5])
            lst_all_data.append(tuple(tmp))

    # 写入excel
    work_book = xlwt.Workbook()
    sheet = work_book.add_sheet('Data')

    sheet.write(0,0,'X')
    sheet.write(0,1,'Y')
    for index,lst_iter_data in enumerate(lst_all_data):
        sheet.write(index+1,0,lst_iter_data[0])
        sheet.write(index+1,1,lst_iter_data[1])


    work_book.save('demo.xls')

    print 'Finish!'


if __name__ == '__main__':
    Run()