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

    def possible(self, user_id, product_id):
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
            print user_id, product_id,
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

    def __normalized_rating(self, user_id, product_id):
        '''
        归一化后 user对物品的打分
        '''
        the_user = self.dic_user[user_id]

        rating_user_2_product = float(
            the_user.record[product_id][u'overall'])    # 用户对物品的打分

        max_rating = the_user.get_max_rating()
        min_rating = the_user.get_min_rating()

        if max_rating != min_rating:
            normalized_rating = (2 * (rating_user_2_product - min_rating) -
                                 (max_rating - min_rating)) / (max_rating - min_rating)
        else:   # 如果相等 将他们的差值设置为0.01
            normalized_rating = (
                2 * (rating_user_2_product - min_rating) - 0.01) / (0.01)

        return normalized_rating

    def __return_normalized_rating(self, user_id, NR):
        '''
        反归一化函数，将-1~1转换为1~5空间的数
        '''
        the_user = self.dic_user[user_id]

        max_rating = the_user.get_max_rating()
        min_rating = the_user.get_min_rating()

        return 0.5 * ((NR + 1) * (max_rating - min_rating)) + min_rating

    def __normalized(self,score):
        '''归一化'''
        return 0.5 * score - 1.5

    def __return_normalized(self,score):
        '''将归一化的数据恢复原来的取值'''
        return (2.0 * score) +3


class Formula_sentiment(object):
    '''
    这个类放公式，利用情感极性作为评测标准
    u'polarity'：情感极性
    u'subjectivity'：情感主观性
    '''

    def __init__(self, dic_product, dic_user):
        self.dic_product = deepcopy(dic_product)    # 采用深拷贝 使两个对象不是对方的引用
        self.dic_user = deepcopy(dic_user)

    def possible(self, user_id, product_id):
        '''
        预测user id对product的打分，利用用户的历史打分来计算
        '''

        # 找相似的物品：找当前用户还对其他的什么物品也打了分
        lst_similiar_2_product = [record for record in self.dic_user[user_id].record.values() if record['asin'] != product_id]
        numerator = denominator = 0  # 初始化分子和分母

        # 说明有共同的数据
        if lst_similiar_2_product != []:
            for product in lst_similiar_2_product:  # 这个product是个record
                # print type(product[u'asin']),product_id
                similiarity = self.__similiar(product[u'asin'], product_id)    # 相似度计算

                # print 'similiarity of',product[u'asin'],' & ',product_id,'  :  ',similiarity

                # numerator += (similiarity * self.__get_NR(user_id, product_id))
                numerator += (similiarity * self.dic_user[user_id].record[product[u'asin']][u'polarity'])
                denominator += fabs(similiarity)
                # if denominator == 0:
                #     denominator = 0.01
                #     print 'denominator is 0'
            # return self.__return_normalized_rating(user_id, numerator / denominator)

            return numerator / denominator

        # 如果没有共同的数据
        else:
            print '没有共同数据',user_id, product_id,
            return 0

    def __similiar(self, product_id_i, product_id_j):
        '''
        计算物品i和物品j的相似度（改进后的余弦）
        如果
        '''
        obj_i = self.dic_product[unicode(product_id_i)]  # 物品i的product对象
        obj_j = self.dic_product[unicode(product_id_j)]  # 物品j的product对象

        lst_users_i = obj_i.record.keys()   # 对物品i打过分的用户id列表
        lst_users_j = obj_j.record.keys()   # 对物品j打过分的用户id列表

        both_user = list(set(lst_users_i).intersection(
            set(lst_users_j)))   # 对物品i和j都打分的用户id列表

        # 如果不存在给这两个物品打过分的用户，说明两个物品相似度为0，返回0.1
        if len(both_user) == 0:
            return 0.1
        else:
            denominator = numerator = 0.0
            denominator_1 = denominator_2 = 0.0

            for one_user in both_user:

                # average_rating = float(self.dic_user[one_user].get_average_rating())

                # average_rating = self.__return_normalized_rating(
                    # one_user, self.dic_user[one_user].get_average_polarity())  # 获取去情感极性的平均值,1~5
                
                average_rating = self.dic_user[one_user].get_average_polarity() # 获取平均值

                rating_user_2_i = obj_i.record[one_user][u'polarity']
                rating_user_2_j = obj_j.record[one_user][u'polarity']

                # rating_user_2_i = self.__return_normalized_rating(
                #     one_user, obj_i.record[one_user][u'polarity'])   # 用户i的情感极性，1~5
                # rating_user_2_j = self.__return_normalized_rating(
                #     one_user, obj_j.record[one_user][u'polarity'])
                
                # rating_user_2_i = float(obj_i.record[one_user][u'overall']) # 用户oneuser对物品i的评分
                # rating_user_2_j = float(obj_j.record[one_user][u'overall']) # 用户oneuser对物品j的评分

                # 分子部分
                numerator_1 = rating_user_2_i - average_rating
                numerator_2 = rating_user_2_j - average_rating
                numerator += (numerator_1 * numerator_2)

                # 分母部分
                denominator_1 += (rating_user_2_i - average_rating)**2
                denominator_2 += (rating_user_2_j - average_rating)**2

            # 处理分子为0的情况
            if numerator == 0:  # 说明这个用户打分都是一样的
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

    def __get_NR(self, user_id, product_id):
        '''
        返回当前record的情感打分
        '''
        for record in self.dic_user[user_id].record.values():
            if record[u'asin'] == product_id:
                return record[u'polarity']  # 返回情感极性

    def __normalized_rating(self, user_id, product_id):
        '''
        归一化后 user对物品的打分
        up:这个函数应该没用
        '''
        the_user = self.dic_user[user_id]

        rating_user_2_product = float(
            the_user.record[product_id][u'overall'])    # 用户对物品的打分

        max_rating = the_user.get_max_rating()
        min_rating = the_user.get_min_rating()

        if max_rating != min_rating:
            normalized_rating = (2 * (rating_user_2_product - min_rating) -
                                 (max_rating - min_rating)) / (max_rating - min_rating)
        else:   # 如果相等 将他们的差值设置为0.01
            normalized_rating = (
                2 * (rating_user_2_product - min_rating) - 0.01) / (0.01)

        return normalized_rating

    def __return_normalized_rating(self, user_id, NR):
        '''
        反归一化函数，将-1~1转换为1~5空间的数
        '''
        the_user = self.dic_user[user_id]

        max_rating = the_user.get_max_rating()
        min_rating = the_user.get_min_rating()

        return 0.5 * ((NR + 1) * (max_rating - min_rating)) + min_rating

    def __normalized(self,score):
        '''归一化'''
        return 0.5 * score - 1.5

    def __return_normalized(self,score):
        '''将归一化的数据恢复原来的取值'''
        return (2.0 * score) +3

class Formulas_SA(object):
    def __init__(self, dic_product, dic_user):
        self.dic_product = deepcopy(dic_product)    # 采用深拷贝 使两个对象不是对方的引用
        self.dic_user = deepcopy(dic_user)

    def possible(self, user_id, product_id, build_score):
        '''
        预测user id对product的打分，利用用户的历史打分来计算
        '''

        # 找相似的物品：找当前用户还对其他的什么物品也打了分
        lst_similiar_2_product = [record for record in self.dic_user[user_id].record.values() if record['asin'] != product_id]
        numerator = denominator = 0  # 初始化分子和分母

        # 说明有共同的数据
        if lst_similiar_2_product != []:
            for product in lst_similiar_2_product:  # 这个product是个record
                # print type(product[u'asin']),product_id
                similiarity = self.__similiar(product[u'asin'], product_id)    # 相似度计算

                # print 'similiarity of',product[u'asin'],' & ',product_id,'  :  ',similiarity

                numerator += (similiarity * build_score)    # 分子
                # numerator += (similiarity * self.dic_user[user_id].record[product[u'asin']][u'polarity'])
                denominator += fabs(similiarity)
                # if denominator == 0:
                #     denominator = 0.01
                #     print 'denominator is 0'
            # return self.__return_normalized_rating(user_id, numerator / denominator)

            return numerator / denominator

        # 如果没有共同的数据
        else:
            print '没有共同数据',user_id, product_id,
            return 0

    def __similiar(self, product_id_i, product_id_j):
        '''
        计算物品i和物品j的相似度（改进后的余弦）
        如果
        '''
        obj_i = self.dic_product[unicode(product_id_i)]  # 物品i的product对象
        obj_j = self.dic_product[unicode(product_id_j)]  # 物品j的product对象

        lst_users_i = obj_i.record.keys()   # 对物品i打过分的用户id列表
        lst_users_j = obj_j.record.keys()   # 对物品j打过分的用户id列表

        both_user = list(set(lst_users_i).intersection(
            set(lst_users_j)))   # 对物品i和j都打分的用户id列表

        # 如果不存在给这两个物品打过分的用户，说明两个物品相似度为0，返回0.1
        if len(both_user) == 0:
            return 0.1
        else:
            denominator = numerator = 0.0
            denominator_1 = denominator_2 = 0.0

            for one_user in both_user:

                # average_rating = float(self.dic_user[one_user].get_average_rating())

                # average_rating = self.__return_normalized_rating(
                    # one_user, self.dic_user[one_user].get_average_polarity())  # 获取去情感极性的平均值,1~5
                
                average_rating = self.dic_user[one_user].get_average_polarity() # 获取平均值

                rating_user_2_i = obj_i.record[one_user][u'polarity']
                rating_user_2_j = obj_j.record[one_user][u'polarity']

                # rating_user_2_i = self.__return_normalized_rating(
                #     one_user, obj_i.record[one_user][u'polarity'])   # 用户i的情感极性，1~5
                # rating_user_2_j = self.__return_normalized_rating(
                #     one_user, obj_j.record[one_user][u'polarity'])
                
                # rating_user_2_i = float(obj_i.record[one_user][u'overall']) # 用户oneuser对物品i的评分
                # rating_user_2_j = float(obj_j.record[one_user][u'overall']) # 用户oneuser对物品j的评分

                # 分子部分
                numerator_1 = rating_user_2_i - average_rating
                numerator_2 = rating_user_2_j - average_rating
                numerator += (numerator_1 * numerator_2)

                # 分母部分
                denominator_1 += (rating_user_2_i - average_rating)**2
                denominator_2 += (rating_user_2_j - average_rating)**2

            # 处理分子为0的情况
            if numerator == 0:  # 说明这个用户打分都是一样的
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

    def normalized(self, user_id, product_id):
        the_user = self.dic_user[user_id]

        rating_user_2_product = float(
            the_user.record[product_id][u'overall'])    # 用户对物品的打分

        max_rating = the_user.get_max_rating()
        min_rating = the_user.get_min_rating()

        if max_rating != min_rating:
            normalized_rating = (2 * (rating_user_2_product - min_rating) -
                                 (max_rating - min_rating)) / (max_rating - min_rating)
        else:   # 如果相等 将他们的差值设置为0.01
            normalized_rating = (
                2 * (rating_user_2_product - min_rating) - 0.01) / (0.01)

        return normalized_rating


class test_Formulas_SA(object):
    def __init__(self, dic_product, dic_user):
        self.dic_product = deepcopy(dic_product)    # 采用深拷贝 使两个对象不是对方的引用
        self.dic_user = deepcopy(dic_user)

        self.utils = Utils()

        self.step_1 = tuple([i/10 for i in range(11)])  # 从0.0~1.0
        self.step_2 = tuple(reversed([i/10 for i in range(11)]))    # 从1.0~0.0

    def possible(self, user_id, product_id, index_step):
        '''
        结合打分形成score，然后返回用户对物品的可能打分
        '''
        # 找相似的物品：找当前用户还对其他的什么物品也打了分 | 这个列表推到其实就是那个get need数据
        self.lst_similiar_2_product = [record for record in self.dic_user[user_id].record.values() if record['asin'] != product_id]
        numerator = denominator = 0  # 初始化分子和分母

        # 说明有共同评分的数据
        if self.lst_similiar_2_product != []:
            
            # 先给每个record都产生一个综合打分
            for one_record in self.lst_similiar_2_product:  # 这个one_record是个record

                user_rating = one_record[u'overall']    # 用户的打分
                user_polarity = one_record[u'polarity'] # 用户的情感分

                build_score = self.step_1[index_step] * user_rating + self.step_2[index_step] * user_polarity
                one_record.setdefault(u'build_score',build_score)

            for one_record in self.lst_similiar_2_product:   # 现在每个record带有综合打分的记录
                # print 'Before build score: ',one_record[u'build_score']

                test_similiarity = self.__test_similiar(one_record[u'asin'],product_id,user_id,one_record[u'build_score'])
                
                print 'After build score: ',one_record[u'build_score'],'   sim:   ',test_similiarity

                
                # print self.__normalized(one_record[u'build_score']),one_record[u'build_score'],'  |   ',
                
                numerator += (test_similiarity * one_record[u'build_score'])    # 这里到底要不要归一化呢？
                denominator += fabs(test_similiarity)

                # print numerator,denominator

            poss = numerator / denominator
            print '\npossibile: ',poss,'nor:  ',self.__return_normalized(poss),
            print '-'*30

            return self.__return_normalized(poss)

    def __test_similiar(self, product_id_i,product_id_j,user_id,build_score):
        '''
        计算相似度
        '''
        obj_i = self.dic_product[unicode(product_id_i)]  # 物品i的product对象
        obj_j = self.dic_product[unicode(product_id_j)]  # 物品j的product对象

        lst_users_i = obj_i.record.keys()   # 对物品i打过分的用户id列表
        lst_users_j = obj_j.record.keys()   # 对物品j打过分的用户id列表

        both_user = list(set(lst_users_i).intersection(set(lst_users_j)))   # 对物品i和j都打分的用户id列表

        # 如果不存在给这两个物品打过分的用户，说明两个物品相似度为0，返回0.1
        if len(both_user) == 0:
            return 0.1
        else:
            denominator = numerator = 0.0
            denominator_1 = denominator_2 = 0.0

            for one_user in both_user:

                average_rating = self.__return_normalized(self.utils.get_average(self.lst_similiar_2_product))    # 获取平均值
                # average_rating = self.__return_normalized(average_rating)
                rating_user_2_i = build_score
                rating_user_2_j = obj_j.record[one_user][u'overall']
                # rating_user_2_j = self.__normalized(obj_j.record[one_user][u'overall'])

                # print 'the data: ',build_score,rating_user_2_i,rating_user_2_j,average_rating,self.__return_normalized(average_rating)

                # 分子部分
                numerator_1 = rating_user_2_i - average_rating
                numerator_2 = rating_user_2_j - average_rating
                numerator += (numerator_1 * numerator_2)

                # 分母部分
                denominator_1 += (rating_user_2_i - average_rating)**2
                denominator_2 += (rating_user_2_j - average_rating)**2


            # 处理分子为0的情况
            if numerator == 0:  # 说明这个用户打分都是一样的
                return average_rating  # 返回的自然也是相同的打分

            # 处理分母为0的情况

            # 如果不为0
            if (denominator_1 * denominator_2) != 0:
                denominator = sqrt(denominator_1) * sqrt(denominator_2)   # 分母 正常的计算方式

            # 将不等于0的部分平方
            elif (denominator_1 == 0) and (denominator_2 != 0):
                denominator = denominator_2**2
            elif (denominator_1 != 0) and (denominator_2 == 0):
                denominator = denominator_1**2

            # 如果两个部分都是0，即用户对他们的打分都相同
            elif denominator_1 == 0 and denominator_2 == 0:
                # denominator = 0.9   # 保证最后相似度算完了为1
                return 1.0


        # print 'denominator: ',denominator,'  numerator:  ',numerator,'   result:  ', numerator/denominator

        return numerator / denominator


    def __utils_get_build_score(self,product_id):
        '''
        仅在这个类内使用，返回build score
        '''
        for record in self.lst_similiar_2_product:
            if record[u'asin'] == product_id:
                return float(record[u'build_score'])

    def __similiar(self, product_id_i,product_id_j,user_id):
        '''
        计算相似度
        '''
        obj_i = self.dic_product[unicode(product_id_i)]  # 物品i的product对象
        obj_j = self.dic_product[unicode(product_id_j)]  # 物品j的product对象

        lst_users_i = obj_i.record.keys()   # 对物品i打过分的用户id列表
        lst_users_j = obj_j.record.keys()   # 对物品j打过分的用户id列表

        both_user = list(set(lst_users_i).intersection(set(lst_users_j)))   # 对物品i和j都打分的用户id列表

        # 如果不存在给这两个物品打过分的用户，说明两个物品相似度为0，返回0.1
        if len(both_user) == 0:
            return 0.1
        else:
            denominator = numerator = 0.0
            denominator_1 = denominator_2 = 0.0

            for one_user in both_user:

                average_rating = self.utils.get_average(self.lst_similiar_2_product)    # 获取平均值

                rating_user_2_i = self.__utils_get_build_score(product_id_i)
                rating_user_2_j = self.__normalized(obj_j.record[one_user][u'overall'])

                # 分子部分
                numerator_1 = rating_user_2_i - average_rating
                numerator_2 = rating_user_2_j - average_rating
                numerator += (numerator_1 * numerator_2)

                # 分母部分
                denominator_1 += (rating_user_2_i - average_rating)**2
                denominator_2 += (rating_user_2_j - average_rating)**2

            # 处理分子为0的情况
            if numerator == 0:  # 说明这个用户打分都是一样的
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
    def __init__(self):
        self.dic_user = {}  # user类的字典，user_id:user_class
        self.dic_product = {}  # product的列表，product_id:product_class
        self.utils = Utils()
        self.__load_data()

        self.formula = Formula(self.dic_product, self.dic_user)
        self.formula_sentiment = Formula_sentiment(self.dic_product, self.dic_user)
        self.formula_sa = Formulas_SA(self.dic_product,self.dic_user)

        self.test_formula_sa = test_Formulas_SA(self.dic_product,self.dic_user) # 测试用
        
        self.step_1 = tuple([i/10 for i in range(11)])  # 从0.0~1.0
        self.step_2 = tuple(reversed([i/10 for i in range(11)]))    # 从1.0~0.0

    def __load_data(self, filepath='./Data/split/train_Musical_Instruments_5.json'):
        '''
        加载训练数据
        '''
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

    def new_train_parameter(self):
        '''
        结合两个参数
        '''

        for index_user in self.dic_user:    # 依次对每个user进行处理

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30
    
            nor_maybe_rating_rating, maybe_rating_rating= self.formula.possible(index_user, gold_asin)  # 预测打分，利用用户的历史评分
            maybe_rating_polarity = self.formula_sentiment.possible(index_user,gold_asin)    # 实验，利用情感极性

            # nor_maybe_rating_rating归一化后的预测打分，maybe_rating_polarity 预测的情感极性
            
            # TODO: pass

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

    def training(self):
        '''
        训练a和b
        '''
        for index_user in self.dic_user:    # 依次对每个user进行处理

            # gold数据
            gold_record = self.dic_user[index_user].get_gold_record()
            gold_asin = gold_record[u'asin']  # 那个物品的id
            gold_rating = gold_record[u'overall']    # 用户对于物品的真实打分
            gold_polarity = gold_record[u'polarity']    # 用户对物品的真实情感打分

            print '-' * 30, 'user:  ', index_user, '  gold asin:  ', gold_asin, '-' * 30

            # 接下来依次计算 用户对于物品的预测评分
            need_record = self.dic_user[index_user].get_need_record()   # 剩下的record

            if len(need_record) ==0:
                continue

            dic_result = {}

            for index_step in range(len(self.step_1)):

                poss = self.test_formula_sa.possible(index_user,gold_asin,index_step)

                dic_result.setdefault((gold_rating) - poss,index_step)    # 把差值存起来
                # print gold_rating-poss
        

            index_min_sub = min(dic_result.keys())

            # print index_min_sub,dic_result.get(index_min_sub),dic_result

            index_finall_result = dic_result[index_min_sub]

            para_1,para_2 = self.step_1[index_finall_result],self.step_2[index_finall_result]

            # print para_1,para_2



            # for one_record in need_record.values():

                # user_rating = one_record[u'overall']    # 用户的打分
                # user_polarity = one_record[u'polarity'] # 用户的情感分

                # for index_step in range(len(self.step_1)):

                    # 构建一个打分
                    # user_rating = self.formula_sa.normalized(index_user,one_record[u'asin'])

                    # build_score = self.step_1[index_step] * user_rating + self.step_2[index_step] * user_polarity

                    # print build_score,
                    # poss = self.formula_sa.possible(index_user,one_record[u'asin'])
                    # print poss,

                    # self.test_formula_sa.possible(index_user,one_record[u'asin'],index_step)





    def lab(self):
        '''
        临时测试用
        '''
        print id(self.dic_product), id(self.formula.dic_product)


def check():
    '''
    这个函数用来测试是否加载成功
    '''
    print '-' * 30, 'Running!', '-' * 30

    recomm = Recommend()
    recomm.train_parameter()
    # recomm.training()   # 训练a b

    # recomm.lab()    # 临时测试用


if __name__ == "__main__":
    start_time = clock()
    check()
    # split_file()
    end_time = clock()
    print '\n\n用时:', (end_time - start_time)
