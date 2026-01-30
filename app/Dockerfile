# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies (Nmap is required for the library)
RUN apt-get update && apt-get install -y \
    nmap \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py and any subfolders & logic files into the container
COPY . .

# Run the scanner
CMD ["python", "main.py", "--subnet", "172.20.0.0/24", "--log", "shared/discovery.log", "--output", "shared/discovery-scan.json"]
