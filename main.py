import agent
import sys

def main():
    print("--- Bella Vista Bistro Assistant ---")
    print("Ciao! I am your virtual assistant. How can I help you today?")
    print("(Type 'exit' to quit)")
    
    try:
        chat = agent.get_agent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Please ensure you have a valid GEMINI_API_KEY in your .env file.")
        return

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Assistant: Grazie! Have a wonderful day. Arrivederci!")
            break
        
        if not user_input.strip():
            continue

        print("Assistant: Thinking...", end="\r")
        response = agent.process_message(chat, user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
