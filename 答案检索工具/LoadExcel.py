# -*- coding: UTF-8 –*-
import os
import xlrd

class ExcelFile(object):
    def __init__(self):
        # self.wb=xlrd.open_workbook(os.getcwd()+'\\Data.xlsx')
        self.wwwb=xlrd.open_workbook(os.getcwd()+'\\shit.xlsx')
        self.shitsheet=self.wwwb.sheet_by_index(0)

    def SimpleQuestion(self,hang):
        AnswerIndex=int(self.shitsheet.cell_value(hang,4))
        Answer=unicode(self.shitsheet.cell_value(hang,AnswerIndex+4))
        return Answer

    def MultiQuestion(self,hang):
        AnswerIndex=int(self.shitsheet.cell_value(hang,4))
        Answer=""
        for item in str(AnswerIndex):
            Answer+=unicode(self.shitsheet.cell_value(hang,int(item)+4))
            Answer+=' # '
        return Answer

    def BoolQuestion(self,hang):
        return unicode(self.shitsheet.cell_value(hang,4))

    def LoadEx(self):
        self.Result=[]
        print self.shitsheet.nrows
        for i in range(1,self.shitsheet.nrows):
            Question=self.shitsheet.cell_value(i,2)
            if self.shitsheet.cell_value(i,0)==u'单选题':
                self.Result.append((Question,self.SimpleQuestion(i)))
            elif self.shitsheet.cell_value(i,0)==u'多选题':
                self.Result.append((Question,self.MultiQuestion(i)))
            elif self.shitsheet.cell_value(i,0)==u'判断题':
                self.Result.append((Question,self.BoolQuestion(i)))
            else:
                pass

    def LoadTextOld(self,somestring):
            FinalResult=open(os.getcwd()+'\\OldResult.txt','w')
            self.LoadEx()
            bitch=somestring.split('/')
            for item in bitch:
                Final=""
                item=item.strip('\n').strip(' ')
                for eachitem in self.Result:
                    if item in eachitem[0]: # there is 'in' before
                        Final+=eachitem[1]
                        Final+='\n'
                FinalResult.write('\n')
                FinalResult.write('题目：'+item.encode('utf-8'))
                FinalResult.write('\n')
                FinalResult.write('答案：\n'+Final.encode('utf-8')+'\n')
                FinalResult.write('\n')
                FinalResult.write('-'*100)
                FinalResult.write('\n')

    def LoadTextNew(self,somestring):
        FinalResult=open(os.getcwd()+'\\NewResult.txt','w')
        self.LoadEx()
        fhandle=open(os.getcwd()+'\\TheQuestion.txt','r')
        bitch=[item.strip('\n').strip(' ').strip('/').decode('utf-8') for item in fhandle.readlines()]
        for item in bitch:
            Final=""
            item=item.strip('\n').strip(' ')
            for eachitem in self.Result:
                if item in eachitem[0]: # there is 'in' before
                    Final+=eachitem[1]
                    Final+='\n'
            FinalResult.write('\n')
            FinalResult.write('题目：'+item.encode('utf-8'))
            FinalResult.write('\n')
            FinalResult.write('答案：\n'+Final.encode('utf-8')+'\n')
            FinalResult.write('\n')
            FinalResult.write('-'*100)
            FinalResult.write('\n')


if __name__=='__main__':
    somestr=u'''
                征收机关扣税异常业务明细表，反映当日与TIPS对账失败且需要手工调账的实时扣税和批量扣税的业务明细，是营业机构进行异常处理和账务调整的依据。/
        银行端缴税业务清单，反映营业机构上一日发生的银行端缴税/
        除9级、3级用户外，其余用户在当天正式签退后重新签到（    ）。/
        2djfasjklfdsajkl/
        新增人工用户时，登录认证方式默认为（   ），在新增用户交易中不可以修改，但可在用户新增成功后，通过修改用户功能，进行修改。/
        柜员指纹认证系统管理的指纹用户范围包括（）等系统用户，并可根据业务发展拓展管理范围。/
        关于以前年度差错处理，以下说法正确的是（    ）。/
档案库房监控录像应至少保存半年备查。/
生产系统中的对账签约，就是将银客/
临柜业务手工登记薄的设立，实行集中管理 归口审批的要求，必须经（）审批后方可设置。/
下列（）情况开户银行有权责令其停止违法活动，/
伪造的货币是指仿照真币的图案、形状、色彩，并利用挖补、/
测试用例1


'''
    Test=ExcelFile()
    Test.LoadTextOld(somestr)
    Test.LoadTextNew(somestr)