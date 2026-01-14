# Frontend-Backend Connection Guide

## Overview
The frontend has been successfully connected to the backend API. All HTML pages now communicate with the Flask backend server.

## Files Created/Updated

### 1. `api.js` - API Utility Module
Central API configuration and helper functions:
- `API_BASE_URL`: Backend server URL (http://localhost:5000/api)
- Authentication token management
- API request wrapper functions
- `authAPI`: Authentication endpoints (signup, login, logout)
- `voiceAPI`: Voice analysis endpoints (upload, analyze, history, files)

### 2. `loginpage.html` - Updated
- Connected to `/api/auth/login` endpoint
- Sends email and password to backend
- Stores JWT token in localStorage
- Shows error messages on failed login
- Redirects to dashboard on success

### 3. `signup.html` - Updated
- Connected to `/api/auth/signup` endpoint
- Sends email and password to backend
- Stores JWT token in localStorage
- Shows error messages on failed signup
- Redirects to dashboard on success

### 4. `dashboard.html` - Completely Rewritten
- **Authentication**: Checks for JWT token, redirects to login if not authenticated
- **File Upload**: 
  - Drag & drop support
  - File browser support
  - File validation (type and size)
  - Uploads to `/api/voice/upload`
- **Analysis**: 
  - Automatically analyzes uploaded files
  - Calls `/api/voice/analyze/<file_id>`
  - Displays results with confidence scores
  - Shows AI detection status
  - Displays scam patterns
- **History Tab**: 
  - Loads analysis history from `/api/voice/history`
  - Displays previous analyses with dates and results
- **Logout**: Clears token and redirects to login

## API Endpoints Used

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login

### Voice Analysis
- `POST /api/voice/upload` - Upload audio file (requires authentication)
- `POST /api/voice/analyze/<file_id>` - Analyze uploaded file (requires authentication)
- `GET /api/voice/history` - Get analysis history (requires authentication)

## Authentication Flow

1. User signs up/logs in
2. Backend returns JWT token
3. Token stored in localStorage
4. Token sent in `Authorization: Bearer <token>` header for authenticated requests
5. If token is missing/invalid, user redirected to login page

## File Upload Flow

1. User selects/drops audio file
2. Frontend validates file (type and size)
3. File uploaded to `/api/voice/upload`
4. Backend returns file_id
5. Frontend calls `/api/voice/analyze/<file_id>`
6. Backend analyzes file and returns results
7. Frontend displays results with:
   - AI detection status
   - Confidence score
   - Scam patterns
   - Visual indicators

## Running the Application

### 1. Start Backend Server
```bash
python app.py
```
Server runs on `http://localhost:5000`

### 2. Open Frontend
Open `mainpage.html`, `loginpage.html`, or `dashboard.html` in a web browser.

**Note**: For full functionality, serve the HTML files through a web server (not just file://) to avoid CORS issues. You can:
- Use the Flask server (serves static files)
- Use a simple HTTP server: `python -m http.server 8000`
- Use VS Code Live Server extension

### 3. Test the Connection

1. **Sign Up**: Create a new account at signup.html
2. **Login**: Login with credentials at loginpage.html
3. **Upload File**: Go to dashboard and upload an audio file
4. **View Results**: See analysis results immediately
5. **View History**: Switch to History tab to see past analyses

## Error Handling

- Login/Signup errors displayed to user
- Upload errors shown with descriptive messages
- Network errors handled gracefully
- Authentication errors redirect to login

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Uses Fetch API for HTTP requests
- Uses localStorage for token storage

## Security Notes

- JWT tokens stored in localStorage
- Tokens sent in Authorization header
- Passwords never stored on frontend
- File validation on frontend (also validated on backend)
- CORS enabled on backend for localhost development

## Next Steps

1. **Test the full flow**: Sign up → Login → Upload → Analyze
2. **Customize UI**: Adjust styling as needed
3. **Add features**: Consider adding:
   - File preview before upload
   - Progress bars for upload
   - More detailed analysis views
   - Export results functionality

## Troubleshooting

### CORS Errors
- Make sure backend is running
- Check API_BASE_URL in api.js matches backend URL
- Ensure Flask CORS is enabled

### Authentication Errors
- Check token is being stored in localStorage
- Verify token is sent in Authorization header
- Check backend logs for authentication errors

### File Upload Errors
- Check file size (max 50MB)
- Verify file format (MP3, WAV, M4A, OGG, FLAC)
- Check backend upload folder permissions
- Verify backend is running
