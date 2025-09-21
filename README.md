Legal Analyzer

📖 Overview
Legal Analyzer is a full-stack web application designed to simplify the analysis of legal documents.
It enables users (lawyers, students, businesses, or individuals) to upload contracts, policies, or case files and receive AI-powered insights, OCR text extraction, and structured reports.

The project combines a modern frontend with a high-performance backend to deliver a smooth, intuitive, and reliable experience.

✨ Key Features

📂 Document Upload & Management – Upload PDFs or images securely.
🔍 OCR & Text Extraction – Extract text from scanned files using PyMuPDF and pytesseract.
🤖 AI-Powered Analysis – Summarization, clause detection, and risk spotting via google-generativeai.
📊 Interactive Dashboard – View extracted insights and visualizations in real time.
📑 Report Exporting – Generate PDF reports with ReportLab.
⚡ Fast & Scalable – Built with FastAPI and Vite for rapid performance.

🛠 Technology Stack
Frontend: React, Vite, Tailwind CSS
Backend: Python, FastAPI, Uvicorn
OCR / NLP: PyMuPDF, pytesseract, Google Generative AI
Database (optional / configurable): PostgreSQL or MongoDB
Deployment: Vercel, AWS (configurable)


📂 Project Structure
LEGAL_ANALYZER/
├── frontend/ # React + Vite frontend
│ ├── src/ # UI components, hooks, pages
│ ├── public/ # Static assets
│ └── package.json
│
├── backend/ # FastAPI backend
│ ├── app/ # API routes, services
│ ├── models/ # Data models / schemas
│ ├── venv/ # Virtual environment
│ └── requirements.txt
│
└── README.md # Project documentation

🚀 Getting Started
Follow these steps to set up the project locally.

✅ Prerequisites
Node.js v18+
Python 3.10+
pip & virtualenv
🔧 Installation

Clone the repository
git clone https://github.com/[your-username]/legal-analyzer.git

cd legal-analyzer

Frontend setup
cd frontend
npm install

Backend setup
cd ../backend
python -m venv venv
.\venv\Scripts\activate # Windows

# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
Environment variables
Copy .env.example to .env (backend) and .env.local (frontend)
Add your API keys, DB credentials, etc.

▶️ Usage

Run frontend
cd frontend
npm run dev
Access at: http://localhost:5173

Run backend
cd backend
uvicorn main:app --reload
Access API docs at: http://localhost:8000/docs

🧪 Testing
This section outlines the testing strategy for the project.

### Frontend Testing
A manual testing plan is in place to ensure the quality of the user interface and experience.

- [ ] **UI/UX Testing:** The application's design is intuitive and visually consistent.
- [ ] **Page Loading:** All pages load correctly without errors.
- [ ] **Responsiveness:** The responsive design works as expected on mobile, tablet, and desktop screen sizes.
- [ ] **Navigation:** Navigation between pages is seamless.
- [ ] **Form Validation:** Forms correctly validate user input and provide clear feedback.
- [ ] **Loading States:** Loading indicators are displayed properly during data fetching or processing.
- [ ] **Error Messages:** Error messages are user-friendly and informative.

### Backend Testing
The backend is tested using pytest to ensure API reliability and data integrity.

- [ ] **API Endpoint Tests:** All endpoints return correct status codes and payloads.
- [ ] **Data Validation:** Input data is correctly validated by Pydantic models.
- [ ] **Service Logic:** Business logic in services is tested for correctness.
- [ ] **Error Handling:** API errors are handled gracefully and return informative messages.

🤝 Contributing

Contributions are welcome 🎉

Fork the repo
Create a feature branch (git checkout -b feature/xyz)
Commit changes (git commit -m "Add xyz feature")
Push and open a PR

📜 License
This project is licensed under the MIT License. See the LICENSE
file for details.

🔮 Roadmap

Add user authentication (JWT / OAuth)
Multi-language document support
Advanced clause extraction (e.g., GDPR, contracts)
Cloud storage integration (AWS S3, GCP)
Role-based access (Admin, Lawyer, Client)
