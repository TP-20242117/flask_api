FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages, including apt-utils to suppress warnings
RUN apt-get update && apt-get install -y apt-utils g++ build-essential libgl1 libglib2.0-0

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable for Flask environment and default port
ENV FLASK_APP=app.py  

EXPOSE 8080

# Run the Flask application
CMD ["python3", "app/app.py"]