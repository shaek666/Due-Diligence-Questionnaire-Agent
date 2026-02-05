import { useState } from "react";
import { indexDocument, listDocuments } from "../services/api";
import { useAppStore } from "../state/store";

export default function DocumentManagement() {
  const { documents, addDocument, setDocuments, setLastRequest } = useAppStore();
  const [name, setName] = useState("");
  const [metadata, setMetadata] = useState("{}");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) {
      setError("Document file is required.");
      return;
    }
    setError(null);
    let parsed: Record<string, unknown> = {};
    try {
      parsed = metadata ? JSON.parse(metadata) : {};
    } catch {
      setError("Metadata must be valid JSON.");
      return;
    }
    try {
      const response = await indexDocument({ name: name || file.name, metadata: parsed, file });
      setLastRequest(response.request_id);
      if (response.deduped) {
        setError("Duplicate document detected; existing record reused.");
      }
      addDocument({ id: response.document_id, name: name || file.name, request_id: response.request_id });
    } catch (err: any) {
      setError(err.message ?? "Failed to upload document.");
    }
  };

  const refreshDocuments = async () => {
    try {
      const result = await listDocuments();
      setDocuments((result as any[]).map((doc) => ({ id: doc.id, name: doc.name })));
    } catch (err: any) {
      setError(err.message ?? "Failed to refresh documents.");
    }
  };

  return (
    <div>
      <div className="panel">
        <h2>Document Management</h2>
        {error ? <div className="notice">{error}</div> : null}
        <div className="grid two">
          <label className="field">
            Document name
            <input value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="field">
            Metadata (JSON)
            <input value={metadata} onChange={(event) => setMetadata(event.target.value)} />
          </label>
          <label className="field">
            File
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
        </div>
        <div className="actions">
          <button className="button" onClick={handleUpload}>
            Upload & Index
          </button>
          <button className="button secondary" onClick={refreshDocuments}>
            Refresh List
          </button>
        </div>
      </div>

      <div className="panel">
        <h2>Recently Uploaded</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Request ID</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan={2}>No documents uploaded yet.</td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.name}</td>
                  <td className="tag">{doc.request_id ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
