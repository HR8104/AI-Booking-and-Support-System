import datetime
import csv
import os

DB_FILE = 'db.csv'

def load_all_reservations():
    """Reads all reservations from the CSV file."""
    reservations = []
    if not os.path.exists(DB_FILE):
        return reservations
    try:
        with open(DB_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reservations.append(row)
    except Exception as e:
        print(f"Error reading DB: {e}")
    return reservations

def save_reservation(date, time, party_size, name, email, booking_id):
    """Appends a new reservation to the CSV file."""
    print(f"Attempting to save reservation: {booking_id} for {name}")
    file_exists = os.path.exists(DB_FILE)
    try:
        with open(DB_FILE, mode='a', encoding='utf-8', newline='') as f:
            fieldnames = ['booking_id', 'date', 'time', 'party_size', 'name', 'email', 'status', 'created_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                'booking_id': booking_id,
                'date': date,
                'time': time,
                'party_size': int(party_size),
                'name': name,
                'email': email,
                'status': 'confirmed',
                'created_at': datetime.datetime.now().isoformat()
            })
        print(f"✓ Reservation {booking_id} saved to CSV.")
        send_confirmation_email(email, name, date, time, party_size, booking_id)
    except Exception as e:
        print(f"Error writing to DB: {e}")

def update_db(reservations):
    """Overwrites the CSV file with updated reservations."""
    try:
        with open(DB_FILE, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ['booking_id', 'date', 'time', 'party_size', 'name', 'email', 'status', 'created_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reservations)
        print("✓ Database updated successfully.")
    except Exception as e:
        print(f"Error updating DB: {e}")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_confirmation_email(email, name, date, time, party_size, booking_id):
    """Sends a real confirmation email using SMTP."""
    print(f"Preparing to send email to {email}...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", 587)
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_from = os.getenv("EMAIL_FROM", f"Bella Vista Bistro <{smtp_user}>")

    if not all([smtp_host, smtp_user, smtp_pass]):
        print("\n--- SMTP NOT CONFIGURED. MOCK EMAIL BELOW ---")
        print(f"To: {email}\nSubject: Booking Confirmation\nCiao {name}, your table for {party_size} on {date} at {time} is confirmed!\nBooking ID: {booking_id}")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        msg['Subject'] = f"Booking Confirmation - Bella Vista Bistro"

        body = f"""
        Ciao {name},

        Your table reservation at Bella Vista Bistro is confirmed!

        DETAILS:
        - Date: {date}
        - Time: {time}
        - Party Size: {party_size}
        - Booking ID: {booking_id}

        To manage your booking, use the links below:
        - Reschedule: http://localhost:5000/reschedule/{booking_id}
        - Cancel: http://localhost:5000/cancel/{booking_id}

        We look forward to seeing you!
        Bella Vista Bistro Team
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.set_debuglevel(1) # Extra logging
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"✓ Real email sent to {email}")

    except Exception as e:
        print(f"Error sending email: {e}")

def check_availability(date: str, time: str, party_size: int) -> str:
    """
    Checks if a table is available for a given date, time, and party size.
    Important: date must be in YYYY-MM-DD format, time in HH:MM or HH:MM AM/PM.
    """
    print(f"Checking availability for {date} at {time} for {party_size} people")
    reservations = load_all_reservations()
    # Count only 'confirmed' or 'rescheduled' bookings with robust int parsing
    current_total = 0
    for r in reservations:
        if r['date'] == date and r['time'] == time and r['status'] != 'cancelled':
            try:
                current_total += int(float(r['party_size']))
            except (ValueError, TypeError):
                continue
    
    if current_total + int(party_size) <= 80:
        return f"Table is available for {party_size} people on {date} at {time}."
    else:
        return f"Sorry, we are fully booked for {party_size} people on {date} at {time}."

def make_reservation(date: str, time: str, party_size: int, name: str, email: str, booking_id: str) -> str:
    """
    Places a reservation for a customer and persists it to db.csv.
    Important: date must be in YYYY-MM-DD format.
    """
    print(f"Tool make_reservation called: {date}, {time}, {party_size}, {name}, {email}, {booking_id}")
    availability = check_availability(date, time, party_size)
    if "available" in availability.lower():
        save_reservation(date, time, party_size, name, email, booking_id)
        return f"Successfully booked a table for {name} ({party_size} people) on {date} at {time}. A confirmation email has been sent to {email}. Booking ID is {booking_id}."
    else:
        print(f"Reservation failed: {availability}")
        return availability

def cancel_reservation(booking_id: str) -> str:
    """
    Cancels an existing reservation in the system.
    """
    reservations = load_all_reservations()
    found = False
    for r in reservations:
        if r['booking_id'] == booking_id:
            r['status'] = 'cancelled'
            found = True
            break
    
    if found:
        update_db(reservations)
        return f"Reservation {booking_id} has been successfully cancelled."
    else:
        return f"Reservation ID {booking_id} not found."

def reschedule_reservation(booking_id: str, new_date: str, new_time: str) -> str:
    """
    Changes the date and time of an existing reservation.
    """
    reservations = load_all_reservations()
    target_res = None
    for r in reservations:
        if r['booking_id'] == booking_id:
            target_res = r
            break
    
    if not target_res:
        return f"Reservation ID {booking_id} not found."
    
    # Check availability for the new slot
    availability = check_availability(new_date, new_time, int(target_res['party_size']))
    if "available" in availability.lower():
        target_res['date'] = new_date
        target_res['time'] = new_time
        target_res['status'] = 'rescheduled'
        update_db(reservations)
        return f"Reservation {booking_id} has been rescheduled to {new_date} at {new_time}."
    else:
        return f"Sorry, the new slot ({new_date} at {new_time}) is not available."

def get_order_status(order_id: str) -> str:
    """
    Mocks checking the status of a food order for support inquiries.
    """
    # Mock logic based on order ID patterns
    if order_id.startswith("BV123"):
        return "Order #BV123 is currently being prepared and will be ready in 10 minutes."
    elif order_id.startswith("BV456"):
        return "Order #BV456 has been delivered."
    else:
        return f"Order #{order_id} not found. Please double-check your order ID."

def get_menu_info() -> str:
    """
    Returns the current menu information.
    """
    try:
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            content = f.read()
            # Extract only the menu section
            start = content.find("## Menu")
            end = content.find("## Booking Policies")
            if start != -1 and end != -1:
                return content[start:end].strip()
            return content
    except FileNotFoundError:
        return "Menu information is currently unavailable."
