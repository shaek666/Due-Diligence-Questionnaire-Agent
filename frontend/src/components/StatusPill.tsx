import { ProjectStatus, RequestStatus, AnswerStatus } from "../state/store";

const statusClassMap: Record<string, string> = {
  READY: "ready",
  OUTDATED: "outdated",
};

export default function StatusPill({ status }: { status: ProjectStatus | RequestStatus | AnswerStatus }) {
  const className = statusClassMap[status] ?? "";
  return <span className={`status-pill ${className}`}>{status}</span>;
}
