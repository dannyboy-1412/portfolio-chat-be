# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Poetry and system dependencies
RUN pip install poetry

# Copy only necessary project files to the container
COPY pyproject.toml poetry.lock ./

# Install dependencies with Poetry
RUN poetry install --no-interaction --no-root

# Copy the source code
COPY src ./src
COPY requirements.txt ./

# Set environment variables for FastAPI and Mangum
ENV PORT=8080

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
