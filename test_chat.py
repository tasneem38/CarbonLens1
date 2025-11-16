from groq import Groq
import os
import dotenv
dotenv.load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("\nTesting llama-3.1-8b-instant...\n")

resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Say hi in one sentence."}
    ]
)

print(resp)
print("\nDONE\n")
