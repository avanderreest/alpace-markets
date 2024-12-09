# Use the slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install build dependencies and debugging tools
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    pkg-config \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    bash \
    curl \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Install and configure OpenSSH for SSH access
# RUN apt-get install -y openssh-server
# RUN mkdir /var/run/sshd
# RUN echo 'root:password' | chpasswd
# EXPOSE 22

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 and 5010 for the application and potential debugging
EXPOSE 80 5010

# Set the entrypoint to bash for debugging (optional)
# CMD ["bash"]

# Command to run the application
CMD ["python", "alpaca_connector.py"] 