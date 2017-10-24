# -*- coding: UTF-8 –*-
from __future__ import division
import os
import math
import sqlite3
import time

# 2017-04-11：TODO: 在求平均哪里有问题，从哪里开始修改

movies_data_path = os.getcwd() + "\Data\movies.dat"
ratings_data_path = os.getcwd() + "\Data\\ratings.dat"
users_data_path = os.getcwd() + "\Data\\users.dat"
db_path = os.getcwd() + '\Rating.db'
db2_path = os.getcwd()+'\Similiar.db'


class User(object):
    def __init__(self):
        self.UserId = 0
        self.Gender = "M"
        self.Age = 0
        self.Occupation = "Stu"
        self.RatingData = {}


class Rating(object):
    def __init__(self):
        self.UserId = 0
        self.MovieId = 0
        self.Rating = 0


class Movie(object):
    def __init__(self):
        self.MovieId = 0
        self.Title = "Title"
        self.Genres = "Commendy"


class DataSet(object):
    def __init__(self):
        self.hdl_movies = open(movies_data_path, 'r')
        self.hdl_users = open(users_data_path, 'r')
        self.hdl_ratings = open(ratings_data_path, 'r')
        self.lst_users = []
        self.dic_ratings = {}  # id: userid,value:list of rating object
        self.lst_movies = []
        self.lst_rating = []
        self.dic_average = {}  # 放每个user打分的平均值，id:userid ,value:average

        # 加载数据
        self.load_movie()
        self.load_user()
        self.count_average()

        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

        self.conn2 = sqlite3.connect(db2_path)  #
        self.similiar_cur = self.conn2.cursor() # 专用给相似度矩阵数据的数据库

    def load_movie(self):
        print '加载movies.dat中......',
        for eachline in self.hdl_movies:
            lst_res = eachline.split("::")
            obj_movie = Movie()
            obj_movie.MovieId, obj_movie.Title, obj_movie.Genres = lst_res[0], lst_res[1], lst_res[2]
            self.lst_movies.append(obj_movie)  # 把movie对象存在list中
        print '加载movies完成'

    def __load_rating(self):
        print '加载Rating.dat中......',
        for eachline in self.hdl_ratings:
            lst_res = eachline.split("::")
            obj_rating = Rating()
            obj_rating.UserId = lst_res[0]
            obj_rating.MovieId = lst_res[1]
            obj_rating.Rating = lst_res[2]

            self.lst_rating.append(obj_rating)

            if lst_res[0] not in self.dic_ratings:
                self.dic_ratings.setdefault(lst_res[0], [])

            self.dic_ratings[lst_res[0]].append(obj_rating)  # 将rating对象添加到字典的list中
        print '加载rating完成'

    def load_user(self):
        self.__load_rating()  # 加载RatingData
        print '加载users.dat中......',
        for eachline in self.hdl_users:
            lst_res = eachline.split("::")
            obj_user = User()
            obj_user.UserId = lst_res[0]
            obj_user.Gender = lst_res[1]
            obj_user.Age = lst_res[2]
            obj_user.Occupation = lst_res[3]
            obj_user.RatingData = self.dic_ratings[lst_res[0]]
            self.lst_users.append(obj_user)
        print '加载users完成'

    def count_average(self):
        for userid_iter in self.dic_ratings:
            average = 0
            for obj_iter_rating in self.dic_ratings[userid_iter]:  # 取出每个rating对象
                average += int(obj_iter_rating.Rating)

            average /= len(self.dic_ratings[userid_iter])

            self.dic_average[userid_iter] = average  # 把平均值存起来

    def tools_delete_userrating(self, userid):
        return [item for item in self.lst_rating if item.UserId != userid]  # item是rating object

    def tools_similarity(self, dic_var_movie1, dic_var_movie2):
        """
        给定两个电影的打分list，返回相似度
        :param dic_var_movie1:  userid:rating
        :param dic_var_movie2:  userid:rating
        :return:
        """
        numerator = 0
        denominator_1 = 0
        denominator_2 = 0

        for index_movie in dic_var_movie1:  # 这里两个dict长度应该是相等的
            user_average = self.dic_average[index_movie]  # 获取平均评分

            numerator += (float(dic_var_movie1[index_movie]) - user_average) * (
                float(dic_var_movie2[index_movie]) - user_average)

            denominator_1 += (float(dic_var_movie1[index_movie]) - user_average) ** 2
            denominator_2 += (float(dic_var_movie2[index_movie]) - user_average) ** 2

        denominator = math.sqrt(denominator_1) * math.sqrt(denominator_2)

        if numerator != 0 and denominator_1 != 0 and denominator_2 != 0:
            similiar = numerator / denominator
        else:
            similiar = -2  # 说明是有问题的状态码

        return similiar

    def tools_NR(self, userid, obj_var_movie):
        """
        进行归一化，如果用户对当前的movie没有评分，就返回0
        :param userid:
        :param obj_var_movie:
        :return:
        """
        str_select = "SELECT rating FROM Rating WHERE userid=" + str(userid) + " AND movieid=" + str(
            obj_var_movie.MovieId) + ";"
        # print str_select
        for obj_iter_rating in self.lst_rating:
            # print obj_iter_rating.UserId,userid,'\t',obj_iter_rating.MovieId,obj_var_movie.MovieId
            this_rating = self.cur.execute(str_select).fetchone()
            # print userid, obj_var_movie.MovieId, '打分：', this_rating
            if obj_iter_rating.UserId == userid and obj_iter_rating.MovieId == obj_var_movie.MovieId:
                return float(this_rating[0]) * 0.5 - 1.5  # 归一化公式就是这么写的
            else:
                return 0

    def possible(self, userid, obj_movie):
        """
        计算userid对movieid的打分
        :param userid:
        :param movieid:
        :return:
        """
        # 计算movieid和剩下的movie的相似度
        dic_user_rating = {}  # { movieid：[user1,user2] } 电影对应的用户id
        for obj_iter_rating in self.lst_rating:
            if obj_iter_rating.MovieId not in dic_user_rating:
                dic_user_rating.setdefault(obj_iter_rating.MovieId, [])
            dic_user_rating[obj_iter_rating.MovieId].append(obj_iter_rating)  # 将rating object 放进去

        numerator, denominator = 0, 0

        # 删除一个movie，得到新的movie list，后面的对这个新list进行迭代
        lst_new_movies = self.lst_movies
        lst_new_movies.pop(lst_new_movies.index(obj_movie))  # 将这个movie去除，得到新的movie list

        # 先取出一个movie object，依次处理 | 当前movie与剩下的movie的相似度,即从剩下的取一个movie object
        for obj_iter_movie in lst_new_movies:
            # 先计算这个movie与待求得movie的相似度，然后计算用户对这个movie的评分（可能需要归一化）
            # 将以上步骤的结果相乘再求和就是分子部分的结果
            # 对相似度求和就是分母部分

            dic_source_movie = {}  # 源电影的打分情况 格式为：{ Userid：打分 }
            dic_sim_movie = {}  # 待比较movie的打分情况 格式为：{userid：打分}

            try:
                # for item in [ rating obj1,rating obj2...] 先找对source movie的
                for obj_iter_rating in dic_user_rating[obj_movie.MovieId]:
                    dic_source_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating  # user id ： rating

                for obj_iter_rating in dic_user_rating[obj_iter_movie.MovieId]:
                    dic_sim_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating
            except KeyError, e:
                print 'Error in :', obj_movie.MovieId, obj_iter_movie.MovieId, e
                continue
            # for obj_iter_rating in self.dic_ratings[userid]:  # 对评分数据进行迭代，获取打分情况。先获取所有打分数据，下一步再进行处理
            #     # print lst_ratings
            #     # for obj_iter_rating in lst_ratings:
            #     if obj_iter_rating.MovieId == obj_movie.MovieId:  # 选择对当前电影打过分的用户
            #         dic_source_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating
            #     elif obj_iter_rating.MovieId == obj_iter_movie.MovieId: # 对选出的电影打分的用户
            #         dic_sim_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating

            # 以下操作是提取出对源movie和现有movie都评分的用户，
            set_source = set(dic_source_movie.keys())
            set_sim = set(dic_sim_movie.keys())
            set_res = set_source.intersection(set_sim)  # 里面元素是userid
            dic_new_source, dic_new_sim = {}, {}
            for userid_iter in set_res:
                dic_new_source[userid_iter] = dic_source_movie[userid_iter]
                dic_new_sim[userid_iter] = dic_sim_movie[userid_iter]

            similiar_movie_movie = self.tools_similarity(dic_new_source, dic_new_sim)  # 计算相似度

            denominator += math.fabs(similiar_movie_movie)  # 这是分母

            NR_un = self.tools_NR(userid, obj_iter_movie)

            numerator += (similiar_movie_movie * NR_un)

        return numerator / denominator

    def recommend(self, userid):
        """
        推荐方法，给定userid，给出他可能感兴趣的电影
        :param userid:
        :return:
        """
        dic_possible = {}  # movieid：possible
        for obj_iter_movie in self.lst_movies[0:1]:  # 依次计算userid对每个movies的possible   obj_iter_movie是movie对象
            possible = self.possible(userid, obj_iter_movie)  # 概率
            dic_possible[obj_iter_movie.MovieId] = possible

        print "相似度为：", dic_possible

    def count_similiar(self):
        """
        这个函数用来计算相似度矩阵，计算好的结果放在数据库中
        """
        # 计算movieid和剩下的movie的相似度
        dic_user_rating = {}  # { movieid：[rating obj1,rating obj2] } 对应的rating object
        for obj_iter_rating in self.lst_rating:
            if obj_iter_rating.MovieId not in dic_user_rating:
                dic_user_rating.setdefault(obj_iter_rating.MovieId, [])
            dic_user_rating[obj_iter_rating.MovieId].append(obj_iter_rating)  # 将rating object 放进去

        # 维护一个list，存放已经计算过的数据,格式为：[ set( mov1,mov2),set(mov2,mov3)。。。]
        lst_finish = []

        # 维护一个list，存放已经在数据库中的表格，格式为：[(u'SIMILIAR_219',),(u'SIMILIAR_220',),(u'SIMILIAR_222',) ]
        lst_tables = self.similiar_cur.execute("SELECT name FROM sqlite_master;").fetchall()


        # 开始计算相似度矩阵
        for obj_iter_movie in self.lst_movies:
            lst_new_movies = [item for item in self.lst_movies if item.MovieId != obj_iter_movie.MovieId]

            # 判断数据库中是否有这个表，如果有就continue
            # print (("SIMILIAR_"+str(obj_iter_movie.MovieId)).decode('utf-8'),)
            if (("SIMILIAR_"+str(obj_iter_movie.MovieId)).decode('utf-8'),) in lst_tables:
                print "SIMILIAR_",str(obj_iter_movie.MovieId),"已经存在！"
                continue

            str_create = "CREATE TABLE SIMILIAR_"+str(obj_iter_movie.MovieId)+"(movieid1 VARCHAR (20),movieid2 VARCHAR (20),similiar VARCHAR (100));"
            self.similiar_cur.execute(str_create)
            print str_create,'\t',

            # 源电影的打分情况 格式为：{ Userid：打分 }
            dic_source_movie = {}
            if obj_iter_movie.MovieId in dic_user_rating:  # 说明这个movie有用户的评分数据
                # for item in [ rating obj1,rating obj2...] 先找对source movie的
                for obj_iter_rating in dic_user_rating[obj_iter_movie.MovieId]:
                    dic_source_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating  # user id ： rating
            else:
                continue  # 跳过底下的逻辑

            # 内层迭代，对剩下的计算相似度
            for obj_iter_each_movie in lst_new_movies:
                dic_sim_movie = {}  # 待比较movie的打分情况 格式为：{userid：打分}
                if obj_iter_each_movie.MovieId in dic_user_rating:
                    for obj_iter_rating in dic_user_rating[obj_iter_each_movie.MovieId]:
                        dic_sim_movie[obj_iter_rating.UserId] = obj_iter_rating.Rating
                else:  # 说明迭代电影没有评价数据
                    continue  # 跳过底下逻辑

                # 判断当前的两个movie是否计算过
                if set([obj_iter_movie.MovieId, obj_iter_each_movie.MovieId]) in lst_finish:
                    continue  # 跳到下一个for内层循环

                set_source = set(dic_source_movie.keys())
                set_sim = set(dic_sim_movie.keys())
                set_res = set_source.intersection(set_sim)  # 里面元素是userid
                dic_new_source, dic_new_sim = {}, {}
                for userid_iter in set_res:
                    dic_new_source[userid_iter] = dic_source_movie[userid_iter]
                    dic_new_sim[userid_iter] = dic_sim_movie[userid_iter]

                similiar = self.tools_similarity(dic_new_source, dic_new_sim)  # 计算相似度
                str_insert = "INSERT INTO SIMILIAR_"+str(obj_iter_movie.MovieId)+" VALUES ("+str(obj_iter_movie.MovieId)+","+str(obj_iter_each_movie.MovieId)+","+str(similiar)+");"
                # print str_insert
                self.similiar_cur.execute(str_insert)
                # print str_insert
                lst_finish.append(set([obj_iter_movie.MovieId, obj_iter_each_movie.MovieId]))  # 加入list中

            print '完成。'

            self.conn2.commit()
        self.close_all_db()

    def close_all_db(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()
        self.similiar_cur.close()
        self.conn2.commit()
        self.conn2.close()

class TestFunction(object):
    def __init__(self):
        self.Data = DataSet()
        self.dic_test_1 = {"u1": 4, "u2": 4, "u3": 5}
        self.dic_test_2 = {"u1": 3, "u2": 4, "u3": 4}

    def Test(self):
        # self.Data.recommend(str(1))  # 括号内是userid
        self.Data.count_similiar()
        # print self.Data.tools_similarity(self.dic_test_1,self.dic_test_2)
        # for i in self.Data.dic_ratings:
        #     print i,self.Data.dic_ratings[i]
        # print len(self.Data.dic_ratings)


if __name__ == "__main__":
    start = time.clock()

    demo = TestFunction()
    demo.Test()

    end = time.clock()
    print '一共耗时: ', (end - start)
