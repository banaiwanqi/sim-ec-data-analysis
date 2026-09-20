import pymysql
import random
from datetime import datetime, timedelta

# ========== 数据库配置 ==========
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'soldierbar8',
    'charset': 'utf8mb4',
    'database': 'ecommerce_dw'
}

def connect_db(database=None):
    """建立数据库连接（database=None 则不指定库，用于执行建库语句）"""
    config = dict(DB_CONFIG)
    if database:
        config['database'] = database
    else:
        config.pop('database', None)
    return pymysql.connect(**config)

def create_tables():
    """基于 models.sql 创建表结构（models.sql 为唯一建表源，不做任何修改）"""
    import os
    import re

    # 读取 models.sql
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sql')
    with open(sql_path, 'r', encoding='utf8') as f:
        sql_content = f.read()

    # 连接时不指定 database，让 CREATE DATABASE / USE 语句自行生效
    conn = connect_db(None)
    cursor = conn.cursor()

    # 先清理可能存在的旧表（在当前连接默认库上，若已存在 ecommerce_dw）
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.fact_order")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.dim_user")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.dim_goods")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.dim_time")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.dim_area")
        cursor.execute("DROP TABLE IF EXISTS ecommerce_dw.dim_pay")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("旧表已清理")
    except Exception:
        pass

    # 剥离行注释（-- 开头到行尾），避免注释干扰语句分割
    sql_clean = re.sub(r'--.*?$', '', sql_content, flags=re.MULTILINE)
    # 按分号分割，逐条执行
    statements = [stmt.strip() for stmt in sql_clean.split(';') if stmt.strip()]

    for stmt in statements:
        try:
            cursor.execute(stmt)
            conn.commit()
        except Exception as e:
            print(f"执行失败: {stmt[:60]}... -> {e}")

    print("表结构创建完成")
    cursor.close()
    conn.close()

def insert_dimension_tables():
    """插入维度表数据"""
    conn = connect_db('ecommerce_dw')
    cursor = conn.cursor()
    
    # ========== 1. 用户维度表 dim_user（500条） ==========
    user_genders = [1, 2]  # 1男 2女
    user_levels = [1, 2, 3]  # 会员等级
    
    user_count = 0
    for i in range(1, 501):
        name = f'A{i}'
        gender = random.choice(user_genders)
        age = random.randint(18, 60)
        level = random.choice(user_levels)
        sql = "INSERT INTO dim_user (user_name, user_gender, user_age, user_level) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, gender, age, level))
        user_count += 1
    print(f"用户维度表插入 {user_count} 条")
    
    # ========== 2. 商品维度表 dim_goods ==========
    goods_data = [
        ('iPhone 15', '手机', 5999.00),
        ('iPhone 15 Pro', '手机', 7999.00),
        ('华为Mate 60', '手机', 4999.00),
        ('小米14', '手机', 3999.00),
        ('iPad Air', '平板', 4999.00),
        ('iPad Pro', '平板', 6999.00),
        ('华为MatePad', '平板', 3499.00),
        ('MacBook Pro', '笔记本', 12999.00),
        ('ThinkPad X1', '笔记本', 8999.00),
        ('戴尔XPS', '笔记本', 9999.00),
        ('AirPods Pro', '耳机', 1899.00),
        ('华为FreeBuds', '耳机', 999.00),
        ('小米手环8', '智能穿戴', 199.00),
        ('Apple Watch', '智能穿戴', 2999.00),
        ('华为GT4', '智能穿戴', 1499.00),
        ('任天堂Switch', '游戏机', 2099.00),
        ('PS5', '游戏机', 3899.00),
        ('小米电视', '家电', 2999.00),
        ('戴森吸尘器', '家电', 3999.00),
        ('海尔冰箱', '家电', 4999.00)
    ]
    
    goods_count = 0
    for name, category, price in goods_data:
        sql = "INSERT INTO dim_goods (goods_name, goods_category, goods_price) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, category, price))
        goods_count += 1
    print(f"商品维度表插入 {goods_count} 条")
    
    # ========== 3. 时间维度表 dim_time ==========
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    time_count = 0
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day
        quarter = (month - 1) // 3 + 1
        sql = "INSERT INTO dim_time (full_date, year, month, day, quarter) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (current_date.date(), year, month, day, quarter))
        time_count += 1
        current_date += timedelta(days=1)
    print(f"时间维度表插入 {time_count} 条")
    
    # ========== 4. 地区维度表 dim_area ==========
    area_data = [
        ('北京市', '北京市'),
        ('上海市', '上海市'),
        ('广东省', '广州市'),
        ('广东省', '深圳市'),
        ('浙江省', '杭州市'),
        ('江苏省', '南京市'),
        ('四川省', '成都市'),
        ('湖北省', '武汉市'),
        ('陕西省', '西安市'),
        ('山东省', '济南市')
    ]
    
    area_count = 0
    for province, city in area_data:
        sql = "INSERT INTO dim_area (province, city) VALUES (%s, %s)"
        cursor.execute(sql, (province, city))
        area_count += 1
    print(f"地区维度表插入 {area_count} 条")
    
    # ========== 5. 支付方式维度表 dim_pay ==========
    # 按设计文档：微信/支付宝/银行卡
    pay_methods = ['微信', '支付宝', '银行卡']
    
    pay_count = 0
    for pay in pay_methods:
        sql = "INSERT INTO dim_pay (pay_name) VALUES (%s)"
        cursor.execute(sql, (pay,))
        pay_count += 1
    print(f"支付方式维度表插入 {pay_count} 条")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return user_count, goods_count, time_count, area_count, pay_count

def insert_fact_orders(num_orders=5000):
    """插入事实表数据（确保主外键一致）"""
    conn = connect_db('ecommerce_dw')
    cursor = conn.cursor()
    
    # 先查询各个维度表的ID范围
    cursor.execute("SELECT MAX(user_id) FROM dim_user")
    max_user_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(goods_id) FROM dim_goods")
    max_goods_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(time_id) FROM dim_time")
    max_time_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(area_id) FROM dim_area")
    max_area_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(pay_id) FROM dim_pay")
    max_pay_id = cursor.fetchone()[0]
    
    print(f"\n维度表ID范围:")
    print(f"  用户ID: 1-{max_user_id}")
    print(f"  商品ID: 1-{max_goods_id}")
    print(f"  时间ID: 1-{max_time_id}")
    print(f"  地区ID: 1-{max_area_id}")
    print(f"  支付ID: 1-{max_pay_id}")
    
    # 查询商品价格用于计算订单金额，构建价格负相关权重
    cursor.execute("SELECT goods_id, goods_price FROM dim_goods")
    goods_prices = {row[0]: float(row[1]) for row in cursor.fetchall()}
    goods_ids = list(goods_prices.keys())
    # 权重与价格成反比：便宜的卖得多，贵的卖得少
    goods_weights = [1.0 / goods_prices[gid] for gid in goods_ids]
    goods_total_w = sum(goods_weights)
    goods_weights = [w / goods_total_w for w in goods_weights]  # 归一化为概率

    # 地区权重：东部多、西部少
    # 按顺序对应 dim_area 插入顺序：北京/上海/广州/深圳/杭州/南京/成都/武汉/西安/济南
    area_weights_raw = [0.20, 0.18, 0.15, 0.15, 0.12, 0.08, 0.04, 0.03, 0.02, 0.03]
    # 注意：该权重会在下方被 1/area_id^1.1 幂律权重覆盖（ID越小=一线城市越靠前，同样满足"东多西少"）
    
    # ===== 模拟真实购买分布：购买次数服从正态分布 =====
    # μ=15, σ=7：多数用户集中在 8~22 次，少数低频(1~2次)和重度(30+次)，分布拉大更有区分度
    purchase_counts = []
    for uid in range(1, max_user_id + 1):
        n = int(random.gauss(15, 7))
        n = max(1, min(n, 60))  # 限制在 1~60 次
        purchase_counts.append(n)

    total = sum(purchase_counts)
    # 不足5000 → 轮流给用户 +1，均匀补足（避免全部堆给某个人）
    i = 0
    while total < num_orders:
        purchase_counts[i % len(purchase_counts)] += 1
        total += 1
        i += 1
    # 超出5000 → 从尾部用户逐个扣减（每人至少保留1单）
    j = len(purchase_counts) - 1
    while total > num_orders:
        if purchase_counts[j] > 1:
            purchase_counts[j] -= 1
            total -= 1
        j = (j - 1) % len(purchase_counts)

    # ===== 为各维度构建偏斜权重 =====
    # 1) 商品：权重与价格成反比（已在上方按 1/价格 构建 goods_weights）
    #    便宜的卖得多，贵的卖得少
    goods_pool = list(range(1, max_goods_id + 1))

    # 2) 时间：按月份加权（6月618、11月双11、1-2月春节为高峰，9月开学季次之）
    #    先查 dim_time 每个月的 time_id 范围，再按月份权重挑日期
    cursor.execute("""
        SELECT month, MIN(time_id), MAX(time_id)
        FROM dim_time GROUP BY month ORDER BY month
    """)
    month_ranges = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    month_weights = {
        1: 1.4, 2: 1.5, 3: 1.0, 4: 0.9, 5: 1.0, 6: 1.8,
        7: 0.85, 8: 0.9, 9: 1.3, 10: 1.1, 11: 2.0, 12: 1.6
    }
    months_pool = list(month_weights.keys())
    months_wlist = [month_weights[m] for m in months_pool]

    # 3) 地区：一线/新一线权重高，内陆低（area_id 偏小为北上广深杭）
    area_weights = [1.0 / (aid ** 1.1) for aid in range(1, max_area_id + 1)]
    area_pool = list(range(1, max_area_id + 1))

    # 4) 支付方式：微信>支付宝>银行卡（占比约 5:3:2）
    pay_weights = [0.5, 0.3, 0.2][:max_pay_id]
    pay_pool = list(range(1, max_pay_id + 1))

    # 5) 订单状态：历史订单不应有未支付(0)，只保留已支付/已取消
    order_status_weights = [0, 0.90, 0.10]  # 已支付 90%，已取消 10%

    # 6) 购买数量：长尾，多数买1~2件，少量大单
    order_num_weights = [0.30, 0.25, 0.15, 0.10, 0.08, 0.05, 0.03, 0.02, 0.01, 0.01]
    order_num_pool = list(range(1, 11))

    # 生成订单数据
    order_count = 0
    for uid, cnt in enumerate(purchase_counts, start=1):
        for _ in range(cnt):
            # 带权重的外键选择（每个维度都是偏斜分布）
            goods_id = random.choices(goods_pool, weights=goods_weights, k=1)[0]
            province_id, city_id = month_ranges[random.choices(months_pool, weights=months_wlist, k=1)[0]]
            time_id = random.randint(province_id, city_id)
            area_id = random.choices(area_pool, weights=area_weights, k=1)[0]
            pay_id = random.choices(pay_pool, weights=pay_weights, k=1)[0]

            # 生成度量值
            order_num = random.choices(order_num_pool, weights=order_num_weights, k=1)[0]
            order_amount = goods_prices[goods_id] * order_num  # 订单金额
            order_status = random.choices([0, 1, 2], weights=order_status_weights, k=1)[0]
            
            sql = """INSERT INTO fact_order 
                     (user_id, goods_id, time_id, area_id, pay_id, 
                      order_num, order_amount, order_status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (uid, goods_id, time_id, area_id, pay_id,
                                order_num, order_amount, order_status))
            order_count += 1
            
            if order_count % 500 == 0:
                print(f"已插入 {order_count} 条订单...")
    
    conn.commit()
    print(f"\n订单事实表插入 {order_count} 条")
    
    cursor.close()
    conn.close()

def verify_data():
    """验证数据完整性"""
    conn = connect_db('ecommerce_dw')
    cursor = conn.cursor()
    
    print("\n========== 数据验证 ==========")
    
    # 各表数据量
    tables = ['dim_user', 'dim_goods', 'dim_time', 'dim_area', 'dim_pay', 'fact_order']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} 条")
    
    # 验证外键一致性（检查是否有孤立数据）
    print("\n外键一致性检查:")
    
    # 检查fact_order中的user_id是否都存在于dim_user
    cursor.execute("""
        SELECT COUNT(*) FROM fact_order fo 
        LEFT JOIN dim_user du ON fo.user_id = du.user_id 
        WHERE du.user_id IS NULL
    """)
    orphan_user = cursor.fetchone()[0]
    print(f"  孤立用户数据: {orphan_user} 条" if orphan_user > 0 else "  用户外键: ✓")
    
    # 检查fact_order中的goods_id是否都存在于dim_goods
    cursor.execute("""
        SELECT COUNT(*) FROM fact_order fo 
        LEFT JOIN dim_goods dg ON fo.goods_id = dg.goods_id 
        WHERE dg.goods_id IS NULL
    """)
    orphan_goods = cursor.fetchone()[0]
    print(f"  孤立商品数据: {orphan_goods} 条" if orphan_goods > 0 else "  商品外键: ✓")
    
    # 检查fact_order中的time_id是否都存在于dim_time
    cursor.execute("""
        SELECT COUNT(*) FROM fact_order fo 
        LEFT JOIN dim_time dt ON fo.time_id = dt.time_id 
        WHERE dt.time_id IS NULL
    """)
    orphan_time = cursor.fetchone()[0]
    print(f"  孤立时间数据: {orphan_time} 条" if orphan_time > 0 else "  时间外键: ✓")
    
    # 检查fact_order中的area_id是否都存在于dim_area
    cursor.execute("""
        SELECT COUNT(*) FROM fact_order fo 
        LEFT JOIN dim_area da ON fo.area_id = da.area_id 
        WHERE da.area_id IS NULL
    """)
    orphan_area = cursor.fetchone()[0]
    print(f"  孤立地区数据: {orphan_area} 条" if orphan_area > 0 else "  地区外键: ✓")
    
    # 检查fact_order中的pay_id是否都存在于dim_pay
    cursor.execute("""
        SELECT COUNT(*) FROM fact_order fo 
        LEFT JOIN dim_pay dp ON fo.pay_id = dp.pay_id 
        WHERE dp.pay_id IS NULL
    """)
    orphan_pay = cursor.fetchone()[0]
    print(f"  孤立支付数据: {orphan_pay} 条" if orphan_pay > 0 else "  支付外键: ✓")
    
    # 统计总金额
    cursor.execute("SELECT SUM(order_amount), AVG(order_amount), COUNT(*) FROM fact_order")
    total, avg, count = cursor.fetchone()
    print(f"\n订单统计:")
    print(f"  总订单数: {count}")
    print(f"  总金额: ¥{total:,.2f}")
    print(f"  平均金额: ¥{avg:,.2f}")
    
    # 按商品品类统计
    print("\n商品品类销售统计:")
    cursor.execute("""
        SELECT dg.goods_category, 
               COUNT(*) as order_count,
               SUM(fo.order_amount) as total_sales
        FROM fact_order fo
        JOIN dim_goods dg ON fo.goods_id = dg.goods_id
        GROUP BY dg.goods_category
        ORDER BY total_sales DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}单, ¥{row[2]:,.2f}")

    # 按月份统计（季节性高峰）
    print("\n月度销售统计（应看到 6月/11月 高峰）:")
    cursor.execute("""
        SELECT dt.month, COUNT(*) cnt, SUM(fo.order_amount) total_sales
        FROM fact_order fo
        JOIN dim_time dt ON fo.time_id = dt.time_id
        GROUP BY dt.month
        ORDER BY total_sales DESC
        LIMIT 6
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}月: {row[1]}单, ¥{row[2]:,.2f}")

    # 按支付方式统计
    print("\n支付方式占比:")
    cursor.execute("""
        SELECT dp.pay_name, COUNT(*) cnt
        FROM fact_order fo
        JOIN dim_pay dp ON fo.pay_id = dp.pay_id
        GROUP BY dp.pay_name
        ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}单 ({row[1]/count*100:.1f}%)")

    # 按地区统计
    print("\n地区销售统计 Top5:")
    cursor.execute("""
        SELECT da.province, da.city, COUNT(*) cnt, SUM(fo.order_amount) total_sales
        FROM fact_order fo
        JOIN dim_area da ON fo.area_id = da.area_id
        GROUP BY da.province, da.city
        ORDER BY cnt DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}-{row[1]}: {row[2]}单, ¥{row[3]:,.2f}")

    # 下单用户分布（正态）
    print("\n用户下单次数分布:")
    cursor.execute("""
        SELECT cnt, COUNT(*) AS user_num FROM (
            SELECT user_id, COUNT(*) cnt FROM fact_order GROUP BY user_id
        ) t GROUP BY cnt ORDER BY cnt
    """)
    dist = cursor.fetchall()
    for cnt, usernum in dist:
        bar = '█' * min(usernum, 40)
        print(f"  {int(cnt):>3}单: {usernum:>3}人 {bar}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("开始生成电商销售数据...\n")
    
    # 创建表结构
    print("1. 创建表结构...")
    create_tables()
    
    # 插入维度表数据
    print("\n2. 插入维度表数据...")
    insert_dimension_tables()
    
    # 插入事实表数据
    print("\n3. 插入订单事实表数据...")
    insert_fact_orders(5000)
    
    # 验证数据
    print("\n4. 验证数据完整性...")
    verify_data()
    
    print("\n========== 完成 ==========")