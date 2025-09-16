# NQL Agent Makefile

.PHONY: help build up down logs test clean restart

# Default target
help:
	@echo "NQL Agent - Available Commands:"
	@echo ""
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start the application"
	@echo "  make down      - Stop the application"
	@echo "  make restart   - Restart the application"
	@echo "  make logs      - Show application logs"
	@echo "  make test      - Run test queries"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make dev       - Start in development mode"
	@echo ""

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start the application
up:
	@echo "🚀 Starting NQL Agent..."
	docker-compose up -d
	@echo "✅ Application started!"
	@echo "🌐 Web interface: http://localhost:8000"
	@echo "📊 API docs: http://localhost:8000/docs"

# Stop the application
down:
	@echo "🛑 Stopping NQL Agent..."
	docker-compose down

# Restart the application
restart: down up

# Show logs
logs:
	@echo "📋 Showing application logs..."
	docker-compose logs -f

# Run tests
test:
	@echo "🧪 Running test queries..."
	python test_queries.py

# Development mode (with live reload)
dev:
	@echo "🔧 Starting in development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Check status
status:
	@echo "📊 Application Status:"
	@docker-compose ps

# Initialize database
init-db:
	@echo "🗄️ Initializing database..."
	docker-compose exec nql-agent python app/init_db.py
