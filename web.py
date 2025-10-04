from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

# Load trained model and MultiLabelBinarizer
model = joblib.load('cuisine_pipeline_model.pkl')
mlb = joblib.load('cuisine_multilevel_encoder.pkl')

# List of features used during training (must match model)
features = pd.Index([
    'Average Cost for two',
    'Price range',
    'Aggregate rating',
    'Has Table booking',
    'Has Online delivery'
])

def predict_cuisine(user_input: dict, top_n=3, threshold=0.3):
    input_df = pd.DataFrame([user_input])

    # Convert Yes/No to binary
    input_df['Has Table booking'] = input_df['Has Table booking'].map({'Yes': 1, 'No': 0})
    input_df['Has Online delivery'] = input_df['Has Online delivery'].map({'Yes': 1, 'No': 0})

    # Ensure correct column order
    input_df = input_df[features]

    # Predict probabilities
    proba = model.predict_proba(input_df)

    # Apply threshold
    binary_pred = (proba >= threshold).astype(int)

    if not binary_pred.any():
        # Pick top_n highest if none pass threshold
        top_indices = np.argsort(proba[0])[::-1][:top_n]
        predicted_labels = [mlb.classes_[i] for i in top_indices]
    else:
        predicted_labels = [mlb.classes_[i] for i in np.where(binary_pred[0] == 1)[0]]

    return predicted_labels


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form values
        user_input = {
            'Average Cost for two': float(request.form['cost']),
            'Price range': int(request.form['price_range']),
            'Aggregate rating': float(request.form['rating']),
            'Has Table booking': request.form['table_booking'],
            'Has Online delivery': request.form['online_delivery']
        }

        # Predict cuisine
        prediction = predict_cuisine(user_input)

        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)