FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /ask_sharkevich

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY ask_sharkevich .

# Expose the port Django will run on
EXPOSE 8000

# Run the Django application using Gunicorn for production
# For development, you might use: CMD python manage.py runserver 0.0.0.0:8000
COPY run.sh .

RUN chmod +x run.sh

CMD ["./run.sh"]