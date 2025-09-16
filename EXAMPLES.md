# 🎯 NQL Agent - Example Queries

This document provides comprehensive examples of natural language queries that you can use with the NQL Agent. The examples are organized by category and complexity.

## 📋 Table of Contents

- [Basic Queries](#basic-queries)
- [Filtering Queries](#filtering-queries)
- [Aggregation Queries](#aggregation-queries)
- [Complex Queries](#complex-queries)
- [Query Patterns](#query-patterns)

## 🔍 Basic Queries

### Show All Data
```
Show all users
Display all products
List all orders
Get all categories
```

### Show Specific Columns
```
Show user names
Display product names and prices
List order IDs and dates
Get user emails
```

## 🔎 Filtering Queries

### Simple Filters
```
Show users with age greater than 30
Find products with price less than 100
Display orders with status completed
Show users with email containing john
```

### Multiple Conditions
```
Find users with age between 25 and 35
Show products with price greater than 50 and less than 200
Display completed orders from last month
Find users with name starting with J
```

### Text Matching
```
Show products with name containing laptop
Find users with email ending with .com
Display orders with status like pending
Show products with description containing wireless
```

## 📊 Aggregation Queries

### Counting
```
Count all users
How many products are there?
Count orders with status completed
Show number of users with age greater than 25
```

### Sum and Average
```
What is the total amount of all orders?
Show average price of products
Find sum of quantities in orders
What is the average age of users?
```

### Min and Max
```
What is the maximum price of products?
Show minimum age of users
Find highest order amount
What is the oldest user age?
```

### Grouped Aggregations
```
Count products by category
Show average price by category
Find total sales by user
Count orders by status
```

## 🔗 Complex Queries

### Date-based Queries
```
Show orders from today
Find users created in the last month
Display products added this week
Show orders from last year
```

### Range Queries
```
Find products with price between 50 and 150
Show users with age between 20 and 40
Display orders with amount greater than 100
Find products with price less than 50
```

### Pattern Matching
```
Show users with names starting with A
Find products with names containing Pro
Display orders with status ending with ed
Show users with emails containing @gmail
```

## 🎨 Query Patterns

### Question Format
```
How many users are there?
What is the average price?
Which products cost more than 100?
Who are the users with age greater than 30?
```

### Command Format
```
Show me all users
Find products with price greater than 50
Display orders with status completed
Get users with email containing john
```

### Descriptive Format
```
Users with age greater than 25
Products that cost less than 100
Orders that are completed
Users whose email contains gmail
```

## 💡 Tips for Better Queries

### 1. Be Specific
- ✅ "Show users with age greater than 30"
- ❌ "Show old users"

### 2. Use Clear Operators
- ✅ "Find products with price greater than 100"
- ✅ "Show users with age less than 25"
- ✅ "Display orders with status equals completed"

### 3. Include Context
- ✅ "Show all users in the database"
- ✅ "Find products with price greater than 50"
- ✅ "Display completed orders"

### 4. Use Natural Language
- ✅ "What is the average price of products?"
- ✅ "How many users are there?"
- ✅ "Which products cost more than 100?"

## 🚫 Common Limitations

### Not Supported Yet
- JOIN operations between tables
- Complex subqueries
- Date arithmetic (e.g., "orders from 30 days ago")
- Custom functions
- Multiple table queries

### Workarounds
- Use simple filters instead of complex conditions
- Break complex queries into multiple simple ones
- Use exact values instead of relative dates

## 🧪 Testing Your Queries

### 1. Start Simple
Begin with basic queries to understand the data structure:
```
Show all users
Display all products
List all orders
```

### 2. Add Filters
Gradually add filtering conditions:
```
Show users with age greater than 25
Find products with price less than 100
Display completed orders
```

### 3. Try Aggregations
Test counting and mathematical operations:
```
Count all users
What is the average price?
Find the maximum age
```

### 4. Experiment with Patterns
Try different ways to express the same query:
```
Show users with age greater than 30
Find users older than 30
Display users with age more than 30
```

## 📈 Performance Tips

### 1. Use Specific Filters
- More specific queries are faster
- Use exact matches when possible
- Limit results with conditions

### 2. Avoid "Show All"
- Always add some filtering
- Use LIMIT for large datasets
- Be specific about what you want

### 3. Test Query Performance
- Check execution time in the UI
- Use the health endpoint to monitor
- Optimize based on results

## 🔧 Troubleshooting

### Common Issues

#### "No results found"
- Check if the data exists
- Verify filter conditions
- Try a simpler query first

#### "Query execution failed"
- Check the generated SQL
- Verify column names
- Use simpler syntax

#### "Schema not loading"
- Check database connection
- Verify Docker containers are running
- Check the health endpoint

### Getting Help

1. Check the generated SQL query
2. Try a simpler version of your query
3. Use the example queries as templates
4. Check the API health endpoint
5. Review the database schema

## 🎯 Advanced Examples

### Business Intelligence Queries
```
Show total revenue from all orders
Find the most expensive product
Display users who have placed the most orders
What is the average order value?
```

### Data Analysis Queries
```
Count products by category
Show age distribution of users
Find orders with highest amounts
Display users created this month
```

### Reporting Queries
```
Show all completed orders
Find users with multiple orders
Display products with low stock
Show recent user registrations
```

---

*Remember: The NQL Agent is designed to understand natural language, so don't worry about perfect syntax. Just describe what you want to find in plain English!*
