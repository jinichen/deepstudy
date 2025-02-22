# DeepStudy - AI-Powered Research Report Generator

## Overview

DeepStudy is an innovative application designed to automate the process of in-depth research and report generation. Leveraging the power of AI, DeepStudy can quickly gather information on a given topic from the web, analyze the data, and generate comprehensive research reports in Markdown format. This tool is ideal for researchers, analysts, and anyone needing to quickly get up to speed on a new topic or generate detailed reports.

## Features

- **AI-Driven Research Planning:** Automatically breaks down research topics into key questions and formulates effective search queries.
- **Comprehensive Web Search:** Utilizes the Tavily API to perform in-depth web searches, gathering data from a wide range of sources, including academic papers, industry reports, and news articles.
- **Credibility Scoring:** Evaluates the credibility of search results, prioritizing authoritative sources for higher quality data.
- **Intelligent Data Analysis:** Employs the Gemini AI model to analyze research data, identify key trends, and extract meaningful insights across various dimensions like market size, technology trends, and competitive landscape.
- **Automated Report Generation:** Generates detailed research reports in Markdown format, complete with sections on摘要 (Abstract), 研究背景 (Research Background), 研究方法 (Research Methods), 市场分析 (Market Analysis), 技术分析 (Technology Analysis), 机遇与挑战 (Opportunities and Challenges), 投资分析 (Investment Analysis), 结论和建议 (Conclusions and Recommendations), and 参考文献 (References).
- **Customizable Research Depth:** Allows users to adjust the depth of research, influencing the breadth and detail of the generated report.
- **Multilingual Search:** Supports research and report generation in multiple languages (currently configured for Chinese and English).
- **Streaming Report Generation:** Provides a streaming API endpoint for real-time report generation, allowing users to follow the research process step-by-step.

## Architecture

DeepStudy follows a modular architecture, comprising a frontend and a backend, orchestrated by a LangGraph workflow.

- **Frontend (frontend/)**:
    - Built with Next.js and TypeScript.
    - Provides a user interface for submitting research topics and displaying generated reports.
    - Includes components for research forms, report display, and UI elements styled with a custom theme.
    - Communicates with the backend API to initiate research and retrieve reports.

- **Backend (backend/)**:
    - Developed using FastAPI and Python.
    - Exposes REST API endpoints for research report generation.
    - Integrates with:
        - **Gemini AI Model (via `langchain_google_genai`)**: For research planning, data analysis, and report generation.
        - **Tavily API (via `tavily-python`)**: For web search and data retrieval.
        - **LangGraph**: To orchestrate the research workflow.
    - Implements a multi-stage research workflow:
        1. **Search**: Information gathering using Tavily API based on a research plan generated by Gemini.
        2. **Analyze**: Data analysis using Gemini to extract insights and validate data.
        3. **Generate**: Report generation in Markdown format using Gemini, incorporating analysis results and references.

- **Workflow (LangGraph)**:
    - Defines a state-driven workflow to manage the research process.
    - Ensures sequential execution of search, analysis, and report generation steps.
    - Facilitates error handling and logging throughout the research lifecycle.

## Technologies Used

- **Frontend:**
    - Next.js
    - TypeScript
    - Tailwind CSS
    - React
    - `components.json` (likely for UI component configuration)
    - `eslint` for linting

- **Backend:**
    - FastAPI
    - Python
    - LangChain (`langchain_google_genai`)
    - Tavily API (`tavily-python`)
    - Pydantic
    - `uvicorn` (for ASGI server)
    - `.dotenv` (for environment variable management)

## Setup and Installation

To run DeepStudy locally, you need to set up both the frontend and backend components.

### Backend Setup (backend/)

1. **Navigate to the backend directory:**
   ```bash
   cd backend```
2. **Create a virtual environment (optional but recommended):**
   
    python3 -m venv venv
   
    source venv/bin/activate  # On Linux/macOS
   
    venv\Scripts\activate  # On Windows
   
4. **Install backend dependencies:**
   
    pip install -r requirement.txt
   
6. **Set up environment variables:**
   
    Create a .env file in the backend/ directory.
   
    Add your Google API Key and Tavily API Key to the .env file:
   
    GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
   
    TAVILY_API_KEY=YOUR_TAVILY_API_KEY
   
    Note: You will need to obtain API keys from Google AI and Tavily to use the application.
8. **Run the backend server:**
   
    python backend/src/main.py
   
        The backend server will start at http://0.0.0.0:8000.
   
    Frontend Setup (frontend/)
   
        Navigate to the frontend directory:
   
            cd frontend
   
            Install frontend dependencies:
   
                npm install  # or pnpm install or yarn install
   
            Run the frontend development server:
   
                npm run dev # or pnpm run dev or yarn dev
   
    The frontend application will be accessible at http://localhost:3000.
   
10. **Usage**
    
    Start both the backend and frontend servers as described in the Setup and Installation section.
    
    Open your browser and navigate to http://localhost:3000.
    
    Use the Research Form to enter your research topic, select research depth, and focus areas.
    
    Submit the form to initiate the research report generation process.
    
    View the generated research report displayed on the frontend. You can download the report in Markdown format.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

