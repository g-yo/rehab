# Use Python 3.10 as base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Django port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "rehab_center.wsgi:application"]
