import re
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class NQLEngine:
    """
    Natural Query Language Engine that converts natural language queries to SQL
    """
    
    def __init__(self):
        self.conversation_history = []
        self.context = {}
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
            'price': ['price', 'cost', 'amount', 'total', 'total_amount', 'unit_price'],
            'date': ['created_at', 'updated_at', 'order_date', 'date', 'registration_date', 'last_login'],
            'id': ['id', 'user_id', 'order_id', 'product_id', 'customer_id', 'category_id'],
            'status': ['status', 'order_status', 'user_status', 'payment_status', 'is_active'],
            'quantity': ['quantity', 'qty', 'amount', 'stock_quantity'],
            'description': ['description', 'desc', 'details', 'comment'],
            'rating': ['rating', 'review_rating'],
            'city': ['city', 'location'],
            'state': ['state', 'province'],
            'country': ['country'],
            'brand': ['brand', 'manufacturer'],
            'category': ['category', 'category_name'],
            'age': ['age'],
            'gender': ['gender'],
            'phone': ['phone', 'phone_number'],
            'address': ['address', 'shipping_address', 'billing_address']
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

    def nql_to_sql(self, nql_query: str, conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convert natural language query to SQL with conversational context
        """
        nql_query = nql_query.lower().strip()
        
        # Store conversation context
        if conversation_context:
            self.context.update(conversation_context)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': nql_query,
            'context': self.context.copy()
        })
        
        # Analyze query intent and provide intelligent responses
        response = self._analyze_query_intent(nql_query)
        
        # Handle different query types
        if self._is_select_query(nql_query):
            sql_query = self._process_select_query(nql_query)
        elif self._is_aggregate_query(nql_query):
            sql_query = self._process_aggregate_query(nql_query)
        elif self._is_filter_query(nql_query):
            sql_query = self._process_filter_query(nql_query)
        else:
            sql_query = self._process_general_query(nql_query)
        
        # Generate follow-up suggestions
        suggestions = self._generate_suggestions(nql_query, sql_query)
        
        # Provide query explanation
        explanation = self._explain_query(nql_query, sql_query)
        
        return {
            'sql_query': sql_query,
            'explanation': explanation,
            'suggestions': suggestions,
            'context': self.context,
            'response': response
        }

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

    def _analyze_query_intent(self, query: str) -> str:
        """Analyze query intent and provide intelligent response"""
        if 'help' in query or 'what can' in query:
            return "I can help you query your database using natural language! Try asking me to show data, count records, or find specific information."
        
        if 'explain' in query or 'how' in query:
            return "I'll explain how your query works and what data it will return."
        
        if 'show' in query or 'display' in query:
            return "I'll show you the requested data from the database."
        
        if 'count' in query or 'how many' in query:
            return "I'll count the records that match your criteria."
        
        if 'find' in query or 'search' in query:
            return "I'll search for records that match your criteria."
        
        return "I'll process your query and show you the results."

    def _generate_suggestions(self, query: str, sql_query: str) -> List[str]:
        """Generate intelligent follow-up suggestions based on the query"""
        suggestions = []
        
        # Context-aware suggestions for large dataset
        if 'users' in query or 'user' in query:
            suggestions.extend([
                "Show users by city and state",
                "Find users with premium subscriptions",
                "Count users by age group",
                "Show users who haven't logged in recently",
                "Find users from specific cities"
            ])
        
        if 'products' in query or 'product' in query:
            suggestions.extend([
                "Show products by brand and category",
                "Find products with low stock",
                "Show average rating by category",
                "Find the most expensive products",
                "Show products with high review counts"
            ])
        
        if 'orders' in query or 'order' in query:
            suggestions.extend([
                "Show orders by status and payment method",
                "Find orders from the last 30 days",
                "Show total revenue by month",
                "Find orders with high values",
                "Show order trends by city"
            ])
        
        if 'reviews' in query or 'review' in query:
            suggestions.extend([
                "Show reviews by rating",
                "Find verified reviews",
                "Show most helpful reviews",
                "Find reviews for specific products"
            ])
        
        if 'count' in query or 'how many' in query:
            suggestions.extend([
                "Show breakdown by category",
                "Find trends over time",
                "Compare different segments"
            ])
        
        if 'average' in query or 'avg' in query:
            suggestions.extend([
                "Show by different categories",
                "Find outliers",
                "Compare with median values"
            ])
        
        # Advanced analytical suggestions
        suggestions.extend([
            "Show data distribution and patterns",
            "Find correlations between different metrics",
            "Identify top performers and trends",
            "Analyze customer behavior patterns",
            "Show business insights and KPIs"
        ])
        
        return suggestions[:6]  # Return top 6 suggestions

    def _explain_query(self, nql_query: str, sql_query: str) -> str:
        """Explain what the query does in plain English"""
        explanation = f"I translated your request '{nql_query}' into the SQL query: {sql_query}\n\n"
        
        if 'SELECT *' in sql_query:
            explanation += "This query retrieves all columns from the specified table."
        elif 'COUNT' in sql_query:
            explanation += "This query counts the number of records that match your criteria."
        elif 'WHERE' in sql_query:
            explanation += "This query filters the data based on your specified conditions."
        elif 'AVG' in sql_query or 'SUM' in sql_query or 'MAX' in sql_query or 'MIN' in sql_query:
            explanation += "This query performs a mathematical calculation on the data."
        
        return explanation

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        return self.conversation_history

    def clear_context(self):
        """Clear conversation context"""
        self.context = {}
        self.conversation_history = []

    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        if not self.context:
            return "No specific context set. I'm ready to help you explore your database!"
        
        summary = "Current context:\n"
        for key, value in self.context.items():
            summary += f"- {key}: {value}\n"
        
        return summary
