from datetime import datetime
import pymysql
import Controller.DB.DB_basic as db_basic

def dateFormat(date):
    res = datetime.strptime(date, "%Y-%m-%d").strftime('%Y/%#m/%#d')
    return res

def getTrend(date):
    db = pymysql.connect(host=db_basic.db['host'], user=db_basic.db['user'], password=db_basic.db['pwd'], database=db_basic.db['db_name'])
    dataInput = dateFormat(date)

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT trends FROM aggregation WHERE date = '" + dataInput + "'"
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

# getTrend('2020-09-09')