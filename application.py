from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql
import urllib.request, urllib.parse

application = Flask(__name__)
today = datetime.today().strftime('%Y.%m.%d')

def DB_select_company(what,where="",order='asc'):
    conn = pymysql.connect(host='localhost', user='root', password='rlagmlwn', db='company')
    try:
        with conn.cursor() as curs:
            if what == "all":
                query = 'select title,comp_name,place,e_date from companies where state="진행중"'
                if where:#회사명지정
                    query += 'and '+where
            else:
                query = 'select '+what+' from companies where state="진행중"'
            if order == 'asc': # 마감임박
                query += ' order by e_date asc limit 15'
            elif order == 'desc': # 최신공고
                query += ' order by s_date desc limit 15'
            curs.execute(query)
            return curs.fetchall()
        conn.commit()
    finally:
        conn.close()
        
def DB_select_test(table):
    conn = pymysql.connect(host='localhost', user='root', password='rlagmlwn', db='test')
    try:
        with conn.cursor() as curs:
            if table == 'engineering':
                query = 'select title, one_regist, one_test, one_pass, two_regist,two_test, two_pass from '+table
            elif table == 'toeic':
                query = 'select test, announce, regist_end, url from '+table
            elif table == 'history':
                query = 'select name, regist, test, announce from '+table
            curs.execute(query)
            return curs.fetchall()
        conn.commit()
    finally:
        conn.close()

def return_dataSend(description, comp_name=[],content='',order='asc'):
    url = DB_select_company("url",order=order)
    description = [" ".join([str(y)+"\n" for y in list(x)]) for x in description]
    comp_name = [x[0] for x in comp_name]
    url = [x[0] for x in url]
    cards = []
    for i in range(len(description)):
        if comp_name:
            comp = comp_name[i]
        else:
            comp = content
        parsing = description[i].split('\n')
        card = {
            "title": '✔"'+comp+'" 관련 채용 정보입니다',
            "description":'👉🏻채용제목: '+parsing[0]+'\n👉🏻기관명: '+comp+'\n👉🏻근무지: '+parsing[2]+'\n👉🏻마감일: '+parsing[3],
            "buttons":[
                {
                    "type":"url",
                    "label":"더 알아보기",
                    "data":{
                        "url": url[i]
                    }
                }
            ]
        }
        cards.append(card)
    dataSend = {
        "contents": [
            {
                "type": "card.image",
                "cards": cards
            }
        ]
    }
    return dataSend
        
@application.route("/")
def Hello():
    return ' '

@application.route("/company",methods=['POST'])
def Comp():
    content = request.get_json()
    content = content['userRequest']['utterance']
    where = 'comp_name like "%'+content+'%"'
    description = DB_select_company("all",where)
    url = DB_select_company("url")
    cards=[]
    if description:
        dataSend = return_dataSend(description,content=content)
    else:
        dataSend = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text":"😢 '"+content+"'에 관한 채용정보가 없습니다."
                        }
                    }
                ]
            }
        }
    return jsonify(dataSend)

@application.route("/message", methods=['POST'])
def Message():
    content = request.get_json()
    content = content['userRequest']
    content = content['utterance']
    comp_name_finish = DB_select_company("comp_name")
    comp_name_new = DB_select_company("comp_name",order='desc')
    
    if content == "마감임박":
        description = DB_select_company("all",order='asc')
        dataSend = return_dataSend(description,comp_name_finish,order='asc')
    elif content == "최신공고":
        description = DB_select_company("all",order='desc')
        dataSend = return_dataSend(description,comp_name_new,order='desc')
    return jsonify(dataSend)

@application.route("/test",methods=['POST'])
def test():
    content = request.get_json()
    content = content['userRequest']
    content = content['utterance']
    dataSend = {}
    if content == '정보처리기사' or content == '정처기':
        description = DB_select_test('engineering')
        cards = []
        for i in description:
            if i[1] and i[4]:
                one_regist_start = i[1].split('~')[0]
                one_regist_end = i[1].split('~')[1]
                one_regist_start = ''.join(one_regist_start.split())
                one_regist_end = ''.join(one_regist_end.split())
                two_regist_start = i[4].split('~')[0]
                two_regist_end = i[4].split('~')[1]
                two_regist_start = ''.join(two_regist_start.split())
                two_regist_end = ''.join(two_regist_end.split())
                one_test = i[2].split('~')[0]
                two_test = i[5].split('~')[0]
                if today < one_test and today <= one_regist_end:
                    card = {
                        "title": '✔ '+i[0]+' 필기',
                        "description":'👉🏻원서접수: '+i[1]+'\n👉🏻필기날짜:'+i[2],
                        "buttons":[
                            {
                                "type":"url",
                                "label":i[0]+" 필기",
                                "data":{
                                    "url":"http://www.q-net.or.kr/crf005.do?id=crf00505&jmCd=1320"
                                }
                            }
                        ]
                    }
                    cards.append(card)
                if today < two_test and today <= two_regist_end:
                    card = {
                        "title": '✔ '+i[0]+' 실기',
                        "description":'👉🏻원서접수: '+i[4]+'\n👉🏻실기날짜:'+i[5],
                        "buttons":[
                            {
                                "type":"url",
                                "label":i[0]+" 실기",
                                "data":{
                                    "url":"http://www.q-net.or.kr/crf005.do?id=crf00505&jmCd=1320"
                                }
                            }
                        ]
                    }
                    cards.append(card)
                card = {} # for----->
        if not cards:
            dataSend = {
                        "contents":[
                            {
                              "type":"card.text",
                              "cards":[
                                {
                                  "description":'😢 올해 예정된 시험이 모두 끝났습니다.',
                                  "buttons":[
                                    {
                                      "type":"url",
                                      "label":'더 알아보기',
                                      "data":{
                                          "url":"http://www.q-net.or.kr/crf005.do?id=crf00505&jmCd=1320"
                                      }
                                    }
                                  ]
                                }
                              ]
                            }
                          ]
                        }
        else:
            dataSend = {
                "contents": [
                    {
                        "type": "card.image",
                        "cards": cards
                    }
                ]
            }#정처기------>
    elif content=="토익" or content=="toeic":
        description = DB_select_test('toeic')
        cards = []
        for i in description:
            card = {
                "title": '✔ '+i[0],
                "description": '👉🏻 '+i[1]+'\n👉🏻 '+i[2],
                "buttons":[
                    {
                        "type":"url",
                        "label":"더 알아보기",
                        "data":{
                            "url": i[3]
                        }
                    }
                ]
            }
            cards.append(card)
        dataSend = {
            "contents": [
                {
                    "type": "card.image",
                    "cards": cards
                }
            ]
        }
    elif content=='한국사' or content=='한국사 시험':
        description = DB_select_test('history')
        cards = []
        for i in description:
            parsing = i[2].replace('년 ','.').replace('월','.').replace('일','').replace(' ','').split('(')[0].split('.')
            test = datetime(int(parsing[0]),int(parsing[1]),int(parsing[2])).strftime('%Y.%m.%d')
            parsing = i[1].split('~')[1].split('(')[0].replace('년 ','.').replace('월 ','.').replace('일','').replace(' ','').split('.')
            regist = datetime(int(parsing[0]),int(parsing[1]),int(parsing[2])).strftime('%Y.%m.%d')
            if today < test and today < regist: # 시험일자, 접수일자 지난 것은 출력 X
                card = {
                    "title": '✔ '+i[0]+' 한국사능력검정시험',
                    "description": '👉🏻접수기간: '+i[1]+'\n👉🏻시험일시: '+i[2]+'\n합격자발표: '+i[3],
                    "buttons":[
                        {
                            "type":"url",
                            "label":"더 알아보기",
                            "data":{
                                "url": 'http://www.historyexam.go.kr/pst/view.do?bbs=noti&pst_sno=1000029601&pageIndex=1&searchCondition=pstTitle&searchKeyword=&pageUnit=10'
                            }
                        }
                    ]
                }
                cards.append(card)
        if not cards:
            dataSend = {
                        "contents":[
                            {
                              "type":"card.text",
                              "cards":[
                                {
                                  "description":'😢 올해 예정된 시험이 모두 끝났습니다.',
                                  "buttons":[
                                    {
                                      "type":"url",
                                      "label":'더 알아보기',
                                      "data":{
                                          "url":"http://www.historyexam.go.kr/pst/view.do?bbs=noti&pst_sno=1000029601&pageIndex=1&searchCondition=pstTitle&searchKeyword=&pageUnit=10"
                                      }
                                    }
                                  ]
                                }
                              ]
                            }
                          ]
                        }
        else:
            dataSend = {
                "contents": [
                    {
                        "type": "card.image",
                        "cards": cards
                    }
                ]
            }
    return jsonify(dataSend)
    
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=6666)
