import pytest
from app.services.pii_service import PIIDetector
from app.models.event import Classification

def test_no_pii():
    text, cls = PIIDetector.process_text("Just a normal log message.")
    assert text == "Just a normal log message."
    assert cls == Classification.PUBLIC

def test_email():
    text, cls = PIIDetector.process_text("User bob@example.com logged in.")
    assert text == "User [email] logged in."
    assert cls == Classification.INTERNAL

def test_multiple_emails():
    text, cls = PIIDetector.process_text("Emails a@b.com and c@d.com sent.")
    assert text == "Emails [email] and [email] sent."
    assert cls == Classification.INTERNAL

def test_phone():
    text, cls = PIIDetector.process_text("Call me at 9876543210 or +91-9988776655.")
    assert text == "Call me at [phone] or [phone]."
    assert cls == Classification.INTERNAL

def test_invalid_phone():
    text, cls = PIIDetector.process_text("My ID is 1234567890.")
    assert text == "My ID is 1234567890." # Should not match because it doesn't start with 6-9
    assert cls == Classification.PUBLIC

def test_aadhaar():
    text, cls = PIIDetector.process_text("Aadhaar is 234567890124.")
    assert text == "Aadhaar is [aadhaar]."
    assert cls == Classification.CONFIDENTIAL

def test_invalid_aadhaar():
    text, cls = PIIDetector.process_text("Aadhaar is 234567890123.")
    assert text == "Aadhaar is 234567890123."
    assert cls == Classification.PUBLIC

def test_pan():
    text, cls = PIIDetector.process_text("My PAN is ABCDE1234F.")
    assert text == "My PAN is [pan]."
    assert cls == Classification.CONFIDENTIAL

def test_invalid_pan():
    text, cls = PIIDetector.process_text("My PAN is ABCDE12345.")
    assert text == "My PAN is ABCDE12345."
    assert cls == Classification.PUBLIC

def test_credit_card():
    text, cls = PIIDetector.process_text("Card: 4242 4242 4242 4242")
    assert text == "Card: [credit_card]"
    assert cls == Classification.RESTRICTED

def test_invalid_credit_card():
    text, cls = PIIDetector.process_text("Card: 4242 4242 4242 4243")
    assert text == "Card: 4242 4242 4242 4243"
    assert cls == Classification.PUBLIC

def test_multiple_pii():
    text, cls = PIIDetector.process_text("Email a@b.com PAN ABCDE1234F")
    assert text == "Email [email] PAN [pan]"
    assert cls == Classification.CONFIDENTIAL

    text, cls = PIIDetector.process_text("Email a@b.com Card: 4242 4242 4242 4242")
    assert text == "Email [email] Card: [credit_card]"
    assert cls == Classification.RESTRICTED
