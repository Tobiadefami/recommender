import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

MODEL = genai.GenerativeModel('gemini-1.5-flash')

def process_text_for_product_review(data):
    
    prompt = (
        "Analyze the following text and determine if it is a product review. Consider the following detailed criteria "
        "and respond with 'True' if the text can be classified as a product review, otherwise respond with 'False'.\n\n"
        "1. **Product Identification:** Does the text mention a specific product, including its brand, model, or type? "
        "Even if the text is negative or warns others to avoid the product, it should still be considered a product review "
        "if it describes a personal experience with the product.\n"
        "2. **Performance and Experience Evaluation:** Does the text discuss the performance or functionality of the product, "
        "such as issues encountered, durability, or quality? For example, mentioning problems like screen issues, GPU problems, "
        "or other defects counts as performance evaluation.\n"
        "3. **User Experience and Satisfaction:** Does the text reflect on the user’s experience, satisfaction, or dissatisfaction "
        "with the product? Even complaints or expressions of disappointment should be considered as they reflect the user’s personal "
        "experience.\n"
        "4. **Recommendation or Warning:** Does the text conclude with advice, recommendations, or warnings to others about the product? "
        "Text that advises against buying the product or suggests alternatives should still be classified as a review.\n"
        "5. **Sentiment Analysis:** Consider the overall sentiment of the text. Even if the sentiment is negative, it should be "
        "recognized as a review if it discusses specific aspects of the product’s performance, quality, or user experience.\n\n"
        f"Text: {data}"
    )
    
    # Send the prompt to the Gemini API
    response = MODEL.generate_content(
        prompt,
    )
    
    # Extract the model's determinationq
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