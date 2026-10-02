import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def clean_text(text):
    """
    Simple text preprocessing:
    - Convert to lowercase
    - Remove special characters and numbers (optional, but requested simple: remove unnecessary punctuation)
    - Remove extra spaces
    """
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text) # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip() # Remove extra spaces
    return text

def main():
    print("--- 1. LOADING DATASET ---")
    # Load dataset
    df = pd.read_csv('data/helpdesk_tickets.csv')
    
    # Check if there are duplicate 'id' columns from concatenation
    # Drop them and keep only one, or just select what we need
    # The columns are likely: ['id', 'text', 'id', 'category_truth']
    
    # To avoid issues with duplicated 'id' column names
    df = df.loc[:,~df.columns.duplicated()].copy()

    # Identifying columns
    text_col = 'text'
    category_col = 'category_truth'
    
    print(f"Number of rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    
    print("\nCategory Distribution:")
    print(df[category_col].value_counts())
    
    print("\nSample Tickets:")
    for idx, row in df.head(3).iterrows():
        print(f"[{row[category_col]}] {row[text_col][:100]}...")
        
    print("\n--- 2. PREPROCESSING ---")
    df['cleaned_text'] = df[text_col].apply(clean_text)
    
    # Handle any empty strings if they appeared after cleaning
    df = df[df['cleaned_text'] != '']
    
    X = df['cleaned_text']
    y = df[category_col]
    
    print("\n--- 3. TRAIN/TEST SPLIT ---")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train)} rows")
    print(f"Testing set: {len(X_test)} rows")
    
    print("\n--- 4. TF-IDF VECTORIZATION ---")
    tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, stop_words='english')
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    print(f"TF-IDF features: {X_train_tfidf.shape[1]}")
    
    print("\n--- 5. MODEL TRAINING (Logistic Regression) ---")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_tfidf, y_train)
    
    print("\n--- 6. EVALUATION ---")
    y_pred = model.predict(X_test_tfidf)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-score:  {f1:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion Matrix Visualization
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=model.classes_, yticklabels=model.classes_)
    plt.title('Confusion Matrix - IT Helpdesk Support Tickets')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig('outputs/confusion_matrix.png')
    print("\nConfusion matrix saved to outputs/confusion_matrix.png")
    
    print("\n--- 7. SAVING MODELS ---")
    joblib.dump(model, 'models/model.pkl')
    joblib.dump(tfidf, 'models/tfidf.pkl')
    print("Model saved to models/model.pkl")
    print("TF-IDF Vectorizer saved to models/tfidf.pkl")

if __name__ == '__main__':
    main()
