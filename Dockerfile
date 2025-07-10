FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY script.py /app/script.py
WORKDIR /app

# Run the script on container start
CMD ["python", "script.py", "/input", "/output"]

