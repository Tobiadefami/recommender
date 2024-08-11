import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

MODEL = genai.GenerativeModel('gemini-1.5-flash')

def process_text_for_product_review(data):
    
    prompt = (
        "Analyze the following text and determine if it is a product review. "
        "Consider the following criteria when making your decision:\n\n"
        "1. Does the text describe a specific product, including details like the model, make, version, or type?\n"
        "2. Does the text evaluate the product's performance, functionality, or features?\n"
        "3. Does the text discuss the user experience, such as ease of use, comfort, or the user interface?\n"
        "4. Is there any mention of the product's quality, durability, or maintenance requirements?\n"
        "5. Does the text analyze the value for money, considering the price versus features?\n"
        "6. Are there any pros and cons listed, highlighting what the user liked or disliked about the product?\n"
        "7. Does the text conclude with an overall impression, recommendation, or rating of the product?\n\n"
        "Respond with 'True' if the text meets several of these criteria and can be considered a product review, otherwise respond with 'False'.\n\n"
        f"Text: {data}"
    )
    
    # Send the prompt to the Gemini API
    response = MODEL.generate_content(
        prompt,
    )
    
    # Extract the model's determination
    determination = response.text.strip()
    
    if determination.lower() == 'true':
        return True
    
    return False

# Example usage
text = "this is a boy"
processed_text = process_text_for_product_review(text)
if processed_text:
    print("Accepted text:", processed_text)
else:
    print("Discarded text")