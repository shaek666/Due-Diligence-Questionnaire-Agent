import { useEffect, useState } from "react";
import { useAppStore } from "../state/store";
import {
  createChatSession,
  listChatMessages,
  listChatSessions,
  sendChatMessage,
  getRequestStatus,
} from "../services/api";

export default function Chat() {
  const {
    chatSessionId,
    setChatSessionId,
    chatMessages,
    setChatMessages,
    setLastRequest,
  } = useAppStore();
  const [input, setInput] = useState("");
  const [sessions, setSessions] = useState<Array<{ id: string; created_at: string }>>([]);
  const [loading, setLoading] = useState(false);

  const refreshSessions = async () => {
    const data = await listChatSessions();
    setSessions(data);
  };

  const refreshMessages = async (sessionId: string) => {
    const data = await listChatMessages(sessionId);
    setChatMessages(data);
  };

  useEffect(() => {
    refreshSessions();
  }, []);

  useEffect(() => {
    if (chatSessionId) {
      refreshMessages(chatSessionId);
    }
  }, [chatSessionId]);

  const handleNewSession = async () => {
    const session = await createChatSession();
    setChatSessionId(session.id);
    setChatMessages([]);
    await refreshSessions();
  };

  const handleSend = async () => {
    const message = input.trim();
    if (!message) return;
    setLoading(true);
    setInput("");
    const response = await sendChatMessage({ session_id: chatSessionId, message });
    setChatSessionId(response.session_id);
    setLastRequest(response.request_id);
    await refreshSessions();
    // Poll until complete
    for (let attempt = 0; attempt < 60; attempt += 1) {
      const status = await getRequestStatus(response.request_id);
      if (status.status === "SUCCEEDED" || status.status === "FAILED") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
    await refreshMessages(response.session_id);
    setLoading(false);
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Chat Console</h2>
        <p>Read-only Q&A against indexed documents with citations.</p>
      </div>
      <div className="card">
        <div className="field">
          <label>Session</label>
          <div className="row">
            <select
              value={chatSessionId ?? ""}
              onChange={(event) => setChatSessionId(event.target.value || undefined)}
            >
              <option value="">New session</option>
              {sessions.map((session) => (
                <option key={session.id} value={session.id}>
                  {session.id.slice(0, 8)} · {new Date(session.created_at).toLocaleString()}
                </option>
              ))}
            </select>
            <button className="button" onClick={handleNewSession}>
              New Session
            </button>
          </div>
        </div>
      </div>
      <div className="chat-box">
        {chatMessages.length === 0 && <div className="muted">No messages yet.</div>}
        {chatMessages.map((message) => (
          <div key={message.id} className={`chat-message ${message.role}`}>
            <div className="chat-role">{message.role.toUpperCase()}</div>
            <div className="chat-content">{message.content}</div>
            {message.answer_payload?.citations?.length ? (
              <div className="chat-citations">
                {message.answer_payload.citations.map((citation, idx) => (
                  <div key={`${message.id}-${idx}`} className="citation">
                    p.{citation.page_number} · score {citation.score.toFixed(2)}
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        ))}
      </div>
      <div className="card">
        <div className="field">
          <label>Message</label>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about the indexed documents..."
          />
        </div>
        <button className="button" onClick={handleSend} disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </section>
  );
}
