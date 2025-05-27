# backend/Dockerfile


# Dockerfile to build a Python 3.10-slim image, installs dependencies, copies the app code, exposes port 8000, and starts the FastAPI service with Uvicorn
# using slim Python image
FROM python:3.10-slim

# Set a working directory
WORKDIR /usr/src/app

# copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in your application code
COPY app ./app
# COPY .env .env

# Expose port and start Uvicorn
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
