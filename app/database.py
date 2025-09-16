import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any
import logging

class DatabaseManager:
    """
    Database manager for PostgreSQL operations
    """
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'nql_demo'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def test_connection(self):
        """Test database connection"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            raise

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            result_list = [dict(row) for row in results]
            
            cursor.close()
            conn.close()
            
            return result_list
            
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            raise Exception(f"Query execution failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            
            for table in tables:
                # Get columns for each table
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table,))
                
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        'name': row[0],
                        'type': row[1],
                        'nullable': row[2] == 'YES'
                    })
                
                schema[table] = {
                    'columns': columns,
                    'row_count': self._get_table_row_count(cursor, table)
                }
            
            cursor.close()
            conn.close()
            
            return schema
            
        except Exception as e:
            logging.error(f"Schema retrieval failed: {e}")
            raise Exception(f"Schema retrieval failed: {str(e)}")

    def _get_table_row_count(self, cursor, table_name: str) -> int:
        """Get row count for a table"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except:
            return 0

    def initialize_sample_data(self):
        """Initialize large-scale sample data for demonstration"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create comprehensive tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    age INTEGER,
                    gender VARCHAR(10),
                    city VARCHAR(50),
                    state VARCHAR(50),
                    country VARCHAR(50),
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    subscription_type VARCHAR(20) DEFAULT 'free'
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_category_id INTEGER REFERENCES categories(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    cost DECIMAL(10,2),
                    category_id INTEGER REFERENCES categories(id),
                    brand VARCHAR(100),
                    sku VARCHAR(50) UNIQUE,
                    stock_quantity INTEGER DEFAULT 0,
                    weight DECIMAL(8,2),
                    dimensions VARCHAR(50),
                    color VARCHAR(30),
                    size VARCHAR(20),
                    rating DECIMAL(3,2),
                    review_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending',
                    total_amount DECIMAL(12,2) NOT NULL,
                    tax_amount DECIMAL(10,2) DEFAULT 0,
                    shipping_amount DECIMAL(10,2) DEFAULT 0,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    payment_method VARCHAR(50),
                    payment_status VARCHAR(20) DEFAULT 'pending',
                    shipping_address TEXT,
                    billing_address TEXT,
                    notes TEXT
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id),
                    product_id INTEGER REFERENCES products(id),
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(12,2) NOT NULL,
                    discount_percent DECIMAL(5,2) DEFAULT 0
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    product_id INTEGER REFERENCES products(id),
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    title VARCHAR(200),
                    comment TEXT,
                    is_verified BOOLEAN DEFAULT false,
                    helpful_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    contact_person VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    city VARCHAR(50),
                    country VARCHAR(50),
                    rating DECIMAL(3,2),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    supplier_id INTEGER REFERENCES suppliers(id),
                    quantity INTEGER NOT NULL,
                    reserved_quantity INTEGER DEFAULT 0,
                    reorder_level INTEGER DEFAULT 10,
                    last_restocked TIMESTAMP,
                    location VARCHAR(100)
                );
            """)
            
            # Generate large-scale data
            self._generate_large_dataset(cursor)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logging.info("Large-scale sample data initialized successfully")
            
        except Exception as e:
            logging.error(f"Sample data initialization failed: {e}")
            raise

    def _generate_large_dataset(self, cursor):
        """Generate large-scale realistic data"""
        import random
        from datetime import datetime, timedelta
        
        # Sample data arrays
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica', 'William', 'Ashley',
                      'James', 'Amanda', 'Christopher', 'Jennifer', 'Daniel', 'Lisa', 'Matthew', 'Nancy', 'Anthony', 'Karen',
                      'Mark', 'Betty', 'Donald', 'Helen', 'Steven', 'Sandra', 'Paul', 'Donna', 'Andrew', 'Carol',
                      'Joshua', 'Ruth', 'Kenneth', 'Sharon', 'Kevin', 'Michelle', 'Brian', 'Laura', 'George', 'Sarah',
                      'Edward', 'Kimberly', 'Ronald', 'Deborah', 'Timothy', 'Dorothy', 'Jason', 'Lisa', 'Jeffrey', 'Nancy']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                     'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
                     'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
                     'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts']
        
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego',
                 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco',
                 'Indianapolis', 'Seattle', 'Denver', 'Washington', 'Boston', 'El Paso', 'Nashville', 'Detroit', 'Oklahoma City']
        
        states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI', 'CO', 'MN', 'SC', 'AL', 'LA']
        
        categories_data = [
            ('Electronics', 'Electronic devices and gadgets'),
            ('Clothing', 'Apparel and accessories'),
            ('Home & Garden', 'Home improvement and garden supplies'),
            ('Sports & Outdoors', 'Sports equipment and outdoor gear'),
            ('Books', 'Books and educational materials'),
            ('Health & Beauty', 'Health and beauty products'),
            ('Automotive', 'Car parts and accessories'),
            ('Toys & Games', 'Toys and gaming products'),
            ('Food & Beverages', 'Food and drink products'),
            ('Office Supplies', 'Office and business supplies')
        ]
        
        brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'Microsoft', 'Google', 'Amazon', 'Tesla', 'BMW',
                 'Mercedes', 'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Dell', 'HP', 'Lenovo', 'Canon', 'Nikon']
        
        # Insert categories
        for name, desc in categories_data:
            cursor.execute("""
                INSERT INTO categories (name, description) VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (name, desc))
        
        # Generate 50,000 users
        print("Generating 50,000 users...")
        for i in range(50000):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            age = random.randint(18, 80)
            city = random.choice(cities)
            state = random.choice(states)
            registration_date = datetime.now() - timedelta(days=random.randint(1, 3650))
            last_login = registration_date + timedelta(days=random.randint(0, 30))
            subscription_type = random.choice(['free', 'premium', 'enterprise'])
            
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, age, city, state, country, 
                                 registration_date, last_login, subscription_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, age, city, state, 'USA', 
                  registration_date, last_login, subscription_type))
            
            if i % 5000 == 0:
                print(f"Generated {i} users...")
        
        # Generate 10,000 products
        print("Generating 10,000 products...")
        for i in range(10000):
            category_id = random.randint(1, len(categories_data))
            brand = random.choice(brands)
            name = f"{brand} Product {i+1}"
            price = round(random.uniform(10, 2000), 2)
            cost = round(price * random.uniform(0.3, 0.7), 2)
            stock_quantity = random.randint(0, 1000)
            rating = round(random.uniform(1, 5), 2)
            review_count = random.randint(0, 500)
            
            cursor.execute("""
                INSERT INTO products (name, price, cost, category_id, brand, sku, stock_quantity, 
                                    rating, review_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, price, cost, category_id, brand, f"SKU-{i+1:06d}", 
                  stock_quantity, rating, review_count))
            
            if i % 1000 == 0:
                print(f"Generated {i} products...")
        
        # Generate 100,000 orders
        print("Generating 100,000 orders...")
        for i in range(100000):
            user_id = random.randint(1, 50000)
            order_date = datetime.now() - timedelta(days=random.randint(1, 365))
            status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
            total_amount = round(random.uniform(20, 2000), 2)
            tax_amount = round(total_amount * 0.08, 2)
            shipping_amount = round(random.uniform(5, 50), 2)
            payment_method = random.choice(['credit_card', 'debit_card', 'paypal', 'apple_pay'])
            payment_status = random.choice(['pending', 'paid', 'failed', 'refunded'])
            
            cursor.execute("""
                INSERT INTO orders (user_id, order_number, order_date, status, total_amount, 
                                  tax_amount, shipping_amount, payment_method, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, f"ORD-{i+1:08d}", order_date, status, total_amount, 
                  tax_amount, shipping_amount, payment_method, payment_status))
            
            if i % 10000 == 0:
                print(f"Generated {i} orders...")
        
        # Generate 200,000 order items
        print("Generating 200,000 order items...")
        for i in range(200000):
            order_id = random.randint(1, 100000)
            product_id = random.randint(1, 10000)
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            total_price = round(unit_price * quantity, 2)
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id, quantity, unit_price, total_price))
            
            if i % 20000 == 0:
                print(f"Generated {i} order items...")
        
        # Generate 50,000 reviews
        print("Generating 50,000 reviews...")
        for i in range(50000):
            user_id = random.randint(1, 50000)
            product_id = random.randint(1, 10000)
            rating = random.randint(1, 5)
            title = f"Review {i+1}"
            comment = f"This is a review for product {product_id} by user {user_id}."
            is_verified = random.choice([True, False])
            helpful_count = random.randint(0, 50)
            created_at = datetime.now() - timedelta(days=random.randint(1, 365))
            
            cursor.execute("""
                INSERT INTO reviews (user_id, product_id, rating, title, comment, 
                                   is_verified, helpful_count, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, product_id, rating, title, comment, is_verified, helpful_count, created_at))
            
            if i % 5000 == 0:
                print(f"Generated {i} reviews...")
        
        print("Large-scale data generation completed!")
