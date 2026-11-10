"""Tests for the agent's code-level guards (no LLM needed). Uses a temporary CSV."""
import os
import tempfile

import tools

tools.send_confirmation_email = lambda *a, **k: False  # never send real email from tests

import agent  # noqa: E402
from test_tools import next_weekday  # noqa: E402


def say(chat, text):
    chat.turn += 1
    chat.messages.append({"role": "user", "content": text})


def test_guards():
    tools.DB_FILE = os.path.join(tempfile.mkdtemp(), "guard.csv")
    day = next_weekday(1)
    chat = agent.get_agent()

    # Email never typed by the customer -> refused
    say(chat, "Book a table for 3 tomorrow")
    assert "NOT made" in chat.make_reservation(day, "19:00", 3, "Mario", "mario@example.com")

    # First call only returns a summary with the correct weekday
    say(chat, "I'm Ann, ann@example.com, 3 people at 7 PM")
    first = chat.make_reservation(day, "7 PM", 3, "Ann", "ann@example.com")
    assert first.startswith("NOT BOOKED YET") and "Tuesday" in first, first
    assert tools.load_all_reservations() == []

    # Calling again in the same turn (without the customer replying) still doesn't book
    assert chat.make_reservation(day, "19:00", 3, "Ann", "ann@example.com").startswith("NOT BOOKED YET")

    # Customer says no / changes -> not booked
    say(chat, "No wait, change it")
    assert chat.make_reservation(day, "19:00", 3, "Ann", "ann@example.com").startswith("NOT BOOKED YET")

    # Different details than the ones confirmed -> new summary, not booked
    say(chat, "yes")
    assert chat.make_reservation(day, "20:00", 3, "Ann", "ann@example.com").startswith("NOT BOOKED YET")

    # Customer confirms the summary they saw -> booked
    say(chat, "Yes, confirm")
    done = chat.make_reservation(day, "20:00", 3, "Ann", "ann@example.com")
    assert done.startswith("Successfully booked"), done
    assert len(tools.load_all_reservations()) == 1
    print("OK two-step confirmation")

    # Claim detector
    assert agent.CLAIM.search("Your new booking has been confirmed.")
    assert agent.CLAIM.search("I've cancelled your booking.")
    assert not agent.CLAIM.search("Could you confirm the date and time?")
    print("OK success-claim detector")

    # Date must come from the customer
    assert agent.customer_gave_date("2026-11-24", "3 person at 24 november 2026, 7 PM")
    assert agent.customer_gave_date("2026-11-24", "how about Nov 24th")
    assert agent.customer_gave_date("2026-11-24", "on 24/11 please")
    assert not agent.customer_gave_date("2026-11-13", "book table for 3 people, name hitendra")
    fresh = agent.get_agent()
    say(fresh, "Table for 3 please, I'm Bo, bo@example.com")
    assert "has not said which date" in fresh.make_reservation(day, "19:00", 3, "Bo", "bo@example.com")
    print("OK date-given guard")

    # Leaked tool instructions are removed from replies
    leaked = "Table for 3 on Tuesday. After they say yes, call make_reservation again with the same details. Shall I book it?"
    assert agent.clean_reply(leaked) == "Table for 3 on Tuesday. Shall I book it?", agent.clean_reply(leaked)
    print("OK instruction-leak cleanup")

    # modify_reservation changes party size
    bid = tools.load_all_reservations()[0]["booking_id"]
    res = tools.modify_reservation(bid, "ann@example.com", new_party_size=4)
    assert "4 people" in res and tools.find_reservation(bid)["party_size"] == "4", res
    print("OK modify party size")


if __name__ == "__main__":
    test_guards()
    print("\nAll agent guard tests passed successfully!")
