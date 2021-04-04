from datetime import datetime
import pandas as pd
import pymysql
import Controller.DB.DB_basic as db_basic

# 打开数据库连接
db = pymysql.connect(host=db_basic.db['host'], user=db_basic.db['user'], password=db_basic.db['pwd'],
                     database=db_basic.db['db_name'])


def dataFormat(data):
    res = datetime.strptime(data, "%Y-%m-%d").strftime('%#d/%#m/%Y')

    # dataNew = data.split('-')
    # year = dataNew[0]
    # month = dataNew[1]
    # day = dataNew[2]
    # res = day + "/" + month + "/" + year
    return res

def dataFormat2(data):
    dataNew = data.split('-')
    year = dataNew[0]
    month = dataNew[1]
    day = dataNew[2]
    res = day + "/" + month + "/" + year

    return res


def selectComment(data):
    dataInput = dataFormat(data)
    dataInput2 = dataFormat2(data)

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT comment_text FROM comment WHERE comment_datetime = '" + dataInput +"' or comment_datetime = '" + dataInput2 + "'"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()

    except:
        print("Error: unable to fetch data")

    res = list(results)
    res_new = pd.Series(res)

    print(res)
    print(res_new)
    # 关闭数据库连接
    db.close()

    return res_new

# selectComment('2020-09-09')
