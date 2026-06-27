from google import genai

client = genai.Client(api_key="AQ.Ab8RN6JE5JkSz1sHCOCyHrq6APhq4UBAJqmHQReR4dO-zXKuUg")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print(response.text)
except Exception as e:
    import traceback
    traceback.print_exc()