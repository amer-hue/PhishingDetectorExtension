from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

app = Flask(__name__)
CORS(app)

# Load and inspect dataset
data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Phishing_Email.csv')

# Load the CSV file
data = pd.read_csv(data_path)

# Print column names and the first few rows to verify data
print("Columns in the dataset:", data.columns)
print(data.head())

# Use the correct columns
data = data[['Email Text', 'Email Type']]  # Selecting relevant columns
data.columns = ['email_content', 'label']  # Rename for consistency

# Map 'Safe Email' to 0 and 'Phishing Email' to 1
data['label'] = data['label'].map({'Safe Email': 0, 'Phishing Email': 1})

# Check unique values in the label column
print("Unique values in 'label':", data['label'].unique())

# Remove rows with NaN values in the 'email_content' column
data = data.dropna(subset=['email_content'])

# Check for any empty strings in the 'email_content' column and remove them
data = data[data['email_content'].str.strip().astype(bool)]

# Balance the data
phishing = data[data['label'] == 1]
legitimate = data[data['label'] == 0]
print("Number of phishing samples:", len(phishing))
print("Number of legitimate samples:", len(legitimate))

# Ensure both phishing and legitimate categories contain data
if len(phishing) == 0 or len(legitimate) == 0:
    raise ValueError("No samples found for either phishing or legitimate emails. Check label values and data loading.")

# Balance the data by sampling the smaller category
min_samples = min(len(phishing), len(legitimate))
balanced_data = pd.concat([phishing.sample(min_samples), legitimate.sample(min_samples)])
balanced_data = balanced_data.sample(frac=1).reset_index(drop=True)
print("Balanced data sample:")
print(balanced_data.head())

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(balanced_data['email_content'], balanced_data['label'], test_size=0.3, random_state=42)

# Initialize vectorizer and transform data
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_df=0.95, min_df=5)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train the model
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# (Optional) Evaluate model
predictions = model.predict(X_test_tfidf)
print(classification_report(y_test, predictions, target_names=['Legitimate', 'Phishing']))

# Define paths for saving model and vectorizer
model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'model')
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Save model and vectorizer
with open(os.path.join(model_dir, 'phishing_model.pkl'), 'wb') as model_file:
    pickle.dump(model, model_file)

with open(os.path.join(model_dir, 'vectorizer.pkl'), 'wb') as vec_file:
    pickle.dump(vectorizer, vec_file)

# Load model and vectorizer for API use
with open(os.path.join(model_dir, 'phishing_model.pkl'), 'rb') as model_file:
    model = pickle.load(model_file)

with open(os.path.join(model_dir, 'vectorizer.pkl'), 'rb') as vec_file:
    vectorizer = pickle.load(vec_file)

@app.route('/predict', methods=['POST'])
def predict():
    email_content = request.json.get('email')
    if not email_content:
        return jsonify({'error': 'No email content provided'}), 400

    email_vectorized = vectorizer.transform([email_content])
    prediction = model.predict(email_vectorized)[0]
    result = "Phishing" if prediction == 1 else "Legitimate"
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(port=5000)