# EduAI: AI-Powered Educational Content Generator

EduAI is an AI-powered educational content generator that creates personalized learning materials based on user-specified topics and audience levels. This project was developed for NVIDIA's World's Shortest Hackathon at GTC 2025.

## Features

### Content Generator
- **Topic-based Content Generation**: Enter any educational topic and receive tailored content
- **Audience Level Customization**: Adapt content for different educational levels (elementary to graduate)
- **AI-Generated Text Explanations**: Detailed educational content created using NVIDIA's LLM endpoints
- **AI-Generated Visual Representations**: Custom images to illustrate key concepts
- **Image Regeneration**: Regenerate images or edit prompts for better results
- **HTML Export**: Download complete lessons as HTML files for offline use

### Deep Research
- **Comprehensive Research**: In-depth exploration of educational topics with detailed sections
- **Academic References**: Properly formatted citations for academic research
- **Key Concepts Extraction**: Identification of the most important concepts in the topic
- **Related Topics Suggestions**: Recommendations for further research
- **Visualization Generation**: Custom visualizations to enhance understanding
- **Academic Levels**: Support for high school, undergraduate, and graduate level research
- **Trending Topics**: Discover popular research topics in different academic disciplines

## Architecture

EduAI follows a modern web application architecture:

- **Frontend**: Next.js, React, TailwindCSS
- **Backend**: Python FastAPI
- **AI Services**: NVIDIA NIM API endpoints
  - LLM endpoints for text generation
  - Text-to-image endpoints for visual content

## Getting Started

### Prerequisites

- Docker and Docker Compose
- NVIDIA API key (optional for production use; development mode uses mock data)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eduai.git
   cd eduai
   ```

2. Set up environment variables:
   ```bash
   # For backend
   cp backend/.env.example backend/.env
   
   # For frontend
   cp frontend/.env.example frontend/.env
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up
   ```

4. Access the application at http://localhost:3000

## Development Mode

By default, the application runs in development mode using mock data instead of calling the NVIDIA API. This is controlled by the `USE_MOCK_DATA` setting in the backend's `.env` file.

To use the actual NVIDIA API:

1. Obtain an API key from NVIDIA
2. Update the `NVIDIA_API_KEY` in the backend's `.env` file
3. Set `USE_MOCK_DATA=False` in the backend's `.env` file

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
eduai-project/
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── EduAI.jsx       # Content generator component
│   │   │   ├── DeepResearch.jsx # Deep research component
│   │   │   ├── Navbar.jsx      # Navigation component
│   │   │   └── ...
│   │   ├── pages/              # Next.js pages
│   │   ├── services/           # Frontend services
│   │   └── styles/             # CSS/styling
│   └── ...
│
├── backend/                    # Python backend
│   ├── app/                    # Main application code
│   │   ├── routers/            # API route handlers
│   │   ├── services/           # Business logic
│   │   ├── models/             # Data models
│   │   └── nvidia_api/         # NVIDIA API integration
│   └── ...
│
└── docker-compose.yml          # Docker Compose configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NVIDIA for hosting the World's Shortest Hackathon at GTC 2025
- NVIDIA NIM for providing the AI endpoints
- Vercel for Next.js and frontend technologies
