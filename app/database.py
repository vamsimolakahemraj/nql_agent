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
        """Initialize sample data for demonstration"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    category VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    product_id INTEGER REFERENCES products(id),
                    quantity INTEGER NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending'
                );
            """)
            
            # Insert sample data
            cursor.execute("""
                INSERT INTO users (name, email, age) VALUES
                ('John Doe', 'john@example.com', 30),
                ('Jane Smith', 'jane@example.com', 25),
                ('Bob Johnson', 'bob@example.com', 35),
                ('Alice Brown', 'alice@example.com', 28),
                ('Charlie Wilson', 'charlie@example.com', 42)
                ON CONFLICT (email) DO NOTHING;
            """)
            
            cursor.execute("""
                INSERT INTO products (name, price, category, description) VALUES
                ('Laptop', 999.99, 'Electronics', 'High-performance laptop'),
                ('Smartphone', 699.99, 'Electronics', 'Latest smartphone model'),
                ('Coffee Mug', 12.99, 'Kitchen', 'Ceramic coffee mug'),
                ('Book', 19.99, 'Education', 'Programming book'),
                ('Headphones', 149.99, 'Electronics', 'Wireless headphones')
                ON CONFLICT DO NOTHING;
            """)
            
            cursor.execute("""
                INSERT INTO orders (user_id, product_id, quantity, total_amount, status) VALUES
                (1, 1, 1, 999.99, 'completed'),
                (2, 2, 1, 699.99, 'pending'),
                (3, 3, 2, 25.98, 'completed'),
                (1, 4, 1, 19.99, 'shipped'),
                (4, 5, 1, 149.99, 'pending')
                ON CONFLICT DO NOTHING;
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logging.info("Sample data initialized successfully")
            
        except Exception as e:
            logging.error(f"Sample data initialization failed: {e}")
            raise
