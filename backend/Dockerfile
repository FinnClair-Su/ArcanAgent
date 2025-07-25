# Dockerfile for backend

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY ./backend /app/backend
COPY ./main.py /app/main.py
COPY ./config.json /app/config.json
COPY ./.env /app/.env
COPY ./knowledge_base /app/knowledge_base

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Run main_server.py when the container launches
CMD ["uvicorn", "backend.main_server:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
