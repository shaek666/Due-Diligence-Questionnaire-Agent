import { useState } from "react";
import { evaluateProject, listEvaluations } from "../services/api";
import { exportCsv, exportExcel } from "../utils/export";
import { EvaluationResult } from "../state/store";

export default function EvaluationReport() {
  const [projectId, setProjectId] = useState("");
  const [runs, setRuns] = useState<EvaluationResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const runEvaluation = async () => {
    if (!projectId) return;
    try {
      await evaluateProject(projectId);
      await refreshRuns();
    } catch (err: any) {
      setError(err.message ?? "Failed to run evaluation");
    }
  };

  const refreshRuns = async () => {
    if (!projectId) return;
    const result = await listEvaluations(projectId);
    setRuns(result as EvaluationResult[]);
  };

  const exportRun = (run: EvaluationResult, format: "csv" | "xlsx") => {
    const rows = [
      ["Question ID", "Score", "AI Answer", "Manual Answer"],
      ...run.metrics.map((metric) => [
        metric.question_id,
        metric.score.toFixed(3),
        metric.ai_answer,
        metric.manual_answer,
      ]),
    ];
    if (format === "csv") {
      exportCsv(`evaluation-${run.id}.csv`, rows);
    } else {
      exportExcel(`evaluation-${run.id}.xlsx`, rows);
    }
  };

  return (
    <div>
      <div className="panel">
        <h2>Evaluation Report</h2>
        {error ? <div className="notice">{error}</div> : null}
        <div className="grid two">
          <label className="field">
            Project ID
            <input value={projectId} onChange={(event) => setProjectId(event.target.value)} />
          </label>
        </div>
        <div className="actions">
          <button className="button" onClick={runEvaluation}>
            Run Evaluation
          </button>
          <button className="button secondary" onClick={refreshRuns}>
            Refresh Runs
          </button>
        </div>
      </div>

      <div className="panel">
        <h2>Evaluation Runs</h2>
        {runs.length === 0 ? (
          <div className="notice">No evaluation runs yet.</div>
        ) : (
          runs.map((run) => (
            <div key={run.id} className="panel">
              <div className="tag">Run ID: {run.id}</div>
              <p>
                Average score: {run.summary.average_score.toFixed(3)} ({run.summary.question_count} questions)
              </p>
              <div className="actions">
                <button className="button secondary" onClick={() => exportRun(run, "csv")}>
                  Export CSV
                </button>
                <button className="button secondary" onClick={() => exportRun(run, "xlsx")}>
                  Export Excel
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
