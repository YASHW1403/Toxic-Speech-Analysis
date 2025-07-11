import streamlit as st
import requests
import os
import json
import re
from dotenv import load_dotenv

# Load API key
load_dotenv()
GROQ_API_KEY = "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"

# Groq API URL
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function to classify comment with more detailed output
def classify_comment(comment):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        "You're a toxicity detection AI. For the given comment, analyze it and respond with:\n"
        "- A toxicity score (0-100)\n"
        "- Traits (like insult, hate, threat, rude, profanity, spam, etc.)\n"
        "- Emotion (angry, neutral, happy, sad, etc.)\n"
        "- Tone (friendly, rude, sarcastic, etc.)\n"
        "- Final Classification: appropriate or inappropriate\n\n"
        f"Comment: {comment}\n\n"
        "Respond in JSON format like this:\n"
        "{\n"
        "  \"toxicity_score\": 85,\n"
        "  \"traits\": [\"insult\", \"profanity\"],\n"
        "  \"emotion\": \"angry\",\n"
        "  \"tone\": \"rude\",\n"
        "  \"classification\": \"inappropriate\"\n"
        "}"
    )

    payload = {
        "model": "llama3-8b-8192",
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(GROQ_URL, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            raw = response.json()["choices"][0]["message"]["content"]
            # Extract JSON block even if extra text is present
            json_str = re.search(r"\{.*\}", raw, re.DOTALL).group()
            result = json.loads(json_str)
            return result
        except Exception as e:
            return {"error": f"Couldn't parse AI response: {e}", "raw": raw}
    else:
        return {"error": f"API error {response.status_code}", "raw": response.text}

# ---------------------------
# Streamlit UI starts here
# ---------------------------

st.set_page_config(
    page_title="🛡️ Toxic Comment Classifier",
    page_icon="🧠",
    layout="centered"
)

# Stylish title and header
st.markdown(
    """
    <h1 style='text-align: center; color: #6C63FF;'>🛡️ AI Comment Moderator</h1>
    <p style='text-align: center; font-size:18px;'>Detect how toxic a comment is and classify it using Groq's LLaMA 3 AI</p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Input
user_input = st.text_area("✍️ Enter a comment:", height=120, placeholder="Type your comment here...")

# Button
if st.button("🔍 Classify"):
    if not user_input.strip():
        st.warning("Please enter a comment.")
    else:
        with st.spinner("Classifying..."):
            result = classify_comment(user_input)

        # Display result
        if "error" in result:
            st.warning(result["error"])
            st.code(result.get("raw", ""))
        else:
            st.metric("🧠 Toxicity Score", f"{result['toxicity_score']}%")
            st.markdown(f"**💬 Traits:** {', '.join(result['traits'])}")
            st.markdown(f"**😡 Emotion:** {result['emotion'].capitalize()}")
            st.markdown(f"**🎯 Tone:** {result['tone'].capitalize()}")

            if result["classification"] == "appropriate":
                st.success("✅ This comment is **appropriate**.")
            else:
                st.error("🚫 This comment is **inappropriate**.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>Made using AI by Yash Samir Wadekar</div>",
    unsafe_allow_html=True
)
