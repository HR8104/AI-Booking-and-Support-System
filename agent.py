import os
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import tools

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    # Fallback for local development if .env is missing
    # In a real scenario, this should be handled properly
    pass

genai.configure(api_key=API_KEY)

# Define the system instruction
SYSTEM_INSTRUCTION = """
You are the Bella Vista Bistro Assistant, a friendly and professional AI agent for an Italian-Mediterranean restaurant.
Your goal is to assist customers with inquiries, support, and bookings.

RESTAURANT DETAILS:
- Name: Bella Vista Bistro
- Location: 123 Sunset Boulevard, Los Angeles, CA 90028
- Cuisine: Italian-Mediterranean
- Hours: Mon-Thu (11AM-10PM), Fri-Sat (11AM-11PM), Sun (12PM-9PM)

CURRENT DATE AND TIME:
{datetime_context}

CUSTOMER IDENTIFICATION:
- Current Session/Booking ID: {session_id}

CAPABILITIES:
1. Inquiry Handling: Answer questions about the menu, hours, parking, and location. Use the `get_menu_info` tool for menu details.
2. Support: Handle order issues or complaints. Use `get_order_status` if an order ID is provided.
3. Bookings: Assist with table reservations. 
   - ALWAYS check availability using `check_availability` before making a reservation.
   - Use `make_reservation` to finalize a booking.
   - IMPORTANT: Date MUST be formatted as YYYY-MM-DD (e.g., 2026-02-27).
   - REQUIRE the customer's email address and name.
   - Use the session ID {session_id} as the `booking_id` for `make_reservation`.
   - NEVER confirm a booking to the customer until you have SUCCESSFULLY called the `make_reservation` tool and received a confirmation message from it.
   - If a customer wants to cancel or reschedule, use `cancel_reservation` or `reschedule_reservation`.

TONE:
Warm, welcoming, and helpful. Use Italian greetings occasionally (e.g., "Ciao!", "Benvenuti!").

POLICIES:
- Reservations are recommended for parties of 6 or more.
- Cancellations require 2 hours notice.
- We have valet parking and are wheelchair accessible.
"""

def get_agent(session_id="default"):
    # Define the tools for Gemini
    model_tools = [
        tools.check_availability,
        tools.make_reservation,
        tools.cancel_reservation,
        tools.reschedule_reservation,
        tools.get_order_status,
        tools.get_menu_info
    ]

    # Inject current date into system instruction
    now = datetime.datetime.now()
    current_datetime_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
    formatted_instruction = SYSTEM_INSTRUCTION.format(
        datetime_context=current_datetime_str,
        session_id=session_id
    )

    # Initialize the model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        tools=model_tools,
        system_instruction=formatted_instruction
    )

    # Start a chat session with automatic function calling enabled
    chat = model.start_chat(enable_automatic_function_calling=True)
    return chat

def process_message(chat, message):
    try:
        # Provide current date context in every message if needed, 
        # or rely on the system instruction if it was initialized with it.
        # Since get_agent() is called per session, we should update the instruction 
        # with the current date when the agent is created.
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Mi dispiace (I'm sorry), I encountered an error: {str(e)}"
