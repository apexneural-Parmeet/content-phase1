import { useState, useEffect } from 'react'
import './App.css'
import { FacebookIcon, InstagramIcon, TwitterIcon, RedditIcon } from './components/SocialIcons'
import Logo from './components/Logo'
import subjectImg from './assets/Subject.png'
import downloadImg from './assets/rename.jpg'

function App() {
  const [caption, setCaption] = useState('')
  const [photo, setPhoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [platformStatus, setPlatformStatus] = useState({
    facebook: { connected: false, loading: true },
    instagram: { connected: false, loading: true },
    twitter: { connected: false, loading: true },
    reddit: { connected: false, loading: true }
  })

  // Check platform connections on mount
  useEffect(() => {
    checkPlatformConnections()
  }, [])

  const checkPlatformConnections = async () => {
    try {
      const response = await fetch('/api/verify-token')
      const data = await response.json()
      
      setPlatformStatus({
        facebook: { connected: data.facebook?.valid || false, loading: false },
        instagram: { connected: data.instagram?.valid || false, loading: false },
        twitter: { connected: data.twitter?.valid || false, loading: false },
        reddit: { connected: data.reddit?.valid || false, loading: false }
      })
    } catch (error) {
      setPlatformStatus({
        facebook: { connected: false, loading: false },
        instagram: { connected: false, loading: false },
        twitter: { connected: false, loading: false },
        reddit: { connected: false, loading: false }
      })
    }
  }

  const handlePhotoChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setPhoto(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleRemoveImage = () => {
    setPhoto(null)
    setPreview(null)
    // Reset file input
    document.getElementById('photo-input').value = ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!photo) {
      setMessage({ type: 'error', text: '❌ Please select a photo' })
      return
    }

    setIsLoading(true)
    setMessage(null)

    const formData = new FormData()
    formData.append('photo', photo)
    formData.append('caption', caption)

    try {
      const response = await fetch('/api/post', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: `🎉 ${data.message}` })
        // Reset form
        setCaption('')
        setPhoto(null)
        setPreview(null)
        document.getElementById('photo-input').value = ''
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => setMessage(null), 5000)
      } else {
        setMessage({ type: 'error', text: `❌ ${data.detail || 'Failed to post'}` })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `❌ Network error: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="container">
        <header className="header">
          <div className="logo-wrap">
            <Logo size={56} />
          </div>
          <h1 className="title">Social Media AI Manager</h1>
        </header>

        {/* Platform Status */}
        <div className="platform-status">
          <div className="platform-grid">
            <div className={`platform-item ${platformStatus.facebook.connected ? 'connected' : 'disconnected'}`}>
              <div className="platform-icon">
                <FacebookIcon size={16} />
              </div>
              <div className="platform-info">
                <span className="platform-name">Facebook</span>
                <span className="platform-status-text">
                  {platformStatus.facebook.loading ? 'Checking...' : 
                   platformStatus.facebook.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className={`platform-item ${platformStatus.instagram.connected ? 'connected' : 'disconnected'}`}>
              <div className="platform-icon">
                <InstagramIcon size={16} />
              </div>
              <div className="platform-info">
                <span className="platform-name">Instagram</span>
                <span className="platform-status-text">
                  {platformStatus.instagram.loading ? 'Checking...' : 
                   platformStatus.instagram.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className={`platform-item ${platformStatus.twitter.connected ? 'connected' : 'disconnected'}`}>
              <div className="platform-icon">
                <TwitterIcon size={16} />
              </div>
              <div className="platform-info">
                <span className="platform-name">Twitter</span>
                <span className="platform-status-text">
                  {platformStatus.twitter.loading ? 'Checking...' : 
                   platformStatus.twitter.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className={`platform-item ${platformStatus.reddit.connected ? 'connected' : 'disconnected'}`}>
              <div className="platform-icon">
                <RedditIcon size={16} />
              </div>
              <div className="platform-info">
                <span className="platform-name">Reddit</span>
                <span className="platform-status-text">
                  {platformStatus.reddit.loading ? 'Checking...' : 
                   platformStatus.reddit.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          {/* Upload Form */}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="caption">Content</label>
              <textarea
                id="caption"
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                rows="4"
                placeholder="Write what your heart says..."
                required
              />
              <span className="char-count">{caption.length} character{caption.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="form-group">
              <label htmlFor="photo-input">Photo</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="photo-input"
                  accept="image/jpeg,image/png,image/gif,image/jpg"
                  onChange={handlePhotoChange}
                  required
                />
                <div className="file-input-display">
                  <img src={downloadImg} alt="upload" className="file-icon-img" />
                  <span className="file-text">
                    {photo ? photo.name : 'Drop your Image here '}
                  </span>
                </div>
              </div>
              <small className="help-text">Supported formats: JPEG, PNG, GIF (Max 10MB)</small>
            </div>

            {/* Image Preview */}
            {preview && (
              <div className="image-preview">
                <img src={preview} alt="Preview" />
                <button type="button" onClick={handleRemoveImage} className="remove-btn">
                  ✕
                </button>
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? (
                <span className="btn-loading">
                  <span className="spinner"></span> Posting to all platforms...
                </span>
              ) : (
                <span className="btn-text">Post to All Platforms</span>
              )}
            </button>
          </form>

          {/* Result Message */}
          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}
        </div>

        <footer className="footer">
          <p>Made with ❤️ for easy social media management</p>
          <div className="subject-wrap">
            <img src={subjectImg} alt="subject" className="subject-img" />
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
