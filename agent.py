import os
import logging
import datetime
import asyncio
import google.cloud.logging
from google.cloud import datastore
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from mcp.server.fastmcp import FastMCP 

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- 1. Setup Logging ---
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

load_dotenv()
model_name = os.getenv("MODEL", "gemini-1.5-flash")

# --- 2. Database Setup ---
# PRO TIP: For the default database, leaving arguments empty is the most stable 
# way to deploy on Google Cloud. It auto-detects the project and (default) DB.
DB_ID="student"
db = datastore.Client(database=DB_ID) 

mcp = FastMCP("StudentProjectCoordinator")

# ================= 3. TOOLS =================

@mcp.tool()
def create_project_task(title: str, deadline: str, assignee: str = "") -> str:
    """Creates a new project task with deadline and optional assignee."""
    try:
        key = db.key('ProjectTask')
        task = datastore.Entity(key=key)
        
        # Parse deadline if provided
        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except:
                deadline_date = datetime.datetime.now() + datetime.timedelta(days=7)
        
        task.update({
            'title': title,
            'deadline': deadline_date,
            'assignee': assignee if assignee else "Unassigned",
            'completed': False,
            'created_at': datetime.datetime.now(),
            'completed_at': None
        })
        db.put(task)
        return f"✅ Project task '{title}' created successfully (ID: {task.key.id}). Deadline: {deadline if deadline else 'Not set'}. Assignee: {assignee if assignee else 'Unassigned'}"
    except Exception as e:
        logging.error(f"DB Error in create_project_task: {e}")
        return f"Database Error: {str(e)}"

@mcp.tool()
def list_project_tasks() -> str:
    """Lists all current project tasks."""
    try:
        query = db.query(kind='ProjectTask')
        tasks = list(query.fetch())
        if not tasks: 
            return "📭 No project tasks found. Create one using 'create_project_task'."
        
        res = ["📊 Student Project Tasks:"]
        for t in tasks:
            status = "✅" if t.get('completed') else "⏳"
            deadline_str = f" | Due: {t.get('deadline').strftime('%Y-%m-%d')}" if t.get('deadline') else ""
            assignee_str = f" | 👤 {t.get('assignee', 'Unassigned')}"
            res.append(f"{status} {t.get('title')} (ID: {t.key.id}){deadline_str}{assignee_str}")
        return "\n".join(res)
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def complete_project_task(task_id: str) -> str:
    """Marks a project task as complete. Input must be the numeric ID."""
    try:
        numeric_id = int(''.join(filter(str.isdigit, task_id)))
        key = db.key('ProjectTask', numeric_id)
        task = db.get(key)
        if task:
            task['completed'] = True
            task['completed_at'] = datetime.datetime.now()
            db.put(task)
            return f"🎉 Project task '{task.get('title')}' (ID: {numeric_id}) marked as complete!"
        return f"❌ Project task with ID {numeric_id} not found."
    except Exception as e:
        return f"Error processing task ID: {str(e)}"

@mcp.tool()
def add_project_note(title: str, content: str) -> str:
    """Saves a detailed project meeting note or professor announcement."""
    try:
        key = db.key('ProjectNote')
        note = datastore.Entity(key=key)
        note.update({
            'title': title, 
            'content': content, 
            'created_at': datetime.datetime.now()
        })
        db.put(note)
        return f"📝 Project note '{title}' saved successfully."
    except Exception as e:
        return f"Database Error: {str(e)}"

# ================= 4. AGENTS =================

def add_prompt_to_state(tool_context: ToolContext, prompt: str):
    """Internal tool to bridge user intent across the agent workflow."""
    tool_context.state["PROMPT"] = prompt
    return {"status": "ok"}

def project_coordinator_instruction(ctx):
    # This pulls from the state we set in the root_agent
    user_prompt = ctx.state.get("PROMPT", "Welcome the user to the Student Project Coordinator.")
    return f"""
You are the Student Project Coordinator Assistant for university group projects, bootcamp teams, and study groups.
Always start with a helpful, encouraging greeting for students.
Your goal is to help teams manage tasks and meet deadlines.

Capabilities:
- Create and track project tasks with deadlines and assignees
- List all project tasks with status
- Mark tasks as complete when finished
- Store meeting notes and professor announcements

For this request: {user_prompt}

Use the appropriate tools to help the student team complete their project successfully.
Be supportive and educational in your responses.
"""

def root_instruction(ctx):
    # Pulls the prompt directly from the API call
    raw_input = ctx.state.get("user_input", "Hello")
    return f"""
1. Save this user input using 'add_prompt_to_state': {raw_input}
2. Hand off control to the 'project_workflow' agent.
"""

project_agent = Agent(
    name="project_coordinator",
    model=model_name,
    instruction=project_coordinator_instruction,
    tools=[create_project_task, list_project_tasks, complete_project_task, add_project_note]
)

project_workflow = SequentialAgent(
    name="project_workflow",
    sub_agents=[project_agent]
)

root_agent = Agent(
    name="root",
    model=model_name,
    instruction=root_instruction,
    tools=[add_prompt_to_state],
    sub_agents=[project_workflow]
)

# ================= 5. API =================

app = FastAPI(title="Student Project Coordinator API", description="API for coordinating student group projects, tracking tasks, and managing deadlines")

class UserRequest(BaseModel):
    prompt: str

@app.post("/api/v1/project/chat")
async def chat(request: UserRequest):
    try:
        final_reply = ""
        # Inject user_input into the agent state
        async for event in root_agent.run_async({"user_input": request.prompt}):
            if hasattr(event, 'text') and event.text:
                final_reply = event.text

        return {
            "status": "success",
            "reply": final_reply if final_reply else "Request processed."
        }

    except Exception as e:
        logging.error(f"Chat Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/project/health")
async def health_check():
    """Health check endpoint for the Student Project Coordinator."""
    return {
        "status": "healthy",
        "service": "Student Project Coordinator",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)