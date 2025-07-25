FROM python:3.9
LABEL authors="HARFOUSH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the service account key file into the container (if it exists)
# COPY rare-tape-382912-60409b30b3cc.json /usr/src/app/rare-tape-382912-60409b30b3cc.json

# Set the environment variable for Google Cloud authentication
# ENV GOOGLE_APPLICATION_CREDENTIALS="/usr/src/app/rare-tape-382912-60409b30b3cc.json"

EXPOSE 5100

CMD ["chainlit", "run", "app.py", "-h", "--port", "5100"]
