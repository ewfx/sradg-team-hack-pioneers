# Anomaly Detection in Reconciliation Data

## Overview

This project is an anomaly detection system for reconciliation data using machine learning and OpenAI's GPT models. It processes uploaded datasets, detects anomalies, and provides a summarized resolution of identified anomalies.

## Features

- Detect anomalies using Isolation Forest
- Provide comments for each anomaly from the dataset
- Summarize break resolutions using OpenAI
- Flask-based API endpoints for easy integration

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup Instructions

1. Clone the repository:
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:  
   pandas,scikit-learn,openai,python-dotenv,werkzeug

## Usage

### Running the Flask Server

```sh
python app.py
```

The server will start at `http://127.0.0.1:5000/`

### API Endpoints

#### 1. Detect Anomalies

- **Endpoint:** `/detect_anomalies`
- **Method:** `POST`
- **Request:**
  - `file`: CSV or Excel file containing transaction data.
  - `config`: JSON object specifying key columns (e.g.,
    {
    "key_columns": ["Transaction_ID"],
    "criteria_columns": ["Amount"],
    "date_columns": ["Transaction_Date"],
    "comments_column": "Comments"
    }).
- **Response:**
  ```json
  {
    "anomalies": [
      {
        "TransactionID": "TXN832",
        "is_anomaly": "Normal",
        "Comments": "Duplicate transaction"
      },
      {
        "TransactionID": "TXN841",
        "is_anomaly": "Normal",
        "Comments": "Duplicate transaction"
      },
      {
        "TransactionID": "TXN777",
        "is_anomaly": "Anomaly",
        "Comments": "No Anomaly"
      }
    ]
  }
  ```

#### 2. Summarize Break Resolutions

- **Endpoint:** `/summarize_resolutions`
- **Method:** `POST`
- **Request:**
  - JSON object containing a list of anomalies with their comments.
    eg.
    {
    "anomalies": [
    {
    "Comments": "No Anomaly",
    "TransactionID": "TXN1127",
    "is_anomaly": "Normal"
    },
    {
    "Comments": "Delayed settlement due to bank issue",
    "TransactionID": "TXN1438",
    "is_anomaly": "Anomaly"
    }]
    }
- **Response:**
  ```json
  {
    "summary": [
      {
        "comments": "Delayed settlement due to bank issue",
        "summary": "OPENAI response"
      },
      {
        "comments": "Incorrect transaction amount",
        "summary": "OPENAI response"
      }
    ]
  }
  ```
