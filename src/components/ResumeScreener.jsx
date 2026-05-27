import { useState } from 'react'
import ResumeForm from './ResumeForm'
import ResultsDisplay from './ResultsDisplay'
import '../styles/ResumeScreener.css'

const PROCESSING_STEPS = [
  { id: 1, label: 'Uploading resume', icon: '📤' },
  { id: 2, label: 'Extracting information', icon: '📋' },
  { id: 3, label: 'Analyzing job match', icon: '🔍' },
  { id: 4, label: 'Generating insights', icon: '✨' },
  { id: 5, label: 'Preparing report', icon: '📊' },
]

function ResumeScreener() {
  const [state, setState] = useState('form')
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [completedSteps, setCompletedSteps] = useState([])
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (formData) => {
    setState('processing')
    setCurrentStepIndex(0)
    setCompletedSteps([])

    try {
      // Simulate step progression with varying durations
      const stepDurations = [800, 1200, 1500, 1200, 800]

      for (let i = 0; i < PROCESSING_STEPS.length; i++) {
        setCurrentStepIndex(i)
        await new Promise(resolve => setTimeout(resolve, stepDurations[i]))
        setCompletedSteps(prev => [...prev, PROCESSING_STEPS[i].id])
      }

      // Make actual API call
      const submitFormData = new FormData()
      submitFormData.append('jobTitle', formData.jobTitle)
      submitFormData.append('resumeFile', formData.resumeFile)
      submitFormData.append('jobDescription', formData.jobDescription)
      submitFormData.append('userConsent', true)

      const response = await fetch('http://localhost:8006/api/screen-resume', {
        method: 'POST',
        body: submitFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to screen resume')
      }

      const data = await response.json()
      setResults(data)
      setState('results')
    } catch (err) {
      setError(err.message || 'Unknown error occurred')
      setState('error')
    }
  }

  const handleReset = () => {
    setState('form')
    setResults(null)
    setError('')
    setCurrentStepIndex(0)
    setCompletedSteps([])
  }

  return (
    <div className="screener-wrapper">
      <header className="screener-header">
        <div className="header-content">
          <h1>Resume Screening</h1>
          <p className="subtitle">Evaluate candidates with AI-powered insights</p>
        </div>
      </header>

      <main className="screener-main">
        {state === 'form' && <ResumeForm onSubmit={handleSubmit} />}

        {state === 'processing' && (
          <div className="processing-container">
            <div className="processing-card">
              <div className="processing-header">
                <h2>Processing application</h2>
                <p>Analyzing resume and matching with job requirements</p>
              </div>

              <div className="progress-visualization">
                <div className="steps-grid">
                  {PROCESSING_STEPS.map((step, idx) => {
                    const isCompleted = completedSteps.includes(step.id)
                    const isCurrent = idx === currentStepIndex
                    const isPending = idx > currentStepIndex

                    return (
                      <div
                        key={step.id}
                        className={`step-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'active' : ''} ${isPending ? 'pending' : ''}`}
                      >
                        <div className="step-indicator">
                          {isCompleted ? (
                            <div className="step-icon completed-icon">
                              <span>✓</span>
                            </div>
                          ) : isCurrent ? (
                            <div className="step-icon active-icon">
                              <div className="pulse-ring"></div>
                              <span className="step-number">{idx + 1}</span>
                            </div>
                          ) : (
                            <div className="step-icon pending-icon">
                              <span className="step-number">{idx + 1}</span>
                            </div>
                          )}
                        </div>
                        <div className="step-details">
                          <p className="step-label">{step.label}</p>
                          <p className="step-icon-text">{step.icon}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="progress-bar-section">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${Math.min(((completedSteps.length + (currentStepIndex > 0 ? 0.5 : 0)) / PROCESSING_STEPS.length) * 100, 100)}%`,
                      }}
                    ></div>
                  </div>
                  <div className="progress-stats">
                    <span className="progress-text">
                      {completedSteps.length} of {PROCESSING_STEPS.length} completed
                    </span>
                    <span className="progress-percent">
                      {Math.min(Math.round(((completedSteps.length + (currentStepIndex > 0 ? 0.5 : 0)) / PROCESSING_STEPS.length) * 100), 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="processing-footer">
                <p className="processing-message">
                  {currentStepIndex < PROCESSING_STEPS.length
                    ? `Processing: ${PROCESSING_STEPS[currentStepIndex].label}`
                    : 'Finalizing results...'}
                </p>
              </div>
            </div>
          </div>
        )}

        {state === 'results' && results && (
          <ResultsDisplay results={results} onReset={handleReset} />
        )}

        {state === 'error' && (
          <div className="error-container">
            <div className="error-card">
              <div className="error-icon">⚠️</div>
              <h2>Unable to process application</h2>
              <p className="error-message">{error}</p>
              <button className="btn-error-reset" onClick={handleReset}>
                Try again
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default ResumeScreener
