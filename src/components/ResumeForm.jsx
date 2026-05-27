import { useState } from 'react'
import '../styles/ResumeForm.css'

function ResumeForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    jobTitle: '',
    resumeFile: null,
    jobDescription: ''
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value, files } = e.target
    if (name === 'resumeFile') {
      setFormData({ ...formData, resumeFile: files[0] })
      if (errors.resumeFile) setErrors({ ...errors, resumeFile: '' })
    } else {
      setFormData({ ...formData, [name]: value })
      if (errors[name]) setErrors({ ...errors, [name]: '' })
    }
  }

  const validateForm = () => {
    const newErrors = {}
    if (!formData.jobTitle.trim()) newErrors.jobTitle = 'Job title is required'
    if (!formData.resumeFile) newErrors.resumeFile = 'Resume file is required'
    if (!formData.jobDescription.trim()) newErrors.jobDescription = 'Job description is required'
    return newErrors
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const newErrors = validateForm()
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    setIsSubmitting(true)
    setErrors({})
    onSubmit(formData)
  }

  return (
    <div className="form-container">
      <div className="form-card">
        <div className="form-header">
          <h2>New Screening</h2>
          <p>Upload a candidate resume and job details for AI-powered matching</p>
        </div>

        <div className="privacy-notice">
          <span className="notice-icon">🔒</span>
          <p>Candidate data is anonymized before processing</p>
        </div>

        <form onSubmit={handleSubmit} className="form-body">
          <div className="form-group">
            <label htmlFor="jobTitle" className="form-label">
              Job Title <span className="required">*</span>
            </label>
            <input
              type="text"
              id="jobTitle"
              name="jobTitle"
              placeholder="e.g., Senior Software Engineer"
              value={formData.jobTitle}
              onChange={handleChange}
              disabled={isSubmitting}
              className="form-input"
            />
            {errors.jobTitle && <span className="error-text">{errors.jobTitle}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="resumeFile" className="form-label">
              Resume File <span className="required">*</span>
            </label>
            <div className="file-upload-section">
              <input
                type="file"
                id="resumeFile"
                name="resumeFile"
                accept=".txt,.pdf"
                onChange={handleChange}
                disabled={isSubmitting}
                className="file-input-hidden"
              />
              <label htmlFor="resumeFile" className="file-upload-label">
                <div className="file-upload-content">
                  {formData.resumeFile ? (
                    <>
                      <div className="file-icon">📄</div>
                      <div className="file-info">
                        <p className="file-name">{formData.resumeFile.name}</p>
                        <p className="file-size">
                          {(formData.resumeFile.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="upload-icon">📁</div>
                      <div className="upload-text">
                        <p className="upload-title">Choose file or drag and drop</p>
                        <p className="upload-hint">TXT or PDF, max 50 MB</p>
                      </div>
                    </>
                  )}
                </div>
              </label>
            </div>
            {errors.resumeFile && <span className="error-text">{errors.resumeFile}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="jobDescription" className="form-label">
              Job Description <span className="required">*</span>
            </label>
            <textarea
              id="jobDescription"
              name="jobDescription"
              placeholder="Paste the complete job description here..."
              rows="7"
              value={formData.jobDescription}
              onChange={handleChange}
              disabled={isSubmitting}
              className="form-textarea"
            />
            {errors.jobDescription && <span className="error-text">{errors.jobDescription}</span>}
          </div>

          <button type="submit" className="btn-submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <span className="btn-spinner"></span>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Start Screening</span>
                <span className="btn-arrow">→</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default ResumeForm
