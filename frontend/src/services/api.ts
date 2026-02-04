export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const headers = {
  Accept: "application/json",
};

async function handleJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getProjectInfo(projectId: string) {
  const response = await fetch(`${API_URL}/get-project-info?project_id=${projectId}`, { headers });
  return handleJson(response);
}

export async function getProjectStatus(projectId: string) {
  const response = await fetch(`${API_URL}/get-project-status?project_id=${projectId}`, { headers });
  return handleJson(response);
}

export async function listProjects() {
  const response = await fetch(`${API_URL}/list-projects`, { headers });
  return handleJson(response);
}

export async function createProject(payload: {
  name: string;
  scope: string[];
  questionnaire: File;
}) {
  const formData = new FormData();
  formData.append("name", payload.name);
  formData.append("scope", JSON.stringify(payload.scope));
  formData.append("questionnaire", payload.questionnaire);
  const response = await fetch(`${API_URL}/create-project-async`, {
    method: "POST",
    body: formData,
  });
  return handleJson(response);
}

export async function indexDocument(payload: {
  name: string;
  metadata: Record<string, unknown>;
  file: File;
}) {
  const formData = new FormData();
  formData.append("name", payload.name);
  formData.append("metadata", JSON.stringify(payload.metadata));
  formData.append("file", payload.file);
  const response = await fetch(`${API_URL}/index-document-async`, {
    method: "POST",
    body: formData,
  });
  return handleJson(response);
}

export async function listDocuments() {
  const response = await fetch(`${API_URL}/list-documents`, { headers });
  return handleJson(response);
}

export async function generateAllAnswers(projectId: string) {
  const response = await fetch(`${API_URL}/generate-all-answers`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId }),
  });
  return handleJson(response);
}

export async function generateSingleAnswer(projectId: string, questionId: string) {
  const response = await fetch(`${API_URL}/generate-single-answer`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId, question_id: questionId }),
  });
  return handleJson(response);
}

export async function updateProject(projectId: string, scope: string[]) {
  const response = await fetch(`${API_URL}/update-project-async`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId, scope }),
  });
  return handleJson(response);
}

export async function updateAnswer(payload: {
  answer_id: string;
  status: string;
  manual_answer?: {
    answer: string;
    answerable: boolean;
    answerability_statement?: string;
    confidence: number;
    citations: any[];
  };
}) {
  const response = await fetch(`${API_URL}/update-answer`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleJson(response);
}

export async function getRequestStatus(requestId: string) {
  const response = await fetch(`${API_URL}/get-request-status?request_id=${requestId}`, { headers });
  return handleJson(response);
}

export async function listRequests() {
  const response = await fetch(`${API_URL}/list-requests`, { headers });
  return handleJson(response);
}

export async function evaluateProject(projectId: string) {
  const response = await fetch(`${API_URL}/evaluate-project-async?project_id=${projectId}`, {
    method: "POST",
    headers,
  });
  return handleJson(response);
}

export async function getEvaluation(evaluationId: string) {
  const response = await fetch(`${API_URL}/get-evaluation?evaluation_id=${evaluationId}`, { headers });
  return handleJson(response);
}

export async function listEvaluations(projectId: string) {
  const response = await fetch(`${API_URL}/list-evaluations?project_id=${projectId}`, { headers });
  return handleJson(response);
}

export async function createChatSession() {
  const response = await fetch(`${API_URL}/create-chat-session`, {
    method: "POST",
    headers,
  });
  return handleJson(response);
}

export async function listChatSessions() {
  const response = await fetch(`${API_URL}/list-chat-sessions`, { headers });
  return handleJson(response);
}

export async function sendChatMessage(payload: { session_id?: string; message: string }) {
  const response = await fetch(`${API_URL}/chat-message-async`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleJson(response);
}

export async function listChatMessages(sessionId: string) {
  const response = await fetch(`${API_URL}/list-chat-messages?session_id=${sessionId}`, { headers });
  return handleJson(response);
}
