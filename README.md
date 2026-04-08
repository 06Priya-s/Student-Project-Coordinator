# 🤖 Student Project Coordinator

An intelligent AI-powered multi-agent system that helps student teams manage group projects, track tasks, monitor deadlines, and coordinate team contributions using modern AI capabilities.

## 🚀 Features

* 💬 Natural language conversation for task creation and project management
* ⚡ Fast API using FastAPI with async support
* ☁️ Deployable on Google Cloud Run with auto-scaling
* 🔗 Modular agent architecture with Google ADK and FastMCP
* 🧠 AI-powered responses using Gemini 1.5 Flash
* 📦 Easy to extend MCP tools for new integrations
* ✅ Create, list, and complete project tasks with deadlines
* 📝 Store meeting notes and professor announcements
* 📊 Real-time project summaries and progress tracking
* 🗄️ Persistent storage with Google Cloud Datastore

## 🛠️ Tech Stack

* Python 3.11+
* FastAPI
* Google ADK (Agent Development Kit)
* FastMCP (Model Context Protocol)
* Google Gemini 1.5 Flash
* Google Cloud Datastore
* Google Cloud Run
* Uvicorn
* Pydantic

<img width="1903" height="1067" alt="Screenshot 2026-04-08 231043" src="https://github.com/user-attachments/assets/a92b1dae-bb07-4ee5-89c1-c5a6ff0ba50a" />

## 📂 Project Structure
<pre>  
├── agent.py # Main agent with MCP tools and API
├── requirements.txt # Python dependencies
├── Dockerfile # Container configuration for Cloud Run
├── .env # Environment variables
└── README.md # Project documentation</pre>

## Live Demo Link: 
https://1drv.ms/v/c/17270035d5783350/IQAbH5EF_QF3Tr5aRZzknEZjAbDj4s2LYr4MIfpmPQ1LunQ?e=D5cqEa

## Live App URL: 
https://spc-agent-941910953451.europe-west1.run.app/

## ⚙️ Installation

git clone https://github.com/06Priya-s/Student-Project-Coordinator.git
cd student-project-coordinator
pip install -r requirements.txt 

## ▶️ Run Locally
bash
python agent.py
or
uvicorn agent:app --reload --host 0.0.0.0 --port 8080

## 🧪 Test the API

bash
# Create a task
curl -X POST "http://localhost:8080/api/v1/project/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create task called Final Report due 2024-12-10 assigned to John"}'

# List all tasks
curl -X POST "http://localhost:8080/api/v1/project/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all tasks"}'

# Complete a task
curl -X POST "http://localhost:8080/api/v1/project/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Complete task with ID 1"}'

## Health check
curl -X GET "http://localhost:8080/api/v1/project/health"


## ☁️ Deploy to Cloud Run

bash
# Build and deploy using gcloud
gcloud builds submit --tag gcr.io/$PROJECT_ID/student-project-coordinator

gcloud run deploy student-project-coordinator \
  --image gcr.io/$PROJECT_ID/student-project-coordinator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

# Or using ADK deploy (if applicable)
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west1 \
  --service_name=emotional-resonance-guide \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=an-adk \
  --service-account=$SERVICE_ACCOUNT



## 🔐 Environment Variables

Create .env file:
text
PROJECT_ID=your-project-id
MODEL=gemini-1.5-flash
GOOGLE_APPLICATION_CREDENTIALS=path-to-key.json
PORT=8080


## 📌 Usage
Start the server locally or deploy to Cloud Run

Send POST requests to /api/v1/project/chat with natural language prompts

The agent will create tasks, list tasks, complete tasks, or save notes

Use /api/v1/project/health for monitoring

## Example Prompt
<pre>
Create task called Abstract due 2024-12-10 assigned to John
List all tasks
Complete task with ID 1
Add note Professor extended deadline as Class Update</pre>


## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
MIT License




