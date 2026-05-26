import '../../styles/InterviewQuestions.css'

function InterviewQuestions({ questions }) {
  return (
    <div className="result-card interview-questions">
      <h3>🎯 Advanced Technical Interview Questions</h3>
      <p className="interview-intro">
        Based on the strong match, here are advanced technical questions tailored for this candidate:
      </p>
      <ol className="questions-list">
        {questions.map((question, idx) => (
          <li key={idx} className="question-item">
            <span className="question-number">{idx + 1}</span>
            <span className="question-text">{question}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default InterviewQuestions
