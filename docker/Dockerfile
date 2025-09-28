FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip \
    ffmpeg portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Download models
RUN python3 scripts/download_models.py

# Expose port
EXPOSE 8000

# Run LEONA
CMD ["python3", "backend/main.py"]