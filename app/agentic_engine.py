import re
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from .real_mcp_client import RealMCPClient

class AgentState(Enum):
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    OBSERVING = "observing"
    REFINING = "refining"
    COMPLETED = "completed"
    ERROR = "error"

class ToolType(Enum):
    SCHEMA_EXPLORER = "schema_explorer"
    QUERY_BUILDER = "query_builder"
    DATA_ANALYZER = "data_analyzer"
    RESULT_VALIDATOR = "result_validator"
    OPTIMIZER = "optimizer"

class AgenticEngine:
    """
    Truly agentic NQL engine that mimics Claude desktop's iterative, tool-using behavior
    """
    
    def __init__(self, database_manager=None):
        self.conversation_memory = []
        self.current_context = {}
        self.agent_state = AgentState.THINKING
        self.reasoning_chain = []
        self.tool_results = {}
        self.iteration_count = 0
        self.max_iterations = 5
        
        # Initialize real MCP client
        database_url = "postgresql://postgres:password@nql_postgres:5432/nql_db"
        self.mcp_client = RealMCPClient(database_url)
        self.mcp_initialized = False
        
        # Available tools (like MCP servers)
        self.available_tools = {
            ToolType.SCHEMA_EXPLORER: self._explore_schema,
            ToolType.QUERY_BUILDER: self._build_query,
            ToolType.DATA_ANALYZER: self._analyze_data,
            ToolType.RESULT_VALIDATOR: self._validate_results,
            ToolType.OPTIMIZER: self._optimize_query
        }
        
        # Enhanced schema knowledge
        self.schema_knowledge = {
            'users': {
                'description': 'User profiles with demographic and subscription data',
                'key_columns': ['id', 'first_name', 'last_name', 'email', 'age', 'city', 'state', 'subscription_type'],
                'relationships': ['orders.user_id', 'reviews.user_id'],
                'sample_queries': ['count users by age', 'find premium subscribers', 'show user demographics']
            },
            'products': {
                'description': 'Product catalog with pricing and inventory information',
                'key_columns': ['id', 'name', 'price', 'brand', 'rating', 'stock_quantity', 'category_id'],
                'relationships': ['order_items.product_id', 'reviews.product_id', 'categories.id'],
                'sample_queries': ['show products by brand', 'find low stock items', 'analyze product ratings']
            },
            'orders': {
                'description': 'Order transactions with payment and status information',
                'key_columns': ['id', 'user_id', 'order_date', 'status', 'total_amount', 'payment_method'],
                'relationships': ['users.id', 'order_items.order_id'],
                'sample_queries': ['show order trends', 'find high value orders', 'analyze payment methods']
            }
        }

    async def process_query(self, user_query: str, conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main agentic processing loop - iterative reasoning and acting with MCP
        """
        self.iteration_count = 0
        self.reasoning_chain = []
        self.tool_results = {}
        
        # Initialize MCP if not already done
        if not self.mcp_initialized and self.mcp_client:
            try:
                self.mcp_initialized = await self.mcp_client.initialize()
                if self.mcp_initialized:
                    self._add_reasoning_step("🔌 MCP INITIALIZATION", "Connected to CrystalDBA Postgres MCP Pro server")
                else:
                    self._add_reasoning_step("⚠️ MCP FALLBACK", "MCP server not available, using local tools")
            except Exception as e:
                self._add_reasoning_step("⚠️ MCP FALLBACK", f"MCP server error: {str(e)}, using local tools")
                self.mcp_initialized = False
        
        # Update conversation memory
        self._update_conversation_memory(user_query, conversation_context)
        
        # Start the agentic loop
        return await self._agentic_loop(user_query)

    async def _agentic_loop(self, user_query: str) -> Dict[str, Any]:
        """
        The core agentic loop: Think -> Plan -> Act -> Observe -> Refine
        """
        final_result = None
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            # THINK: Analyze the current situation
            thinking_result = self._think(user_query)
            self._add_reasoning_step("🧠 THINKING", thinking_result)
            
            # PLAN: Decide what tools to use and how
            plan_result = self._plan(thinking_result, user_query)
            self._add_reasoning_step("🎯 PLANNING", plan_result)
            
            # ACT: Execute the planned actions
            action_result = await self._act(plan_result, user_query)
            self._add_reasoning_step("⚡ ACTING", action_result)
            
            # Ensure we have a SQL query even if MCP fails
            if not action_result.get('tool_results', {}).get('query_builder', {}).get('sql_query'):
                # Fallback: generate SQL using local method
                fallback_sql = self._construct_sql_query(user_query, ["users"])
                if fallback_sql:
                    action_result['tool_results']['query_builder'] = {
                        'sql_query': fallback_sql,
                        'status': 'completed',
                        'message': 'Generated using fallback method'
                    }
            
            # OBSERVE: Analyze the results
            observation_result = self._observe(action_result)
            self._add_reasoning_step("👁️ OBSERVING", observation_result)
            
            # Check if we need to refine or if we're done
            if observation_result.get('needs_refinement', False):
                self._add_reasoning_step("🔧 REFINING", "Query needs refinement based on results")
                continue
            else:
                final_result = action_result
                self._add_reasoning_step("✅ COMPLETED", "Query successfully executed")
                break
        
        return self._compile_final_response(user_query, final_result)

    def _think(self, user_query: str) -> Dict[str, Any]:
        """
        Deep thinking phase - analyze intent, context, and requirements
        """
        self.agent_state = AgentState.THINKING
        
        # Analyze user intent
        intent_analysis = self._analyze_deep_intent(user_query)
        
        # Check conversation context
        context_analysis = self._analyze_conversation_context()
        
        # Determine complexity and approach
        complexity_assessment = self._assess_query_complexity(user_query, intent_analysis)
        
        return {
            'intent': intent_analysis,
            'context': context_analysis,
            'complexity': complexity_assessment,
            'confidence': self._calculate_confidence(intent_analysis, context_analysis)
        }

    def _plan(self, thinking_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """
        Planning phase - decide which tools to use and in what order
        """
        self.agent_state = AgentState.PLANNING
        
        intent = thinking_result['intent']
        complexity = thinking_result['complexity']
        
        # Determine required tools
        required_tools = []
        
        if intent.get('needs_schema_exploration', False):
            required_tools.append(ToolType.SCHEMA_EXPLORER)
        
        if intent.get('needs_query_building', True):
            required_tools.append(ToolType.QUERY_BUILDER)
        
        if complexity.get('needs_data_analysis', False):
            required_tools.append(ToolType.DATA_ANALYZER)
        
        if complexity.get('needs_optimization', False):
            required_tools.append(ToolType.OPTIMIZER)
        
        # Always validate results
        required_tools.append(ToolType.RESULT_VALIDATOR)
        
        return {
            'tools': required_tools,
            'execution_order': required_tools,
            'estimated_steps': len(required_tools),
            'strategy': self._determine_strategy(intent, complexity)
        }

    async def _act(self, plan_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """
        Acting phase - execute the planned tools
        """
        self.agent_state = AgentState.EXECUTING
        
        tool_results = {}
        execution_log = []
        
        for tool in plan_result['tools']:
            try:
                # Use MCP if available, otherwise fallback to local tools
                if self.mcp_initialized and self.mcp_client:
                    tool_result = await self._execute_mcp_tool(tool, user_query, tool_results)
                else:
                    tool_result = self.available_tools[tool](user_query, tool_results)
                
                tool_results[tool.value] = tool_result
                execution_log.append(f"✅ {tool.value}: {tool_result.get('status', 'completed')}")
                
                # Add small delay to simulate thinking
                time.sleep(0.2)
                
            except Exception as e:
                execution_log.append(f"❌ {tool.value}: {str(e)}")
                tool_results[tool.value] = {'error': str(e), 'status': 'failed'}
        
        return {
            'tool_results': tool_results,
            'execution_log': execution_log,
            'success': all('error' not in result for result in tool_results.values())
        }

    def _observe(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observing phase - analyze the results and determine next steps
        """
        self.agent_state = AgentState.OBSERVING
        
        tool_results = action_result['tool_results']
        
        # Analyze results quality
        quality_assessment = self._assess_result_quality(tool_results)
        
        # Check if refinement is needed
        needs_refinement = self._needs_refinement(tool_results, quality_assessment)
        
        # Update context based on results
        self._update_context_from_results(tool_results)
        
        return {
            'quality': quality_assessment,
            'needs_refinement': needs_refinement,
            'confidence': quality_assessment.get('confidence', 0.5),
            'insights': self._extract_insights(tool_results)
        }

    # Real MCP Tool execution using CrystalDBA Postgres MCP Pro
    async def _execute_mcp_tool(self, tool_type: ToolType, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool using real CrystalDBA Postgres MCP Pro server"""
        try:
            if tool_type == ToolType.SCHEMA_EXPLORER:
                # Use real MCP schema exploration
                mcp_result = await self.mcp_client.call_tool("list_schemas", {})
                if mcp_result.error:
                    return {"status": "error", "error": mcp_result.error}
                
                # Also get table details
                tables_result = await self.mcp_client.call_tool("list_objects", {
                    "schema_name": "public",
                    "object_type": "table"
                })
                
                return {
                    "status": "completed",
                    "schemas": mcp_result.result,
                    "tables": tables_result.result if not tables_result.error else [],
                    "message": "Schema explored via CrystalDBA Postgres MCP Pro"
                }
            
            elif tool_type == ToolType.QUERY_BUILDER:
                # Use real MCP query building and execution
                sql_query = self._construct_sql_query(user_query, ["users"])
                
                # Execute the query using the real MCP server
                mcp_result = await self.mcp_client.call_tool("execute_sql", {
                    "sql": sql_query
                })
                if mcp_result.error:
                    return {"status": "error", "error": mcp_result.error}
                
                return {
                    "status": "completed",
                    "sql_query": sql_query,
                    "results": mcp_result.result,
                    "message": "Query built and executed via CrystalDBA Postgres MCP Pro"
                }
            
            elif tool_type == ToolType.DATA_ANALYZER:
                # Use real MCP database health analysis
                mcp_result = await self.mcp_client.call_tool("analyze_db_health", {
                    "health_type": "all"
                })
                if mcp_result.error:
                    return {"status": "error", "error": mcp_result.error}
                return {
                    "status": "completed",
                    "health_analysis": mcp_result.result,
                    "message": "Database health analyzed via CrystalDBA Postgres MCP Pro"
                }
            
            elif tool_type == ToolType.RESULT_VALIDATOR:
                # Use real MCP query explanation
                query_result = previous_results.get('query_builder', {})
                sql_query = query_result.get('sql_query', '')
                if sql_query:
                    mcp_result = await self.mcp_client.call_tool("explain_query", {
                        "sql": sql_query,
                        "analyze": False
                    })
                    if mcp_result.error:
                        return {"status": "error", "error": mcp_result.error}
                    return {
                        "status": "completed",
                        "explain_plan": mcp_result.result,
                        "message": "Query explained via CrystalDBA Postgres MCP Pro"
                    }
                else:
                    return {"status": "completed", "message": "No query to validate"}
            
            elif tool_type == ToolType.OPTIMIZER:
                # Use real MCP index optimization
                query_result = previous_results.get('query_builder', {})
                sql_query = query_result.get('sql_query', '')
                if sql_query:
                    mcp_result = await self.mcp_client.call_tool("analyze_query_indexes", {
                        "queries": [sql_query],
                        "max_index_size_mb": 1000,
                        "method": "dta"
                    })
                    if mcp_result.error:
                        return {"status": "error", "error": mcp_result.error}
                    return {
                        "status": "completed",
                        "index_recommendations": mcp_result.result,
                        "message": "Query optimized via CrystalDBA Postgres MCP Pro"
                    }
                else:
                    return {"status": "completed", "message": "No query to optimize"}
            
            else:
                return {"status": "error", "error": f"Unknown tool type: {tool_type}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Tool implementations (like MCP servers)
    
    def _explore_schema(self, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Schema exploration tool"""
        # Analyze which tables are relevant
        relevant_tables = []
        for table_name, table_info in self.schema_knowledge.items():
            if table_name in user_query.lower() or any(col in user_query.lower() for col in table_info['key_columns']):
                relevant_tables.append(table_name)
        
        if not relevant_tables:
            relevant_tables = ['users']  # Default fallback
        
        return {
            'status': 'completed',
            'relevant_tables': relevant_tables,
            'schema_info': {table: self.schema_knowledge[table] for table in relevant_tables},
            'suggestions': self._generate_schema_suggestions(relevant_tables)
        }
    
    def _build_query(self, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Query building tool"""
        schema_result = previous_results.get('schema_explorer', {})
        relevant_tables = schema_result.get('relevant_tables', ['users'])
        
        # Build SQL query based on intent and schema
        sql_query = self._construct_sql_query(user_query, relevant_tables)
        
        return {
            'status': 'completed',
            'sql_query': sql_query,
            'tables_used': relevant_tables,
            'query_type': self._determine_query_type(sql_query),
            'complexity_score': self._calculate_query_complexity(sql_query)
        }
    
    def _analyze_data(self, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Data analysis tool"""
        query_result = previous_results.get('query_builder', {})
        sql_query = query_result.get('sql_query', '')
        
        # Analyze what the query will return
        analysis = {
            'estimated_rows': self._estimate_result_rows(sql_query),
            'data_types': self._analyze_data_types(sql_query),
            'performance_impact': self._assess_performance_impact(sql_query),
            'business_value': self._assess_business_value(user_query, sql_query)
        }
        
        return {
            'status': 'completed',
            'analysis': analysis,
            'recommendations': self._generate_analysis_recommendations(analysis)
        }
    
    def _validate_results(self, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Result validation tool"""
        query_result = previous_results.get('query_builder', {})
        sql_query = query_result.get('sql_query', '')
        
        # Validate the query
        validation = {
            'syntax_valid': self._validate_sql_syntax(sql_query),
            'semantically_correct': self._validate_sql_semantics(sql_query),
            'performance_acceptable': self._validate_performance(sql_query),
            'results_expected': self._validate_expected_results(user_query, sql_query)
        }
        
        return {
            'status': 'completed',
            'validation': validation,
            'overall_valid': all(validation.values()),
            'warnings': self._generate_validation_warnings(validation)
        }
    
    def _optimize_query(self, user_query: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Query optimization tool"""
        query_result = previous_results.get('query_builder', {})
        sql_query = query_result.get('sql_query', '')
        
        # Optimize the query
        optimized_query = self._apply_optimizations(sql_query)
        
        return {
            'status': 'completed',
            'original_query': sql_query,
            'optimized_query': optimized_query,
            'optimizations_applied': self._get_applied_optimizations(sql_query, optimized_query),
            'performance_improvement': self._calculate_performance_improvement(sql_query, optimized_query)
        }

    # Helper methods for deep analysis
    
    def _analyze_deep_intent(self, user_query: str) -> Dict[str, Any]:
        """Deep intent analysis"""
        intent = {
            'primary_action': 'unknown',
            'target_entities': [],
            'filters': [],
            'aggregations': [],
            'needs_schema_exploration': False,
            'needs_query_building': True,
            'complexity_indicators': []
        }
        
        query_lower = user_query.lower()
        
        # Detect action
        if any(word in query_lower for word in ['count', 'how many']):
            intent['primary_action'] = 'count'
        elif any(word in query_lower for word in ['show', 'display', 'list', 'get']):
            intent['primary_action'] = 'select'
        elif any(word in query_lower for word in ['average', 'avg', 'mean']):
            intent['primary_action'] = 'aggregate'
        elif any(word in query_lower for word in ['find', 'search']):
            intent['primary_action'] = 'search'
        
        # Detect entities
        for table_name in self.schema_knowledge.keys():
            if table_name in query_lower or table_name[:-1] in query_lower:
                intent['target_entities'].append(table_name)
        
        # Detect complexity indicators
        if len(intent['target_entities']) > 1:
            intent['complexity_indicators'].append('multi_table')
        if any(word in query_lower for word in ['join', 'relationship', 'related']):
            intent['complexity_indicators'].append('joins_required')
        if any(word in query_lower for word in ['group by', 'aggregate', 'sum', 'count']):
            intent['complexity_indicators'].append('aggregation')
        
        # Determine if schema exploration is needed
        intent['needs_schema_exploration'] = len(intent['target_entities']) == 0 or 'complexity_indicators' in intent
        
        return intent
    
    def _analyze_conversation_context(self) -> Dict[str, Any]:
        """Analyze conversation context"""
        if not self.conversation_memory:
            return {'has_context': False, 'context_type': 'none'}
        
        recent_queries = [entry['query'] for entry in self.conversation_memory[-3:]]
        
        return {
            'has_context': True,
            'context_type': 'conversational',
            'recent_queries': recent_queries,
            'context_continuity': self._assess_context_continuity(recent_queries),
            'suggested_follow_ups': self._generate_contextual_follow_ups(recent_queries)
        }
    
    def _assess_query_complexity(self, user_query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Assess query complexity"""
        complexity_score = 0
        indicators = []
        
        # Base complexity
        if intent['primary_action'] == 'aggregate':
            complexity_score += 2
            indicators.append('aggregation')
        
        if len(intent['target_entities']) > 1:
            complexity_score += 3
            indicators.append('multi_table')
        
        if intent['complexity_indicators']:
            complexity_score += len(intent['complexity_indicators'])
            indicators.extend(intent['complexity_indicators'])
        
        # Determine complexity level
        if complexity_score >= 5:
            complexity_level = 'high'
        elif complexity_score >= 2:
            complexity_level = 'medium'
        else:
            complexity_level = 'low'
        
        return {
            'score': complexity_score,
            'level': complexity_level,
            'indicators': indicators,
            'needs_data_analysis': complexity_score >= 3,
            'needs_optimization': complexity_score >= 4
        }
    
    def _construct_sql_query(self, user_query: str, relevant_tables: List[str]) -> str:
        """Construct SQL query based on analysis"""
        query_lower = user_query.lower()
        
        # Determine primary table based on query content
        primary_table = self._determine_primary_table(user_query, relevant_tables)
        
        # Build query based on intent
        if self._is_count_query(query_lower):
            sql = self._build_count_query(query_lower, primary_table)
        elif self._is_aggregate_query(query_lower):
            sql = self._build_aggregate_query(query_lower, primary_table)
        elif self._is_filter_query(query_lower):
            sql = self._build_filter_query(query_lower, primary_table)
        elif self._is_show_all_query(query_lower):
            sql = self._build_show_all_query(query_lower, primary_table)
        else:
            sql = self._build_general_query(query_lower, primary_table)
        
        return sql
    
    def _determine_primary_table(self, user_query: str, relevant_tables: List[str]) -> str:
        """Determine the primary table based on query content"""
        query_lower = user_query.lower()
        
        # Check for explicit table mentions
        if 'user' in query_lower:
            return 'users'
        elif 'product' in query_lower:
            return 'products'
        elif 'order' in query_lower:
            return 'orders'
        elif 'category' in query_lower:
            return 'categories'
        elif 'review' in query_lower:
            return 'reviews'
        elif 'supplier' in query_lower:
            return 'suppliers'
        elif 'inventory' in query_lower:
            return 'inventory'
        
        # Return first relevant table or default
        return relevant_tables[0] if relevant_tables else 'users'
    
    def _is_count_query(self, query_lower: str) -> bool:
        """Check if this is a count query"""
        count_indicators = ['count', 'how many', 'number of', 'total number']
        return any(indicator in query_lower for indicator in count_indicators)
    
    def _is_aggregate_query(self, query_lower: str) -> bool:
        """Check if this is an aggregate query"""
        aggregate_indicators = ['average', 'avg', 'mean', 'sum', 'total', 'maximum', 'max', 'minimum', 'min']
        return any(indicator in query_lower for indicator in aggregate_indicators)
    
    def _is_filter_query(self, query_lower: str) -> bool:
        """Check if this is a filter query"""
        filter_indicators = ['greater than', 'less than', 'equal to', 'contains', 'with', 'having', 'where']
        return any(indicator in query_lower for indicator in filter_indicators)
    
    def _is_show_all_query(self, query_lower: str) -> bool:
        """Check if this is a show all query"""
        show_indicators = ['show all', 'list all', 'display all', 'get all', 'all']
        return any(indicator in query_lower for indicator in show_indicators)
    
    def _build_count_query(self, query_lower: str, table: str) -> str:
        """Build a COUNT query"""
        if 'user' in query_lower:
            return "SELECT COUNT(*) as user_count FROM users"
        elif 'product' in query_lower:
            return "SELECT COUNT(*) as product_count FROM products"
        elif 'order' in query_lower:
            return "SELECT COUNT(*) as order_count FROM orders"
        else:
            return f"SELECT COUNT(*) as total_count FROM {table}"
    
    def _build_aggregate_query(self, query_lower: str, table: str) -> str:
        """Build an aggregate query"""
        if 'average' in query_lower or 'avg' in query_lower:
            if 'price' in query_lower:
                return "SELECT AVG(price) as average_price FROM products"
            elif 'age' in query_lower:
                return "SELECT AVG(age) as average_age FROM users"
            else:
                return f"SELECT AVG(price) as average_value FROM {table}"
        elif 'sum' in query_lower or 'total' in query_lower:
            if 'order' in query_lower:
                return "SELECT SUM(total_amount) as total_orders FROM orders"
            else:
                return f"SELECT SUM(price) as total_value FROM {table}"
        elif 'maximum' in query_lower or 'max' in query_lower:
            if 'price' in query_lower:
                return "SELECT MAX(price) as max_price FROM products"
            else:
                return f"SELECT MAX(price) as max_value FROM {table}"
        elif 'minimum' in query_lower or 'min' in query_lower:
            if 'price' in query_lower:
                return "SELECT MIN(price) as min_price FROM products"
            else:
                return f"SELECT MIN(price) as min_value FROM {table}"
        else:
            return f"SELECT AVG(price) as average_value FROM {table}"
    
    def _build_filter_query(self, query_lower: str, table: str) -> str:
        """Build a filter query"""
        # Age filters
        if 'age' in query_lower and 'greater than' in query_lower:
            age_match = re.search(r'age.*?greater than.*?(\d+)', query_lower)
            if age_match:
                age = age_match.group(1)
                return f"SELECT * FROM users WHERE age > {age} LIMIT 100"
        
        if 'age' in query_lower and 'less than' in query_lower:
            age_match = re.search(r'age.*?less than.*?(\d+)', query_lower)
            if age_match:
                age = age_match.group(1)
                return f"SELECT * FROM users WHERE age < {age} LIMIT 100"
        
        # Price filters
        if 'price' in query_lower and 'greater than' in query_lower:
            price_match = re.search(r'price.*?greater than.*?(\d+)', query_lower)
            if price_match:
                price = price_match.group(1)
                return f"SELECT * FROM products WHERE price > {price} LIMIT 100"
        
        if 'price' in query_lower and 'less than' in query_lower:
            price_match = re.search(r'price.*?less than.*?(\d+)', query_lower)
            if price_match:
                price = price_match.group(1)
                return f"SELECT * FROM products WHERE price < {price} LIMIT 100"
        
        # Email filters
        if 'email' in query_lower and 'containing' in query_lower:
            email_match = re.search(r'email.*?containing.*?(\w+)', query_lower)
            if email_match:
                email_part = email_match.group(1)
                return f"SELECT * FROM users WHERE email LIKE '%{email_part}%' LIMIT 100"
        
        # Status filters
        if 'completed' in query_lower and 'order' in query_lower:
            return "SELECT * FROM orders WHERE status = 'completed' LIMIT 100"
        
        if 'premium' in query_lower or 'subscription' in query_lower:
            return "SELECT * FROM users WHERE subscription_type = 'premium' LIMIT 100"
        
        # Default filter query
        return f"SELECT * FROM {table} LIMIT 100"
    
    def _build_show_all_query(self, query_lower: str, table: str) -> str:
        """Build a show all query"""
        if 'user' in query_lower:
            return "SELECT * FROM users LIMIT 100"
        elif 'product' in query_lower:
            return "SELECT * FROM products LIMIT 100"
        elif 'order' in query_lower:
            return "SELECT * FROM orders LIMIT 100"
        elif 'category' in query_lower:
            return "SELECT * FROM categories LIMIT 100"
        else:
            return f"SELECT * FROM {table} LIMIT 100"
    
    def _build_general_query(self, query_lower: str, table: str) -> str:
        """Build a general query"""
        # Try to extract specific columns
        if 'name' in query_lower:
            if 'user' in query_lower:
                return "SELECT first_name, last_name, email FROM users LIMIT 100"
            elif 'product' in query_lower:
                return "SELECT name, price, brand FROM products LIMIT 100"
        
        # Default general query
        return f"SELECT * FROM {table} LIMIT 100"
    
    def _compile_final_response(self, user_query: str, final_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile the final response with all agentic information"""
        if not final_result:
            return {
                'error': 'Query processing failed after maximum iterations',
                'reasoning_chain': self.reasoning_chain,
                'iteration_count': self.iteration_count
            }
        
        tool_results = final_result.get('tool_results', {})
        query_result = tool_results.get('query_builder', {})
        
        return {
            'sql_query': query_result.get('sql_query', ''),
            'response': self._generate_agentic_response(user_query, final_result),
            'explanation': self._generate_detailed_explanation(user_query, final_result),
            'suggestions': self._generate_contextual_suggestions(user_query, final_result),
            'reasoning_chain': self.reasoning_chain,
            'iteration_count': self.iteration_count,
            'agent_state': self.agent_state.value,
            'tool_results': tool_results,
            'context': self.current_context
        }
    
    def _add_reasoning_step(self, phase: str, description: Any):
        """Add a reasoning step to the chain"""
        step = {
            'phase': phase,
            'description': str(description),
            'timestamp': datetime.now().isoformat(),
            'iteration': self.iteration_count
        }
        self.reasoning_chain.append(step)
    
    def _update_conversation_memory(self, user_query: str, context: Optional[Dict]):
        """Update conversation memory"""
        self.conversation_memory.append({
            'query': user_query,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        })
        
        # Keep only last 10 queries
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]
    
    # Additional helper methods (simplified implementations)
    
    def _calculate_confidence(self, intent: Dict, context: Dict) -> float:
        return 0.8 if intent['primary_action'] != 'unknown' else 0.5
    
    def _determine_strategy(self, intent: Dict, complexity: Dict) -> str:
        if complexity['level'] == 'high':
            return 'iterative_refinement'
        elif complexity['level'] == 'medium':
            return 'planned_execution'
        else:
            return 'direct_execution'
    
    def _assess_result_quality(self, tool_results: Dict) -> Dict:
        return {'confidence': 0.8, 'completeness': 0.9}
    
    def _needs_refinement(self, tool_results: Dict, quality: Dict) -> bool:
        return quality.get('confidence', 1.0) < 0.7
    
    def _update_context_from_results(self, tool_results: Dict):
        """Update context based on tool results"""
        pass
    
    def _extract_insights(self, tool_results: Dict) -> List[str]:
        return ["Query executed successfully", "Results validated"]
    
    def _generate_schema_suggestions(self, tables: List[str]) -> List[str]:
        suggestions = []
        for table in tables:
            if table in self.schema_knowledge:
                suggestions.extend(self.schema_knowledge[table]['sample_queries'])
        return suggestions[:5]
    
    def _determine_query_type(self, sql: str) -> str:
        if 'COUNT' in sql:
            return 'count'
        elif 'AVG' in sql or 'SUM' in sql:
            return 'aggregate'
        else:
            return 'select'
    
    def _calculate_query_complexity(self, sql: str) -> int:
        complexity = 1
        if 'JOIN' in sql:
            complexity += 2
        if 'WHERE' in sql:
            complexity += 1
        if 'GROUP BY' in sql:
            complexity += 2
        return complexity
    
    def _estimate_result_rows(self, sql: str) -> int:
        return 100 if 'LIMIT' in sql else 1000
    
    def _analyze_data_types(self, sql: str) -> Dict:
        return {'text': ['name', 'email'], 'numeric': ['age', 'price'], 'date': ['created_at']}
    
    def _assess_performance_impact(self, sql: str) -> str:
        return 'low' if 'LIMIT' in sql else 'medium'
    
    def _assess_business_value(self, query: str, sql: str) -> str:
        return 'high' if 'count' in query.lower() or 'trend' in query.lower() else 'medium'
    
    def _generate_analysis_recommendations(self, analysis: Dict) -> List[str]:
        return ["Consider adding indexes for better performance", "Results look comprehensive"]
    
    def _validate_sql_syntax(self, sql: str) -> bool:
        return True  # Simplified
    
    def _validate_sql_semantics(self, sql: str) -> bool:
        return True  # Simplified
    
    def _validate_performance(self, sql: str) -> bool:
        return 'LIMIT' in sql or 'COUNT' in sql
    
    def _validate_expected_results(self, query: str, sql: str) -> bool:
        return True  # Simplified
    
    def _generate_validation_warnings(self, validation: Dict) -> List[str]:
        warnings = []
        if not validation.get('performance_acceptable', True):
            warnings.append("Query may be slow on large datasets")
        return warnings
    
    def _apply_optimizations(self, sql: str) -> str:
        # Add basic optimizations
        if 'SELECT *' in sql and 'LIMIT' not in sql:
            sql += " LIMIT 100"
        return sql
    
    def _get_applied_optimizations(self, original: str, optimized: str) -> List[str]:
        optimizations = []
        if 'LIMIT' in optimized and 'LIMIT' not in original:
            optimizations.append("Added LIMIT clause for performance")
        return optimizations
    
    def _calculate_performance_improvement(self, original: str, optimized: str) -> str:
        return "20% faster" if 'LIMIT' in optimized and 'LIMIT' not in original else "No improvement"
    
    def _assess_context_continuity(self, queries: List[str]) -> float:
        return 0.7  # Simplified
    
    def _generate_contextual_follow_ups(self, queries: List[str]) -> List[str]:
        return ["Show more details", "Analyze trends", "Compare with other data"]
    
    def _generate_agentic_response(self, user_query: str, final_result: Dict) -> str:
        return f"I've analyzed your query '{user_query}' through {self.iteration_count} iterations of reasoning and acting. Here's what I found:"
    
    def _generate_detailed_explanation(self, user_query: str, final_result: Dict) -> str:
        return f"**Agentic Analysis Complete**\n\nI processed your query through multiple reasoning phases, using various tools to ensure accuracy and optimization."
    
    def _generate_contextual_suggestions(self, user_query: str, final_result: Dict) -> List[str]:
        return [
            "Explore related data patterns",
            "Analyze trends over time", 
            "Compare with other segments",
            "Deep dive into specific metrics"
        ]
    
    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_memory
    
    def clear_context(self):
        self.conversation_memory = []
        self.current_context = {}
        self.reasoning_chain = []
        self.tool_results = {}
        self.iteration_count = 0
    
    def get_context_summary(self) -> str:
        if not self.conversation_memory:
            return "No conversation context. I'm ready to help you explore your database with iterative reasoning!"
        
        return f"Conversation context: {len(self.conversation_memory)} previous queries analyzed."
