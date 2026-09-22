from flask import Flask, jsonify, send_from_directory
from db.db import query, execute


app = Flask(__name__, static_folder='../frontend', static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/summary')
def summary():
    # 获取总销量数据
    sql = "select sum(order_num) as total_quantity, sum(order_amount) as total_revenue, count(*) as total_records, (select sum(if(user_level = 1, 1, 0)) / count(*)  as avg_member from dim_user) as avg_member from fact_order"
    result = query(sql)
    return jsonify(result[0])

@app.route('/api/monthly')
def monthly():
    # 获取月度销量和营收数据
    sql = "select concat(d.year, '-', lpad(d.month, 2, '0')) as month_year, sum(f.order_num) as total_quantity, sum(f.order_amount) as total_revenue from fact_order f left join dim_time d on d.time_id = f.time_id group by d.month, d.year order by d.year, d.month asc"
    result = query(sql)
    return jsonify(result)

@app.route('/api/products')
def products():
    # 获取产品销量和营收数据
    sql = "select g.goods_name, count(*) as total_amount from fact_order f left join dim_goods g on g.goods_id = f.goods_id group by g.goods_name order by total_amount desc"
    result = query(sql)
    return jsonify(result)

@app.route('/api/regions')
def regions():
    # 获取地区销量和营收数据
    sql = "select r.region_name, sum(f.order_num) as total_quantity, sum(f.order_amount) as total_revenue from fact_order f left join dim_region r on r.region_id = f.region_id group by r.region_name order by total_quantity desc"
    result = query(sql)
    return jsonify(result)

@app.route('/api/members')
def members():
    sql = "select user_level, count(*) as member_count from dim_user group by user_level"
    result = query(sql)
    return jsonify(result)

@app.route('/api/regions-sales')
def regions_sales():
    sql = "select da.province, sum(fo.order_num) as total_quantity from fact_order fo left join dim_area da on fo.area_id = da.area_id group by da.province"
    result = query(sql)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080, debug=True)