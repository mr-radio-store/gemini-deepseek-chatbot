import streamlit as st
import PIL.Image

from pipeline import solve_math_cooperative

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Cooperative Math AI", layout="wide")

# --- CUSTOM HEADER WITH PROFILE PHOTO ---
col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.title("📐 Math Problem-Solving Chatbot")
    st.markdown(
        "Personal-learning Chatbot with **V. Pichkanika** | Gemini + DeepSeek Cooperative System"
    )

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "math_image" not in st.session_state:
    st.session_state.math_image = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    # 1. Profile Photo Customization
    st.header("👤 Personal Math Chatbot")
    profile_photo = st.file_uploader("Upload your photo", type=['png', 'jpg', 'jpeg'], key="profile")
    
    # Slider to customize photo width (Visual customization)
    img_width = st.slider("Adjust Photo Size", min_value=50, max_value=300, value=150, step=10)
    
    st.divider()

    # 2. Math Diagram Upload
    st.header("📷 Math Diagram")
    uploaded = st.file_uploader("Upload math diagram", type=["png", "jpg", "jpeg"], key="math")

    if uploaded:
        st.session_state.math_image = PIL.Image.open(uploaded)
        st.image(
            st.session_state.math_image, 
            caption="Problem Diagram", 
            use_container_width=True
        )

    if st.button("🧹 Clear Chat"):
        st.session_state.history = []
        st.session_state.math_image = None
        st.rerun()

# --- Display Profile Photo in Header ---
with col2:
    if profile_photo:
        st.image(profile_photo, width=img_width)
    else:
        st.info("Upload photo in sidebar")

st.divider()

# ---------------- CONTRIBUTION FUNCTION ----------------
def estimate_contribution(plan, solution, final_answer):
    p_len = len(plan.split())
    s_len = len(solution.split())
    f_len = len(final_answer.split())
    
    g_score = p_len + f_len
    total = g_score + s_len + 1e-6
    return g_score / total, s_len / total

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        # NEW: Show the Strategy Remark if it exists in history
        if msg["role"] == "assistant" and "strategy" in msg:
            st.info(f"💡 **Major Strategy:** {msg['strategy']}")
        st.markdown(msg["content"])

# ---------------- INPUT & PIPELINE ----------------
if question := st.chat_input("Ask a math problem..."):

    st.chat_message("user").markdown(question)

    # 1. Run the cooperative pipeline
    final_answer, plan, solution = solve_math_cooperative(question)
    g_rate, d_rate = estimate_contribution(plan, solution, final_answer)

    # --- NEW: STRATEGY DETECTION LOGIC ---
    strategy_keywords = {
        "Calculus": ["derivative", "integral", "limit", "optimize", "dx"],
        "Algebra": ["solve for x", "equation", "variable", "coefficient", "simplify"],
        "Geometry": ["area", "volume", "triangle", "circle", "angle", "radius"],
        "Trigonometry": ["sin", "cos", "tan", "theta", "hypotenuse", "pi"],
        "Arithmetic": ["sum", "product", "division", "ratio", "percentage"]
    }
    
    detected_strategy = "General Logic"
    combined_text = (plan + " " + solution).lower()
    for strategy, keywords in strategy_keywords.items():
        if any(k in combined_text for k in keywords):
            detected_strategy = strategy
            break

    with st.chat_message("assistant"):
        # Display the Strategy Remark
        st.info(f"💡 **Major Strategy:** {detected_strategy}")
        
        st.markdown(final_answer)

        # Visualizing Contribution with Metrics
        st.subheader("📊 Collaborative Breakdown")
        m1, m2 = st.columns(2)
        m1.metric("🟢 Gemini (Strategy)", f"{g_rate:.1%}")
        m2.metric("🔵 DeepSeek (Logic)", f"{d_rate:.1%}")

        with st.expander("🔍 See AI Cooperation Process"):
            st.markdown(f"**Gemini Plan:**\n{plan}")
            st.markdown(f"**DeepSeek Solution:**\n{solution}")

    # 2. SAVE TO HISTORY (Including the detected strategy)
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append({
        "role": "assistant", 
        "content": final_answer,
        "strategy": detected_strategy # Saved for persistence
    })