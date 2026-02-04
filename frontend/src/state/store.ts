import { create } from "zustand";

export type ProjectStatus =
  | "CREATED"
  | "INDEXING"
  | "READY"
  | "OUTDATED"
  | "REGENERATING";

export type AnswerStatus =
  | "GENERATED"
  | "CONFIRMED"
  | "REJECTED"
  | "MANUAL_UPDATED"
  | "MISSING_DATA";

export type RequestStatus = "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED";

export interface Citation {
  document_id: string;
  page_number: number;
  chunk_id: string;
  snippet: string;
  score: number;
}

export interface AnswerPayload {
  answer: string;
  answerable: boolean;
  answerability_statement?: string;
  confidence: number;
  citations: Citation[];
}

export interface AnswerRecord {
  id: string;
  question_id: string;
  status: AnswerStatus;
  ai_answer?: AnswerPayload | null;
  manual_answer?: AnswerPayload | null;
  updated_at: string;
}

export interface QuestionRecord {
  id: string;
  section_title: string;
  order: number;
  prompt: string;
  answer?: AnswerRecord | null;
}

export interface ProjectRecord {
  id: string;
  name: string;
  status: ProjectStatus;
  scope: string[];
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends ProjectRecord {
  questions: QuestionRecord[];
}

export interface RequestRecord {
  id: string;
  status: RequestStatus;
  detail?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EvaluationResult {
  id: string;
  project_id: string;
  metrics: Array<{
    question_id: string;
    score: number;
    ai_answer: string;
    manual_answer: string;
  }>;
  summary: {
    average_score: number;
    question_count: number;
  };
  created_at: string;
}

export type TabKey =
  | "projects"
  | "details"
  | "review"
  | "documents"
  | "evaluation"
  | "requests";

interface AppState {
  activeTab: TabKey;
  setActiveTab: (tab: TabKey) => void;
  projects: ProjectRecord[];
  addProject: (project: ProjectRecord) => void;
  documents: Array<{ id: string; name: string; request_id?: string }>;
  addDocument: (doc: { id: string; name: string; request_id?: string }) => void;
  setDocuments: (docs: Array<{ id: string; name: string; request_id?: string }>) => void;
  lastRequest?: string;
  setLastRequest: (id?: string) => void;
  currentProject?: ProjectDetail;
  setCurrentProject: (project?: ProjectDetail) => void;
  requests: RequestRecord[];
  setRequests: (requests: RequestRecord[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: "projects",
  setActiveTab: (tab) => set({ activeTab: tab }),
  projects: [],
  addProject: (project) =>
    set((state) => ({
      projects: [project, ...state.projects.filter((item) => item.id !== project.id)],
    })),
  documents: [],
  addDocument: (doc) =>
    set((state) => ({
      documents: [doc, ...state.documents.filter((item) => item.id !== doc.id)],
    })),
  setDocuments: (docs) => set({ documents: docs }),
  lastRequest: undefined,
  setLastRequest: (id) => set({ lastRequest: id }),
  currentProject: undefined,
  setCurrentProject: (project) => set({ currentProject: project }),
  requests: [],
  setRequests: (requests) => set({ requests }),
}));
