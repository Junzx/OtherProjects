# -*- coding: UTF-8 –*-
"""
程序任务描述：
1. 将现有的文件分割为两部分，分别为90%的训练数据，10%测试数据。
2. 针对训练数据，加载所有数据到内存。
3. 针对一个用户的评分记录，留下一个记录作为测试
4. 根据公式计算出用户对留下的那个物品的预测打分，差值如果在1内则认为是准确的，记录a，b；如果不正确，调整ab直到差值小于1
5. 对每个用户都这样，得到a b的list，求取平均值
6. 在测试数据上进行实验，得到的差值就是描述算法性能的描述

# LOG:
2017年7月17日：
新增加一个类，与现有Formalura的类的功能类似，但是这里采用的是情感极性。
由于情感极性的数值也是－１～１，因此在正规化部分可以不用需要进行新的修改。
2017年7月27日：
训练ab参数的方法有问题，先放下了。
现在train_para~()的函数是正常的，可以输出：

------------------------------ user:   A2JMJVNTBL7K7E   gold asin:   B000WS1QC6 ------------------------------
根据rating：   预测打分： 4.0             归一化： 0.5          实际打分： 5.0
根据polarity：   预测： 0.129237528345          实际： 0.116844919786

现在缺少评测函数
"""
from __future__ import division
import json
import textblob
import os
import sys
import types
from math import sqrt, fabs
from time import clock
from copy import deepcopy


def split_file():
    '''
    将文件分割为训练数据和测试数据
    90%作为训练数据，10%作为评价系统性能用的数据
    '''
    file_path = './Data/Musical_Instruments_5.json'
    # 文件名，如Musical_Instruments_5
    file_name = file_path.split('/')[-1].split('.')[0]
    train_file = './Data/split/train_' + file_name + '.json'  # ./Data/train_Musical_Instruments_5.json
    dev_file = './Data/split/dev_' + file_name + '.json'      # ./Data/dev_Musical_Instruments_5.json

    # 先把split的文件清空
    splited_files = os.listdir('./Data/split')  # split文件夹已有的文件
    if splited_files != []:
        for path in splited_files:
            os.remove('./Data/split/' + path)

    # 再创建新的文件
    with open(file_path, 'r') as hdl_original:
        hdl_train = open(train_file, 'a+')
        hdl_dev = open(dev_file, 'a+')

        data = hdl_original.readlines()  # 原文件的数据
        len_orginal = len(data)     # 原文件的行数
        split_index = int(len_orginal * 0.9)    # 分割

        for (index, line) in enumerate(data):
            if index < split_index:
                hdl_train.write(line)
            elif split_index <= index <= len_orginal:
                hdl_dev.write(line)

        hdl_train.close()
        hdl_dev.close()


class Utils(object):
    def split_records(self, dic_records):
        '''
        接受一个record的字典，抽取最后一个record作为gold，剩下的部分作为信息来源。
        gold_record 是单个record的dict
        need_record 是个record的dict，key-value和原来的dic_records相同
        '''
        dic_records = deepcopy(dic_records)  # 深拷贝 防止修改原dict
        index_gold_record = dic_records.keys()[-1]
        gold_record = dic_records[index_gold_record]    # gold结果,是一个record
        del dic_records[index_gold_record]  # 删掉gold
        need_record = dic_records           # need结果，key是asin，value是record
        return (gold_record, need_record)

    def write(self, one_string):
        '''
        用来将结果写入到文件
        '''
        with open('Log.txt', 'a') as fhandle:
            pass

    def get_average(self,lst_record):
        '''
        给定一个record list，返回它的平均值
        '''
        num = index = 0
        for record in lst_record:
            num += float(record[u'build_score'])
            index += 1
        return num/index

    def mae(self, auto_data, gold_data):
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
            return numerator / len_auto_data

        else:
            raise


class Product(object):
    '''
    这个类存放一个物品的属性，包含它收到的用户打分，用户评论，用户id（用户类）
    '''

    def __init__(self, asin):
        '''
        :param asin:商品id
        :param record:dict，key为user_id，value为记录的dict
        '''
        self.asin = asin
        self.record = {}


class User(object):
    '''
    存放一个用户所有的评论等内容
    '''

    def __init__(self, reviewer_id):
        '''
        :param reviewer_id: 用户id
        :param record: 用户评论过的记录，是个dict，key是商品id，value是dict记录（record）
        '''
        self.reviewer_id = reviewer_id
        self.record = {}  # 初始化为空dict

    def get_average_rating(self):
        '''
        返回当前用户对所有物品的平均打分
        '''
        all_rating = [float(each_record[u'overall'])
                      for each_record in self.record.values()]
        numerator = sum(all_rating)
        denominator = len(all_rating)
        return numerator / denominator

        # return sum([float(each.record[u'overall']) for each in self.record.values()])/len(self.record)

    def get_max_rating(self):
        '''
        返回当前用户的最大打分
        '''
        return max([float(each[u'overall']) for each in self.record.values()])

    def get_min_rating(self):
        '''
        返回用户的最小打分
        '''
        return min([float(each[u'overall']) for each in self.record.values()])

    def split_records(self, dic_records):
        '''
        接受一个record的字典，抽取最后一个record作为gold，剩下的部分作为信息来源。
        gold_record 是单个record的dict
        need_record 是个record的dict，key-value和原来的dic_records相同
        '''
        dic_records = deepcopy(dic_records)  # 深拷贝 防止修改原dict
        index_gold_record = dic_records.keys()[-1]
        gold_record = dic_records[index_gold_record]    # gold结果,是一个record
        del dic_records[index_gold_record]  # 删掉gold
        need_record = dic_records           # need结果，key是asin，value是record
        return (gold_record, need_record)

    def get_gold_record(self):
        '''
        返回最后一个record作为gold结果，
        '''
        return self.record[self.record.keys()[-1]]  # dict of record

    def get_need_record(self):
        '''
        返回除了最后一个的record剩下的record。
        返回一个dict，key为asin，value为对应的record （dict）
        '''
        tmp_records = deepcopy(self.record)
        del tmp_records[tmp_records.keys()[-1]]
        return tmp_records

    def get_rat_product(self):
        '''
        返回这个用户打过分的物品list
        '''
        return [record[u'asin'] for record in self.record.values()]

    def get_average_polarity(self):
        '''
        返回情感极性的平均值
        '''
        return sum([float(record[u'polarity']) for record in self.record.values()])

    def get_max_polarity(self):
        '''
        获取最大的情感极性
        '''
        return max([float(each[u'polarity']) for each in self.record.values()])

    def get_min_polarity(self):
        '''
        获取最小的情感极性
        '''
        return min([float(each[u'polarity']) for each in self.record.values()])


class Formula(object):
    '''
    传统的方法，利用打分数据
    2017年7月18日11:17:24：这个函数没错了！如没有需求，不更新。
    '''

    def __init__(self, dic_product, dic_user):
        self.dic_product = deepcopy(dic_product)    # 采用深拷贝 使两个对象不是对方的引用
        self.dic_user = deepcopy(dic_user)

        self.step_1 = tuple([i/10 for i in range(11)])  # 从0.0~1.0
        self.step_2 = tuple(reversed([i/10 for i in range(11)]))    # 从1.0~0.0

    def possible(self, user_id, product_id,index_step):
        '''
        预测user id对product的打分，利用用户的历史打分来计算
        '''

        # 当前用户对其他物品的打分
        # lst_similiar_2_product = [record for record in self.dic_user[user_id].get_need_record()]
        lst_similiar_2_product = [record for record in self.dic_user[user_id].record.values() if record['asin'] != product_id]
        numerator = denominator = 0  # 初始化分子和分母

        # 说明有共同的数据
        if lst_similiar_2_product != []:
            for product in lst_similiar_2_product:
                # print type(product[u'asin']),product_id

                user_overall = product[u'overall']
                similiarity = self.__similiar(product[u'asin'], product_id)    # 相似度计算

                # print 'similiarity of',product[u'asin'],' & ',product_id,'  :  ',similiarity

                numerator += (similiarity *
                              self.__normalized(user_overall))
                denominator += fabs(similiarity)
                if denominator == 0:
                    denominator = 0.01

            normalized_ans = self.__return_normalized(numerator / denominator)    # 归一化后结果
            ans = numerator/denominator

            return (normalized_ans,ans)

            # return numerator / denominator

        # 如果没有共同的数据
        else:
            # print user_id, product_id,
            return (0,0)

    def __similiar(self, product_id_i, product_id_j):
        '''
        计算物品i和物品j的相似度（改进后的余弦）
        如果
        '''
        obj_i = self.dic_product[unicode(product_id_i)]  # 物品i的product对象
        obj_j = self.dic_product[unicode(product_id_j)]  # 物品j的product对象

        lst_users_i = obj_i.record.keys()   # 对物品i打过分的用户id列表
        lst_users_j = obj_j.record.keys()   # 对物品j打过分的用户id列表

        both_user = list(set(lst_users_i).intersection(set(lst_users_j)))   # 对物品i和j都打分的用户id列表

        # 如果不存在给这两个物品打过分的用户，说明两个物品相似度为0，返回0.01
        if len(both_user) == 0:
            return 0.1
        else:
            denominator = numerator = 0.0
            denominator_1 = denominator_2 = 0.0

            for one_user in both_user:

                average_rating = float(
                    self.dic_user[one_user].get_average_rating())
                rating_user_2_i = float(
                    obj_i.record[one_user][u'overall'])  # 用户oneuser对物品i的评分
                rating_user_2_j = float(
                    obj_j.record[one_user][u'overall'])  # 用户oneuser对物品j的评分

                # 分子部分
                numerator_1 = rating_user_2_i - average_rating
                numerator_2 = rating_user_2_j - average_rating
                numerator += (numerator_1 * numerator_2)  # 分子

                # 分母部分
                denominator_1 += (rating_user_2_i - average_rating)**2
                denominator_2 += (rating_user_2_j - average_rating)**2

            # 处理分子为0的情况
            if numerator == 0:
                return 0.9  # 这个数字是拍脑袋想的

            # 处理分母为0的情况

            # 如果不为0
            if (denominator_1 * denominator_2) != 0:
                denominator = sqrt(denominator_1) * \
                    sqrt(denominator_2)   # 分母 正常的计算方式

            # 将不等于0的部分平方
            elif (denominator_1 == 0) and (denominator_2 != 0):
                denominator = denominator_2**2
            elif (denominator_1 != 0) and (denominator_2 == 0):
                denominator = denominator_1**2

            # 如果两个部分都是0，即用户对他们的打分都相同
            elif denominator_1 == 0 and denominator_2 == 0:
                denominator = 0.9   # 保证最后相似度算完了为1

        return numerator / denominator

    def __normalized(self,score):
        '''归一化'''
        return 0.5 * score - 1.5

    def __return_normalized(self,score):
        '''将归一化的数据恢复原来的取值'''
        return (2.0 * score) +3


class Recommend(object):
    def __init__(self,filepath):
        self.dic_user = {}  # user类的字典，user_id:user_class
        self.dic_product = {}  # product的列表，product_id:product_class
        self.utils = Utils()
        self.__load_data(filepath)

        self.formula = Formula(self.dic_product, self.dic_user)
        self.formula_sentiment = Formula_sentiment(self.dic_product, self.dic_user)
        # self.formula_sa = Formulas_SA(self.dic_product,self.dic_user)

        # self.test_formula_sa = test_Formulas_SA(self.dic_product,self.dic_user) # 测试用
        
        self.step_1 = tuple([i/10 for i in range(11)])  # 从0.0~1.0
        self.step_2 = tuple(reversed([i/10 for i in range(11)]))    # 从1.0~0.0

    def __load_data(self, filepath='./Data/split/train_Musical_Instruments_5.json'):
        '''
        加载训练数据
        '''
        print 'Loading...',filepath,'   ',

        lst_all_data = []  # 放json文件的所有的记录，里面的元素是dict格式

        # 读取数据
        for eachline in open(filepath):
            one_data = json.loads(eachline)  # 这是一条记录，是dict类型

            # 计算情感极性和主观性
            tb = textblob.TextBlob(one_data['reviewText'])
            polarity = tb.sentiment.polarity    # 极性
            subjectivity = tb.sentiment.subjectivity    # 主观性
            one_data.setdefault(u'polarity', polarity)
            one_data.setdefault(u'subjectivity', subjectivity)

            lst_all_data.append(one_data)  # 存起来

        # 构建类对象
        for each_record in lst_all_data:
            reviewer_id = each_record['reviewerID']     # 写评论的人的id
            asin = each_record['asin']                  # 被评论的物品的id

            if reviewer_id not in self.dic_user.keys():  # 说明这个是个新的纪录
                obj_user = User(reviewer_id)  # 创建这个类
                self.dic_user.setdefault(reviewer_id, obj_user)  # 放到总的list中

            if asin not in self.dic_product.keys():  # 说明这是个新的记录
                obj_product = Product(asin)
                self.dic_product.setdefault(asin, obj_product)

            self.dic_user[reviewer_id].record.setdefault(asin, each_record)
            self.dic_product[asin].record.setdefault(reviewer_id, each_record)
        print 'Load File Success ! ...'

    def train_parameter(self):
        '''
        选择每个用户的最后一条数据作为比对，训练两个参数
        '''
            
        # log_handle = open('Log.txt', 'a')

        for index_user in self.dic_user:    # 依次对每个user进行处理

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30
            # print self.dic_user[index_user].get_rat_product() # 输出当前用户评价过的物品的list

            nor_maybe_rating_rating, maybe_rating_rating= self.formula.possible(index_user, gold_asin)  # 预测打分，利用用户的历史评分
            maybe_rating_polarity = self.formula_sentiment.possible(index_user,gold_asin)    # 实验，利用情感极性

            # 在屏幕输出部分
            print '根据rating：  '.decode('UTF-8').encode('CP936'),
            print '预测打分：'.decode('UTF-8').encode('CP936'), str(nor_maybe_rating_rating),'\t\t',
            print '  归一化：'.decode('UTF-8').encode('CP936'),str(maybe_rating_rating),'\t\t',
            print '实际打分：'.decode('UTF-8').encode('CP936'), str(gold_rating)

            print '根据polarity：  '.decode('UTF-8').encode('CP936'),
            print '预测：'.decode('UTF-8').encode('CP936'),str(maybe_rating_polarity),'\t\t',
            print '实际：'.decode('UTF-8').encode('CP936'),str(gold_polarity)

            # 写入文件部分
        #     log_handle.write('-' * 30 + 'user:  ' + index_user +
        #                      '  gold asin:  ' + gold_asin + '-' * 30 + '\n')
        #     log_handle.write('预测打分：' + str(maybe_rating) + '\n')
        #     log_handle.write('实际打分：' + str(gold_rating) + '\n')
        #     log_handle.write('\n')

        # log_handle.close()

    def test_polarity(self):
        '''
        计算rating的准确性
        '''
        auto_data = []
        gold_data = []

        for index_user in self.dic_user:    # 依次对每个user进行处理 

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            # print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30
            # print self.dic_user[index_user].get_rat_product() # 输出当前用户评价过的物品的list

            maybe_rating_polarity = self.formula_sentiment.possible(index_user,gold_asin)    # 实验，利用情感极性

            # print '根据polarity：  '.decode('UTF-8').encode('CP936'),
            # print '预测：'.decode('UTF-8').encode('CP936'),str(maybe_rating_polarity),'\t\t',
            # print '实际：'.decode('UTF-8').encode('CP936'),str(gold_polarity)

            auto_data.append(maybe_rating_polarity)
            gold_data.append(gold_polarity)

        #     print maybe_rating_polarity,gold_polarity

        # print auto_data[-1],gold_data[-1]

        result = self.utils.mae(auto_data, gold_data)  # 算
        return result

    def test_rating(self):
        '''
        利用情感极性进行测试
        '''
        auto_data = []
        gold_data = []

        del_log = open('del_log.txt','a+')

        for index_user in self.dic_user:    # 依次对每个user进行处理 

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            # print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30
            # print self.dic_user[index_user].get_rat_product() # 输出当前用户评价过的物品的list

            nor_maybe_rating_rating, maybe_rating_rating= self.formula.possible(index_user, gold_asin)  # 预测打分，利用用户的历史评分

            # nor_maybe_rating_rating 是未归一化的结果

        #     print '根据rating：  '.decode('UTF-8').encode('CP936'),
        #     print '预测打分：'.decode('UTF-8').encode('CP936'), str(nor_maybe_rating_rating),'\t\t',
        #     print '  归一化：'.decode('UTF-8').encode('CP936'),str(maybe_rating_rating),'\t\t',
        #     print '实际打分：'.decode('UTF-8').encode('CP936'), str(gold_rating)

            auto_data.append(nor_maybe_rating_rating)
            gold_data.append(gold_rating)
            # print nor_maybe_rating_rating,gold_rating
            del_log.write(str(nor_maybe_rating_rating)+'/'+str(gold_rating)+'\n')


        result = self.utils.mae(auto_data, gold_data)  # 算
        return result

    def test_sa(self,index_step):
        '''
        结合情感和打分
        '''
        auto_data = []
        gold_data = []

        for index_user in self.dic_user:    # 依次对每个user进行处理 

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            # print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30
            # print self.dic_user[index_user].get_rat_product() # 输出当前用户评价过的物品的list

            maybe_rating_polarity = self.formula.possible(index_user,gold_asin)    # 实验，利用情感极性

            # print '根据polarity：  '.decode('UTF-8').encode('CP936'),
            # print '预测：'.decode('UTF-8').encode('CP936'),str(maybe_rating_polarity),'\t\t',
            # print '实际：'.decode('UTF-8').encode('CP936'),str(gold_polarity)

            auto_data.append(maybe_rating_polarity)
            gold_data.append(gold_polarity)

        #     print maybe_rating_polarity,gold_polarity

        # print auto_data[-1],gold_data[-1]

        result = self.utils.mae(auto_data, gold_data)  # 算
        return result


def make_file_list(floder_path):
    if 'home' not in floder_path:
        return [floder_path+'\\'+file_name for file_name in os.listdir(floder_path)]
    elif 'home' in floder_path:
        print 'check '
        return [floder_path+'/'+file_name for file_name in os.listdir(floder_path)]

def check():
    '''
    主函数
    '''

    data_path_sever = '/home/yqzhu/Recomm_data'
    data_path_J = 'D:\Data\Data'
    data_path_Lab = 'F:\Data\small'


    print '-' * 30, 'Running!', '-' * 30
    Result_Log = open('Result.txt','a')

    all_files = make_file_list(data_path_Lab)    # 所有数据的位置

    print all_files

    for one_file_path in all_files:
        
        try:
            recomm = Recommend(one_file_path)   # 初始化

            Result_Log.write('\n'+str(one_file_path)+'\n')


            for i in [0,1,3,5,7]:
                recomm.test_sa(i)



        except Exception,e:
            print '-'*50
            print 'Error! ',e
            print '-'*50
            continue

    Result_Log.close()

    # recomm.training()   # 训练a b

    # recomm.lab()    # 临时测试用


if __name__ == "__main__":
    start_time = clock()
    check()

    # print make_file_list()
    # split_file()
    end_time = clock()
    print '\n\n用时:', (end_time - start_time)
