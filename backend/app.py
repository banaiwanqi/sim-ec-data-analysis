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
    # 获取会员数量
    sql = "select user_level, count(*) as member_count from dim_user group by user_level"
    result = query(sql)
    return jsonify(result)

@app.route('/api/regions-sales')
def regions_sales():
    # 获取地区购买量
    sql = "select da.province, sum(fo.order_num) as total_quantity from fact_order fo left join dim_area da on fo.area_id = da.area_id group by da.province"
    result = query(sql)
    return jsonify(result)

@app.route('/api/repurchase')
def repurchase():
    # 按每月获取每月
    sql = "with user_month_order as (select dt.`month` as order_month, fo.user_id, count(fo.order_id) as order_cnt from fact_order fo left join dim_time dt on dt.time_id = fo.time_id group by dt.`month`, fo.user_id) select order_month, count(distinct case when order_cnt >= 2 then user_id end) as rpc_user, count(distinct user_id) as total_user, round(count(distinct case when order_cnt >= 2 then user_id end) * 100.0 / count(distinct user_id),2) as repurchase_rate from user_month_order group by order_month;"
    result = query(sql)
    return jsonify(result)

@app.route('/api/conversion')
def conversion():
    # 二次购买留存率
    sql = "with user_first_order as (select user_id, min(dt.`month`) as first_month from fact_order fo left join dim_time dt on dt.time_id=fo.time_id group by user_id), user_total_order as (select fo.user_id, count(fo.order_id) as total_order_cnt from fact_order fo group by fo.user_id) select count(distinct case when total_order_cnt>=2 then ufo.user_id end) as repurchase_2nd_user, count(distinct ufo.user_id) as first_buy_user, round(count(distinct case when total_order_cnt>=2 then ufo.user_id end)*100.0/count(distinct ufo.user_id),2) as total_second_buy_rate from user_first_order ufo left join user_total_order uto on ufo.user_id=uto.user_id;"
    result = query(sql)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080, debug=True)