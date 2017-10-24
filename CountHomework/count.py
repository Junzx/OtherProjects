# -*- coding: UTF-8 –*-
import os
import re
from time import sleep

class FileProcess(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.rewords_1 = '<div class="dP0" [\s\S]*?</div>'  # 抽取发件人
        self.rewords_2 = '<div class="il0" [\s\S]*?</div>'  # 抽取邮件标题
        self.rewords_3 = '<div class="nui-ico[\s\S]*?</div>'  # 判断是否包含附件

        self.html_files = [self.filepath + '\\' + item for item in os.listdir(filepath) if "html" in item]

    def fileprocess(self):
        self.delete_useless_files()
        for index in range(len(self.html_files)):
            self.fp(self.html_files[index], self.html_files[index].split('\\')[-1].split('.')[0])

    def delete_useless_files(self):
        files = os.listdir(self.filepath)
        for eachitem in files:
            if '.' not in eachitem:
                str_tmp_path = self.filepath + '\\' + eachitem
                for eachfile in os.listdir(str_tmp_path):
                    if 'js' in eachfile:
                        tmp_filepath = str_tmp_path + '\\' + eachfile
                        os.system('del ' + tmp_filepath)
        print '删除js...',
        sleep(2)
        print '删除成功！'

    def fp(self, filepath, filename):
        with open(filepath, 'r') as fhandle:
            File = fhandle.read()
            writefile = open(self.filepath + '\\' + filename + '.txt', 'a+')
            final_names = []  # 发件人姓名
            final_titles = []  # 邮件主题
            final_flags = []  # 是否有附件

            pattern = re.compile(self.rewords_1)  # 编译第一个表达式
            lst_res_name = re.findall(pattern, File)
            for item in lst_res_name:
                if "手机号码邮箱" not in item and "易信用户" not in item and "星标联系人" not in item:
                    final_names.append(item[item.index("title") + 9:item.index("</span>")])
                    # print item[item.index("title") + 9:item.index("</span>")]
                elif "手机号码邮箱"in item:
                    final_names.append(item[item.find("手机号码邮箱") + 24:item.index("</span>")])
                elif "易信用户" in item:
                    final_names.append(item[item.find("易信用户")+18:item.find("</span>")])
                elif "星标联系人" in item:
                    final_names.append(item[item.find("星标联系人")+21:item.find("</span>")])

            pattern = re.compile(self.rewords_2)  # 编译第二个表达式
            lst_res_title = re.findall(pattern, File)
            final_titles = [item[item.index("<span") + 18:item.index("</span>")] for item in lst_res_title]

            pattern = re.compile(self.rewords_3)  # 编译第三个表达式
            lst_res_flag = re.findall(pattern, File)
            for item in lst_res_flag:
                if "此邮件包含附件" in item:
                    final_flags.append(1)
                elif "visibility:hidden" in item:
                    final_flags.append(-1)

            for i in range(len(final_names)):
                # print i,'\t',self.final_names[i],self.final_titles[i]
                tmp_string = str(i) + '\t' + str(final_flags[i]) + '\t' + final_names[i] + '\t\t\t' + final_titles[i]+'\n'
                writefile.write(tmp_string)
            writefile.close()
            print filename, '.txt   is ok!'


if __name__ == '__main__':
    fp = FileProcess(r'D:\AllDownLoads\format')
    fp.fileprocess()
