## Assignment 2
### Overview
This project implements a conversational AI system that integrates multiple services into a unified chat interface. The goal is to demonstrate the ability to design and build an AI-powered application that can:
Handle user queries through natural language
Route requests to appropriate backend services
Maintain conversational context
Apply guardrails to restrict unsafe or disallowed inputs
The system is implemented using Python and provides a chat-based interface built with Gradio
### System Architecture
The system consists of the following components:
- Chat Interface (Gradio) – Handles user interaction
- Router (run_semantic.py) – Determines which service to call
- Service Layer:
    - API Service
    - Semantic Search Service
    - Task Management Service
- Persistent Storage:
    - ChromaDB (for embeddings)
    - JSON file (for task storage)

### Chat Interface
The user interacts with the system through a Gradio-based chatbot UI.
Features:
- Conversational interface
- Maintains chat history during the session
- Simple and responsive interaction loop

### Services
#### API Service (Stock + News Insights)
This service retrieves stock market data and recent news articles related to a company.
Implementation:
- Uses Marketstack API to fetch stock data (end-of-day pricing)
- Uses News API to retrieve recent articles
- Combines both sources into a structured, readable summary
Features:
- Displays stock price, high/low, and volume
- Computes simple insights (e.g., daily range)
- Lists latest relevant news headlines
Example Query:
```
What is the stock price of AAPL?
```
Output:
- Stock summary
- Basic analytics
- Latest news headlines

#### Semantic Search (Python Knowledge Base)
This service answers questions using a semantic search over a custom dataset.
Dataset:
- Python 101 tutorial content (scraped and processed)
- Multiple chapters covering core Python concepts
Implementation:
- Text is scraped and split into chunks
- Embeddings are generated using an embedding model
- Stored in a persistent ChromaDB collection
- Query is embedded and matched against stored vectors
Features:
- Retrieves relevant content using semantic similarity
- Generates answers grounded in the dataset
- Includes source references for transparency
Example Query:
```
What are Python functions?
```
#### Task Management (Function Calling)
This service allows users to manage tasks using natural language.
Implementation:
- Uses OpenAI function calling to interpret user intent
- Executes task operations based on structured function calls
- Stores tasks in a local JSON file
Supported Actions:
- Add a task
- List tasks
- Mark task as complete
- Delete a task
Example Queries:
```
Add task: Submit assignment
Show my tasks
Complete task 1
```
Features:
- Persistent task storage
- Structured task management
- Natural language interaction

#### Memory
The system maintains short-term memory using chat history stored in the UI state.
- Each message-response pair is preserved
- No long-term memory is implemented
- Suitable for short conversations within context limits

#### Gaurdrails
The system includes safeguards to prevent misuse.
Restricted Topics:
- Cats or dogs
- Horoscopes or zodiac signs
- Taylor Swift
If a user asks about restricted topics, the system responds with a refusal message.
Prompt Protection:
- The system does not expose or allow modification of internal prompts
- Input is filtered before processing

#### Setup
- In addition to dependencies for cohort labs, I have used `beautifulsoup` to crawl webpages
- For the setup to function `MARKETSTACK_API_KEY` and `NEWS_API_KEY` must be added to the `.secrets` file
- Run `python semantic_service.py` to scrap data, generate embeddings, and stod to chromaDB
- Launch app using `python app.py` and navigate in browser to `http://127.0.0.1:7860`
