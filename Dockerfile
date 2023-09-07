# Use python3.11-slim as the base image
FROM python:3.11-slim

RUN mkdir -p /app

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --compile --only main

# Copy the rest of the application code
COPY main.py /app/main.py
COPY bunny2 /app/bunny2
COPY plugins /app/plugins


# Expose the uvicorn server port
EXPOSE 8000

# Run the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]