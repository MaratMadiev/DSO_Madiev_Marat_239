# Makefile
.PHONY: build run test scan clean

# Build the Docker image
build:
	docker build -t suggestion-box:latest -f docker/Dockerfile .

# Run with docker-compose
run:
	docker-compose up --build

# Run in background
run-detached:
	docker-compose up -d --build

# Stop services
stop:
	docker-compose down

# Run tests in container
test:
	docker build -t suggestion-box-test -f docker/Dockerfile .
	docker run --rm suggestion-box-test python -m pytest tests/ -v

# Security scan
scan:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image suggestion-box:latest

# Lint Dockerfile
lint:
	docker run --rm -i hadolint/hadolint < docker/Dockerfile

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Check container health
health:
	curl -f http://localhost:8000/health || echo "Container is not healthy"

# Show logs
logs:
	docker-compose logs -f
