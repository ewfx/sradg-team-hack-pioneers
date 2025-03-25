import os
import pandas as pd
import json
import openai
import time
from flask import Flask, request, jsonify
from sklearn.ensemble import IsolationForest
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()
openai.api_key = "<YOUR_OPEN_AI_KEY>"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "data"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_data(file_path):
    """Load reconciliation data from CSV or Excel."""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format.")

def detect_anomalies(df, criteria_columns, comments_column):
    """Detect anomalies using Isolation Forest and include existing comments."""    
    # Step 1: Train the Isolation Forest model
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[criteria_columns])
    
    # Step 2: Mark anomalies
    df['is_anomaly'] = df['anomaly_score'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')

    # Step 3: Extract existing comments from the dataset
    if comments_column in df.columns:
        df['Comments'] = df[comments_column]  # Use provided comments
    else:
        df['Comments'] = "No comment available"  # Default message if missing

    df['Comments'] = df['Comments'].fillna("No Anomaly")

    # Step 4: Prepare final response including comments
    response = {
        "anomalies": df[['TransactionID', 'is_anomaly', 'Comments']].to_dict(orient='records')
    }
    
    return response


def summarize_break_resolutions(anomalies_df):
    """Generate LLM-based summary of break resolutions."""    
    # Extract unique comments
    unique_comments = anomalies_df['Comments'].dropna().unique()
    summaries = []            
    for comment in unique_comments:
        prompt = f"Summarize the following reconciliation break reason:\n{comment}"              
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary_text = response.choices[0].message.content        
        summaries.append({"Comment-type": comment, "Summary": summary_text})
        time.sleep(60)

    return summaries


@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies_api():
    """API endpoint to detect anomalies."""
    if 'file' not in request.files or 'config' not in request.form:
        return jsonify({"error": "File and config JSON are required."}), 400
    
    file = request.files['file']
    config = json.loads(request.form['config'])
    
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    df = load_data(file_path)
    df = detect_anomalies(df, config['criteria_columns'],config['comments_column'])    
    return jsonify(df)


@app.route('/summarize_resolutions', methods=['POST'])
def summarize_resolutions_api():
    """API endpoint to summarize break resolutions."""
    data = request.json
    df = pd.DataFrame(data['anomalies'])
    summary = summarize_break_resolutions(df)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)


