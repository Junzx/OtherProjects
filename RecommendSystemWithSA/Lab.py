# -*- coding: UTF-8 –*-
from math import fabs

fhandle = open('del_log.txt','r')

def mae(auto_data, gold_data):
    '''
    auto_data 是程序跑出来的list
    gold_data 是真正的数据的list
    '''
    # 先确认两个list长度是否相等 如果不相等则报错
    len_auto_data = len(auto_data)
    len_gold_data = len(gold_data)
    if len_auto_data == len_gold_data:
        numerator = 0   # 初始化分子

        for index_data in range(len_auto_data):
            numerator += fabs(float(auto_data[index_data]) - float(gold_data[index_data]))

        print numerator,len_auto_data
        return numerator / len_auto_data

    else:
        raise

auto_data = list()
gold_data = list()


for line in fhandle:
	auto_data.append(line.split('/')[0])
	gold_data.append(line.split('/')[1])
	# print line.split('/')
	# print line
	# print

print mae(auto_data,gold_data)