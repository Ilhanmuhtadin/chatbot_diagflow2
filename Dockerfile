 
# Gunakan Python 3.9 sebagai base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file ke dalam container
COPY . .

# Install Ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list \
    && apt update && apt install ngrok

# Set Authtoken Ngrok (Gantilah dengan token milikmu)
ENV NGROK_AUTHTOKEN="2uLB0XFqIxHqWZX5R8g08MzQU2H_B1k6ynCoGX7RTLoMwYMX"

# Jalankan FastAPI dan Ngrok secara bersamaan
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & ngrok http 8000 --authtoken $NGROK_AUTHTOKEN

