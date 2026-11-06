from fastapi import FastAPI
from pydantic import BaseModel
from app.database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

#FastAPI Validation
class Expense(BaseModel):
    expense_name:str
    expense_amount: float
    
class Trip(BaseModel):
    place_name: str
    image_path : str | None=None
    notes : str | None=None
    expenses : list[Expense] = []
    
#Add data into Tables
@app.post("/trips")
def add_trip(trip:Trip):
    try:
        connection = get_db_connection()
        cursor =connection.cursor()
        query = """INSERT INTO trips(place_name, image_path, notes) VALUES (%s, %s, %s)"""
        values=(
            trip.place_name,
            trip.image_path,
            trip.notes
        )
        cursor.execute(query,values)
        trip_id = cursor.lastrowid
        
        for exp in trip.expenses:
            cursor.execute(""" INSERT INTO trip_expenses(trips_id,expense_name,expense_amount) VALUES (%s,%s,%s) """,
                           (trip_id,exp.expense_name,exp.expense_amount))
        connection.commit()
        cursor.close()
        connection.close()
        return {
            "message" : "Trip added sucessfully",
            "trip_id" : trip_id
        }
    except Exception as e:
        print("Error while adding trip", e)
        raise
        
        
#image display
app.mount("/uploads", StaticFiles(directory="uploads"),name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173"
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
    