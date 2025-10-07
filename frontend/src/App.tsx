import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import AnalysisReportSkeleton from './components/AnalysisReportSkeleton';
import ConfirmationDialog from './components/ConfirmationDialog';
import { analyzeDocument, exportAnalysis, viewOriginalDocument, getSupportedFormats, AnalysisResult, SupportedFormats, ApiError, clearHistory } from './api/api';

const Header = () => (
  <header className="bg-base-200/80 backdrop-blur-lg sticky top-0 z-10 border-b border-base-300">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-primary rounded-lg shadow-md">
          <FileText className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-200 tracking-tight">Legal Document Analyzer</h1>
          <p className="text-neutral text-sm">AI-Powered Document Insights</p>
        </div>
      </div>
    </div>
  </header>
);

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null);
  const [originalFileId, setOriginalFileId] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    const fetchSupportedFormats = async () => {
      try {
        const formats = await getSupportedFormats();
        setSupportedFormats(formats);
      } catch (error) {
        console.error("Failed to fetch supported formats:", error);
        setError({ message: "Could not connect to the backend. Please ensure it's running." });
      }
    };
    fetchSupportedFormats();
  }, []);

  const handleFileSelect = (file: File | null) => {
    setError(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!supportedFormats) {
      setError({ message: "Supported formats not loaded yet. Please try again." });
      return;
    }

    const allowedExtensions = supportedFormats.formats.map(f => `.${f.toLowerCase()}`);
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

    const isValidExtension = allowedExtensions.includes(fileExtension);

    if (isValidExtension) {
      setSelectedFile(file);
    } else {
      setError({ message: `Unsupported file type. Please select one of: ${allowedExtensions.join(', ')}` });
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setError(null);
    setUploadProgress(0);
    try {
      const result = await analyzeDocument(selectedFile, setUploadProgress);
      setAnalysis(result);
      setOriginalFileId(result.file_id??null);
    } catch (err: unknown) {
      console.error("Analysis error:", err);
      setError({ message: "Analysis failed. This could be due to a server issue or a problem with the document. Please try again." });
    } finally {
      setIsAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const handleExport = async (format: 'pdf' | 'json') => {
    if (!originalFileId) return;
    try {
      await exportAnalysis(originalFileId, format);
    } catch (err: unknown) {
      console.error(`Export error for ${format}:`, err);
      setError({ message: `Failed to export the ${format} report. Please try again later.` });
    }
  };

  const handleViewOriginal = async () => {
    if (!originalFileId) return;
    try {
      await viewOriginalDocument(originalFileId);
    } catch (err: unknown) {
      console.error("View original error:", err);
      setError({ message: "Could not load the original document. Please try again later." });
    }
  };

  const handleClearHistory = () => {
    if (analysis) {
      setShowConfirmation(true);
    } else {
      reset();
    }
  };

  const reset = async () => {
    try {
      await clearHistory();
    } catch (error) {
      console.error("Failed to clear history:", error);
      setError({ message: "Failed to clear history. Please try again later." });
    }
    setSelectedFile(null);
    setAnalysis(null);
    setError(null);
    setOriginalFileId(null);
    setShowConfirmation(false);
  };

  return (
    <div className="min-h-screen bg-base-100 text-gray-300 font-sans">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isAnalyzing ? (
          <AnalysisReportSkeleton />
        ) : analysis ? (
          <Dashboard
            analysis={analysis}
            onExport={handleExport}
            onViewOriginal={handleViewOriginal}
            onClearHistory={handleClearHistory}
            onReset={reset}
            selectedFile={selectedFile}
          />
        ) : (
          <FileUpload 
            onFileSelect={handleFileSelect}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            selectedFile={selectedFile}
            supportedFormats={supportedFormats}
            error={error}
            onErrorClose={() => setError(null)}
            uploadProgress={uploadProgress}
          />
        )}
        {showConfirmation && (
          <ConfirmationDialog 
            message="Starting a new analysis will discard the current results. Are you sure you want to continue?"
            onConfirm={reset}
            onCancel={() => setShowConfirmation(false)}
          />
        )}
      </main>
    </div>
  );
}

export default App;