from datetime import datetime
import pymysql

def dateFormat(date):
    res = datetime.strptime(date, "%Y-%m-%d").strftime('%Y/%#m/%#d')
    return res

def getPrice(date):
    db = pymysql.connect(host="localhost", user="root", password="", database="bitcoin")
    dataInput = dateFormat(date)

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT closePrice FROM price WHERE date = '" + dataInput + "'"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()

    except:
        print("Error: unable to fetch data")



    print(results)
    # 关闭数据库连接
    db.close()

    return results

# getPrice('2020-09-09')