import '../../styles/RejectionFeedback.css'

function RejectionFeedback({ reasons, suggestions }) {
  return (
    <div className="result-card rejection-feedback">
      <h3>❌ Feedback & Improvement</h3>

      {reasons && reasons.length > 0 && (
        <div className="rejection-section">
          <h4>Reasons for Not Meeting Requirements</h4>
          <ul className="reasons-list">
            {reasons.map((reason, idx) => (
              <li key={idx} className="reason-item">
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {suggestions && suggestions.length > 0 && (
        <div className="suggestions-section">
          <h4>💡 Improvement Suggestions</h4>
          <ul className="suggestions-list">
            {suggestions.map((suggestion, idx) => (
              <li key={idx} className="suggestion-item">
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default RejectionFeedback
