#!/usr/bin/env python3
"""
PostgreSQL 数据库初始化脚本
独立运行，自动创建电商表结构并生成mock数据
"""

import sys
import subprocess
import logging
from datetime import datetime, timedelta
import random
import os

# 导入公共数据库配置
from common.db_config import (
    POSTGRES_CONFIG, ECOMMERCE_TABLES,
    check_psycopg2_dependency, get_db_connection,
    check_tables_exist, get_table_counts, execute_query,
    execute_batch_insert, get_database_summary
)

# 设置Windows环境编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform.startswith('win'):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_init.log', encoding='utf-8')
    ]
)

def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    return check_psycopg2_dependency()

def test_postgres_connection():
    """测试PostgreSQL连接"""
    try:
        logging.info("🔄 尝试PostgreSQL连接...")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                logging.info(f"✅ PostgreSQL连接成功！")
                logging.info(f"📋 数据库版本: {version[:50]}...")
                return True, conn
                
    except Exception as e:
        logging.error(f"❌ PostgreSQL连接失败: {e}")
        return False, None

def get_postgres_connection():
    """获取PostgreSQL连接（保持兼容性）"""
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            database=POSTGRES_CONFIG["database"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            port=POSTGRES_CONFIG["port"]
        )
        return conn
    except Exception as e:
        logging.error(f"❌ PostgreSQL连接失败: {e}")
        return None

def drop_existing_tables_sql(conn):
    """删除现有表（使用SQL）"""
    tables_to_drop = [
        'marketing_campaigns', 'inventory', 'order_items', 
        'orders', 'products', 'customers'
    ]
    
    logging.info("🧹 清理现有表...")
    cur = conn.cursor()
    for table in tables_to_drop:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            logging.info(f"  ✅ 删除表: {table}")
        except Exception as e:
            logging.warning(f"  ⚠️ 删除表 {table} 时出错: {e}")
    
    conn.commit()
    cur.close()

def create_ecommerce_schema_sql(conn):
    """创建电商表结构（使用SQL）"""
    logging.info("🏗️ 创建电商表结构...")
    
    # 表定义
    tables = {
        "customers": """
        CREATE TABLE customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            country VARCHAR(50),
            region VARCHAR(50),
            city VARCHAR(50),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer_type VARCHAR(20) DEFAULT 'regular',
            total_orders INTEGER DEFAULT 0,
            total_spent DECIMAL(12,2) DEFAULT 0.00,
            last_order_date TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        "products": """
        CREATE TABLE products (
            product_id VARCHAR(50) PRIMARY KEY,
            sku VARCHAR(100) UNIQUE NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            category VARCHAR(50),
            subcategory VARCHAR(50),
            brand VARCHAR(50),
            cost_price DECIMAL(8,2),
            selling_price DECIMAL(8,2),
            weight DECIMAL(6,2),
            dimensions VARCHAR(50),
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        "orders": """
        CREATE TABLE orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) REFERENCES customers(customer_id),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            order_status VARCHAR(20) DEFAULT 'pending',
            total_amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            platform VARCHAR(20) NOT NULL,
            market VARCHAR(20),
            payment_method VARCHAR(30),
            shipping_fee DECIMAL(8,2) DEFAULT 0.00,
            tax_amount DECIMAL(8,2) DEFAULT 0.00,
            discount_amount DECIMAL(8,2) DEFAULT 0.00,
            shipping_address TEXT,
            tracking_number VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        "order_items": """
        CREATE TABLE order_items (
            item_id SERIAL PRIMARY KEY,
            order_id VARCHAR(50) REFERENCES orders(order_id),
            product_id VARCHAR(50) REFERENCES products(product_id),
            sku VARCHAR(100),
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(8,2) NOT NULL,
            discount_amount DECIMAL(8,2) DEFAULT 0.00,
            total_price DECIMAL(10,2) NOT NULL
        )
        """,
        
        "inventory": """
        CREATE TABLE inventory (
            inventory_id SERIAL PRIMARY KEY,
            sku VARCHAR(100) NOT NULL,
            warehouse VARCHAR(50) NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            reserved_quantity INTEGER DEFAULT 0,
            available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
            cost DECIMAL(8,2),
            location VARCHAR(100),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sku, warehouse)
        )
        """,
        
        "marketing_campaigns": """
        CREATE TABLE marketing_campaigns (
            campaign_id VARCHAR(50) PRIMARY KEY,
            campaign_name VARCHAR(100) NOT NULL,
            platform VARCHAR(20),
            campaign_type VARCHAR(30),
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            budget DECIMAL(10,2),
            spent DECIMAL(10,2) DEFAULT 0.00,
            impressions BIGINT DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            conversion_value DECIMAL(10,2) DEFAULT 0.00,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    }
    
    cur = conn.cursor()
    
    # 创建表
    for table_name, sql in tables.items():
        try:
            cur.execute(sql)
            logging.info(f"  ✅ 创建表: {table_name}")
        except Exception as e:
            logging.error(f"  ❌ 创建表 {table_name} 失败: {e}")
            cur.close()
            return False
    
    # 创建索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)",
        "CREATE INDEX IF NOT EXISTS idx_orders_platform ON orders(platform)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory(sku)",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
        "CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country)"
    ]
    
    logging.info("📊 创建索引...")
    for index_sql in indexes:
        try:
            cur.execute(index_sql)
        except Exception as e:
            logging.warning(f"  ⚠️ 创建索引失败: {e}")
    
    conn.commit()
    cur.close()
    return True

def generate_customers_data(count: int = 50):
    """生成客户数据"""
    customers = []
    countries = ['US', 'UK', 'CA', 'DE', 'FR', 'AU', 'JP', 'CN', 'KR', 'IN']
    customer_types = ['regular', 'premium', 'vip']
    
    for i in range(count):
        customer = {
            'customer_id': f'C{i+1:04d}',
            'email': f'customer{i+1}@example.com',
            'first_name': f'FirstName{i+1}',
            'last_name': f'LastName{i+1}',
            'country': random.choice(countries),
            'region': random.choice(['North', 'South', 'East', 'West', 'Central']),
            'city': f'City{i+1}',
            'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            'customer_type': random.choice(customer_types),
            'status': 'active'
        }
        customers.append(customer)
    
    return customers

def generate_products_data(count: int = 100):
    """生成商品数据"""
    products = []
    categories = ['Electronics', 'Home & Garden', 'Clothing', 'Sports', 'Books', 'Beauty']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
    
    for i in range(count):
        category = random.choice(categories)
        cost_price = round(random.uniform(10, 500), 2)
        selling_price = round(cost_price * random.uniform(1.2, 3.0), 2)
        
        product = {
            'product_id': f'P{i+1:04d}',
            'sku': f'SKU{i+1:04d}',
            'product_name': f'{category} Product {i+1}',
            'category': category,
            'subcategory': f'{category} Sub{random.randint(1, 3)}',
            'brand': random.choice(brands),
            'cost_price': cost_price,
            'selling_price': selling_price,
            'weight': round(random.uniform(0.1, 5.0), 2),
            'dimensions': f'{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)}cm',
            'description': f'High quality {category.lower()} product',
            'status': 'active'
        }
        products.append(product)
    
    return products

def generate_orders_data(customers_data, count: int = 200):
    """生成订单数据"""
    orders = []
    platforms = ['Amazon', 'eBay', 'Shopify', 'WooCommerce']
    markets = ['US', 'UK', 'CA', 'DE', 'FR', 'AU']
    statuses = ['completed', 'pending', 'shipped', 'cancelled']
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Apple Pay']
    
    for i in range(count):
        customer = random.choice(customers_data)
        order_date = (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        total_amount = round(random.uniform(20, 1000), 2)
        
        order = {
            'order_id': f'ORD{i+1:06d}',
            'customer_id': customer['customer_id'],
            'order_date': order_date,
            'order_status': random.choice(statuses),
            'total_amount': total_amount,
            'currency': 'USD',
            'platform': random.choice(platforms),
            'market': random.choice(markets),
            'payment_method': random.choice(payment_methods),
            'shipping_fee': round(random.uniform(5, 25), 2),
            'tax_amount': round(total_amount * 0.1, 2),
            'discount_amount': round(random.uniform(0, 50), 2),
            'shipping_address': f'{customer["city"]}, {customer["country"]}',
            'tracking_number': f'TRK{i+1:08d}'
        }
        orders.append(order)
    
    return orders

def generate_order_items_data(orders_data, products_data):
    """生成订单明细数据"""
    order_items = []
    
    for order in orders_data:
        items_count = random.randint(1, 5)
        selected_products = random.sample(products_data, min(items_count, len(products_data)))
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            unit_price = product['selling_price']
            discount_amount = round(random.uniform(0, unit_price * 0.2), 2)
            total_price = round((unit_price - discount_amount) * quantity, 2)
            
            item = {
                'order_id': order['order_id'],
                'product_id': product['product_id'],
                'sku': product['sku'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_amount': discount_amount,
                'total_price': total_price
            }
            order_items.append(item)
    
    return order_items

def generate_inventory_data(products_data):
    """生成库存数据"""
    inventory = []
    warehouses = ['US-West', 'US-East', 'UK-London', 'DE-Berlin', 'CN-Shenzhen']
    
    for product in products_data:
        selected_warehouses = random.sample(warehouses, random.randint(2, 3))
        
        for warehouse in selected_warehouses:
            quantity = random.randint(0, 1000)
            reserved = random.randint(0, min(50, quantity))
            
            inv = {
                'sku': product['sku'],
                'warehouse': warehouse,
                'quantity': quantity,
                'reserved_quantity': reserved,
                'cost': product['cost_price'],
                'location': f'A{random.randint(1, 20)}-B{random.randint(1, 10)}'
            }
            inventory.append(inv)
    
    return inventory

def generate_campaigns_data(count: int = 20):
    """生成营销活动数据"""
    campaigns = []
    platforms = ['Google Ads', 'Facebook', 'Amazon PPC', 'TikTok', 'Instagram']
    campaign_types = ['Search', 'Display', 'Video', 'Shopping', 'Social']
    
    for i in range(count):
        start_date = (datetime.now() - timedelta(days=random.randint(30, 120))).isoformat()
        end_date = (datetime.now() - timedelta(days=random.randint(7, 60))).isoformat()
        budget = round(random.uniform(500, 10000), 2)
        spent = round(budget * random.uniform(0.3, 0.95), 2)
        impressions = random.randint(10000, 1000000)
        clicks = random.randint(100, impressions // 100)
        conversions = random.randint(1, clicks // 10)
        
        campaign = {
            'campaign_id': f'CMP{i+1:04d}',
            'campaign_name': f'Campaign {i+1} - {random.choice(campaign_types)}',
            'platform': random.choice(platforms),
            'campaign_type': random.choice(campaign_types),
            'start_date': start_date,
            'end_date': end_date,
            'budget': budget,
            'spent': spent,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'conversion_value': round(conversions * random.uniform(20, 200), 2),
            'status': random.choice(['active', 'paused', 'completed'])
        }
        campaigns.append(campaign)
    
    return campaigns

def insert_mock_data_sql(conn):
    """使用SQL插入Mock数据"""
    logging.info("📝 生成Mock数据...")
    
    # 生成数据
    customers_data = generate_customers_data(50)
    products_data = generate_products_data(100)
    orders_data = generate_orders_data(customers_data, 200)
    order_items_data = generate_order_items_data(orders_data, products_data)
    inventory_data = generate_inventory_data(products_data)
    campaigns_data = generate_campaigns_data(20)
    
    cur = conn.cursor()
    
    try:
        # 插入客户数据
        logging.info("  📊 插入客户数据...")
        customer_insert_sql = """
        INSERT INTO customers (customer_id, email, first_name, last_name, country, region, city, 
                              registration_date, customer_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        customer_values = [(c['customer_id'], c['email'], c['first_name'], c['last_name'], 
                           c['country'], c['region'], c['city'], c['registration_date'], 
                           c['customer_type'], c['status']) for c in customers_data]
        cur.executemany(customer_insert_sql, customer_values)
        logging.info(f"    ✅ 插入客户数据: {len(customer_values)} 条")
        
        # 插入商品数据
        logging.info("  🛍️ 插入商品数据...")
        product_insert_sql = """
        INSERT INTO products (product_id, sku, product_name, category, subcategory, brand,
                             cost_price, selling_price, weight, dimensions, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        product_values = [(p['product_id'], p['sku'], p['product_name'], p['category'], 
                          p['subcategory'], p['brand'], p['cost_price'], p['selling_price'],
                          p['weight'], p['dimensions'], p['description'], p['status']) 
                         for p in products_data]
        cur.executemany(product_insert_sql, product_values)
        logging.info(f"    ✅ 插入商品数据: {len(product_values)} 条")
        
        # 插入订单数据
        logging.info("  📦 插入订单数据...")
        order_insert_sql = """
        INSERT INTO orders (order_id, customer_id, order_date, order_status, total_amount,
                           currency, platform, market, payment_method, shipping_fee,
                           tax_amount, discount_amount, shipping_address, tracking_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        order_values = [(o['order_id'], o['customer_id'], o['order_date'], o['order_status'],
                        o['total_amount'], o['currency'], o['platform'], o['market'],
                        o['payment_method'], o['shipping_fee'], o['tax_amount'],
                        o['discount_amount'], o['shipping_address'], o['tracking_number'])
                       for o in orders_data]
        cur.executemany(order_insert_sql, order_values)
        logging.info(f"    ✅ 插入订单数据: {len(order_values)} 条")
        
        # 插入订单明细数据
        logging.info("  📋 插入订单明细数据...")
        item_insert_sql = """
        INSERT INTO order_items (order_id, product_id, sku, quantity, unit_price, 
                                discount_amount, total_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        item_values = [(i['order_id'], i['product_id'], i['sku'], i['quantity'],
                       i['unit_price'], i['discount_amount'], i['total_price'])
                      for i in order_items_data]
        cur.executemany(item_insert_sql, item_values)
        logging.info(f"    ✅ 插入订单明细数据: {len(item_values)} 条")
        
        # 插入库存数据
        logging.info("  📈 插入库存数据...")
        inventory_insert_sql = """
        INSERT INTO inventory (sku, warehouse, quantity, reserved_quantity, cost, location)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        inventory_values = [(i['sku'], i['warehouse'], i['quantity'], i['reserved_quantity'],
                            i['cost'], i['location']) for i in inventory_data]
        cur.executemany(inventory_insert_sql, inventory_values)
        logging.info(f"    ✅ 插入库存数据: {len(inventory_values)} 条")
        
        # 插入营销活动数据
        logging.info("  📢 插入营销活动数据...")
        campaign_insert_sql = """
        INSERT INTO marketing_campaigns (campaign_id, campaign_name, platform, campaign_type,
                                       start_date, end_date, budget, spent, impressions,
                                       clicks, conversions, conversion_value, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        campaign_values = [(c['campaign_id'], c['campaign_name'], c['platform'], c['campaign_type'],
                           c['start_date'], c['end_date'], c['budget'], c['spent'],
                           c['impressions'], c['clicks'], c['conversions'], 
                           c['conversion_value'], c['status']) for c in campaigns_data]
        cur.executemany(campaign_insert_sql, campaign_values)
        logging.info(f"    ✅ 插入营销活动数据: {len(campaign_values)} 条")
        
        conn.commit()
        cur.close()
        
        return {
            'customers': len(customers_data),
            'products': len(products_data),
            'orders': len(orders_data),
            'order_items': len(order_items_data),
            'inventory': len(inventory_data),
            'marketing_campaigns': len(campaigns_data)
        }
        
    except Exception as e:
        logging.error(f"❌ 数据插入失败: {e}")
        conn.rollback()
        cur.close()
        return None

def verify_database_state_sql(conn):
    """使用SQL验证数据库状态"""
    logging.info("✅ 验证数据库状态...")
    table_counts = get_table_counts(conn)
    total_records = sum(table_counts.values())
    
    for table, count in table_counts.items():
        logging.info(f"  📊 {table}: {count} 条记录")
    
    logging.info(f"🎯 总计: {total_records} 条记录")
    return total_records

def run_sample_queries_sql(conn):
    """使用SQL运行示例查询"""
    logging.info("🔍 运行示例查询...")
    
    try:
        # 平台销售统计
        logging.info("  📊 平台销售统计:")
        platform_stats = execute_query(conn, """
            SELECT platform, COUNT(*) as order_count, SUM(total_amount) as total_sales
            FROM orders 
            GROUP BY platform 
            ORDER BY total_sales DESC
        """)
        for row in platform_stats:
            logging.info(f"    {row['platform']}: {row['order_count']} 订单, 总额: ${row['total_sales']:.2f}")
        
        # 产品类别分析
        logging.info("  📊 产品类别分析:")
        category_stats = execute_query(conn, """
            SELECT category, COUNT(*) as product_count, AVG(selling_price) as avg_price
            FROM products 
            GROUP BY category 
            ORDER BY product_count DESC
        """)
        for row in category_stats:
            logging.info(f"    {row['category']}: {row['product_count']} 产品, 平均价格: ${row['avg_price']:.2f}")
        
        # 客户地区分布
        logging.info("  📊 客户地区分布:")
        country_stats = execute_query(conn, """
            SELECT country, COUNT(*) as customer_count
            FROM customers 
            GROUP BY country 
            ORDER BY customer_count DESC 
            LIMIT 5
        """)
        for row in country_stats:
            logging.info(f"    {row['country']}: {row['customer_count']} 客户")
                
    except Exception as e:
        logging.error(f"  ❌ 查询失败: {e}")

def main():
    """主函数"""
    print("🚀 PostgreSQL 电商数据库初始化器")
    print("=" * 50)
    
    # 检查依赖
    logging.info("📦 检查依赖...")
    if not check_and_install_dependencies():
        logging.error("❌ 依赖检查失败，程序退出")
        return
    
    # 测试PostgreSQL连接
    logging.info("🔗 测试PostgreSQL连接...")
    with get_db_connection() as conn:
        if not conn:
            logging.error("❌ PostgreSQL连接失败，程序退出")
            return
            
        try:
            # 检查表是否已存在
            tables_exist, existing_tables = check_tables_exist(conn)
            
            if tables_exist:
                print(f"\n📋 发现已存在的表: {existing_tables}")
                print("⚠️  是否删除现有表并重新创建？ (y/N): ", end="")
                user_input = input().strip().lower()
                drop_existing = user_input in ['y', 'yes', '是']
                
                if drop_existing:
                    drop_existing_tables_sql(conn)
                    
                    # 创建表结构
                    if create_ecommerce_schema_sql(conn):
                        logging.info("✅ 表结构创建成功")
                    else:
                        logging.error("❌ 表结构创建失败")
                        return
                    
                    # 插入Mock数据
                    data_counts = insert_mock_data_sql(conn)
                    if data_counts:
                        logging.info("✅ Mock数据插入成功")
                    else:
                        logging.error("❌ Mock数据插入失败")
                        return
                else:
                    print("✅ 跳过表创建，使用现有表结构")
                    print("📊 验证现有数据...")
                    
                    # 只验证数据，不插入新数据
                    total_records = verify_database_state_sql(conn)
                    run_sample_queries_sql(conn)
                    
                    print(f"\n🎉 现有数据库验证完成！")
                    print(f"📊 总共 {total_records} 条记录")
                    
                    summary = get_database_summary(conn)
                    print(f"\n🔧 数据库概览：")
                    for key, value in summary["数据库配置"].items():
                        print(f"  • {key}: {value}")
                    
                    return
            else:
                print("\n📋 未发现现有表，将创建新的表结构")
                
                # 创建表结构
                if create_ecommerce_schema_sql(conn):
                    logging.info("✅ 表结构创建成功")
                else:
                    logging.error("❌ 表结构创建失败")
                    return
                
                # 插入Mock数据
                data_counts = insert_mock_data_sql(conn)
                if data_counts:
                    logging.info("✅ Mock数据插入成功")
                else:
                    logging.error("❌ Mock数据插入失败")
                    return
            
            # 验证数据
            total_records = verify_database_state_sql(conn)
            
            # 运行示例查询
            run_sample_queries_sql(conn)
            
            print("\n🎉 数据库初始化完成！")
            print(f"📊 总共 {total_records} 条记录")
            
            # 只有在插入新数据时才显示表统计
            if 'data_counts' in locals() and data_counts:
                print("\n📋 已创建的表：")
                for table, count in data_counts.items():
                    print(f"  • {table}: {count} 条记录")
            
            print("\n🔍 下一步：")
            print("1. 使用 database_schema_explorer 查看表结构")
            print("2. 使用 sql_query_executor 执行业务查询")
            print("3. 开始您的跨境电商数据分析！")
            
            summary = get_database_summary(conn)
            print(f"\n🔧 数据库配置信息：")
            for key, value in summary["数据库配置"].items():
                print(f"  • {key}: {value}")
            
        except Exception as e:
            logging.error(f"❌ 初始化过程中出现错误: {e}")
            print(f"\n❌ 初始化失败: {e}")
            print("请检查日志文件 database_init.log 获取详细信息")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        logging.error(f"程序异常: {e}") 