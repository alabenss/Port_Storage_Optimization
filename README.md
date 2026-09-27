# AI Port Storage Optimization Platform

## Intelligent Terminal Storage Management System

Developed during a 1-month internship at **Port Djen Djen - Jijel**

---

## 1. Project Overview

The **AI Port Storage Optimization Platform** is a smart terminal management system designed to assist port operators in managing cargo storage operations.

The platform provides:

- Cargo registration and management.
- Storage zone and position management.
- Automatic storage allocation recommendation.
- Operational monitoring.
- Digital terminal visualization.
- Report generation.
- Intelligent decision-support modules.

The objective is to optimize cargo placement by analyzing cargo characteristics and available storage positions while reducing manual decision-making.

---

# 2. System Architecture

The project follows a separated frontend/backend architecture.

```
AI Port Storage Optimization Platform

            Frontend
        React + Vite
              |
              |
            REST API
              |
              |
            Backend
            FastAPI
              |
              |
          SQLite Database
```

---

# 3. Technologies Used

## Frontend

Technology:

- React.js
- Vite
- JavaScript
- CSS

Main responsibilities:

- User interface.
- Operator interaction.
- Data visualization.
- API communication.
- Displaying recommendations and reports.

---

## Backend

Technology:

- FastAPI
- Python
- SQLAlchemy
- SQLite

Main responsibilities:

- Business logic.
- Database management.
- Cargo processing.
- Storage allocation algorithm.
- Import processing.
- Report generation.
- API services.

---

## Database

Database:

- SQLite

Stores:

- Cargo units.
- Storage zones.
- Storage positions.
- Allocation history.
- Operational records.

---

# 4. Project Structure

```
AI-Port-Storage-Optimization/

│
├── backend/
│
│   ├── app/
│   │
│   ├── routers/
│   │
│   ├── models/
│   │
│   ├── services/
│   │
│   ├── database/
│   │
│   ├── reports/
│   │
│   └── requirements.txt
│
│
├── frontend/
│
│   ├── src/
│   │
│   ├── pages/
│   │
│   ├── components/
│   │
│   ├── api/
│   │
│   └── package.json
│
└── README.md
```

---

# 5. Requirements

Before running the project, install:

## Required Software

### Python

Version:

```
Python 3.10+
```

Check installation:

```bash
python --version
```

---

### Node.js

Version:

```
Node.js 18+
```

Check installation:

```bash
node --version
```

---

# 6. Backend Installation

Open a terminal:

Navigate to backend folder:

```bash
cd backend
```

---

## Create Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

## Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

Main backend libraries:

- FastAPI
- Uvicorn
- SQLAlchemy
- Pandas
- OpenPyXL
- ReportLab

---

# 7. Start Backend Server

Inside the backend folder:

```bash
uvicorn app.main:app --reload
```

The backend will start at:

```
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides documentation:

Swagger UI:

```
http://127.0.0.1:8000/docs
```

The documentation allows testing all API endpoints.

---

# 8. Frontend Installation

Open another terminal.

Navigate to frontend:

```bash
cd frontend
```

---

Install dependencies:

```bash
npm install
```

This installs:

- React
- Vite
- Frontend libraries

---

# 9. Start Frontend Application

Run:

```bash
npm run dev
```

The interface will start:

```
http://localhost:5173
```

---

# 10. Application Workflow

## Cargo Management

The operator can:

- View cargo units.
- Edit cargo information.
- Delete incorrect records.
- View detailed information.
- Request automatic allocation recommendation.
- Release stored cargo.

---

## Storage Management

The storage module manages:

- Storage zones.
- Storage positions.
- Position availability.
- Occupancy information.

The allocation engine uses these parameters to find suitable locations.

---

## Automatic Allocation System

The allocation engine evaluates possible positions according to:

- Cargo type compatibility.
- Storage zone restrictions.
- Position availability.
- Weight limitations.
- Storage rules.

The system returns the most suitable position as a recommendation.

The current implementation is based on optimization rules.

Future versions can integrate machine learning models when enough historical data becomes available.

---

# 11. Import Manifest Processing

The system supports Excel manifest import.

Workflow:

1. User uploads Excel file.
2. Spreadsheet structure is analyzed.
3. Columns are automatically mapped.
4. Data is validated.
5. Cargo records are inserted into database.

Special handling:

Vehicle information is processed separately when cargo nature corresponds to vehicles.

---

# 12. Digital Yard Visualization

The Digital Yard module provides a visual representation of the terminal.

It displays:

- Storage zones.
- Cargo areas.
- Terminal organization.

The objective is to provide a digital view of storage distribution.

---

# 13. AI Control Center

The AI Control Center provides intelligent operational indicators.

Displayed information:

- Recommendation count.
- Allocation activity.
- Multi-position operations.
- Risk monitoring.

The current risk monitoring system uses operational rules and scoring based on:

- Cargo state.
- Allocation status.
- Storage constraints.
- Operational activity.

It is designed to be replaced by machine learning models in future improvements.

---

# 14. Prediction Center

The Prediction Center prepares future predictive modules:

- Cargo dwell time prediction.
- Storage occupancy forecasting.
- Terminal activity forecasting.
- Operational risk prediction.

Important note:

The predictive models are not currently trained because the available historical company data was limited. Only one operational file was provided during the internship, which was not sufficient for reliable machine learning training.

---

# 15. Reports System

The platform provides operational reports:

Available reports:

- Inventory Report.
- Storage Report.
- Movement Report.
- Decision Report.

Export formats:

- JSON.
- PDF.
- Excel.

Reports provide traceability of:

- Cargo information.
- Storage operations.
- Movements.
- Allocation decisions.

---

# 16. Environment Configuration

The frontend communicates with the backend through REST APIs.

Backend URL:

```
http://127.0.0.1:8000
```

Frontend URL:

```
http://localhost:5173
```

Make sure both servers are running simultaneously.

---

# 17. Running the Complete System

## Terminal 1 - Backend

```bash
cd backend

venv\Scripts\activate

uvicorn app.main:app --reload
```

---

## Terminal 2 - Frontend

```bash
cd frontend

npm install

npm run dev
```

---

Open:

```
http://localhost:5173
```

---

# 18. Project Limitations

Due to limited available operational data during the internship:

- Predictive machine learning models could not be fully implemented.
- Storage duration prediction requires historical records.
- Advanced forecasting requires larger datasets.

The developed platform provides the complete architecture required for future intelligent improvements.

---

# 19. Future Improvements

Possible future developments:

- Machine learning prediction models.
- Real storage duration prediction.
- Congestion forecasting.
- IoT sensor integration.
- Real-time terminal monitoring.
- Advanced anomaly detection.
- Digital twin simulation.

---

# 20. Conclusion

The AI Port Storage Optimization Platform provides a complete foundation for intelligent port storage management.

It combines:

- Cargo management.
- Storage optimization.
- Automatic allocation assistance.
- Operational monitoring.
- Reporting.

The system was developed during a one-month internship at Port Djen Djen and demonstrates how digital solutions can improve terminal organization and decision support.

With access to larger historical datasets, the platform can be further enhanced with real predictive AI models and advanced optimization capabilities.

---

## Author

**BENSABRA ALA**

Engineering Student  
National Higher School of Artificial Intelligence (ENSIA)

Specialization:

Artificial Intelligence and Data Science

Internship:

Port Djen Djen - Jijel
