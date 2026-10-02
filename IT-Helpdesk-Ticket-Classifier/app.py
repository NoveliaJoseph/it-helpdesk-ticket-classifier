import streamlit as st
import joblib
import re

# Set page title and layout
st.set_page_config(page_title="IT Helpdesk Ticket Classifier", layout="centered")

@st.cache_resource
def load_models():
    """Load the trained model and TF-IDF vectorizer."""
    try:
        model = joblib.load("models/model.pkl")
        tfidf = joblib.load("models/tfidf.pkl")
        return model, tfidf
    except FileNotFoundError:
        st.error("Model files not found. Please run train_model.py first.")
        return None, None

def clean_text(text):
    """Simple text preprocessing (same as training)."""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_ticket(text, model, tfidf):
    """Predict the category of a new ticket."""
    cleaned = clean_text(text)
    features = tfidf.transform([cleaned])
    prediction = model.predict(features)[0]
    
    # Get confidence if model supports it (Logistic Regression does)
    try:
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
        return prediction, confidence
    except AttributeError:
        return prediction, None

def main():
    st.title("💻 IT Helpdesk Support Ticket Classifier")
    st.markdown("This application uses Machine Learning to automatically classify IT support tickets based on their text descriptions.")
    
    model, tfidf = load_models()
    
    if model and tfidf:
        st.subheader("Enter Support Ticket")
        ticket_text = st.text_area("Ticket Description:", height=150, placeholder="e.g. My computer is not connecting to the network.")
        
        if st.button("Classify Ticket", type="primary"):
            if ticket_text.strip() == "":
                st.warning("Please enter a ticket description.")
            else:
                with st.spinner("Classifying..."):
                    prediction, confidence = predict_ticket(ticket_text, model, tfidf)
                    
                    st.success("Classification Complete!")
                    st.markdown(f"**Predicted Category:** `{prediction}`")
                    
                    if confidence is not None:
                        st.markdown(f"**Confidence:** `{confidence:.2f}%`")
                        
        st.divider()
        st.markdown("""
        ### Example Tickets to Try:
        - *I forgot my password and cannot access my account.* (Usually: Access)
        - *The printer on the 3rd floor is out of paper and ink.* (Usually: Hardware/Printer)
        - *My laptop cannot connect to the office network.* (Usually: Network)
        - *The HR application keeps showing an error when I open it.* (Usually: Software)
        """)

if __name__ == '__main__':
    main()
