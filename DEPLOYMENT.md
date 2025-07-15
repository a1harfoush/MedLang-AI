# MedLang Deployment Guide

This guide covers different deployment options for the MedLang medical chatbot.

## Prerequisites

1. **API Keys Required:**
   - Groq API key for LLM functionality
   - Google Cloud Project with Translation API enabled
   - Google Cloud Service Account JSON file

2. **Environment Setup:**
   - Copy `.env.example` to `.env`
   - Fill in your actual API keys and credentials

## Local Development

### Option 1: Direct Python Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
chainlit run app.py
```

### Option 2: Using Setup Script
```bash
python setup.py
# Follow the prompts to configure your environment
chainlit run app.py
```

## Docker Deployment

### Single Container
```bash
# Build the image
docker build -t medlang .

# Run the container
docker run -p 5100:5100 --env-file .env medlang
```

### Docker Compose
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Cloud Deployment

### Google Cloud Run
1. Build and push to Google Container Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/medlang
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy medlang \
  --image gcr.io/YOUR_PROJECT_ID/medlang \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5100
```

### Heroku
1. Create a Heroku app:
```bash
heroku create your-medlang-app
```

2. Set environment variables:
```bash
heroku config:set GROQ_API_KEY=your_key
heroku config:set GOOGLE_CLOUD_PROJECT_ID=your_project
```

3. Deploy:
```bash
git push heroku main
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `GOOGLE_CLOUD_PROJECT_ID` | Google Cloud project ID | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | Yes |
| `LANGCHAIN_TRACING_V2` | Enable LangChain tracing | No |
| `LANGCHAIN_API_KEY` | LangChain API key | No |

## Health Checks

The application exposes a health check endpoint at `/health` for monitoring.

## Troubleshooting

### Common Issues

1. **Authentication Errors:**
   - Verify Google Cloud credentials are properly set
   - Check service account permissions

2. **API Rate Limits:**
   - Monitor Groq API usage
   - Implement rate limiting if needed

3. **Translation Errors:**
   - Ensure Translation API is enabled in Google Cloud
   - Check project billing is active

### Logs

- Local: Check console output
- Docker: `docker logs container_name`
- Cloud Run: Use Google Cloud Console logs
- Heroku: `heroku logs --tail`