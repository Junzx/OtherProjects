# -*- coding: UTF-8 -*-
"""
尝试用贝叶斯 手动
"""
from __future__ import division
from os import getcwd,listdir
from copy import deepcopy
from random import sample

# 文件夹定义
positive_folder = getcwd() + '\NameCorpus\positive_example'
counter_folder_animal = getcwd() + '\NameCorpus\counter_example\Animal'
counter_folder_botany = getcwd() + '\NameCorpus\counter_example\Botany'

# 文件
positive_files = [getcwd() + '\NameCorpus\positive_example\\' + i for i in listdir(positive_folder)]
counter_files_animal = [getcwd() + '\NameCorpus\counter_example\Animal\\' + i for i in listdir(counter_folder_animal)]
counter_files_botany = [getcwd() + '\NameCorpus\counter_example\Botany\\' + i for i in listdir(counter_folder_botany)]

def load_one_file(file_path):
    with open(file_path,'r') as hdl:
        return map(lambda x:x.strip('\n'),hdl.readlines())


def load_all_files(file_path_list):
    word_list = []
    for file in file_path_list:
        word_list.extend(load_one_file(file))
    return deepcopy(word_list)

def word_list_filter(word_list):
    """
    接受一个word list，除去其中大于3的词语，然后再返回
    """
    return [word for word in word_list if len(word) <= 9]

def list_2_word_dic(word_list):
    """
    给定一个word list，返回一个key为汉字，value为该字频数的字典
    """
    dic_word = {}
    for word in word_list:
        word_temp = []
        len_word = int(len(word) / 3)
        for i in range(len_word):
            word_temp.append(word[i:i + 3])
        for single_word in word_temp:
            if single_word not in dic_word:
                dic_word.setdefault(single_word, 0)
            dic_word[single_word] += 1  # 计算频数
    return dic_word


class Example(object):
    def __init__(self,files):
        self.word_list = word_list_filter(load_all_files(files))
        self.dic_word = list_2_word_dic(self.word_list)


class Byais(object):
    def __init__(self):
        self.positive_example = Example(positive_files)
        self.counter_example = Example(counter_files_animal)
        self.len_posit = len(self.positive_example.dic_word)
        self.len_count = len(self.counter_example.dic_word)

        self.P_1 = self.len_posit / (self.len_posit + self.len_count)
        self.P_0 = self.len_count / (self.len_posit + self.len_count)

    def __get_P_x_i_1(self, word):
        """
        P(X_i|1)
        """
        numerator = self.positive_example.dic_word.get(word)
        denominator = self.len_posit# + self.len_count
        if numerator is None:
            return 0
        return numerator / denominator

    def __get_P_x_i_0(self, word):
        """
        P(X_i|0)
        """
        numerator = self.counter_example.dic_word.get(word)
        denominator = self.len_count# + self.len_posit
        if numerator is None:
            return 0
        return numerator / denominator

    def __get_P_is_1(self, word_list):
        result = 1
        for word in word_list:
            result *= self.__get_P_x_i_1(word)
        return result * self.P_1

    def __get_P_is_0(self, word_list):
        result = 1
        for word in word_list:
            result *= self.__get_P_x_i_0(word)
        return result * self.P_0

    def API(self, name):
        len_word = int(len(name) / 3)
        word_temp = []
        for i in range(len_word):
            word_temp.append(name[i: i + 3])
        is_1 = self.__get_P_is_1(word_temp)
        is_0 = self.__get_P_is_0(word_temp)

        if is_1 > is_0:
            # res = '是'
            return 1
        elif is_1 < is_0:
            # res = '不是'
            return 0
        else:
            return -1
            # res = '你猜'
        # print name, '   ', res

    def test(self):
        """
        测试用，从正例和反例中随机1000个，共计2000个进行评价
        (其实这么评价并不准确
        """
        test_pos = sample(self.positive_example.word_list,1000)
        test_cou = sample(self.counter_example.word_list, 1000)

        count_right = 0
        count_wrong = 0
        for word in test_pos:
            res = self.API(word)
            if res == 1:
                count_right += 1
            else:
                count_wrong += 1

        for word in test_cou:
            res = self.API(word)
            if res == 0:
                count_right += 1
            else:
                count_wrong += 1

        print count_right,count_wrong
        print count_right / 2000
        print count_wrong / 2000

if __name__ == '__main__':
    # print positive_folder
    # print counter_folder_botany
    # print counter_folder_animal
    # print positive_files
    # print counter_files_animal
    # print counter_files_botany
    from time import clock
    start = clock()

    By = Byais()
    print len(By.positive_example.word_list)
    print By.API('朱元卿')
    print By.API('小板凳')
    print By.API('水杯')
    print By.API('水瓶')
    print By.API('肥皂')

    # -----------------------------------------
    '''
    count_right = 0
    count_wrong = 0
    test_data = load_one_file('test_pos.txt')
    for word in test_data:
        res = By.API(word)
        if res == 1:
            count_right += 1
        else:
            count_wrong += 1

    print count_right,count_wrong
    print count_right / 4000
    print count_wrong / 4000
    '''
    # -----------------------------------------

    # By.test()
    # print By.P_1, By.P_0
    # By.API('板凳')
    # By.API('狗蛋')
    # By.API('小花')
    # By.API('小饭桌')
    # By.API('饭桌')
    print 'Use time: ', clock() - start