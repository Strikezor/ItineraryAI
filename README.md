# ✈️ GroqJet Travel Planner

**GroqJet** is an AI-powered travel consultant that builds custom itineraries in seconds. By leveraging the **Llama 3.3 70B** model via **Groq** and real-time web searching through **DuckDuckGo**, GroqJet provides up-to-date recommendations for food, accommodation, and attractions.

---

## ✨ Features

* **Intelligent Itinerary Generation:** Generates multi-day plans based on your source, destination, and dates.
* **Real-Time Web Context (RAG):** Uses DuckDuckGo search to find current events, weather, or local news for your destination.
* **Travel-Only Guardrails:** A strict system prompt ensures the AI stays focused on travel logistics and doesn't wander into unrelated topics.
* **Interactive Chat:** Refine your trip by asking follow-up questions about specific restaurants, packing lists, or cultural tips.
* **Session Management:** Reset your planning session at any time with a single click.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **LLM Engine:** [Groq Cloud SDK](https://console.groq.com/) (Llama-3.3-70b-versatile)
* **Search Engine:** `duckduckgo-search` (DDGS)
* **Environment Management:** `python-dotenv`

---

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.9 or higher.
* A **Groq API Key**. You can get one for free at the [Groq Cloud Console](https://console.groq.com/).

### 2. Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/your-username/groqjet-planner.git
cd groqjet-planner

```

### 3. Install Dependencies

It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

> **Note:** Create a `requirements.txt` file with these contents:
> `streamlit`, `groq`, `duckduckgo-search`, `python-dotenv`

### 4. Environment Setup

Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=your_lp_key_here

```

### 5. Running the App

Start the Streamlit server:

```bash
streamlit run app.py

```

---

## 📖 How to Use

1. **Enter Details:** Input your starting point, destination, and travel dates in the sidebar/main form.
2. **Generate:** Click "Generate Initial Itinerary" to get a baseline plan.
3. **Chat & Refine:** Use the chat box at the bottom to ask things like *"What's the weather like in Tokyo during these dates?"* or *"Suggest some vegan-friendly ramen spots."*
4. **Reset:** Use the sidebar button to clear the conversation and start a new trip.

---

## 🛡️ Mandate & Limitations

* **Scope:** GroqJet is designed to refuse non-travel related queries (coding, politics, etc.).
* **Duration:** It currently supports planning for trips up to 60 days in length.
* **API Limits:** Performance is subject to Groq's rate limits for the `llama-3.3-70b-versatile` model.
