import { useAppStore } from "./state/store";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import QuestionReview from "./pages/QuestionReview";
import DocumentManagement from "./pages/DocumentManagement";
import EvaluationReport from "./pages/EvaluationReport";
import RequestStatusPage from "./pages/RequestStatus";
import Chat from "./pages/Chat";

const tabs = [
  { key: "projects", label: "Projects" },
  { key: "details", label: "Project Detail" },
  { key: "review", label: "Question Review" },
  { key: "documents", label: "Documents" },
  { key: "evaluation", label: "Evaluation" },
  { key: "requests", label: "Request Status" },
  { key: "chat", label: "Chat" },
] as const;

export default function App() {
  const { activeTab, setActiveTab } = useAppStore();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Makeball / Questionnaire Agent</div>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`nav-button ${activeTab === tab.key ? "active" : ""}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </aside>
      <main className="main">
        <div className="header">
          <div>
            <h1>Due Diligence Workspace</h1>
            <p>Retro control room for ingestion, review, and evaluation.</p>
          </div>
        </div>
        {activeTab === "projects" && <ProjectList />}
        {activeTab === "details" && <ProjectDetail />}
        {activeTab === "review" && <QuestionReview />}
        {activeTab === "documents" && <DocumentManagement />}
        {activeTab === "evaluation" && <EvaluationReport />}
        {activeTab === "requests" && <RequestStatusPage />}
        {activeTab === "chat" && <Chat />}
      </main>
    </div>
  );
}
