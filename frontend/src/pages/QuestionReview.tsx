import { useMemo, useState } from "react";
import { generateSingleAnswer, updateAnswer } from "../services/api";
import { useAppStore } from "../state/store";

export default function QuestionReview() {
  const { currentProject, setLastRequest } = useAppStore();
  const [questionId, setQuestionId] = useState("");
  const [manualAnswer, setManualAnswer] = useState("");
  const [status, setStatus] = useState("MANUAL_UPDATED");

  const selectedQuestion = useMemo(() => {
    if (!currentProject) return null;
    return currentProject.questions.find((question) => question.id === questionId) ?? null;
  }, [currentProject, questionId]);

  const runSingleAnswer = async () => {
    if (!currentProject || !questionId) return;
    const response = await generateSingleAnswer(currentProject.id, questionId);
    setLastRequest(response.request_id);
  };

  const submitManual = async () => {
    if (!selectedQuestion?.answer?.id) return;
    await updateAnswer({
      answer_id: selectedQuestion.answer.id,
      status,
      manual_answer: {
        answer: manualAnswer,
        answerable: true,
        answerability_statement: "Reviewed manually.",
        confidence: 0.75,
        citations: [],
      },
    });
  };

  return (
    <div>
      <div className="panel">
        <h2>Question Review</h2>
        {!currentProject ? (
          <div className="notice">Load a project first in Project Detail.</div>
        ) : (
          <>
            <label className="field">
              Question
              <select value={questionId} onChange={(event) => setQuestionId(event.target.value)}>
                <option value="">Select a question</option>
                {currentProject.questions.map((question) => (
                  <option key={question.id} value={question.id}>
                    {question.order}. {question.prompt}
                  </option>
                ))}
              </select>
            </label>
            {selectedQuestion ? (
              <div className="panel">
                <div className="tag">AI Answer</div>
                <p>{selectedQuestion.answer?.ai_answer?.answer ?? "No AI answer yet."}</p>
                <div className="grid two">
                  <label className="field">
                    Manual Status
                    <select value={status} onChange={(event) => setStatus(event.target.value)}>
                      <option value="CONFIRMED">CONFIRMED</option>
                      <option value="REJECTED">REJECTED</option>
                      <option value="MANUAL_UPDATED">MANUAL_UPDATED</option>
                      <option value="MISSING_DATA">MISSING_DATA</option>
                    </select>
                  </label>
                </div>
                <label className="field">
                  Manual Answer
                  <textarea value={manualAnswer} onChange={(event) => setManualAnswer(event.target.value)} />
                </label>
                <div className="actions">
                  <button className="button" onClick={runSingleAnswer}>
                    Regenerate Single Answer
                  </button>
                  <button className="button secondary" onClick={submitManual}>
                    Save Manual Update
                  </button>
                </div>
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}
