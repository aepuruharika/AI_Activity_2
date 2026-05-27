import { useState, useEffect } from 'react'
import '../styles/PIIConsent.css'

function PIIConsent({ onConsentGiven, onDecline }) {
  const [disclosure, setDisclosure] = useState(null)
  const [agreed, setAgreed] = useState(false)

  useEffect(() => {
    // Fetch disclosure info from backend
    fetch('http://localhost:8006/api/pii-disclosure')
      .then(res => res.json())
      .then(data => setDisclosure(data))
      .catch(err => console.error('Failed to fetch disclosure:', err))
  }, [])

  const handleAgree = () => {
    if (!agreed) {
      alert('You must read and agree to continue')
      return
    }

    // Record consent on backend
    fetch('http://localhost:8006/api/consent/record', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'user_consent=true'
    })
      .then(res => res.json())
      .then(() => onConsentGiven(true))
      .catch(err => console.error('Failed to record consent:', err))
  }

  if (!disclosure) return <div className="pii-loading">Loading privacy policy...</div>

  const { data_sent_to_llm, data_not_sent, data_retention, why_needed } = disclosure.disclosure

  return (
    <div className="pii-consent-overlay">
      <div className="pii-consent-card">
        <h2>🔒 Screening Privacy Notice</h2>
        <p className="pii-subtitle">Candidate screening uses AI. Here's how we handle data:</p>

        <div className="pii-section pii-sent">
          <h3>✅ Data Shared with AI</h3>
          <ul className="pii-list">
            {data_sent_to_llm.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
          <p className="pii-note">
            Processed by: <strong>HuggingFace Llama 3.1</strong> ({' '}
            <a href={data_sent_to_llm.privacy_link} target="_blank" rel="noopener noreferrer">
              Privacy Policy
            </a>
            )
          </p>
        </div>

        <div className="pii-section pii-not-sent">
          <h3>❌ Data NOT Shared</h3>
          <ul className="pii-list">
            {data_not_sent.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="pii-section pii-retention">
          <h3>🗑️ Data Retention</h3>
          <p>{data_retention}</p>
        </div>

        <div className="pii-section pii-why">
          <h3>❓ Why This Data?</h3>
          <p>{why_needed}</p>
        </div>

        <label className="pii-agree-checkbox">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
          />
          <span>
            I understand this screening uses HuggingFace AI. Candidate data is anonymized before processing.
          </span>
        </label>

        <div className="pii-actions">
          <button className="pii-btn-decline" onClick={onDecline}>
            Cancel
          </button>
          <button
            className="pii-btn-agree"
            onClick={handleAgree}
            disabled={!agreed}
          >
            Proceed with Screening
          </button>
        </div>
      </div>
    </div>
  )
}

export default PIIConsent
