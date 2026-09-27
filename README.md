
# AI Port Storage Optimization Platform

## Project Overview

The **AI Port Storage Optimization Platform** is a smart terminal management system developed during a 1-month internship at **Djen Djen Port - Jijel**.

The objective of this project is to assist port operators in managing cargo storage operations by providing:

- Cargo management.
- Storage zone and position management.
- Automatic storage allocation recommendation.
- Operational monitoring.
- Data import from Excel manifests.
- Report generation.
- Intelligent decision support modules.

The platform follows a separated **Frontend / Backend architecture**.


# System Architecture

## Frontend

**Technology:**
- React
- Vite

The frontend provides:

- User interface.
- Operator interaction.
- Data visualization.
- Communication with backend APIs.



## Backend

**Technology:**
- FastAPI
- SQLite Database

The backend handles:

- Business logic.
- Database operations.
- Cargo processing.
- Storage allocation engine.
- Import processing.
- Report generation.


# Requirements

Before running the project, install:

## Required Software

- Python 3.10+
- Node.js 18+
- npm

Verify installation:

python --version
node --version
npm --version


# Backend Installation

Open a terminal:

cd backend

Create a virtual environment:

python -m venv venv


Activate it:

### Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the backend server:

uvicorn app.main:app --reload

The backend will start at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs


# Frontend Installation

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend will start at:

http://localhost:5173

# Notes

The current project was developed using the available company data during the internship period.

Due to limited historical data availability, some advanced predictive features are prepared for future integration, such as:

- Machine learning prediction models.
- Storage duration prediction.
- Congestion forecasting.
- Advanced anomaly detection.

The current allocation system is based on intelligent optimization rules and provides the foundation for future AI improvements.

# Author

**BENSABRA ALA**  
Engineering Student - ENSIA  
Artificial Intelligence and Data Science
