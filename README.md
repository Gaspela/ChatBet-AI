# ChatBet AI Assistant

An intelligent conversational AI chatbot designed for sports betting analysis, match recommendations, and interactive sports queries. Built with FastAPI and Google's Gemini AI, this system provides real-time sports data integration with natural language processing capabilities.

## Project Description

ChatBet AI Assistant is a sophisticated chatbot that combines artificial intelligence with real-time sports data to provide users with:

- **Intelligent Sports Queries**: Natural language processing for match schedules, team information, and tournament data
- **Betting Analysis**: Odds comparison, profit simulations, and risk assessment
- **Smart Recommendations**: AI-powered betting suggestions based on competitive analysis
- **Conversational Context**: Maintains conversation history and user preferences
- **Real-time Data Integration**: Live sports information from ChatBet API

## Technologies Used

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.11+
- **Google Gemini AI**: Advanced language model for natural language processing
- **Pydantic**: Data validation and settings management using Python type annotations
- **httpx**: Async HTTP client for external API integration
- **Python 3.11**: Latest Python version with enhanced performance

### Infrastructure
- **Docker & Docker Compose**: Containerization for easy deployment and development
- **Nginx**: Web server for static frontend serving
- **uvicorn**: ASGI server for running the FastAPI application

### AI & Data Processing
- **Google Generative AI SDK**: Integration with Gemini AI models
- **JSON Schema Validation**: Structured response handling
- **Context Management**: In-memory conversation state management
- **Dynamic Prompt Engineering**: Intelligent prompt construction for AI interactions

### Architecture Pattern
- **Modular Design**: Separated concerns with dedicated services
- **Async/Await**: Non-blocking operations for better performance
- **RESTful API**: Standard HTTP methods and status codes
- **MVC Pattern**: Clear separation between models, views, and controllers

## Project Architecture

### Folder Structure
```
ChatBet-AI/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Application configuration
│   │
│   ├── api/                       # API Layer
│   │   ├── __init__.py
│   │   └── routes.py             # All API endpoints
│   │
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── chatbot_service.py    # Main orchestration service
│   │   ├── data_service.py       # Data processing & caching
│   │   └── chatbet_client.py     # External API client
│   │
│   ├── ai/                        # AI Processing Layer
│   │   ├── __init__.py
│   │   ├── analyzers.py          # Betting analysis engine
│   │   └── prompt_builder.py     # AI prompt engineering
│   │
│   └── models/                    # Data Models Layer
│       ├── __init__.py
│       └── schemas.py            # Pydantic data models
│
├── web-client/                    # Frontend Interface
├── docker-compose.yml            # Container orchestration
├── Dockerfile                    # Backend container config
└── requirements.txt              # Python dependencies
```

### Architecture Flow
```
HTTP Request → API Layer (routes.py)
                    ↓
              Services Layer (chatbot_service.py)
                    ↓
            ┌─────────────────────────────────────┐
            │                                     │
         AI Layer                          Data Layer
    (analyzers.py +                   (data_service.py +
     prompt_builder.py)                chatbet_client.py)
            │                                     │
            └─────────────────────────────────────┘
                    ↓
              Models Layer (schemas.py)
                    ↓
               JSON Response
```

### Key Components
- **API Layer**: FastAPI routes and endpoint definitions
- **Services Layer**: Business logic, orchestration, and external integrations  
- **AI Layer**: Google Gemini integration, betting analysis, and prompt engineering
- **Models Layer**: Pydantic models for data validation and serialization

## Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Docker Desktop**: 
   - Windows: [Download Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
   - macOS: [Download Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Google AI API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Save the key for configuration

## Step-by-Step Setup Instructions

### Step 1: Clone and Navigate to Project
```bash
# If you have the project locally
cd /path/to/chatbet-ai

# If cloning from repository
git clone <repository-url>
cd chatbet-ai
```

### Step 2: Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API key
# Replace 'your_google_ai_api_key_here' with your actual Google AI API key
```

**Required .env Configuration:**
```bash
# ChatBet API Configuration
CHATBET_API_BASE_URL=https://v46fnhvrjvtlrsmnismnwhdh5y0lckdl.lambda-url.us-east-1.on.aws
CHATBET_API_TIMEOUT=30

# Google AI Configuration (REQUIRED)
GOOGLE_AI_API_KEY=your_actual_google_ai_api_key_here

# Google AI Model Configuration
GOOGLE_AI_MODEL=gemini-1.5-flash

# Application Settings
DEBUG=true
API_TITLE=ChatBet AI Assistant
API_VERSION=1.0.0
API_DESCRIPTION=Intelligent conversational chatbot for sports betting

# Context Management
MAX_CONVERSATION_HISTORY=10
CONVERSATION_TIMEOUT=3600
```

### Step 3: Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Step 4: Verify Installation
Wait for the services to start, then verify:

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Expected output when services are ready:
```
✔ Container chatbet-ai-chatbet-ai-1   Started
✔ Container chatbet-ai-web-client-1   Started
```

## Required Environment Variables

The `.env.example` file contains all necessary configuration variables:

### Essential Variables
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_AI_API_KEY` | Google AI API authentication key | Yes | `AIzaSyBxxxxxxxxxxxxxxxxxxxxx` |
| `CHATBET_API_BASE_URL` | ChatBet API endpoint URL | Yes | `https://v46fnhvrjvtlrsmnismnwhdh5y0lckdl.lambda-url.us-east-1.on.aws` |

### Optional Configuration
| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `GOOGLE_AI_MODEL` | AI model to use | `gemini-1.5-flash` | `gemini-1.5-flash`, `gemini-pro` |
| `DEBUG` | Enable debug mode | `true` | `true`, `false` |
| `MAX_CONVERSATION_HISTORY` | Messages to keep in context | `10` | Any integer |
| `CONVERSATION_TIMEOUT` | Session timeout in seconds | `3600` | Any integer |
| `CHATBET_API_TIMEOUT` | API request timeout | `30` | Any integer |

## Usage Examples & Sample Interactions

### Using the Web Interface
1. Open http://localhost:3000 in your browser
2. Type your questions in the chat input
3. Press Enter or click Send

### Direct API Usage

#### PowerShell Example (Windows):
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    "message" = "Who plays tomorrow?"
    "session_id" = "user123"
    "user_key" = "test_user"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Headers $headers -Body $body
$response | ConvertTo-Json -Depth 10
```

#### Curl Example (Linux/Mac):
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the odds for Barcelona vs Real Madrid?",
    "session_id": "user123",
    "user_key": "test_user"
  }'
```

### Sample Interactions

#### 1. Team Schedule Queries
```json
// Input
{
  "message": "When does Barcelona play next?",
  "session_id": "user123",
  "user_key": "test_user"
}

// Output
{
  "response": "Barcelona plays tomorrow against Real Madrid in La Liga at 15:00 UTC, and on September 22nd against PSG in the Champions League.",
  "intent": "team_schedule",
  "confidence": 0.95,
  "data": {
    "fixtures": [...],
    "tournaments": [...]
  }
}
```

#### 2. Betting Odds Analysis
```json
// Input
{
  "message": "What are the odds for Liverpool to win?",
  "session_id": "user123", 
  "user_key": "test_user"
}

// Output
{
  "response": "Liverpool has odds of 2.10 to win against Chelsea on Sunday. The draw odds are 3.40, and Chelsea to win is at 3.20.",
  "intent": "odds_query",
  "confidence": 0.92,
  "data": {
    "odds": [...],
    "match_details": {...}
  }
}
```

#### 3. Betting Simulation
```json
// Input  
{
  "message": "Simulate a $100 bet on Manchester United",
  "session_id": "user123",
  "user_key": "test_user"
}

// Output
{
  "response": "With a $100 bet on Manchester United to win (odds 2.50), you would profit $150 for a total return of $250. Remember, this is a simulation only.",
  "intent": "bet_simulation",
  "confidence": 0.88,
  "data": {
    "simulation_results": [...],
    "profit_calculation": {...}
  }
}
```

#### 4. Match Recommendations
```json
// Input
{
  "message": "What's the best match to bet on this weekend?",
  "session_id": "user123",
  "user_key": "test_user"
}

// Output
{
  "response": "I recommend Arsenal vs Tottenham on Sunday. Arsenal has strong home odds at 1.85 with a 54% win probability. Alternative: Chelsea vs Liverpool offers good value with balanced 2.20 odds.",
  "intent": "betting_recommendation", 
  "confidence": 0.87,
  "data": {
    "recommendations": [...],
    "analysis": {...}
  }
}
```

## Technical Decisions Explained

### 1. **Framework Selection - FastAPI**
**Decision**: Choose FastAPI over Flask/Django
**Reasoning**: 
- Modern async/await support for better performance
- Automatic OpenAPI documentation generation
- Built-in data validation with Pydantic
- Excellent performance comparable to Node.js and Go
- Type hints support for better code quality

### 2. **AI Model - Google Gemini 1.5 Flash**
**Decision**: Use Google Gemini instead of OpenAI GPT
**Reasoning**:
- Free tier available for development and testing
- Excellent context window (1M+ tokens)
- Strong performance in structured output generation
- Native JSON mode support
- Good latency and reliability

### 3. **Architecture Pattern - Modular Services**
**Decision**: Separate concerns into dedicated service classes
**Reasoning**:
- **ChatBotService**: Main orchestration and AI interaction
- **PromptBuilder**: Specialized prompt engineering and context management
- **APIAnalyzer**: Complex data analysis and processing logic
- **DataService**: Caching and data optimization
- **ChatBetClient**: External API integration

**Benefits**:
- Easier testing and maintenance
- Clear separation of responsibilities
- Improved code reusability
- Simplified debugging

### 4. **Context Management - In-Memory Storage**
**Decision**: Use in-memory context storage instead of Redis/Database
**Reasoning**:
- Faster access times for development
- Simplified setup and deployment
- Sufficient for prototype/demo purposes
- Easy migration path to Redis for production
- Lower infrastructure requirements

### 5. **Data Processing Strategy - Smart Caching**
**Decision**: Implement intelligent data caching and filtering
**Reasoning**:
- ChatBet API returns large datasets (1000+ fixtures)
- Filter data at the service layer to relevant matches
- Cache frequently accessed data (sports, tournaments)
- Reduce API calls and improve response times

### 6. **Error Handling Strategy**
**Decision**: Graceful degradation with informative error responses
**Reasoning**:
- Never expose internal errors to users
- Provide helpful fallback responses
- Log detailed errors for debugging
- Maintain conversation flow even during API failures

### 7. **Containerization - Docker Compose**
**Decision**: Use Docker for both development and deployment
**Reasoning**:
- Consistent environment across different systems
- Easy dependency management
- Simplified deployment process
- Isolation of services
- Production-ready configuration

## Production Deployment Guide

### Environment-Specific Configuration
```bash
# Production .env
GOOGLE_AI_API_KEY=prod_api_key_here
DEBUG=false
REDIS_URL=redis://production-redis:6379
DATABASE_URL=postgresql://prod-db:5432/chatbet
LOG_LEVEL=INFO
```

## Development Commands

```bash
# Development setup
docker-compose up --build

# Run tests
docker-compose exec chatbet-ai pytest

# View logs
docker-compose logs -f chatbet-ai

# Access container shell
docker-compose exec chatbet-ai bash

# Reset everything
docker-compose down --volumes
docker-compose up --build
```

## Changelog & Architecture Updates

### Version 1.1.0 - September 2025
**🏗️ Major Architecture Restructure**

**New Folder Structure:**
- Reorganized codebase into layered architecture
- Separated concerns by responsibility and functionality
- Improved maintainability and scalability

**Changes Made:**
- ✅ **API Layer**: Moved all endpoints to `app/api/routes.py`
- ✅ **Services Layer**: Centralized business logic in `app/services/`
  - `chatbot_service.py` - Main orchestration
  - `data_service.py` - Data processing & caching  
  - `chatbet_client.py` - External API integration
- ✅ **AI Layer**: AI-specific modules in `app/ai/`
  - `analyzers.py` - Betting analysis engine
  - `prompt_builder.py` - Prompt engineering
- ✅ **Models Layer**: All Pydantic models in `app/models/schemas.py`
- ✅ **Updated Imports**: All imports updated to reflect new structure
- ✅ **Documentation**: Comprehensive docstrings added to all modules

**Benefits:**
- 📦 **Better Organization**: Clear separation of responsibilities
- 🔧 **Easier Maintenance**: Logical grouping of related functionality  
- 🚀 **Enhanced Scalability**: Simple to add new features in appropriate layers
- 🧪 **Improved Testing**: Easier unit testing by layer
- 📚 **Better Documentation**: Clear module purposes and functionality

**Migration Notes:**
- All existing functionality preserved
- API endpoints remain the same
- Docker configuration unchanged
- Environment variables unchanged

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google AI Python SDK](https://github.com/google/generative-ai-python)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## License

This project is a technical demonstration created for ChatBet assessment purposes.

**Version**: 1.1.0  
**Last Updated**: September 2025  
**Architecture**: Layered modular design  
**Developed for**: ChatBet Technical Assessment
