# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies (Nmap, Ruby, and Recog)
RUN apt-get update && apt-get install -y \
    nmap \
    libpcap-dev \
    ruby \
    ruby-dev \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Recog gem
RUN gem install recog

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py and any subfolders & logic files into the container
COPY . .

# No CMD - docker-compose.yml handles keeping container alive for interactive use
