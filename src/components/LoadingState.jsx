import '../styles/LoadingState.css'

function LoadingState({ step }) {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <h3>Processing Resume...</h3>
      <p className="processing-step">{step}</p>
      <div className="progress-dots">
        <span className="dot active"></span>
        <span className="dot"></span>
        <span className="dot"></span>
      </div>
    </div>
  )
}

export default LoadingState
