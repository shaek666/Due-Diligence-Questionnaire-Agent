import { useState } from "react";
import { generateAllAnswers, getProjectInfo } from "../services/api";
import { useAppStore } from "../state/store";
import StatusPill from "../components/StatusPill";

export default function ProjectDetail() {
  const { currentProject, setCurrentProject, setLastRequest } = useAppStore();
  const [projectId, setProjectId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fetchProject = async () => {
    if (!projectId) return;
    try {
      const data = await getProjectInfo(projectId);
      setCurrentProject(data);
      setError(null);
    } catch (err: any) {
      setError(err.message ?? "Failed to load project.");
    }
  };

  const triggerGeneration = async () => {
    if (!currentProject) return;
    try {
      const response = await generateAllAnswers(currentProject.id);
      setLastRequest(response.request_id);
    } catch (err: any) {
      setError(err.message ?? "Failed to trigger generation.");
    }
  };

  return (
    <div>
      <div className="panel">
        <h2>Project Detail</h2>
        {error ? <div className="notice">{error}</div> : null}
        <div className="grid two">
          <label className="field">
            Project ID
            <input value={projectId} onChange={(event) => setProjectId(event.target.value)} />
          </label>
        </div>
        <div className="actions">
          <button className="button" onClick={fetchProject}>
            Load Project
          </button>
          <button className="button secondary" onClick={triggerGeneration} disabled={!currentProject}>
            Generate All Answers
          </button>
        </div>
      </div>

      {currentProject ? (
        <div className="panel">
          <h2>{currentProject.name}</h2>
          <div className="notice">
            <div className="tag">{currentProject.id}</div>
            <StatusPill status={currentProject.status} />
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Section</th>
                <th>Question</th>
                <th>Answer</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {currentProject.questions.length === 0 ? (
                <tr>
                  <td colSpan={4}>No questions parsed yet.</td>
                </tr>
              ) : (
                currentProject.questions.map((question) => (
                  <tr key={question.id}>
                    <td>{question.section_title}</td>
                    <td>{question.prompt}</td>
                    <td>{question.answer?.ai_answer?.answer ?? ""}</td>
                    <td>
                      {question.answer?.status ? (
                        <StatusPill status={question.answer.status} />
                      ) : (
                        ""
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
