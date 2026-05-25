/**
 * API Wrapper — Shared fetch utility with JWT authentication.
 * All API calls go through this module to ensure consistent auth headers
 * and standardized response handling.
 */

const API_BASE_URL = '/api';
const TOKEN_KEY = 'agri_token';

/**
 * Get the stored JWT token.
 */
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store the JWT token.
 */
function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the stored JWT token (logout).
 */
function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated.
 */
function isAuthenticated() {
    return !!getToken();
}

/**
 * Redirect to login if not authenticated.
 * Call this at the top of every protected page.
 */
function requireAuth() {
    if (!isAuthenticated()) {
        ;
        return false;
    }
    return true;
}

/**
 * Make an authenticated API request.
 * 
 * @param {string} endpoint - API endpoint (e.g., '/auth/login')
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });
        
        const data = await response.json();
        
        // If unauthorized, redirect to login
        if (response.status === 401) {
            removeToken();
            const onAuthPage = window.location.pathname.includes('login') || window.location.pathname.includes('register') || window.locati;
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        return {
            success: false,
            error: 'Network error. Please check your connection.',
            code: 0,
        };
    }
}

/**
 * Shorthand for GET requests.
 */
async function apiGet(endpoint) {
    return apiRequest(endpoint, { method: 'GET' });
}

/**
 * Shorthand for POST requests.
 */
async function apiPost(endpoint, body) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
    });
}

/**
 * Shorthand for PUT requests.
 */
async function apiPut(endpoint, body) {
    return apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(body),
    });
}

/**
 * Shorthand for DELETE requests.
 */
async function apiDelete(endpoint) {
    return apiRequest(endpoint, { method: 'DELETE' });
}

/**
 * Upload a file via multipart/form-data.
 */
async function apiUpload(endpoint, formData) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {};
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData,
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            removeToken();
            const onAuthPage = window.location.pathname.includes('login') || window.location.pathname.includes('register') || window.locati;
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Upload failed:', error);
        return {
            success: false,
            error: 'Upload failed. Please try again.',
            code: 0,
        };
    }
}

/**
 * Show a toast notification.
 */
function showToast(message, type = 'info', duration = 3000) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Toast styles
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: '#fff',
        fontSize: '14px',
        fontWeight: '500',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        zIndex: '10000',
        animation: 'fadeInUp 0.3s ease-out',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        background: type === 'success' ? '#2E7D32' : type === 'error' ? '#C62828' : '#1565C0',
    });
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOutUp 0.3s ease-in forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * File Download Utility for Reports
 */
async function downloadReport(predictionType, predictionId) {
    const token = getToken();
    if (!token) {
        if(window.showToast) window.showToast('Authentication required', 'error');
        return;
    }

    try {
        if(window.showToast) window.showToast('Generating PDF...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/report/${predictionType}/${predictionId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if(window.showToast) window.showToast('Could not generate report, please try again', 'error');
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `report_${predictionType}_${predictionId}.pdf`;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        if(window.showToast) window.showToast('Report downloaded successfully!', 'success');
        
    } catch (err) {
        console.error('Download error:', err);
        if(window.showToast) window.showToast('Network error during download', 'error');
    }
}

