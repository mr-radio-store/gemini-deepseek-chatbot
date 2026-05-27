import requests
import base64
from io import BytesIO

# --- CONFIGURATION ---
DEEPSEEK_API_KEY = "sk-45100ce4085247b7ba8c3ebd3b0b5704"
API_URL = "https://api.deepseek.com/chat/completions"

def deepseek_solve(prompt, image=None, temperature=0.2, system_prompt="You are a helpful math expert."):
    """
    Calls the DeepSeek API with support for text and optional images.
    
    :param prompt: The text instruction or question.
    :param image: Optional PIL Image object from Streamlit.
    :param temperature: Determinism of the response (0.2 is best for Math).
    :param system_prompt: The persona the AI should adopt.
    """
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Initialize messages with the persona
    messages = [{"role": "system", "content": system_prompt}]

    # 2. Build the User Message (Supporting Multi-modal content)
    user_content = [{"type": "text", "text": prompt}]

    # 3. Handle the Image (Only if it's a valid PIL image object)
    if image and hasattr(image, 'save'):
        try:
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
            })
        except Exception as img_err:
            return f"ERROR: Image processing failed: {str(img_err)}"

    messages.append({"role": "user", "content": user_content})

    # 4. Execute the API Request
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "model": "deepseek-chat", 
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2048
            },
            timeout=30
        )
        
        # Raise exception for 4XX/5XX errors
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError:
        # Check specific status codes for user-friendly feedback
        if response.status_code == 402:
            return "ERROR: DeepSeek Insufficient Balance. Please top up your account."
        elif response.status_code == 401:
            return "ERROR: DeepSeek API Key is invalid or expired."
        else:
            return f"ERROR: DeepSeek API {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "ERROR: The request to DeepSeek timed out. Try again."
        
    except Exception as e:
        return f"ERROR: Unexpected Failure: {str(e)}"