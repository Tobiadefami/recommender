import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

MODEL = genai.GenerativeModel('gemini-1.5-flash')

def process_text_for_product_review(data):
    
    prompt = f"Determine if the following text is a product review. Respond with 'True' if it is a product review, otherwise respond with 'False'. Text: {text}"
    
    # Send the prompt to the Gemini API
    response = MODEL.generate_content(
        prompt,
    )
    
    # Extract the model's determination
    determination = response.text.strip()
    
    if determination.lower() == 'true':
        return text
    else:
        return "this is not a product review"

# Example usage
text = "this is a boy"
processed_text = process_text_for_product_review(text)
if processed_text:
    print("Accepted text:", processed_text)
else:
    print("Discarded text")