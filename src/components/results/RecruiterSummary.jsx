import '../../styles/RecruiterSummary.css'

function RecruiterSummary({ summary, candidateName }) {
  return (
    <div className="result-card recruiter-summary">
      <h3>📝 Recruiter Summary</h3>

      {summary.executive_summary && (
        <div className="summary-box">
          <h4>Executive Summary</h4>
          <p>{summary.executive_summary}</p>
        </div>
      )}

      {summary.key_highlights && summary.key_highlights.length > 0 && (
        <div className="highlights-box">
          <h4>Key Highlights</h4>
          <ul className="highlights-list">
            {summary.key_highlights.map((highlight, idx) => (
              <li key={idx}>{highlight}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.recommendation && (
        <div className={`recommendation-box ${summary.recommendation.toLowerCase()}`}>
          <h4>Recommendation</h4>
          <div className="recommendation-content">
            <span className={`recommendation-badge ${summary.recommendation.toLowerCase()}`}>
              {summary.recommendation}
            </span>
            {summary.recommendation_reason && (
              <p className="recommendation-reason">{summary.recommendation_reason}</p>
            )}
          </div>
        </div>
      )}

      {summary.interview_complexity && (
        <div className="complexity-box">
          <h4>Interview Complexity Level</h4>
          <span className="complexity-badge">{summary.interview_complexity}</span>
        </div>
      )}

      {summary.next_steps && summary.next_steps.length > 0 && (
        <div className="next-steps-box">
          <h4>Next Steps</h4>
          <ol className="next-steps-list">
            {summary.next_steps.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {summary.expected_salary_range_note && (
        <div className="salary-box">
          <h4>Salary Information</h4>
          <p>{summary.expected_salary_range_note}</p>
        </div>
      )}
    </div>
  )
}

export default RecruiterSummary
