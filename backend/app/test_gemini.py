from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

#gemini-3.8-flash

response = client.models.generate_content(
    model = "gemini-3.6-flash",
    contents = "Suggest a nice 2 days itenary for ooty short and simple"
    
)

print(response.text)