# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (app, tests, etc.)
COPY . .

# Expose port
EXPOSE 5000

# Default command
CMD ["python", "run.py"]
