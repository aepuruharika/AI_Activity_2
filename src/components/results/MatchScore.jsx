import '../../styles/MatchScore.css'

function MatchScore({ analysis, jobTitle }) {
  const score = analysis.match_score || 0
  const isQualified = analysis.is_qualified || score > 70

  return (
    <div className={`result-card match-score ${isQualified ? 'qualified' : 'not-qualified'}`}>
      <h3>📈 Match Score & Analysis</h3>
      <div className="score-display">
        <div className="score-number">{score}%</div>
        <div className={`score-status ${isQualified ? 'qualified' : 'not-qualified'}`}>
          {isQualified ? '✓ QUALIFIED' : '✗ NOT QUALIFIED'}
        </div>
      </div>

      <div className="score-bar">
        <div className="score-bar-label">
          <span>Overall Match</span>
          <span>{score}%</span>
        </div>
        <div className="score-bar-container">
          <div className="score-bar-fill" style={{ width: `${score}%` }}></div>
        </div>
      </div>

      {analysis.score_breakdown && (
        <div className="breakdown-section">
          <h4>Score Breakdown</h4>
          <div className="breakdown-items">
            <div className="breakdown-item">
              <span>Skills Match:</span>
              <span className="score">{analysis.score_breakdown.skills_match || 0}%</span>
            </div>
            <div className="breakdown-item">
              <span>Experience Match:</span>
              <span className="score">{analysis.score_breakdown.experience_match || 0}%</span>
            </div>
            <div className="breakdown-item">
              <span>Education Match:</span>
              <span className="score">{analysis.score_breakdown.education_match || 0}%</span>
            </div>
          </div>
        </div>
      )}

      {analysis.matching_skills && analysis.matching_skills.length > 0 && (
        <div className="skills-match">
          <h4>✓ Matching Skills</h4>
          <div className="tags">
            {analysis.matching_skills.map((skill, idx) => (
              <span key={idx} className="tag matching">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.missing_skills && analysis.missing_skills.length > 0 && (
        <div className="skills-missing">
          <h4>✗ Missing Skills</h4>
          <div className="tags">
            {analysis.missing_skills.map((skill, idx) => (
              <span key={idx} className="tag missing">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.analysis_summary && (
        <div className="analysis-summary">
          <h4>Summary</h4>
          <p>{analysis.analysis_summary}</p>
        </div>
      )}
    </div>
  )
}

export default MatchScore
