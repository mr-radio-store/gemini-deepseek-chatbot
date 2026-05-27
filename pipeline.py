import streamlit as st
from gemini_agent import gemini_plan, gemini_refine
from deepseek_agent import deepseek_solve

def solve_math_cooperative(question):
    """
    Multi-agent pipeline:
    1. Gemini (Planner) -> Analyzes problem and creates a strategy.
    2. DeepSeek (Solver) -> Executes the plan with high logical precision.
    3. Gemini (Refiner) -> Polishes the output for the user.
    """

    # 🟢 Step 0: Extract Image from Streamlit State
    # This avoids passing strings into image slots
    image_data = st.session_state.get("math_image")

    # 🟢 Step 1: Planning Phase (Gemini)
    # We pass the image so Gemini can see the math diagram if it exists
    plan = gemini_plan(question, image=image_data)

    # 🔵 Step 2: Solving Phase (DeepSeek)
    # We combine the question and the plan into the 'prompt' argument.
    # We explicitly pass image=image_data to avoid positional argument errors.
    solve_context = f"User Question: {question}\n\nRecommended Solving Plan: {plan}"
    
    solution = deepseek_solve(
        prompt=solve_context, 
        image=image_data, 
        temperature=0.2  # Low temperature for better math accuracy
    )

    # 🟢 Step 3: Refinement Phase (Gemini)
    # Gemini takes the raw logic from DeepSeek and makes it readable.
    refine_context = (
        f"Original Question: {question}\n\n"
        f"DeepSeek's Logical Solution: {solution}\n\n"
        "Please provide the final formatted answer and a brief explanation."
    )
    final_answer = gemini_refine(refine_context)

    return final_answer, plan, solution