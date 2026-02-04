import { useState } from "react";
import { createProject, getProjectStatus, listProjects } from "../services/api";
import { useAppStore } from "../state/store";
import StatusPill from "../components/StatusPill";

export default function ProjectList() {
  const { projects, addProject, setLastRequest } = useAppStore();
  const [name, setName] = useState("MiniMax - Due Diligence");
  const [scope, setScope] = useState("[]");
  const [questionnaire, setQuestionnaire] = useState<File | null>(null);
  const [statusId, setStatusId] = useState("");
  const [statusResult, setStatusResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!questionnaire) {
      setError("Questionnaire PDF is required.");
      return;
    }
    setError(null);
    let parsedScope: string[] = [];
    try {
      parsedScope = scope ? JSON.parse(scope) : [];
    } catch {
      setError("Scope must be valid JSON.");
      return;
    }
    try {
      const response = await createProject({ name, scope: parsedScope, questionnaire });
      addProject({
        id: response.project_id,
        name,
        status: "CREATED",
        scope: parsedScope,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      setLastRequest(response.request_id);
    } catch (err: any) {
      setError(err.message ?? "Failed to create project.");
    }
  };

  const fetchStatus = async () => {
    if (!statusId) return;
    try {
      const result = await getProjectStatus(statusId);
      setStatusResult(result);
    } catch (err: any) {
      setError(err.message ?? "Failed to fetch status.");
    }
  };

  const refreshProjects = async () => {
    try {
      const result = await listProjects();
      result.forEach((project: any) => addProject(project));
    } catch (err: any) {
      setError(err.message ?? "Failed to refresh projects.");
    }
  };

  return (
    <div>
      <div className="panel">
        <h2>Create Project</h2>
        {error ? <div className="notice">{error}</div> : null}
        <div className="grid two">
          <label className="field">
            Project name
            <input value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="field">
            Scope (JSON array of document IDs)
            <input value={scope} onChange={(event) => setScope(event.target.value)} />
          </label>
          <label className="field">
            Questionnaire PDF
            <input type="file" accept=".pdf" onChange={(event) => setQuestionnaire(event.target.files?.[0] ?? null)} />
          </label>
        </div>
        <div className="actions">
          <button className="button" onClick={handleCreate}>
            Create Project
          </button>
        </div>
      </div>

      <div className="panel">
        <h2>Project Status Lookup</h2>
        <div className="grid two">
          <label className="field">
            Project ID
            <input value={statusId} onChange={(event) => setStatusId(event.target.value)} />
          </label>
        </div>
        <div className="actions">
          <button className="button secondary" onClick={fetchStatus}>
            Fetch Status
          </button>
          <button className="button secondary" onClick={refreshProjects}>
            Refresh List
          </button>
        </div>
        {statusResult ? (
          <div className="notice">
            <div className="tag">{statusResult.name}</div>
            <StatusPill status={statusResult.status} />
          </div>
        ) : null}
      </div>

      <div className="panel">
        <h2>Known Projects</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Status</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {projects.length === 0 ? (
              <tr>
                <td colSpan={3}>No projects added yet.</td>
              </tr>
            ) : (
              projects.map((project) => (
                <tr key={project.id}>
                  <td>
                    <div>{project.name}</div>
                    <div className="tag">{project.id}</div>
                  </td>
                  <td>
                    <StatusPill status={project.status} />
                  </td>
                  <td>{new Date(project.updated_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
