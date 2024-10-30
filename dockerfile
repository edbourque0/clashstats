# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Change working directory to clashstats
WORKDIR /clashstats

# Expose port (modify according to your application)
EXPOSE 8000

# Command to run the application
# Adjust this command based on the entry point for clashstats (e.g., a Flask app might use "flask run", Django "gunicorn")
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]