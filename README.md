# Legal Document Analyzer

## Overview

Legal Analyzer is a full-stack web application designed to simplify the analysis of legal documents. It enables users (lawyers, students, businesses, or individuals) to upload contracts, policies, or case files and receive AI-powered insights, OCR text extraction, and structured reports. The project combines a modern frontend built with React and a high-performance backend powered by FastAPI.

## Key Features

*   **Secure Document Upload & Management**: Upload PDFs and images securely.
*   **OCR & Text Extraction**: Utilizes PyMuPDF and Tesseract to extract text from scanned files.
*   **AI-Powered Analysis**: Leverages OpenRouter with GPT-4-mini for document summarization, clause detection, and risk spotting.
*   **Interactive Dashboard**: View extracted insights and visualizations in real-time.
*   **Report Exporting**: Generate analysis reports in both PDF and JSON formats.
*   **Fast & Scalable**: Built with FastAPI and Vite for a responsive and high-performance experience.
*   **Rate Limiting**: Implemented to prevent abuse and ensure service stability.

## Tech Stack

*   **Frontend**: React, Vite, Tailwind CSS, Axios, Lucide React
*   **Backend**: Python, FastAPI, Uvicorn, Pydantic
*   **AI & OCR**: `openai`, `PyMuPDF`, `pytesseract`, `transformers`, `torch`
*   **API & Networking**: `python-multipart`, `requests`, `httpx`
*   **Tooling**: `eslint`, `postcss`, `pytest`

## Project Structure

```
legal_analyser/
├── backend/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── middleware/
│   ├── tests/
│   ├── .env
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── App.tsx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone <your-repository-url>
    cd legal_analyser
    ```

2.  **Backend Setup**:

    ```bash
    cd backend
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Create `.env` file**:

    *   In the `backend` directory, create a `.env` file by copying `.env.example`.
    *   Add your `OPENROUTER_API_KEY` to the `.env` file.

4.  **Frontend Setup**:

    ```bash
    cd ../frontend
    npm install
    ```

## Running the Application

*   **Backend**:

    ```bash
    cd backend
    python main.py
    ```

    The API will be available at `http://localhost:8000/docs`.

*   **Frontend**:

    ```bash
    cd frontend
    npm run dev
    ```

    The application will be running at `http://localhost:5173`.

## API Endpoints

*   `GET /`: Root endpoint with API information.
*   `GET /health`: Health check for the backend services.
*   `POST /analyze`: Upload a document for analysis.
*   `GET /analysis/{file_id}`: Get the analysis result for a specific file.
*   `POST /export/{file_id}/{format}`: Export the analysis in the specified format (json or pdf).
*   `GET /export/{task_id}`: Get the status of an export task.
*   `GET /supported-formats`: Get the list of supported file formats.
*   `GET /stats`: Get statistics about the service.
*   `DELETE /analyses`: Clear all analysis records.
*   `GET /documents/{file_id}`: Get the original uploaded document.

## Recent Changes

*   **Added New Endpoints**:
    *   `GET /`: Root endpoint with API information.
    *   `GET /stats`: Get statistics about the service.
    *   `DELETE /analyses`: Clear all analysis records.
    *   `GET /documents/{file_id}`: Get the original uploaded document.
*   **Improved Logging**: Implemented structured logging (JSON or text) for better monitoring and debugging.
*   **Enhanced Security**: Added request ID middleware and improved path traversal security for file downloads.
*   **Windows Compatibility**: Added a `if __name__ == "__main__":` block to `backend/main.py` to ensure compatibility with Uvicorn's reloader on Windows.
*   **`.env` File Creation**: Created a `backend/.env` file from the example to facilitate environment variable management.

## Troubleshooting

*   **Connection Errors**: If the frontend cannot connect to the backend, ensure the backend is running on `http://localhost:8000` and that the `ALLOWED_ORIGINS` in `backend/.env` includes `http://localhost:5173`.
*   **Tesseract Not Found**: If you encounter errors related to Tesseract OCR, make sure it is installed on your system and that the path to the executable is correctly configured.
*   **File Upload Issues**: If file uploads are failing, check the browser's developer console for any error messages and ensure the file type is supported by the application.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
