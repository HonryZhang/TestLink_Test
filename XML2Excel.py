#!/usr/bin/python
# _*_ coding:utf-8 _*_

#author:Hongrui
#date:2019/2/14

import sys,xlrd
from xlutils.copy import copy
reload(sys)
sys.setdefaultencoding('utf8')

import xmltodict,os

#去掉xml件中的部分html字符<p>,</p>,<br/>
def transfer_xml(xml_file):
    with open(xml_file,'r')as f:
        lines = f.readlines()
    with open(xml_file,'w')as f_w:
        for line in lines:
            if '<p>' or '</p>' in line:
                line = line.replace('<p>','').replace('</p>','')
            if '<br/>' in line:
                line = line.replace('<br/>','')
            f_w.write(line.decode('gbk').encode('utf-8'))
    new_file = xml_file
    return new_file

#将xml文件转换成json格式
def xml_2_json():
    new_file = transfer_xml(xml_file)

    xml = open(new_file,'r')
    xml_string = xml.read()
    xml.close()
    return xmltodict.parse(xml_string)

#读取json文件，取出需要的数据，以元组的形式存放到datas列表中，方便后续扩展成多用例批量导入
def get_datas():

    datas = []
    test = xml_2_json()
    #print json.dumps(test)
    case_name = test['rss']['channel']['item']['title']
    case_name = ' '.join(case_name.split())
    print case_name
    summary =  test['rss']['channel']['item']['summary']
    print summary
    steps = test['rss']['channel']['item']['customfields']['customfield'][1]['customfieldvalues']['steps']['step']
    precondition = '1.集群状态正常'+'\n'+'2.UI登录正常'+'\n'+'3.已经创建好数据池和缓存池'
    execution_type ='手动'
    importance = '高'

    actions = []
    expected_results=[]
    for i in range(len(steps)):
        step_number = steps[i]['index']
        action = ' '.join(steps[i]['step'].split())
        actions.append(step_number + '.' + action)
        expected_result = steps[i]['result']
        if expected_result is None:
            expected_result = ''
            expected_results.append(expected_result)
        else:
            expected_result = ' '.join(expected_result.split())
            expected_results.append(step_number + '.' + expected_result)

#将获取到的数据按元组形式存放到列表
    datas.append((case_name,summary,precondition,'\n'.join(actions),'\n'.join(expected_results),execution_type,importance))

    xml_to_xls(os.path.join('testCase', 'download_template.xls'), datas)

#读取datas列表中的元素，并按照列表对应的行列关系存入值
def xml_to_xls(file_path,datas):
    # 读取excel模版
    book = xlrd.open_workbook(file_path, formatting_info=True)
    # 复制读取的excel
    new_book = copy(book)

    # 读取复制的excel的第一个sheet
    sheet = new_book.get_sheet(0)
    # 默认第一行已经写好数据
    #line_num = 1

    # print len(datas)
    # 逐个读取datas列表的数据，并根据指定的行和列，写入到excel单元格中
    # 目前只支持单个用例的转换，导入
    for i in range(0, len(datas)):
        case_name, summary, preconditions, actions, expected_results, execution_type, importance=datas[i]

        sheet.write(1, 0, u'%s' % case_name)
        sheet.write(1, 1, u'%s' % summary)
        sheet.write(1, 2, u'%s' % preconditions)
        sheet.write(1, 3, u'%s' % actions)
        sheet.write(1, 4, u'%s' % expected_results)
        sheet.write(1, 5, u'%s' % execution_type)
        sheet.write(1, 6, u'%s' % importance)
        sheet.write(1, 7, u'%s' % author)

        #line_num += 1

    #log.info(u'用例集_<%s>中总共有<%d>条用例' % (suits_name.encode('utf-8'), line_num - 1))
    # 设置导出的excel的保存目录
    report_path = os.path.abspath(os.path.join('testCase'))
    #    print 'report_path is:',report_path
    if not os.path.exists(report_path):
        os.makedirs(report_path)

    # 将用例集下的所有用例保存为以用例集命名的xls文档中
    #log.info(u'开始保存用例')
    try:
        new_book.save(os.path.abspath(os.path.join(report_path, author+'.xls')))
    except Exception as e:
        #log.error(u'保存用例失败', str(e))
        print e
        sys.exit()

    else:
        print 'success'
        #log.info(u'导出用例成功，存放地址为:' + report_path)


if __name__=='__main__':
    xml_file = '/Users/xsky/Downloads/xml_test.xml'
    author = raw_input('Testlink login username:')
    get_datas()