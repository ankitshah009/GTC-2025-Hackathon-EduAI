# EduAI - Educational Content Generator

EduAI is an AI-powered educational content generation platform that helps create educational materials for various academic levels.

## Features

- **Content Generation**: Generate educational content for any topic and audience level
- **Deep Research**: Create comprehensive research content with academic references
- **Image Generation**: Generate relevant educational diagrams and visualizations
  - **NVIDIA API**: High-quality image generation with NVIDIA's advanced models
  - **Google Gemini API**: State-of-the-art multimodal image generation with detailed labeling

## Project Structure

```
.
├── backend/               # FastAPI backend
│   ├── app/               # Main application code
│   │   ├── models/        # Pydantic data models
│   │   ├── nvidia_api/    # NVIDIA API client code
│   │   ├── gemini_api/    # Google Gemini API client code
│   │   ├── routers/       # API route handlers
│   │   └── services/      # Business logic services
│   ├── config/            # Configuration settings
│   ├── Dockerfile         # Backend Docker configuration
│   ├── requirements.txt   # Python dependencies
│   └── main.py            # FastAPI application entry point
├── frontend/              # Next.js frontend
│   ├── components/        # React components
│   ├── lib/               # Utility functions and API clients
│   ├── pages/             # Next.js pages
│   ├── public/            # Static assets
│   ├── styles/            # CSS styles
│   ├── Dockerfile         # Frontend Docker configuration
│   └── package.json       # JavaScript dependencies
├── simple_gemini_test.py  # Standalone test for Gemini API
├── docker-compose.yml     # Docker Compose configuration
├── setup.sh               # Setup script
├── run_backend.sh         # Script to run the backend server
├── test.sh                # Test script
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+
- Docker & Docker Compose (optional, for containerized setup)
- Google Gemini API key for image generation
- NVIDIA API key for alternative image generation

## Quick Start

The easiest way to get started is by using the setup script:

```bash
# Make the scripts executable
chmod +x setup.sh test.sh run_backend.sh

# Run the setup script
./setup.sh
```

The setup script will:

1. Check prerequisites
2. Ask whether you want to set up in development or Docker mode
3. Create necessary environment files
4. Install dependencies
5. Optionally start the application

## Manual Setup

If you prefer to set up manually, follow these steps:

### Backend Setup

```bash
# Create Python virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example or create new)
cp .env.example .env  # Edit as needed with your API keys

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create .env file
cp .env.example .env  # Edit as needed

# Start the frontend development server
npm run dev
```

## Docker Setup

To run the application using Docker:

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## Testing

After starting the application, you can run the test script to verify functionality:

```bash
./test.sh
```

The test script checks:
- Backend health
- API documentation
- Frontend availability
- Content generation API
- Deep research API
- Image generation with NVIDIA and Google Gemini

### Testing Gemini Image Generation

You can test the Gemini image generation separately with the provided test script:

```bash
# Set your API key as an environment variable
export GEMINI_API_KEY=your_api_key_here

# Run the test script
python simple_gemini_test.py

# Alternatively, pass the API key as an argument
python simple_gemini_test.py your_api_key_here
```

## Manual Testing

1. Open http://localhost:3000 in your browser
2. Navigate to the Content Generator or Deep Research pages
3. Enter a topic and other required information
4. Submit the form and verify the results

## API Documentation

When the backend is running, you can access the API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Configuration

### Backend Configuration

Edit the `backend/.env` file to configure:
- API keys (GEMINI_API_KEY, NVIDIA_API_KEY)
- Model settings
- Debug mode
- CORS settings

### Frontend Configuration

Edit the `frontend/.env` file to configure:
- API URL

## Image Generation Features

EduAI supports two state-of-the-art image generation APIs:

### NVIDIA Image Generation

The NVIDIA API client is used for generating images with NVIDIA's powerful generative models. This is ideal for:
- High-quality illustrations
- Photorealistic renderings
- Complex diagrams

### Google Gemini Image Generation

The Google Gemini API integration provides advanced multimodal image generation with:
- Educational context enhancement
- Accurate labeling of scientific concepts
- Clear visual representation of complex ideas

The Gemini implementation follows these steps:
1. Receives a prompt from the user or content generation system
2. Enhances the prompt with educational context
3. Calls the Google Gemini API using the latest models
4. Processes the response and extracts the generated image
5. Saves the image with a unique identifier
6. Returns the URL for frontend display

## Development

For development, it's recommended to run the backend and frontend separately.

In one terminal:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:
```bash
cd frontend
npm run dev
```

## Using the Run Script

For convenience, you can use the provided run script to start the backend:

```bash
./run_backend.sh
```

This script:
1. Activates the virtual environment
2. Sets the necessary environment variables
3. Starts the FastAPI server with hot reloading

## License

This project is licensed under the MIT License - see the LICENSE file for details.