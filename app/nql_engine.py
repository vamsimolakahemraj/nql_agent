import re
from typing import Dict, List, Any
import json

class NQLEngine:
    """
    Natural Query Language Engine that converts natural language queries to SQL
    """
    
    def __init__(self):
        self.table_aliases = {
            'users': 'u',
            'orders': 'o', 
            'products': 'p',
            'categories': 'c',
            'customers': 'cust'
        }
        
        self.column_mappings = {
            'name': ['name', 'first_name', 'last_name', 'product_name', 'category_name'],
            'email': ['email', 'email_address'],
            'price': ['price', 'cost', 'amount', 'total'],
            'date': ['created_at', 'updated_at', 'order_date', 'date'],
            'id': ['id', 'user_id', 'order_id', 'product_id', 'customer_id'],
            'status': ['status', 'order_status', 'user_status'],
            'quantity': ['quantity', 'qty', 'amount'],
            'description': ['description', 'desc', 'details']
        }
        
        self.aggregate_functions = {
            'count': 'COUNT',
            'sum': 'SUM', 
            'average': 'AVG',
            'avg': 'AVG',
            'maximum': 'MAX',
            'max': 'MAX',
            'minimum': 'MIN',
            'min': 'MIN'
        }
        
        self.operators = {
            'equals': '=',
            'is': '=',
            'greater than': '>',
            'less than': '<',
            'greater than or equal': '>=',
            'less than or equal': '<=',
            'contains': 'LIKE',
            'like': 'LIKE',
            'starts with': 'LIKE',
            'ends with': 'LIKE'
        }

    def nql_to_sql(self, nql_query: str) -> str:
        """
        Convert natural language query to SQL
        """
        nql_query = nql_query.lower().strip()
        
        # Handle different query types
        if self._is_select_query(nql_query):
            return self._process_select_query(nql_query)
        elif self._is_aggregate_query(nql_query):
            return self._process_aggregate_query(nql_query)
        elif self._is_filter_query(nql_query):
            return self._process_filter_query(nql_query)
        else:
            return self._process_general_query(nql_query)

    def _is_select_query(self, query: str) -> bool:
        """Check if query is asking to select/show data"""
        select_keywords = ['show', 'display', 'list', 'get', 'find', 'select']
        return any(keyword in query for keyword in select_keywords)

    def _is_aggregate_query(self, query: str) -> bool:
        """Check if query involves aggregation"""
        return any(func in query for func in self.aggregate_functions.keys())

    def _is_filter_query(self, query: str) -> bool:
        """Check if query has filtering conditions"""
        filter_keywords = ['where', 'with', 'that', 'having']
        return any(keyword in query for keyword in filter_keywords)

    def _process_select_query(self, query: str) -> str:
        """Process SELECT queries"""
        # Extract table name
        table = self._extract_table_name(query)
        if not table:
            table = 'users'  # default table
            
        # Extract columns
        columns = self._extract_columns(query, table)
        
        # Extract conditions
        conditions = self._extract_conditions(query)
        
        # Build SQL
        sql = f"SELECT {columns} FROM {table}"
        
        if conditions:
            sql += f" WHERE {conditions}"
            
        # Add LIMIT for safety
        if 'all' not in query and 'limit' not in query:
            sql += " LIMIT 100"
            
        return sql

    def _process_aggregate_query(self, query: str) -> str:
        """Process aggregation queries"""
        table = self._extract_table_name(query)
        if not table:
            table = 'users'
            
        # Extract aggregate function
        agg_func = None
        agg_column = None
        
        for func_name, sql_func in self.aggregate_functions.items():
            if func_name in query:
                agg_func = sql_func
                # Try to find what to aggregate
                agg_column = self._extract_aggregate_column(query)
                break
                
        if not agg_func:
            agg_func = 'COUNT'
            agg_column = '*'
            
        sql = f"SELECT {agg_func}({agg_column}) as result FROM {table}"
        
        # Add conditions
        conditions = self._extract_conditions(query)
        if conditions:
            sql += f" WHERE {conditions}"
            
        return sql

    def _process_filter_query(self, query: str) -> str:
        """Process queries with filters"""
        return self._process_select_query(query)

    def _process_general_query(self, query: str) -> str:
        """Process general queries"""
        # Default to a simple select
        return self._process_select_query(query)

    def _extract_table_name(self, query: str) -> str:
        """Extract table name from query"""
        # Common table patterns
        tables = ['users', 'orders', 'products', 'categories', 'customers']
        
        for table in tables:
            if table in query:
                return table
                
        return None

    def _extract_columns(self, query: str, table: str) -> str:
        """Extract column names from query"""
        # If specific columns mentioned
        for col_type, col_names in self.column_mappings.items():
            if col_type in query:
                for col_name in col_names:
                    if col_name in query:
                        return col_name
                        
        # Default to all columns
        return '*'

    def _extract_conditions(self, query: str) -> str:
        """Extract WHERE conditions from query"""
        conditions = []
        
        # Look for value patterns
        value_patterns = [
            r'(\w+)\s+(equals?|is)\s+["\']?([^"\']+)["\']?',
            r'(\w+)\s+(greater than|>)\s+([0-9.]+)',
            r'(\w+)\s+(less than|<)\s+([0-9.]+)',
            r'(\w+)\s+(contains?|like)\s+["\']?([^"\']+)["\']?'
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                column, operator, value = match
                sql_operator = self.operators.get(operator, '=')
                
                if sql_operator == 'LIKE':
                    value = f"'%{value}%'"
                elif not value.isdigit() and not value.startswith("'"):
                    value = f"'{value}'"
                    
                conditions.append(f"{column} {sql_operator} {value}")
                
        return ' AND '.join(conditions) if conditions else ''

    def _extract_aggregate_column(self, query: str) -> str:
        """Extract column for aggregation"""
        for col_type, col_names in self.column_mappings.items():
            if col_type in query:
                for col_name in col_names:
                    if col_name in query:
                        return col_name
        return '*'
