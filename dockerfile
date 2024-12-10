# Base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Set environment variables
# Puedes agregar más variables de entorno si son necesarias
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run"]

