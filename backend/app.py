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
    sql = "select d.month, sum(f.order_num) as total_quantity, sum(f.order_amount) as total_revenue from fact_order f left join dim_time d on d.time_id = f.time_id group by d.month order by d.month asc"
    result = query(sql)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080, debug=True)