-- Initialize the NQL Demo Database
-- This script creates tables and sample data for the NQL Agent demonstration

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and gadgets'),
('Kitchen', 'Kitchen appliances and utensils'),
('Education', 'Books and educational materials'),
('Clothing', 'Apparel and accessories')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users
INSERT INTO users (name, email, age) VALUES
('John Doe', 'john@example.com', 30),
('Jane Smith', 'jane@example.com', 25),
('Bob Johnson', 'bob@example.com', 35),
('Alice Brown', 'alice@example.com', 28),
('Charlie Wilson', 'charlie@example.com', 42),
('Diana Prince', 'diana@example.com', 29),
('Eve Adams', 'eve@example.com', 31),
('Frank Miller', 'frank@example.com', 45)
ON CONFLICT (email) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, price, category, description) VALUES
('Laptop Pro', 1299.99, 'Electronics', 'High-performance laptop with 16GB RAM'),
('Smartphone X', 799.99, 'Electronics', 'Latest smartphone with advanced camera'),
('Coffee Mug Set', 24.99, 'Kitchen', 'Set of 4 ceramic coffee mugs'),
('Programming Book', 49.99, 'Education', 'Complete guide to Python programming'),
('Wireless Headphones', 199.99, 'Electronics', 'Noise-cancelling wireless headphones'),
('Blender Pro', 89.99, 'Kitchen', 'High-speed kitchen blender'),
('Data Science Book', 39.99, 'Education', 'Introduction to data science'),
('T-Shirt', 19.99, 'Clothing', 'Cotton t-shirt in various colors'),
('Tablet', 399.99, 'Electronics', '10-inch tablet with stylus'),
('Cookbook', 29.99, 'Education', 'Healthy cooking recipes')
ON CONFLICT DO NOTHING;

-- Insert sample orders
INSERT INTO orders (user_id, product_id, quantity, total_amount, status) VALUES
(1, 1, 1, 1299.99, 'completed'),
(2, 2, 1, 799.99, 'pending'),
(3, 3, 2, 49.98, 'completed'),
(1, 4, 1, 49.99, 'shipped'),
(4, 5, 1, 199.99, 'pending'),
(5, 6, 1, 89.99, 'completed'),
(2, 7, 1, 39.99, 'shipped'),
(6, 8, 3, 59.97, 'pending'),
(3, 9, 1, 399.99, 'completed'),
(7, 10, 1, 29.99, 'shipped'),
(8, 1, 1, 1299.99, 'pending'),
(1, 2, 1, 799.99, 'completed')
ON CONFLICT DO NOTHING;

-- Create some indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
