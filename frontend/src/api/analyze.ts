// src/api/analyze.ts

// Get demo token for development
const getDemoToken = async (): Promise<string> => {
  const cachedToken = localStorage.getItem('auth_token');
  if (cachedToken) {
    return cachedToken;
  }
  
  try {
    const response = await fetch("http://localhost:8000/demo-token", {
      method: 'POST'
    });
    const data = await response.json();
    const token = data.access_token;
    localStorage.setItem('auth_token', token);
    return token;
  } catch (error) {
    console.error('Failed to get demo token:', error);
    throw error;
  }
};

export async function analyzeDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const token = await getDemoToken();

  const response = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData,
  });

  if (!response.ok) throw new Error("Failed to analyze document");
  return response.json();
}

export async function exportAnalysis(fileId: string, format: "pdf" | "json") {
  const token = await getDemoToken();

  const response = await fetch(`http://localhost:8000/export/${fileId}/${format}`, {
    method: "GET",
    headers: {
      'Authorization': `Bearer ${token}`
    },
  });

  if (!response.ok) throw new Error(`Failed to export ${format}`);

  // For JSON, force file download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `analysis.${format}`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);
}
