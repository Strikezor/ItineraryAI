import streamlit as st
import datetime
import os
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS

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
6.  **Real-Time Data:** If provided with [Real-Time Web Context], use that information to answer specific questions about events, weather, or news.
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
    st.markdown("1. Fill in your trip details.")
    st.markdown("2. Chat with the AI to refine your plan.")
    
    if st.button("Reset Planner"):
        st.session_state.messages = []
        st.session_state.trip_started = False
        st.session_state.trip_context = {}
        st.rerun()

# --- Helper Function: Web Search ---
def search_web(query, max_results=3):
    """
    Searches DuckDuckGo and returns formatted results.
    """
    try:
        # DDGS().text() returns an iterator, convert to list
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return None
            
        context_str = ""
        for i, res in enumerate(results, 1):
            context_str += f"Source {i}:\n- Title: {res['title']}\n- Snippet: {res['body']}\n- Link: {res['href']}\n\n"
        return context_str
        
    except Exception as e:
        # Fail silently or log error so app doesn't crash
        print(f"Search Error: {e}")
        return None

# --- Helper Function: Call Groq API ---
def get_groq_response(messages, api_key, web_context=None):
    if not api_key:
        st.error("Please set your Groq API Key in the .env file.")
        return None
    
    client = Groq(api_key=api_key)
    
    try:
        # Prepare the conversation history
        # We start with the system prompt
        full_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # We copy the message history so we don't accidentally mutate the session state
        # when adding the web context to the last message
        messages_payload = [msg.copy() for msg in messages]
        
        # If we have web context, inject it into the LAST message (the user's latest prompt)
        # This gives the model the data right when it needs it
        if web_context and messages_payload:
            last_msg = messages_payload[-1]
            last_msg['content'] += f"\n\n[Real-Time Web Context - Use this to answer the user]:\n{web_context}"
        
        full_history.extend(messages_payload)
        
        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile",
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
                with st.status("🗺️ Planning your adventure...", expanded=True) as status:
                    # Optional: We could also search here, but let's keep initial generation pure for speed
                    st.write("Consulting travel maps...")
                    response = get_groq_response(st.session_state.messages, api_key)
                    st.write("Finalizing itinerary...")
                    status.update(label="Itinerary Ready!", state="complete", expanded=False)
                    
                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()

else:
    # Display details summary
    ctx = st.session_state.trip_context
    st.caption(f"Trip: {ctx.get('source')} ➝ {ctx.get('destination')} | {ctx.get('start_date')} to {ctx.get('end_date')}")
    st.divider()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask for changes, restaurant tips, or weather info..."):
        # 1. Append User Message to State (Clean version without RAG data)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Generate Assistant Response
        if api_key:
            with st.chat_message("assistant"):
                # We use a placeholder to show steps
                with st.status("Thinking...", expanded=False) as status:
                    
                    # Step A: Search Web (RAG)
                    st.write("🔎 Searching real-time info...")
                    destination_context = st.session_state.trip_context.get('destination', '')
                    
                    # Construct a search query that includes the destination for better relevance
                    search_query = f"{prompt} {destination_context}"
                    web_data = search_web(search_query)
                    
                    if web_data:
                        st.write("✅ Found relevant data!")
                    else:
                        st.write("❌ No web data found, using internal knowledge.")
                    
                    # Step B: Call LLM with the context
                    st.write("🧠 Generating response...")
                    response = get_groq_response(st.session_state.messages, api_key, web_context=web_data)
                    
                    status.update(label="Complete", state="complete", expanded=False)

                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})