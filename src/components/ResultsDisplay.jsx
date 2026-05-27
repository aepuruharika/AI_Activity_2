import { useState } from 'react'
import CandidateInfo from './results/CandidateInfo'
import MatchScore from './results/MatchScore'
import InterviewQuestions from './results/InterviewQuestions'
import RejectionFeedback from './results/RejectionFeedback'
import RecruiterSummary from './results/RecruiterSummary'
import '../styles/ResultsDisplay.css'

function ResultsDisplay({ results, onReset }) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState('')

  if (!results) return null

  const { extracted_resume, analysis, recruiter_summary, candidate_name, job_title } = results
  const isQualified = analysis.is_qualified || analysis.match_score > 70

  const handleDownloadPDF = async () => {
    setIsDownloading(true)
    setDownloadError('')

    try {
      const response = await fetch('http://localhost:8006/api/download-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_name,
          job_title,
          extracted_resume,
          analysis,
          recruiter_summary
        })
      })

      if (!response.ok) {
        throw new Error('Failed to download PDF')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `Resume_Screening_${candidate_name.replace(/\s+/g, '_')}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setDownloadError('Failed to download PDF. Please try again.')
      console.error('PDF download error:', err)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="results-container">
      <h2>📊 Analysis Results</h2>

      <CandidateInfo candidate={extracted_resume} />

      <MatchScore analysis={analysis} jobTitle={job_title} />

      {isQualified && analysis.interview_questions && analysis.interview_questions.length > 0 && (
        <InterviewQuestions questions={analysis.interview_questions} />
      )}

      {!isQualified && (
        <RejectionFeedback
          reasons={analysis.rejection_reasons}
          suggestions={analysis.improvement_suggestions}
        />
      )}

      <RecruiterSummary summary={recruiter_summary} candidateName={candidate_name} />

      <div className="action-buttons">
        <button
          className="btn-download-pdf"
          onClick={handleDownloadPDF}
          disabled={isDownloading}
        >
          {isDownloading ? '📥 Downloading...' : '📥 Download Summary as PDF'}
        </button>

        <button className="btn-reset" onClick={onReset}>
          Analyze Another Resume
        </button>
      </div>

      {downloadError && (
        <div className="download-error">
          ❌ {downloadError}
        </div>
      )}
    </div>
  )
}

export default ResultsDisplay
