# Use the official Python image as the base image
FROM python:3.11-slim

# Copy the requirements file into the container
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# load the vector store using the create_and_load_vector_db.py script
RUN python3.11 create_and_load_vector_db.py

# Expose the port the app runs on
EXPOSE 8080

# Command to run the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]