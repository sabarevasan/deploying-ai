import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.secrets')

# -----------------------------
# INIT OPENAI CLIENT
# -----------------------------
client_openai = OpenAI(
    base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key="any value",
    default_headers={"x-api-key": os.getenv("API_GATEWAY_KEY")}
)

TASKS_FILE = "./tasks.json"


# -----------------------------
# STORAGE HELPERS
# -----------------------------
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []

    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# -----------------------------
# TASK FUNCTIONS
# -----------------------------
def add_task(title: str):
    tasks = load_tasks()

    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "completed": False
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return f"✅ Task added: {title}"


def list_tasks():
    tasks = load_tasks()

    if not tasks:
        return "No tasks found."

    output = []
    for t in tasks:
        status = "✅" if t["completed"] else "❌"
        output.append(f"{t['id']}. {t['title']} [{status}]")

    return "\n".join(output)


def complete_task(task_id: int):
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            save_tasks(tasks)
            return f"✅ Task {task_id} marked complete."

    return "Task not found."


def delete_task(task_id: int):
    tasks = load_tasks()

    new_tasks = [t for t in tasks if t["id"] != task_id]

    if len(new_tasks) == len(tasks):
        return "Task not found."

    save_tasks(new_tasks)
    return f"🗑️ Task {task_id} deleted."


# -----------------------------
# FUNCTION CALLING SCHEMA
# -----------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        }
    }
]


# -----------------------------
# ROUTER FUNCTION
# -----------------------------
def handle_task_request(user_input: str):
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a task manager assistant. Decide which function to call."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # If no function call → fallback response
    if not message.tool_calls:
        return "I couldn't understand the task request."

    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    # Execute function
    if function_name == "add_task":
        return add_task(arguments["title"])

    elif function_name == "list_tasks":
        return list_tasks()

    elif function_name == "complete_task":
        return complete_task(arguments["task_id"])

    elif function_name == "delete_task":
        return delete_task(arguments["task_id"])

    return "Unknown task operation."