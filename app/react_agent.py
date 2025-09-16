import re
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent for NQL queries
    Shows step-by-step reasoning and iterative refinement
    """
    
    def __init__(self):
        self.conversation_history = []
        self.context = {}
        self.reasoning_steps = []
        
        # Enhanced table and column mappings
        self.table_schema = {
            'users': {
                'columns': ['id', 'first_name', 'last_name', 'email', 'age', 'city', 'state', 'country', 'registration_date', 'subscription_type'],
                'description': 'User profiles with demographic and subscription information'
            },
            'products': {
                'columns': ['id', 'name', 'price', 'category_id', 'brand', 'rating', 'review_count', 'stock_quantity'],
                'description': 'Product catalog with pricing and inventory information'
            },
            'orders': {
                'columns': ['id', 'user_id', 'order_number', 'order_date', 'status', 'total_amount', 'payment_method'],
                'description': 'Order transactions with payment and status information'
            },
            'order_items': {
                'columns': ['id', 'order_id', 'product_id', 'quantity', 'unit_price', 'total_price'],
                'description': 'Individual items within each order'
            },
            'reviews': {
                'columns': ['id', 'user_id', 'product_id', 'rating', 'title', 'comment', 'created_at'],
                'description': 'Product reviews and ratings from users'
            },
            'categories': {
                'columns': ['id', 'name', 'description'],
                'description': 'Product categories and classifications'
            }
        }
        
        self.column_mappings = {
            'name': ['name', 'first_name', 'last_name', 'product_name'],
            'email': ['email', 'email_address'],
            'price': ['price', 'cost', 'amount', 'total', 'total_amount', 'unit_price'],
            'date': ['created_at', 'updated_at', 'order_date', 'date', 'registration_date'],
            'id': ['id', 'user_id', 'order_id', 'product_id', 'category_id'],
            'status': ['status', 'order_status', 'payment_status', 'is_active'],
            'quantity': ['quantity', 'qty', 'amount', 'stock_quantity'],
            'rating': ['rating', 'review_rating'],
            'city': ['city', 'location'],
            'state': ['state', 'province'],
            'brand': ['brand', 'manufacturer'],
            'category': ['category', 'category_name']
        }

    def process_query(self, nql_query: str, conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main ReAct loop: Reasoning -> Acting -> Observing -> Refining
        """
        self.reasoning_steps = []
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
        
        # REACT LOOP START
        self._add_reasoning_step("🧠 REASONING PHASE", "Analyzing the user's natural language query...")
        
        # Step 1: Understand Intent
        intent_analysis = self._analyze_intent(nql_query)
        self._add_reasoning_step("📋 Intent Analysis", intent_analysis)
        
        # Step 2: Plan Query Strategy
        query_plan = self._plan_query_strategy(nql_query, intent_analysis)
        self._add_reasoning_step("🎯 Query Planning", query_plan)
        
        # Step 3: Generate Initial SQL
        initial_sql = self._generate_initial_sql(nql_query, query_plan)
        self._add_reasoning_step("⚡ Initial SQL Generation", f"Generated: {initial_sql}")
        
        # Step 4: Validate and Refine
        refined_sql = self._validate_and_refine_sql(initial_sql, nql_query)
        if refined_sql != initial_sql:
            self._add_reasoning_step("🔧 SQL Refinement", f"Refined to: {refined_sql}")
        
        # Step 5: Generate Explanation
        explanation = self._generate_detailed_explanation(nql_query, refined_sql)
        self._add_reasoning_step("💡 Explanation Generation", "Created detailed explanation of the query")
        
        # Step 6: Generate Smart Suggestions
        suggestions = self._generate_contextual_suggestions(nql_query, refined_sql)
        self._add_reasoning_step("🎨 Suggestion Generation", f"Generated {len(suggestions)} contextual suggestions")
        
        # Step 7: Final Response
        response = self._generate_agent_response(nql_query, intent_analysis)
        self._add_reasoning_step("✅ Final Response", "Prepared comprehensive response with reasoning")
        
        return {
            'sql_query': refined_sql,
            'explanation': explanation,
            'suggestions': suggestions,
            'response': response,
            'context': self.context,
            'reasoning_steps': self.reasoning_steps,
            'intent_analysis': intent_analysis,
            'query_plan': query_plan
        }

    def _add_reasoning_step(self, phase: str, description: str):
        """Add a reasoning step to show the agent's thinking process"""
        step = {
            'phase': phase,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        self.reasoning_steps.append(step)
        # Simulate thinking time
        time.sleep(0.1)

    def _analyze_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the user's intent and extract key information"""
        intent = {
            'primary_action': 'unknown',
            'target_entities': [],
            'filters': [],
            'aggregations': [],
            'complexity': 'simple'
        }
        
        # Detect primary action
        if any(word in query for word in ['show', 'display', 'list', 'get', 'find']):
            intent['primary_action'] = 'select'
        elif any(word in query for word in ['count', 'how many']):
            intent['primary_action'] = 'count'
            intent['aggregations'].append('count')
        elif any(word in query for word in ['average', 'avg', 'mean']):
            intent['primary_action'] = 'aggregate'
            intent['aggregations'].append('average')
        elif any(word in query for word in ['sum', 'total']):
            intent['primary_action'] = 'aggregate'
            intent['aggregations'].append('sum')
        elif any(word in query for word in ['max', 'maximum', 'highest']):
            intent['primary_action'] = 'aggregate'
            intent['aggregations'].append('max')
        elif any(word in query for word in ['min', 'minimum', 'lowest']):
            intent['primary_action'] = 'aggregate'
            intent['aggregations'].append('min')
        
        # Detect target entities (tables)
        for table_name in self.table_schema.keys():
            if table_name in query or table_name[:-1] in query:  # Handle singular/plural
                intent['target_entities'].append(table_name)
        
        # Detect filters
        filter_patterns = [
            r'(\w+)\s+(greater than|>)\s+([0-9.]+)',
            r'(\w+)\s+(less than|<)\s+([0-9.]+)',
            r'(\w+)\s+(equals?|is)\s+["\']?([^"\']+)["\']?',
            r'(\w+)\s+(contains?|like)\s+["\']?([^"\']+)["\']?',
            r'(\w+)\s+(between)\s+([0-9.]+)\s+and\s+([0-9.]+)'
        ]
        
        for pattern in filter_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                intent['filters'].append({
                    'column': match[0],
                    'operator': match[1],
                    'value': match[2] if len(match) > 2 else None
                })
        
        # Assess complexity
        if len(intent['target_entities']) > 1 or len(intent['filters']) > 2 or len(intent['aggregations']) > 0:
            intent['complexity'] = 'complex'
        elif len(intent['filters']) > 0:
            intent['complexity'] = 'moderate'
        
        return intent

    def _plan_query_strategy(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the query execution strategy"""
        plan = {
            'approach': 'direct',
            'tables_needed': intent['target_entities'],
            'joins_required': [],
            'optimization_hints': []
        }
        
        # Determine if joins are needed
        if len(intent['target_entities']) > 1:
            plan['approach'] = 'join'
            plan['joins_required'] = self._determine_joins(intent['target_entities'])
        
        # Add optimization hints
        if intent['complexity'] == 'complex':
            plan['optimization_hints'].append('Consider adding LIMIT for performance')
        
        if any('date' in filter_info.get('column', '') for filter_info in intent['filters']):
            plan['optimization_hints'].append('Date filters detected - ensure proper indexing')
        
        return plan

    def _determine_joins(self, tables: List[str]) -> List[Dict[str, str]]:
        """Determine necessary joins between tables"""
        joins = []
        
        # Define relationship mappings
        relationships = {
            ('orders', 'users'): ('user_id', 'id'),
            ('orders', 'order_items'): ('id', 'order_id'),
            ('order_items', 'products'): ('product_id', 'id'),
            ('products', 'categories'): ('category_id', 'id'),
            ('reviews', 'users'): ('user_id', 'id'),
            ('reviews', 'products'): ('product_id', 'id')
        }
        
        for i in range(len(tables) - 1):
            table1, table2 = tables[i], tables[i + 1]
            if (table1, table2) in relationships:
                join_cols = relationships[(table1, table2)]
                joins.append({
                    'table1': table1,
                    'table2': table2,
                    'column1': join_cols[0],
                    'column2': join_cols[1]
                })
        
        return joins

    def _generate_initial_sql(self, query: str, plan: Dict[str, Any]) -> str:
        """Generate the initial SQL query"""
        intent = self._analyze_intent(query)
        
        if intent['primary_action'] == 'count':
            return self._generate_count_query(intent, plan)
        elif intent['primary_action'] == 'aggregate':
            return self._generate_aggregate_query(intent, plan)
        else:
            return self._generate_select_query(intent, plan)

    def _generate_select_query(self, intent: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Generate SELECT query"""
        if not intent['target_entities']:
            table = 'users'  # Default table
        else:
            table = intent['target_entities'][0]
        
        # Build SELECT clause
        select_clause = "*"
        
        # Build WHERE clause
        where_conditions = []
        for filter_info in intent['filters']:
            column = filter_info['column']
            operator = filter_info['operator']
            value = filter_info['value']
            
            if operator in ['greater than', '>']:
                where_conditions.append(f"{column} > {value}")
            elif operator in ['less than', '<']:
                where_conditions.append(f"{column} < {value}")
            elif operator in ['equals', 'is']:
                if not value.isdigit():
                    value = f"'{value}'"
                where_conditions.append(f"{column} = {value}")
            elif operator in ['contains', 'like']:
                where_conditions.append(f"{column} LIKE '%{value}%'")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else ""
        
        # Build final query
        sql = f"SELECT {select_clause} FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += " LIMIT 100"
        
        return sql

    def _generate_count_query(self, intent: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Generate COUNT query"""
        if not intent['target_entities']:
            table = 'users'
        else:
            table = intent['target_entities'][0]
        
        where_conditions = []
        for filter_info in intent['filters']:
            column = filter_info['column']
            operator = filter_info['operator']
            value = filter_info['value']
            
            if operator in ['greater than', '>']:
                where_conditions.append(f"{column} > {value}")
            elif operator in ['less than', '<']:
                where_conditions.append(f"{column} < {value}")
            elif operator in ['equals', 'is']:
                if not value.isdigit():
                    value = f"'{value}'"
                where_conditions.append(f"{column} = {value}")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else ""
        
        sql = f"SELECT COUNT(*) as result FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        return sql

    def _generate_aggregate_query(self, intent: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Generate aggregation query"""
        if not intent['target_entities']:
            table = 'products'
        else:
            table = intent['target_entities'][0]
        
        # Determine aggregation column
        agg_column = 'price'  # Default
        for filter_info in intent['filters']:
            if filter_info['column'] in ['price', 'amount', 'total']:
                agg_column = filter_info['column']
                break
        
        # Determine aggregation function
        agg_func = 'AVG'
        if 'sum' in intent['aggregations']:
            agg_func = 'SUM'
        elif 'max' in intent['aggregations']:
            agg_func = 'MAX'
        elif 'min' in intent['aggregations']:
            agg_func = 'MIN'
        
        sql = f"SELECT {agg_func}({agg_column}) as result FROM {table}"
        
        # Add WHERE conditions
        where_conditions = []
        for filter_info in intent['filters']:
            if filter_info['column'] != agg_column:  # Don't double-filter aggregation column
                column = filter_info['column']
                operator = filter_info['operator']
                value = filter_info['value']
                
                if operator in ['greater than', '>']:
                    where_conditions.append(f"{column} > {value}")
                elif operator in ['less than', '<']:
                    where_conditions.append(f"{column} < {value}")
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        return sql

    def _validate_and_refine_sql(self, sql: str, original_query: str) -> str:
        """Validate and refine the SQL query"""
        # Basic validation and refinement
        refined_sql = sql
        
        # Add safety limits if not present
        if 'LIMIT' not in sql and 'COUNT' not in sql:
            refined_sql += " LIMIT 100"
        
        # Improve column selection for specific queries
        if 'show users by' in original_query and 'SELECT *' in sql:
            refined_sql = sql.replace('SELECT *', 'SELECT first_name, last_name, city, state')
        
        return refined_sql

    def _generate_detailed_explanation(self, nql_query: str, sql_query: str) -> str:
        """Generate detailed explanation of the query"""
        explanation = f"**Query Analysis:**\n\n"
        explanation += f"**Natural Language:** \"{nql_query}\"\n\n"
        explanation += f"**Generated SQL:** `{sql_query}`\n\n"
        
        # Explain the SQL components
        if 'SELECT *' in sql_query:
            explanation += "**What it does:** Retrieves all columns from the specified table.\n\n"
        elif 'COUNT' in sql_query:
            explanation += "**What it does:** Counts the number of records that match the criteria.\n\n"
        elif 'AVG' in sql_query or 'SUM' in sql_query or 'MAX' in sql_query or 'MIN' in sql_query:
            explanation += "**What it does:** Performs mathematical aggregation on the data.\n\n"
        
        if 'WHERE' in sql_query:
            explanation += "**Filtering:** Applies conditions to narrow down the results.\n\n"
        
        if 'LIMIT' in sql_query:
            explanation += "**Performance:** Limited to 100 results for optimal performance.\n\n"
        
        explanation += "**Business Value:** This query helps you understand your data patterns and make informed decisions."
        
        return explanation

    def _generate_contextual_suggestions(self, query: str, sql_query: str) -> List[str]:
        """Generate contextual suggestions based on the query"""
        suggestions = []
        
        # Context-aware suggestions
        if 'users' in query:
            suggestions.extend([
                "Show user demographics by age group",
                "Find users with premium subscriptions",
                "Analyze user registration trends over time",
                "Show users by geographic distribution"
            ])
        
        if 'products' in query:
            suggestions.extend([
                "Show products by brand and category",
                "Find products with low stock levels",
                "Analyze product rating distributions",
                "Show best-selling products"
            ])
        
        if 'orders' in query:
            suggestions.extend([
                "Show order trends by month",
                "Find high-value orders",
                "Analyze payment method preferences",
                "Show order completion rates"
            ])
        
        if 'count' in query:
            suggestions.extend([
                "Break down the count by categories",
                "Show trends over time",
                "Compare with other metrics"
            ])
        
        # Advanced analytical suggestions
        suggestions.extend([
            "Create a dashboard with multiple metrics",
            "Export results for further analysis",
            "Set up automated reporting",
            "Explore data relationships and correlations"
        ])
        
        return suggestions[:6]

    def _generate_agent_response(self, query: str, intent: Dict[str, Any]) -> str:
        """Generate the agent's conversational response"""
        if intent['primary_action'] == 'count':
            return "I'll count the records that match your criteria and provide you with the exact number."
        elif intent['primary_action'] == 'aggregate':
            return "I'll perform the mathematical calculation you requested and show you the result."
        elif intent['primary_action'] == 'select':
            return "I'll retrieve the data you're looking for and present it in a clear format."
        else:
            return "I'll analyze your request and provide you with the most relevant information from the database."

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        return self.conversation_history

    def clear_context(self):
        """Clear conversation context"""
        self.context = {}
        self.conversation_history = []
        self.reasoning_steps = []

    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        if not self.context:
            return "No specific context set. I'm ready to help you explore your database with intelligent reasoning!"
        
        summary = "Current context:\n"
        for key, value in self.context.items():
            summary += f"- {key}: {value}\n"
        
        return summary

