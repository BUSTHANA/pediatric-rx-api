# 🧒💊 Pediatric Rx API

An AI-powered REST API that helps parents make informed decisions about their children's medications. Built with **FastAPI** and **Google Gemini AI**, it provides personalized, age-and-weight-appropriate medicine guidance.

> ⚠️ **Disclaimer**: This tool is for educational purposes only and should NOT replace professional medical advice. Always consult your child's pediatrician.

## Features

| Endpoint | Description |
|---|---|
| `POST /api/v1/medicine/dosage` | Calculate weight-based dosage with frequency, forms, and safety limits |
| `POST /api/v1/medicine/info` | Get advantages, disadvantages, and a parent-friendly summary |
| `POST /api/v1/medicine/warnings` | Warning signs, when to call a doctor, and when to stop medication |
| `POST /api/v1/medicine/emergency` | Overdose signs, immediate steps, and emergency contacts |
| `POST /api/v1/medicine/interactions` | Check if multiple medicines can be safely taken together |

## Tech Stack

- **FastAPI** — async Python web framework
- **Google Gemini 2.0 Flash** — AI model for medical information
- **Pydantic** — request/response validation

## Getting Started

### Prerequisites
- Python 3.10+
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Installation

```bash
git clone https://github.com/BUSTHANA/pediatric-rx-api.git
cd pediatric-rx-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

### Run

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage Example

```bash
curl -X POST http://localhost:8000/api/v1/medicine/dosage \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_name": "Paracetamol",
    "child_weight_kg": 15.0,
    "child_age_years": 5.0,
    "condition": "fever"
  }'
```

## API Documentation

FastAPI auto-generates interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
