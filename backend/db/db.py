import pymysql
import dbutils.pooled_db
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

POOL = dbutils.pooled_db.PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和    
    blocking=True,  # 是否在连接池用完时阻塞等待
    maxusage=None,  # 一个连接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表
    ping=0,  # ping Mysql服务端，检查是否服务可用
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database='ecommerce_dw',
    charset='utf8mb4'
)

def test_connection():
    """测试数据库连接"""
    try:
        conn = POOL.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"数据库连接成功，MySQL 版本: {version[0]}")
    except Exception as e:
        print(f"数据库连接失败: {e}")
    finally:
        cursor.close()
        conn.close()

def query(sql, params=None):
    """执行查询语句"""
    conn = POOL.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql, params)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

def execute(sql, params=None):
    """执行非查询语句"""
    conn = POOL.connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_connection()