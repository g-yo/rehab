# Use Python 3.10 as base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 80 instead of 8000
EXPOSE 80

# Start Gunicorn server on port 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "rehab_center.wsgi:application"]
