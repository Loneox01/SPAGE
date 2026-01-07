import os
from tools import ALL_TOOLS

from dotenv import load_dotenv

from google import genai
from google.genai import types

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
load_dotenv()

# CORS Setup
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    text: str
    state: dict

with open("SYSTEM_PROMPT.txt", "r") as f:
    system_prompt = f.read()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(
    model='gemini-2.5-flash-lite',
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=ALL_TOOLS,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )
)

available_tools = {f.__name__: f for f in ALL_TOOLS}

MAX_CALLS_PER_TURN = 10

@app.post("/prompt")
async def process_command(request: PromptRequest):
    full_context = f"CURRENT_UI_STATE: {request.state}\nUSER_MESSAGE: {request.text}"
    response = chat.send_message(full_context)
    
    results = []  # list of tool calls

    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if fn := part.function_call:
                if fn.name in available_tools:
                    # execute the tool and add payload to list
                    tool_result = available_tools[fn.name](**fn.args)

                    print(f"Tool Called: {fn.name}")
                    print(f"Args: {fn.args}\n")

                    if(tool_result["error"]):
                        return {"status": "error", "action": "none", "error": tool_result["error"]}  # unsup. command
                    results.append(tool_result)

                    if len(results) >= MAX_CALLS_PER_TURN:
                        # early stop, enforce tool call limit
                        break
    else:
        return {"status": "error", "action": "none", "error": "NO_TOOL_MATCH"}  # bad response
    
    return {"status": "success", "actions": results}
            
