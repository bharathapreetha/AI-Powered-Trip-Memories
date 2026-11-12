from fastapi import FastAPI,HTTPException,UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import shutil
import json
import traceback
from pydantic import BaseModel
from app.database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware


import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key = os.getenv("GEMINI_API_KEY")
)
MODEL_NAME = "gemini-3.6-flash"


#These are Python type hints. They help specify what type of data a variable or field should accept.
from typing import List, Literal
#connect with external API
import httpx  

app = FastAPI()

#Save image into local folder
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

#FastAPI Validation
class Expense(BaseModel):
    expense_name:str
    expense_amount: float
    
class Trip(BaseModel):
    place_name: str
    image_path : str | None=None
    notes : str | None=None
    expenses : list[Expense] = []
    
    
#Chat 
class ChatMessage(BaseModel):
    role : Literal["user","assistant"]
    content:str
    
class ChatRequest(BaseModel):
    messages : List[ChatMessage]


    
#Add data into Tables
@app.post("/trips")
async def add_trip(
    place_name : str = Form(...),
    notes : str = Form(""),
    expenses : str = Form("[]"),
    image: UploadFile = File(None) 
    ):

    connection = None
    cursor =  None
    saved_file = None
    
    try:
        #1. Save image into upload folder
        image_path = None
        if image and image.filename:
            extension =  Path (image.filename).suffix.lower()
            filename = f"{uuid.uuid4().hex}{extension}"
            saved_file = UPLOAD_DIR / filename
            
            contents = await image.read()
            with open (saved_file, "wb") as f:
                f.write(contents)
                
            image_path = f"uploads/{filename}"
        #2. Convert expense JSON string into python list
            expense_list = json.loads(expenses)  # JSON string in to python object
            
        #3. Connect to MySQL
            connection = get_db_connection()
            cursor = connection.cursor()
        #4. Insert trip details
            query = """
            INSERT INTO trips(place_name,image_path,notes) VALUES(%s,%s,%s)
            """
            values = (place_name,image_path,notes)
            cursor.execute(query,values)
            trip_id = cursor.lastrowid
            
        #5. Insert Multiple expenses
        for exp in  expense_list:
            cursor.execute("""
                            INSERT INTO trip_expenses(trips_id,expense_name,expense_amount) VALUES(%s,%s,%s) """, (trip_id,exp["expense_name"],exp["expense_amount"]))
            
        #6. Save all changed
        connection.commit()
        return {
            "message" : "Trip added Sucessfully",
            "trip_id" : trip_id,
            "image_path" : image_path
        }
        
    except Exception as e:
        print("ERROR TYPE:", type(e))
        print("ERROR DETAILS:", repr(e))
        print("ERROR ARGS:", e.args)
        traceback.print_exc()

        if connection:
            connection.rollback()
         #Remove Uploaded image if database  insertion failes
        if saved_file and saved_file.exists():
            saved_file.unlink()
            print("Error while adding trip" , e)
            raise HTTPException(
                status_code = 500,
                detail = str(e)
            )

        raise HTTPException(status_code=500, detail=str(e))
       
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            


# def add_trip(trip:Trip):
#     try:
#         connection = get_db_connection()
#         cursor =connection.cursor()
#         query = """INSERT INTO trips(place_name, image_path, notes) VALUES (%s, %s, %s)"""
#         values=(
#             trip.place_name,
#             trip.image_path,
#             trip.notes
#         )
#         cursor.execute(query,values)
#         trip_id = cursor.lastrowid
        
#         for exp in trip.expenses:
#             cursor.execute(""" INSERT INTO trip_expenses(trips_id,expense_name,expense_amount) VALUES (%s,%s,%s) """,
#                            (trip_id,exp.expense_name,exp.expense_amount))
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {
#             "message" : "Trip added sucessfully",
#             "trip_id" : trip_id
#         }
#     except Exception as e:
#         print("Error while adding trip", e)
#         raise
   
        
        
#image display
app.mount("/uploads", StaticFiles(directory="uploads"),name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Powered Trip memories running"}

@app.get("/trips")
def get_trips():
    try:
        connection =get_db_connection()
        cursor =  connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM trips")
        
        trips = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return trips
    except Exception as e:
        print("Error", e)
        raise
    
#Conversational Chat
SYSTEM_PROMPT = """
You are a Friendly travel companion for the Trip Memories Application.

Help users:
-Explore travel destinations.
-Plan trips and itineraies.
-Suggest attractions, food and activities.
-Answer travel-related questions.
-Organize and recall their travel experiences.

Keep response friendly, helpful and easy to understand.
"""

@app.post('/chat')
async def chat(request : ChatRequest):
    try: 
        #1.Conver conversation history into gemini format
        contents = [
            types.Content( role = "user" if message.role == "user" else "model",
                          parts = [
                              types.Part.from_text(text=message.content)
                          ]
                          )
            for message in request.messages
        ]
        
        #2. Call Gemini API
        response = await client.aio.models.generate_content(
            model = MODEL_NAME,
            contents = contents,
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature = 0.7
            )
        )
        
        #3.Extract AI  response:
        return {
            "reply" : response.text
        }
    except Exception as e:
        print("Gemini API Error", str(e))
        
        raise HTTPException(
            status_code = 502,
            detail=f"Gemini API Error: {str(e)}"
        )
        

    
    