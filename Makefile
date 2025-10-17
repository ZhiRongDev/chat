.PHONY: help dev prod logs health backup restore clean test

# Default target
.DEFAULT_GOAL := help

help:
	@echo "🚀 Chat Application - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  make test         - Test Docker setup and configuration"
	@echo "  make dev          - Start development environment with hot-reload"
	@echo "  make prod         - Deploy production environment"
	@echo "  make logs ENV=dev - View logs (ENV=dev or prod, default: dev)"
	@echo "  make health       - Run health checks"
	@echo "  make backup       - Create database backup"
	@echo "  make restore      - Restore database from backup"
	@echo "  make stop         - Stop all services"
	@echo "  make clean        - Remove all containers, volumes, and images"
	@echo "  make rebuild      - Rebuild all images from scratch"
	@echo ""

# Test setup
test:
	@./scripts/test-setup.sh

# Development environment
dev:
	@./scripts/dev.sh

# Production environment
prod:
	@./scripts/prod.sh

# View logs
logs:
	@./scripts/logs.sh $(ENV)

# Health check
health:
	@./scripts/health-check.sh $(ENV)

# Database backup
backup:
	@./scripts/db-backup.sh $(ENV)

# Database restore
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make restore FILE=backups/backup_file.sql.gz ENV=prod"; \
		exit 1; \
	fi
	@./scripts/db-restore.sh $(FILE) $(ENV)

# Stop services
stop:
	@echo "🛑 Stopping services..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml down 2>/dev/null || true
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true
	@echo "✅ Services stopped"

# Clean everything
clean:
	@echo "⚠️  This will remove all containers, volumes, and images!"
	@read -p "Are you sure? (yes/no): " answer; \
	if [ "$$answer" = "yes" ]; then \
		echo "🧹 Cleaning up..."; \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --rmi all 2>/dev/null || true; \
		docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --rmi all 2>/dev/null || true; \
		echo "✅ Cleanup complete"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi

# Rebuild images
rebuild:
	@echo "🔨 Rebuilding all images..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
	@echo "✅ Rebuild complete"
