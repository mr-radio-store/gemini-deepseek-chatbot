from google import genai
from config import GEMINI_API_KEY

# Initialize the Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def gemini_plan(question, image=None):
    """
    Agent 1: The Architect.
    Analyzes the problem and creates a high-level logical roadmap.
    """
    prompt = (
        "You are a mathematical strategist. Create a clear, step-by-step plan "
        "to solve the following problem. Focus on the logical approach and "
        "necessary formulas. DO NOT provide the final numerical answer.\n\n"
        f"Problem: {question}"
    )
    
    # Build the contents list for multimodal support
    contents_list = [prompt]
    if image:
        contents_list.append(image)

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents_list
        )
        return response.text
    except Exception as e:
        return f"ERROR in Gemini Planning Phase: {str(e)}"


def gemini_refine(context, image=None):
    """
    Agent 3: The Educator.
    Takes DeepSeek's logical output and transforms it into a polished, 
    easy-to-understand student lesson.
    """
    prompt = (
        "You are an expert math teacher. Below is a raw mathematical solution. "
        "Please refine it into a clear, step-by-step educational response. "
        "Ensure the formatting is clean (use Markdown) and the tone is helpful.\n\n"
        f"Context and Raw Solution:\n{context}"
    )
    
    contents_list = [prompt]
    if image:
        contents_list.append(image)

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents_list
        )
        return response.text
    except Exception as e:
        return f"ERROR in Gemini Refinement Phase: {str(e)}"