import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

def explain_decision(invoice: dict, action: str, scores: dict) -> str:
    """
    Explains the financial trade-offs of a decision using Gemini Pro 3.1.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert financial analyst. 
    Explain the financial trade-offs of the following invoice decision in exactly 2-3 plain-English sentences.
    
    Invoice Details:
    - ID: {invoice.get('id')}
    - Supplier: {invoice.get('supplier')}
    - Amount: ${invoice.get('amount')}
    - Due Date: {invoice.get('due_date')}
    - Discount: {invoice.get('discount_pct', 0) * 100}%
    
    Action Taken: {action}
    
    Sub-scores:
    - Liquidity: {scores.get('liquidity')}
    - Cost: {scores.get('cost')}
    - Discount: {scores.get('discount')}
    - Supplier: {scores.get('supplier')}
    - Risk: {scores.get('risk')}
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-pro',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3
        )
    )
    
    return response.text