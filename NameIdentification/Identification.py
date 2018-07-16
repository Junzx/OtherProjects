# -*- coding: UTF-8 -*-
"""
作者你这是瞎编的方法吧我这小暴脾气实现不出来(╯‵□′)╯︵┻━┻
update:修改了文件的路径，本方法使用一种十分不靠谱的方法，所以不管了
"""
from __future__ import division
from os import listdir,getcwd
from copy import deepcopy
from math import sqrt,log
import cPickle as pickle

corpus_folder = getcwd() + r'\NameCorpus'
files = [corpus_folder + '\\' + file for file in listdir(corpus_folder)]

def load_one_file(file_path):
    """
    :param file_path:
    :return: a list
    """
    with open(file_path,'r') as hdl:
        return map(lambda x:x.strip('\n'),hdl.readlines())

class Name(object):
    def __init__(self):
        self.two_words_name, self.three_words_name, self.four_words_name, self.other_name, self.first_name = self.__get_names()
        self.dic_first_name = self.__get_first_name_dic()
        self.dic_first_word = self.__get_first_word_dic()
        self.dic_last_word = self.__get_last_word_dic()
        self.dic_all_word = self.__get_all_word_dic()
        self.all_word = sum(self.dic_all_word.values())


    def __get_names(self):
        """
        按照长短获取姓名list
        """
        two_words_name = []
        three_words_name = []
        four_words_name = []
        other_name = []
        first_name = []
        for file in files:
            data = load_one_file(file)
            for name in data:
                if len(name) / 3 == 2:
                    two_words_name.append(name)
                    first_name.append(name[:3])
                elif len(name) / 3 == 3:
                    three_words_name.append(name)
                    first_name.append(name[:3])
                elif len(name) / 3 == 4:
                    four_words_name.append(name)
                else:
                    other_name.append(name)
        print '读取所有文件完成！'
        return tuple(two_words_name),tuple(three_words_name),tuple(four_words_name),tuple(other_name),tuple(first_name)

    def print_attribute_length(self):
        """
        统计结果:
        len of two word: 425649  | 占比： 0.1790
        len of three word: 1914763  | 占比： 0.8056
        len of four word: 36300  | 占比： 0.0152
        结论：
        在不考虑其他词语的情况下，优先考虑单姓氏的词语，即二字、三字。
        """
        len_two = len(self.two_words_name)
        len_three = len(self.three_words_name)
        len_four = len(self.four_words_name)
        # len_other = len(self.other_name)
        all_count = len_two + len_three + len_four# + len_other
        print 'len of two word:', len(self.two_words_name), ' | 占比：', str(len_two / all_count)[:6]
        print 'len of three word:',len(self.three_words_name), ' | 占比：', str(len_three / all_count)[:6]
        print 'len of four word:',len(self.four_words_name), ' | 占比：', str(len_four / all_count)[:6]
        # print 'len of other word:',len(self.other_name), ' | 占比：', str(len_other / all_count)[:6]

    def __get_first_name_dic(self):
        """
        对于二三字的姓名，找到所有的姓氏
        """
        first_name = []
        for name in self.two_words_name:
            first_name.append(name[:3])
        for name in self.three_words_name:
            first_name.append(name[:3])
        dic_first_name = self.__list_2_dic(first_name)
        return dic_first_name
        #---------------------------------
        # print "共有: ",len(set(first_name))
        # print len(first_name)
        # for index,i in enumerate(list(set(first_name))):
        #     print index, ' ',i,repr(i)

    def __get_first_word_dic(self):
        lst_first_word = []

        for name in self.three_words_name:
            word = name[3:6]
            lst_first_word.append(word)

        dic_first_word = self.__list_2_dic(lst_first_word)
        return dic_first_word

    def __get_last_word_dic(self):
        lst_end_word = []
        for name in self.two_words_name:
            word = name[3:]
            lst_end_word.append(word)

        for name in self.three_words_name:
            word = name[-3:]
            lst_end_word.append(word)

        dic_end_word = self.__list_2_dic(lst_end_word)
        return dic_end_word

    def __get_all_word_dic(self):
        word = []
        for name in self.two_words_name:
            word.append(name[:3])
            word.append(name[3:])

        for name in self.three_words_name:
            word.append(name[:3])
            word.append(name[3:6])
            word.append(name[6:])
        return self.__list_2_dic(word)

    def __list_2_dic(self,lst_words):
        """
        Count a numbers
        :param lst_words:
        :return:
        """
        dic_return = {}
        for word in lst_words:
            if word not in dic_return:
                dic_return.setdefault(word,0)
            dic_return[word] += 1
        return deepcopy(dic_return)

    def __print_sort_dic(self,dic):
        all = sum(dic.values())
        print '共计：',all
        for i in sorted(dic.items(), key=lambda e:e[1], reverse=True)[:100]:
            print i[0],' : ',i[1],' | 占比：', str(i[1] / all)

    def __estimate_two_word_name(self,name):
        """
        name 是一个两个字的字符串
        """
        first_name = name[:3]
        last_word = name[3:]
        F_i = self.dic_first_name[first_name] / self.dic_all_word[first_name]
        F_k = self.dic_first_name[last_word] / self.dic_all_word[last_word]
        E_k = self.dic_last_word[last_word] / self.dic_all_word[last_word]

        p_i_k = F_i * E_k

        # T_min_i = F_i * min(E_k)
        T_min_i = F_i * E_k
        if F_i == 1:
            a_i = 1
        elif 0 < F_i < 1:
            a_i = (1 + sqrt(F_i)) / 2

        B_i = a_i * log(T_min_i)

        print log(p_i_k),B_i
        if log(p_i_k) > B_i:
            print '是'
        else:
            print '非',p_i_k

    def __estimate_three_word_name(self,name):
        """
        name是一个三字姓名
        """
        first_name = name[:3]
        first_word = name[3:6]
        last_word = name[6:9]
        F_i = self.dic_first_name[first_name] / self.dic_all_word[first_name]
        M_j = self.dic_first_word[first_word] / self.dic_all_word[first_word]
        E_k = self.dic_last_word[last_word] / self.dic_all_word[last_word]

        p_i_j_k = F_i * M_j * E_k
        T_min_i = F_i * min([M_j,E_k])
        if F_i == 1:
            a_i = 1
        elif 0 < F_i < 1:
            a_i = (1 + sqrt(F_i)) / 2
        B_i = a_i * log(T_min_i)

        print log(p_i_j_k),B_i
        if log(p_i_j_k) > B_i:
            print '是'
        else:
            print '非',p_i_j_k

    def main(self):
        self.__estimate_two_word_name('朱红')
        # self.__estimate_three_word_name('凳子') # 报错
        self.__estimate_three_word_name('朱元卿')
        self.__estimate_three_word_name('张东海')
        self.__estimate_three_word_name('肖会兰')




if __name__ == '__main__':
    from time import clock
    start = clock()

    name = Name()
    # name.print_attribute_length()
    name.main()

    # ---------------------------------------
    print 'Use: ', clock() - start