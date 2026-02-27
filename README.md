# AI-Powered Intelligent Restaurant Booking Agent

A sophisticated, AI-driven customer assistant for **Bella Vista Bistro**. This agent leverages the **Google Gemini 1.5 Flash LLM** to handle restaurant inquiries, menu management, and real-time table reservations using autonomous **Function Calling**.

## 🚀 Key Features

- **Autonomous Table Booking:** Checks availability and manages reservations via LLM tools.
- **Dynamic Knowledge Base:** Answers questions about the menu, hours, and policies using integrated markdown documentation.
- **Intelligent Support:** Handles order issues and provides real-time status updates.
- **Brand Personality:** Maintains a warm, Italian-Mediterranean persona with contextual greetings.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **AI Core:** Google Gemini 1.5 Flash (Generative AI SDK)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Persistence:** Local CSV-based data storage

## 📋 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Booking Agent"
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (refer to `.env.example`) and add your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application

Start the Flask server:

```bash
python app.py
```

Then, open `index.html` in your browser to start chatting with the agent!

---

> [!NOTE]
> **Future Updates:** This project is actively being developed. New features like payment processing, SMS notifications, and advanced admin analytics will be added in future updates.
