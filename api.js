/**
 * API Utility Functions
 * Shared API configuration and helper functions for frontend
 */

const API_BASE_URL = 'http://localhost:5000/api';

// Get authentication token from localStorage
function getAuthToken() {
  return localStorage.getItem('token');
}

// Set authentication token
function setAuthToken(token) {
  localStorage.setItem('token', token);
}

// Remove authentication token
function clearAuthToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('email');
  localStorage.removeItem('userId');
}

// Get stored user email
function getUserEmail() {
  return localStorage.getItem('email');
}

// Set user info
function setUserInfo(email, userId) {
  localStorage.setItem('email', email);
  localStorage.setItem('userId', userId);
}

// Check if user is authenticated
function isAuthenticated() {
  return !!getAuthToken();
}

// Make API request with authentication
async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Authentication API calls
const authAPI = {
  async signup(email, password) {
    const data = await apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (data.token) {
      setAuthToken(data.token);
      setUserInfo(data.user.email, data.user.id);
    }
    
    return data;
  },
  
  async login(email, password) {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (data.token) {
      setAuthToken(data.token);
      setUserInfo(data.user.email, data.user.id);
    }
    
    return data;
  },
  
  logout() {
    clearAuthToken();
  }
};

// Voice API calls
const voiceAPI = {
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = getAuthToken();
    const url = `${API_BASE_URL}/voice/upload`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type for FormData - browser sets it automatically with boundary
        },
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }
      
      return data;
    } catch (error) {
      console.error('Upload Error:', error);
      throw error;
    }
  },
  
  async analyzeFile(fileId) {
    const data = await apiRequest(`/voice/analyze/${fileId}`, {
      method: 'POST',
    });
    
    return data;
  },
  
  async getHistory() {
    const data = await apiRequest('/voice/history');
    return data;
  },
  
  async getFiles() {
    const data = await apiRequest('/voice/files');
    return data;
  }
};

// Export for use in HTML files
if (typeof window !== 'undefined') {
  window.authAPI = authAPI;
  window.voiceAPI = voiceAPI;
  window.getAuthToken = getAuthToken;
  window.isAuthenticated = isAuthenticated;
  window.clearAuthToken = clearAuthToken;
  window.getUserEmail = getUserEmail;
}
