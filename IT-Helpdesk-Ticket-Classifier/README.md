# Machine Learning Based Classification of IT Helpdesk Support Tickets

## Problem Statement
IT helpdesk teams receive many support requests and manually categorizing them takes time. Machine Learning can automatically classify tickets based on their textual descriptions, saving time and improving response efficiency.

## Objectives
- Automatically classify IT support tickets
- Preprocess ticket text
- Convert text into numerical features using TF-IDF
- Train a Machine Learning classifier
- Evaluate the classifier
- Predict the category of new tickets

## Methodology
Dataset ↓ Text Preprocessing ↓ TF-IDF ↓ Logistic Regression ↓ Prediction ↓ Evaluation

## Technologies
- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Joblib
- Streamlit

## Dataset
This project uses the public dataset **"Classification of IT Support Tickets"** from Zenodo.
Source: [https://zenodo.org/records/7648117](https://zenodo.org/records/7648117)
It contains 2,229 manually classified IT support tickets across 7 categories. The text has been anonymized to remove Personal Identifiable Information (PII).

## Evaluation
The model is evaluated using standard Machine Learning metrics:
- **Accuracy**: The percentage of correctly predicted tickets out of all predictions.
- **Precision**: The percentage of true positive predictions out of all positive predictions for a category.
- **Recall**: The percentage of true positive predictions out of all actual positive instances for a category.
- **F1-score**: The harmonic mean of precision and recall.
- **Confusion Matrix**: A visualization of the actual versus predicted categories.

## How to Run

1. Install the required libraries:
```bash
pip install -r requirements.txt
```

2. Train the model:
```bash
python train_model.py
```

3. Run the Streamlit application:
```bash
streamlit run app.py
```
