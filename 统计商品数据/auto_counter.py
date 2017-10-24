# -*- coding: UTF-8 –*-
from __future__ import division
import xlrd
import xlwt
from xlutils.copy import copy
from os import listdir
from os import getcwd
from os import system


class One_Line(object):
    '''
    单个订单的数据
    '''
    def __init__(self,data_list):
        '''
        data_list = order_id, cost, count,pay,index
        '''
        self.index = data_list[0]  # 当前数据的行数

        self.order_id = data_list[1]    # 订单编号-A
        self.cost = data_list[2]    # 成本-E
        self.count = data_list[3]  # 数量-F
        self.pay = data_list[4] # 支付-J 
        self.G = float(self.cost) * float(self.count)     # 成本*数量-G


class Data(object):
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        
        self.read_handle = xlrd.open_workbook(self.input_file_path,'r')
        self.my_table = self.read_handle.sheets()[0] # sheet1

        self.write_handle = copy(self.read_handle)
        self.write_table = self.write_handle.get_sheet(0)

        self.dic_data = {}  # 只记录第一个订单出现的位置
        self.lst_data = []  # 所有的数据 放在一个list中 元素是obj
        
        self.dic_order_cost = {}    # 每单总额
        self.dic_order_pay = {}     # 每单用户支付

        self.__load_file()  # 加载数据

    def __load_file(self):
        

        rows = self.my_table.nrows   # 行数
        
        for index in range(rows):
            if index == 0:  # 第一行是说明 略过
                continue

            order_id = unicode(self.my_table.cell(index,0))[9:].strip("'") # 产品id-A
            cost = unicode(self.my_table.cell(index,4))[7:]  # 对应成本单价-E
            count = unicode(self.my_table.cell(index,5))[7:] # 数量-F
            pay = unicode(self.my_table.cell(index,9))[7:]      # 买家支付金额

            data_list = [index,order_id,cost,count,pay] # 放在一个list里传进去

            obj_one_line = One_Line(data_list)

            self.lst_data.append(obj_one_line)
            self.dic_data.setdefault(order_id,obj_one_line)

        print '\n\t\t\t载入数据完成！'.decode('UTF-8').encode('CP936'),

    def __save_file(self,output_file_path):
        '''
        保存文件
        '''
        self.write_handle.save(output_file_path)  


    def task_total_cost(self,output_file_path):
        '''
        计算成本总额并写入excel
        '''
        dic_result = {}

        for obj_one_line in self.lst_data:
            order_id = obj_one_line.order_id    # 订单号
            if order_id not in dic_result.keys():
                dic_result.setdefault(order_id, [])
            dic_result[order_id].append(obj_one_line.G)

        # 计算并写入
        for order_id in dic_result:
            total_cost = sum(dic_result[order_id])  # 计算商品总额
            
            self.dic_order_cost.setdefault(order_id,total_cost) # 计算利润时候需要

            this_obj = self.dic_data[order_id]  # 这一行数据 object

            self.write_table.write(this_obj.index,7,unicode(total_cost))

        # self.__save_file(output_file_path)  # 必须调用这个才能保存
        print '计算成本总额...完成！'.decode('UTF-8').encode('CP936'),

    def task_profit(self,output_file_path):
        '''
        计算每单利润并写入excel
        '''
        if self.dic_order_cost == {}:   # 说明还没执行
            self.task_total_cost(output_file_path)

        dic_pay = {}
        for obj_one_line in self.lst_data:
            order_id = obj_one_line.order_id    # 订单号
            if order_id not in dic_pay.keys():
                dic_pay.setdefault(order_id, [])

            dic_pay[order_id].append(float(obj_one_line.pay))

        # 计算每单用户的支付
        for order_id in dic_pay:
            pay = sum(dic_pay[order_id])
            self.dic_order_pay.setdefault(order_id,pay)

        # 校验
        if self.dic_order_pay.keys() == self.dic_order_cost.keys():

            self.write_table.write(0,17,'实际支付总价'.decode('UTF-8'))

            for order_id in self.dic_order_cost:
                res = self.dic_order_pay[order_id] - self.dic_order_cost[order_id]

                this_obj = self.dic_data[order_id]  # 这一行数据 object
                self.write_table.write(this_obj.index,14,unicode(res))  # 利润
                self.write_table.write(this_obj.index,17,unicode(self.dic_order_pay[order_id])) # 支付总额

        self.__save_file(output_file_path)  # 必须调用这个才能保存
        print '计算订单利润...完成！'.decode('UTF-8').encode('CP936')

def print_decode(mystr):
    print mystr.decode('UTF-8').encode('CP936'),

def run_result(input_file):
    # 运行程序
    print '\n\n\t\t\t正在处理：'.decode('UTF-8').encode('CP936')+input_file
    data = Data(input_file)
    output_file_path = 'Result_'+input_file[:-1]    # 为了保存为xls文件

    data.task_profit(output_file_path)


def menu():
    print '-'*80,'\n'
    excel_files = [item for item in listdir(getcwd()) if 'xls' in item or 'xlsx' in item]
    print '\n\t\t\t选择需要处理的文件：\n'.decode('UTF-8').encode('CP936')
    for index,each_file in enumerate(excel_files):
        print '\t\t\t',
        print_decode('『')
        print str(index),
        print_decode('』')
        print each_file

    print '\n','-'*80,'\n'

    while True:
        func_file = raw_input('\t\t\t输入要处理的文件（0~9):  '.decode('UTF-8').encode('CP936'))

        if func_file not in '0123456789':
            print '\t\t\t请检查输入！'.decode('UTF-8').encode('CP936')
            continue
        else:
            if int(func_file) > len(excel_files):
                print '\t\t\t超出索引范围，重新输入。'.decode('UTF-8').encode('CP936')
                continue
            else:
                break

    input_file = excel_files[int(func_file)]    # 待处理的文件

    # 运行程序
    run_result(input_file)

    menu_order = raw_input('\n\n\t\t\t如果需要继续处理请输入 “1” , 退出请随意敲。'.decode('UTF-8').encode('CP936'))
    if menu_order == '1':
        menu()


if __name__ == '__main__':
    system("cls")
    menu()
