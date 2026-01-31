import streamlit as st
import datetime
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="GroqJet Travel Planner",
    page_icon="✈️",
    layout="centered"
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "trip_started" not in st.session_state:
    st.session_state.trip_started = False

if "trip_context" not in st.session_state:
    st.session_state.trip_context = {}

# --- Constants & System Prompt ---
SYSTEM_PROMPT = """
You are GroqJet, an expert AI travel consultant.

YOUR MANDATE:
1.  **Travel Only:** You must ONLY answer questions related to travel, tourism, geography, logistics, packing, culture, and itinerary planning.
2.  **Refusal:** If the user asks about ANY other topic (e.g., coding, math, politics, general life advice, creative writing not related to travel), you must politely but firmly refuse. Example: "I specialize only in travel planning. I cannot assist with non-travel queries."
3.  **Clarification:** If the user provides ambiguous locations (e.g., "Paris" could be France or Texas) or unrealistic constraints, you must ask clarifying questions BEFORE generating an itinerary.
4.  **Tone:** Professional, enthusiastic, and helpful.
5.  **Format:** Use Markdown for itineraries. Use bolding for days (e.g., **Day 1**) and lists for activities.
"""

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    
    if api_key:
        st.success("API Key loaded", icon="✅")
    else:
        st.error("No API Key found. Please set GROQ_API_KEY in your .env file.")
    
    st.markdown("---")
    st.markdown("### 📝 Instructions")
    st.markdown("1. Ensure API Key is set in .env")
    st.markdown("2. Fill in your trip details.")
    st.markdown("3. Chat with the AI to refine your plan.")
    
    if st.button("Reset Planner"):
        st.session_state.messages = []
        st.session_state.trip_started = False
        st.session_state.trip_context = {}
        st.rerun()

# --- Helper Function: Call Groq API ---
def get_groq_response(messages, api_key):
    if not api_key:
        st.error("Please set your Groq API Key in the .env file.")
        return None
    
    client = Groq(api_key=api_key)
    
    try:
        # We prepend the system prompt to the message history
        full_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages
        
        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile", # Using Llama 3 70B for high quality reasoning
            temperature=0.6,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# --- Main Interface ---
st.title("✈️ GroqJet Planner")
st.subheader("AI-Powered Itineraries")

# --- Phase 1: Trip Input Form ---
if not st.session_state.trip_started:
    with st.container():
        st.info("Let's start by gathering some basic details for your trip.")
        
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_input("📍 From (Source)", placeholder="e.g., New York, JFK")
        with col2:
            destination = st.text_input("🏁 To (Destination)", placeholder="e.g., Tokyo, Japan")
            
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("📅 Start Date", min_value=datetime.date.today())
        with col4:
            end_date = st.date_input("📅 End Date", min_value=datetime.date.today())

        if st.button("Generate Initial Itinerary", type="primary"):
            if not source or not destination:
                st.warning("Please provide both a source and a destination.")
            elif not api_key:
                st.warning("Please ensure GROQ_API_KEY is set in your .env file.")
            elif (end_date - start_date).days > 60:
                st.error("Trip duration cannot exceed 2 months. Please check your dates.")
            else:
                # 1. Save Context
                st.session_state.trip_context = {
                    "source": source,
                    "destination": destination,
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                }
                
                # 2. Formulate Initial Prompt
                initial_prompt = (
                    f"Please create a travel itinerary from {source} to {destination} "
                    f"for the dates {start_date} to {end_date}. "
                    f"Include suggestions for accommodation, food, and key attractions."
                )
                
                # 3. Add to history and set state
                st.session_state.messages.append({"role": "user", "content": initial_prompt})
                st.session_state.trip_started = True
                
                # 4. Get AI Response immediately
                # Use st.status for a more engaging loading state during the heavy lifting
                with st.status("🗺️ Planning your adventure...", expanded=True) as status:
                    st.write("Consulting travel maps...")
                    response = get_groq_response(st.session_state.messages, api_key)
                    st.write("Finalizing itinerary...")
                    status.update(label="Itinerary Ready!", state="complete", expanded=False)
                    
                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()

# --- Phase 2: Chat Interface ---
else:
    # Display details summary
    ctx = st.session_state.trip_context
    st.caption(f"Trip: {ctx.get('source')} ➝ {ctx.get('destination')} | {ctx.get('start_date')} to {ctx.get('end_date')}")
    st.divider()

    # Display Chat History
    for msg in st.session_state.messages:
        # We skip the very first user message in the display if it feels too robotic, 
        # but showing it confirms the parameters.
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask for changes, restaurant tips, or weather info..."):
        # 1. Append User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Generate Assistant Response
        if api_key:
            with st.chat_message("assistant"):
                # Use a specific travel-themed spinner text
                with st.spinner("✈️ GroqJet is flying through the data..."):
                    response = get_groq_response(st.session_state.messages, api_key)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})