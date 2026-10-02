from app import load_models, predict_ticket
import pandas as pd

model, tfidf = load_models()

tickets = [
    "My laptop cannot connect to the office network.",
    "The application keeps showing an error when I open it.",
    "I cannot access my account.",
    "Can you give me access to the shared folder for marketing?",
    "Need a new license for Microsoft Word and Excel."
]

print("Testing 5 new ticket descriptions:")
for t in tickets:
    pred, conf = predict_ticket(t, model, tfidf)
    print(f"Ticket: '{t}'")
    print(f"Predicted Category: {pred} (Confidence: {conf:.2f}%)\n")
