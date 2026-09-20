-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_dw DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE ecommerce_dw;
-- 4.2 用户维度表 dim_user
CREATE TABLE IF NOT EXISTS dim_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户维度主键',
    user_name VARCHAR(50) NULL COMMENT '用户名',
    user_gender TINYINT NULL COMMENT '性别 1男 2女',
    user_age INT NULL COMMENT '用户年龄',
    user_level TINYINT NOT NULL DEFAULT 1 COMMENT '用户会员等级'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='用户维度表';
-- 4.3 商品维度表 dim_goods
CREATE TABLE IF NOT EXISTS dim_goods (
    goods_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品主键',
    goods_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    goods_category VARCHAR(50) NOT NULL COMMENT '商品品类',
    goods_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '商品单价'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='商品维度表';
-- 4.4 时间维度表 dim_time
CREATE TABLE IF NOT EXISTS dim_time (
    time_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '时间维度主键',
    full_date DATE NOT NULL COMMENT '完整日期',
    year INT NOT NULL COMMENT '年份',
    month INT NOT NULL COMMENT '月份',
    day INT NOT NULL COMMENT '日期',
    quarter INT NOT NULL COMMENT '季度'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='时间维度表';
-- 4.5 地区维度表 dim_area
CREATE TABLE IF NOT EXISTS dim_area (
    area_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区主键',
    province VARCHAR(30) NOT NULL COMMENT '省份',
    city VARCHAR(30) NOT NULL COMMENT '城市'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='地区维度表';
-- 4.6 支付维度表 dim_pay
CREATE TABLE IF NOT EXISTS dim_pay (
    pay_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '支付方式主键',
    pay_name VARCHAR(20) NOT NULL COMMENT '支付方式名称（微信/支付宝/银行卡）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='支付维度表';
-- 4.1 事实表 fact_order（最后建，因为外键依赖上面5张维度表）
CREATE TABLE IF NOT EXISTS fact_order (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单明细主键',
    user_id INT NOT NULL COMMENT '用户维度外键',
    goods_id INT NOT NULL COMMENT '商品维度外键',
    time_id INT NOT NULL COMMENT '时间维度外键',
    area_id INT NOT NULL COMMENT '地区维度外键',
    pay_id INT NOT NULL COMMENT '支付方式维度外键',
    order_num INT NOT NULL DEFAULT 0 COMMENT '购买数量（度量值）',
    order_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单金额（度量值，核心GMV字段）',
    order_status TINYINT NOT NULL DEFAULT 0 COMMENT '订单状态 0未支付 1已支付 2已取消',
    -- 外键约束
    FOREIGN KEY fk_fact_user (user_id) REFERENCES dim_user(user_id),
    FOREIGN KEY fk_fact_goods (goods_id) REFERENCES dim_goods(goods_id),
    FOREIGN KEY fk_fact_time (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY fk_fact_area (area_id) REFERENCES dim_area(area_id),
    FOREIGN KEY fk_fact_pay (pay_id) REFERENCES dim_pay(pay_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci COMMENT='订单事实表';

-- 索引设计
CREATE INDEX idx_fact_user ON fact_order(user_id); 
CREATE INDEX idx_fact_goods ON fact_order(goods_id); 
CREATE INDEX idx_fact_time ON fact_order(time_id); 
CREATE INDEX idx_fact_area ON fact_order(area_id); 
CREATE INDEX idx_fact_pay ON fact_order(pay_id);
