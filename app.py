import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import agent

app = Flask(__name__, static_folder='static')
CORS(app)

# Dictionary to store chat sessions
# session_id -> chat_session
sessions = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # If no session_id provided, create a new one
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())[:8] # Shorter ID for easier reading
        try:
            sessions[session_id] = agent.get_agent(session_id)
        except Exception as e:
            return jsonify({'error': f'Failed to initialize agent: {str(e)}'}), 500

    chat_session = sessions[session_id]
    
    try:
        response_text = agent.process_message(chat_session, user_message)
        return jsonify({
            'response': response_text,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cancel/<booking_id>')
def cancel_booking(booking_id):
    import tools
    result = tools.cancel_reservation(booking_id)
    return f"<h1>Booking Cancellation</h1><p>{result}</p><a href='/'>Return to Home</a>"

@app.route('/reschedule/<booking_id>')
def reschedule_booking(booking_id):
    return f"<h1>Reschedule Booking</h1><p>To reschedule your booking (ID: {booking_id}), please chat with our AI assistant on the <a href='/'>Home Page</a> and provide the new date and time.</p>"

@app.route('/admin')
def admin_page():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/api/admin/bookings')
def get_all_bookings():
    import tools
    bookings = tools.load_all_reservations()
    return jsonify(bookings)

if __name__ == '__main__':
    # Ensure static folder exists
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
