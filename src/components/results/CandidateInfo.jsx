import '../../styles/CandidateInfo.css'

function CandidateInfo({ candidate }) {
  return (
    <div className="result-card candidate-info">
      <h3>👤 Candidate Information</h3>
      <div className="candidate-details">
        <div className="detail-row">
          <span className="detail-label">Name:</span>
          <span className="detail-value">{candidate.name || 'N/A'}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Email:</span>
          <span className="detail-value">{candidate.email || 'N/A'}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Phone:</span>
          <span className="detail-value">{candidate.phone || 'N/A'}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Education:</span>
          <span className="detail-value">{candidate.education || 'N/A'}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Experience:</span>
          <span className="detail-value">
            {candidate.experience_years ? `${candidate.experience_years} years` : 'N/A'}
          </span>
        </div>

        {candidate.skills && candidate.skills.length > 0 && (
          <div className="skills-section">
            <h4>🛠️ Skills</h4>
            <div className="tags">
              {candidate.skills.map((skill, idx) => (
                <span key={idx} className="tag skill">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {candidate.strengths && candidate.strengths.length > 0 && (
          <div className="strengths-section">
            <h4>💪 Strengths</h4>
            <div className="tags">
              {candidate.strengths.map((strength, idx) => (
                <span key={idx} className="tag strength">
                  {strength}
                </span>
              ))}
            </div>
          </div>
        )}

        {candidate.certifications && candidate.certifications.length > 0 && (
          <div className="certifications-section">
            <h4>🏆 Certifications</h4>
            <div className="tags">
              {candidate.certifications.map((cert, idx) => (
                <span key={idx} className="tag certification">
                  {cert}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CandidateInfo
