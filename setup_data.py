import pandas as pd
import urllib.request
import os

print("Downloading dataset...")
urls = {
    'X_train.csv': 'https://zenodo.org/api/records/7648117/files/X_train.csv/content',
    'X_test.csv': 'https://zenodo.org/api/records/7648117/files/X_test.csv/content',
    'y_train.csv': 'https://zenodo.org/api/records/7648117/files/y_train.csv/content',
    'y_test.csv': 'https://zenodo.org/api/records/7648117/files/y_test.csv/content'
}

for name, url in urls.items():
    print(f"Downloading {name}...")
    urllib.request.urlretrieve(url, name)

print("Loading and combining...")
X_train = pd.read_csv('X_train.csv')
X_test = pd.read_csv('X_test.csv')
y_train = pd.read_csv('y_train.csv')
y_test = pd.read_csv('y_test.csv')

# The dataset files might just have columns like text and category. Let's see them.
# I'll print the head of X_train before combining to make sure the structure.
print("X_train columns:", X_train.columns.tolist())
print("y_train columns:", y_train.columns.tolist())

# Combine X and Y
train = pd.concat([X_train, y_train], axis=1)
test = pd.concat([X_test, y_test], axis=1)

# Combine train and test to create the single dataset as requested by user
full_dataset = pd.concat([train, test], axis=0).reset_index(drop=True)

# Save to data directory
full_dataset.to_csv('IT-Helpdesk-Ticket-Classifier/data/helpdesk_tickets.csv', index=False)
print("Saved to IT-Helpdesk-Ticket-Classifier/data/helpdesk_tickets.csv")

# Clean up downloaded files
for name in urls.keys():
    os.remove(name)
print("Done!")
