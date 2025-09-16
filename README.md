# 🤖 NQL Agent - Natural Query Language for PostgreSQL

A powerful Natural Query Language (NQL) agent that allows you to query PostgreSQL databases using plain English. This project demonstrates how to build an intelligent query interface that translates natural language into SQL queries.

![NQL Agent Demo](https://img.shields.io/badge/Demo-Live-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English
- **Smart SQL Translation**: Automatically converts NQL to optimized SQL
- **Beautiful Web Interface**: Modern, responsive UI for easy interaction
- **Docker Ready**: One-command setup with Docker Compose
- **Sample Database**: Pre-loaded with realistic demo data
- **Real-time Results**: Fast query execution with performance metrics
- **Schema Awareness**: Understands your database structure
- **Error Handling**: Helpful error messages and suggestions

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/nql_agent.git
cd nql_agent
```

### 2. Start the Application

```bash
docker-compose up -d
```

### 3. Access the Web Interface

Open your browser and navigate to: http://localhost:8000

That's it! The application will automatically:
- Start a PostgreSQL database with sample data
- Launch the NQL Agent web interface
- Initialize the database schema

## 📊 Sample Database

The demo includes a realistic e-commerce database with:

- **Users**: Customer information (name, email, age)
- **Products**: Product catalog (name, price, category, description)
- **Orders**: Order history (user, product, quantity, total, status)
- **Categories**: Product categories

## 💡 Example Queries

Try these natural language queries:

### Basic Queries
```
Show all users
Display all products
List all orders
Find users with age greater than 30
```

### Filtered Queries
```
Show products with price greater than 100
Find users with email containing john
Display completed orders
Show electronics products
```

### Aggregation Queries
```
Count all users
What is the average price of products?
Find the maximum age of users
Sum all order amounts
```

### Complex Queries
```
Show users who have placed orders
Find products with price between 50 and 200
Display orders from the last month
Show the most expensive product
```

## 🏗️ Architecture

### Components

1. **NQL Engine** (`app/nql_engine.py`)
   - Parses natural language queries
   - Maps NQL patterns to SQL constructs
   - Handles different query types (SELECT, aggregation, filtering)

2. **Database Manager** (`app/database.py`)
   - Manages PostgreSQL connections
   - Executes SQL queries safely
   - Provides schema information

3. **REST API** (`app/main.py`)
   - FastAPI-based web service
   - Query execution endpoints
   - Health checks and monitoring

4. **Web Interface** (`static/index.html`)
   - Modern, responsive UI
   - Real-time query execution
   - Results visualization

### Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 15
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Containerization**: Docker, Docker Compose
- **Styling**: Modern CSS with gradients and animations

## 🔧 Configuration

### Environment Variables

You can customize the database connection using these environment variables:

```bash
DB_HOST=localhost          # Database host
DB_PORT=5432              # Database port
DB_NAME=nql_demo          # Database name
DB_USER=postgres          # Database user
DB_PASSWORD=password      # Database password
```

### Docker Compose Customization

Edit `docker-compose.yml` to:
- Change exposed ports
- Modify database credentials
- Add persistent volumes
- Configure resource limits

## 🛠️ Development

### Local Development Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL**
   ```bash
   docker-compose up postgres -d
   ```

3. **Run the Application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Adding New Query Patterns

To extend the NQL engine, modify `app/nql_engine.py`:

```python
# Add new column mappings
self.column_mappings['new_field'] = ['new_column', 'alternative_name']

# Add new operators
self.operators['new_operator'] = 'SQL_OPERATOR'

# Add new query patterns
def _process_new_query_type(self, query: str) -> str:
    # Your implementation here
    pass
```

## 📈 Performance

- **Query Response Time**: Typically < 100ms for simple queries
- **Concurrent Users**: Supports multiple simultaneous users
- **Database Optimization**: Includes indexes for common query patterns
- **Memory Usage**: Lightweight container (~200MB)

## 🔒 Security

- **SQL Injection Protection**: Parameterized queries
- **Input Validation**: Query sanitization
- **Container Security**: Non-root user execution
- **Network Isolation**: Docker network segmentation

## 🧪 Testing

### Manual Testing

1. Use the web interface to test various query patterns
2. Check the API endpoints directly:
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "show all users"}'
   ```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/api/health

# Check database schema
curl http://localhost:8000/api/schema
```

## 📝 API Documentation

### Endpoints

- `GET /` - Web interface
- `POST /api/query` - Execute NQL query
- `GET /api/schema` - Get database schema
- `GET /api/health` - Health check

### Query Request Format

```json
{
  "query": "Show all users with age greater than 25"
}
```

### Query Response Format

```json
{
  "sql_query": "SELECT * FROM users WHERE age > 25 LIMIT 100",
  "results": [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30}
  ],
  "execution_time": 0.045,
  "error": null
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to new functions
- Include docstrings for new classes/methods
- Test your changes with various query patterns

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- PostgreSQL for the robust database engine
- Docker for containerization
- The open-source community for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nql_agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nql_agent/discussions)
- **Email**: your.email@example.com

## 🎯 Roadmap

- [ ] Support for JOIN operations
- [ ] Advanced aggregation functions
- [ ] Query history and favorites
- [ ] Export results to CSV/JSON
- [ ] Multi-database support
- [ ] Query optimization suggestions
- [ ] Natural language query suggestions
- [ ] User authentication and query permissions

---

**Made with ❤️ for the developer community**

# Third-party Licenses
- FastAPI (MIT)
- Uvicorn (BSD)
- Psycopg2-binary (LGPL)
- Streamlit (Apache 2.0)
This project uses open-source libraries under MIT, BSD, Apache 2.0, and LGPL licenses. See NOTICE.md for details.

*Star this repository if you find it helpful!*
