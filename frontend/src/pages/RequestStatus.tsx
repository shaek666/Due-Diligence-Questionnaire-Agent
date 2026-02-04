import { useState } from "react";
import { getRequestStatus, listRequests } from "../services/api";
import StatusPill from "../components/StatusPill";
import { useAppStore } from "../state/store";

export default function RequestStatusPage() {
  const { lastRequest, requests, setRequests } = useAppStore();
  const [requestId, setRequestId] = useState(lastRequest ?? "");
  const [status, setStatus] = useState<any>(null);

  const fetchStatus = async () => {
    if (!requestId) return;
    try {
      const result = await getRequestStatus(requestId);
      setStatus(result);
    } catch (err: any) {
      setStatus({ id: requestId, status: "FAILED", detail: err.message ?? "Failed to fetch status" });
    }
  };

  const refreshRequests = async () => {
    const result = await listRequests();
    setRequests(result as any[]);
  };

  return (
    <div>
      <div className="panel">
        <h2>Request Status</h2>
        <div className="grid two">
          <label className="field">
            Request ID
            <input value={requestId} onChange={(event) => setRequestId(event.target.value)} />
          </label>
        </div>
        <div className="actions">
          <button className="button" onClick={fetchStatus}>
            Fetch Status
          </button>
          <button className="button secondary" onClick={refreshRequests}>
            Refresh List
          </button>
        </div>
      </div>

      {status ? (
        <div className="panel">
          <div className="tag">{status.id}</div>
          <StatusPill status={status.status} />
          <p>{status.detail ?? "No details provided."}</p>
        </div>
      ) : null}

      <div className="panel">
        <h2>Recent Requests</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Request</th>
              <th>Status</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {requests.length === 0 ? (
              <tr>
                <td colSpan={3}>No requests yet.</td>
              </tr>
            ) : (
              requests.map((request) => (
                <tr key={request.id}>
                  <td className="tag">{request.id}</td>
                  <td>
                    <StatusPill status={request.status} />
                  </td>
                  <td>{new Date(request.updated_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
