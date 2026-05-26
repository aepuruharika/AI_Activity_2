import { useState } from 'react'
import ResumeForm from './ResumeForm'
import LoadingState from './LoadingState'
import ResultsDisplay from './ResultsDisplay'
import '../styles/ResumeScreener.css'

function ResumeScreener() {
  const [currentStep, setCurrentStep] = useState('form') // form, loading, results, error
  const [processingStep, setProcessingStep] = useState('')
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (formData) => {
    setCurrentStep('loading')
    setProcessingStep('Step 1/3: Extracting resume information...')

    const submitFormData = new FormData()
    submitFormData.append('jobTitle', formData.jobTitle)
    submitFormData.append('resumeFile', formData.resumeFile)
    submitFormData.append('jobDescription', formData.jobDescription)

    try {
      const response = await fetch('http://localhost:8005/api/screen-resume', {
        method: 'POST',
        body: submitFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to screen resume')
      }

      const data = await response.json()
      setResults(data)
      setCurrentStep('results')
    } catch (err) {
      // Handle error properly
      let errorMsg = err.message || 'Unknown error'
      if (typeof err.message === 'object') {
        errorMsg = JSON.stringify(err.message)
      }
      setError(errorMsg)
      setCurrentStep('error')
      console.error('Full error:', err)
    }
  }

  const handleReset = () => {
    setCurrentStep('form')
    setResults(null)
    setError('')
    setProcessingStep('')
  }

  return (
    <div className="resume-screener">
      <header className="screener-header">
        <h1>🚀 Resume Screening & Interview Generator</h1>
        <p className="subtitle">AI-Powered Resume Analysis with Multi-LLM Orchestration</p>
      </header>

      <main className="screener-main">
        {currentStep === 'form' && <ResumeForm onSubmit={handleSubmit} />}
        {currentStep === 'loading' && <LoadingState step={processingStep} />}
        {currentStep === 'results' && <ResultsDisplay results={results} onReset={handleReset} />}
        {currentStep === 'error' && (
          <div className="error-container">
            <h2>❌ Error</h2>
            <p>{error}</p>
            <button className="btn-reset" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

export default ResumeScreener
