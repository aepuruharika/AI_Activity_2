import { useState } from 'react'
import '../styles/ResumeForm.css'

function ResumeForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    jobTitle: '',
    resumeFile: null,
    jobDescription: ''
  })

  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, files } = e.target
    if (name === 'resumeFile') {
      setFormData({ ...formData, resumeFile: files[0] })
    } else {
      setFormData({ ...formData, [name]: value })
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
    setErrors({})
    onSubmit(formData)
  }

  return (
    <div className="form-container">
      <h2>📋 Submit Resume & Job Description</h2>
      <form onSubmit={handleSubmit} className="resume-form">
        <div className="form-group">
          <label htmlFor="jobTitle">Job Title *</label>
          <input
            type="text"
            id="jobTitle"
            name="jobTitle"
            placeholder="e.g., Senior Software Engineer"
            value={formData.jobTitle}
            onChange={handleChange}
          />
          {errors.jobTitle && <span className="error-text">{errors.jobTitle}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="resumeFile">Upload Resume (TXT/PDF file) *</label>
          <div className="file-input-wrapper">
            <input
              type="file"
              id="resumeFile"
              name="resumeFile"
              accept=".txt,.pdf"
              onChange={handleChange}
            />
            <label htmlFor="resumeFile" className="file-label">
              {formData.resumeFile ? formData.resumeFile.name : 'Click to select resume file'}
            </label>
          </div>
          <small>Upload a .txt or .pdf file with your resume</small>
          {errors.resumeFile && <span className="error-text">{errors.resumeFile}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="jobDescription">Job Description *</label>
          <textarea
            id="jobDescription"
            name="jobDescription"
            placeholder="Paste the job description here..."
            rows="8"
            value={formData.jobDescription}
            onChange={handleChange}
          />
          {errors.jobDescription && <span className="error-text">{errors.jobDescription}</span>}
        </div>

        <button type="submit" className="btn-submit">
          Analyze Resume
        </button>
      </form>
    </div>
  )
}

export default ResumeForm
