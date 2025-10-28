# Frontend Integration Guide - Social Authentication

## 🎯 Overview

This guide shows the frontend team how to integrate Google and Facebook social login with the Shopwice backend API.

---

## 📡 Backend Endpoints

### Base URL (Development)
```
http://localhost:8000/api/v1/auth/
```

### Available Endpoints

#### 1. Get API Information
```http
GET /api/v1/auth/
```

**Response:**
```json
{
  "message": "Shopwice Authentication API",
  "available_endpoints": {
    "google_login": "/api/v1/auth/google/",
    "facebook_login": "/api/v1/auth/facebook/"
  },
  "methods": {
    "google": {
      "endpoint": "/api/v1/auth/google/",
      "method": "POST",
      "required_fields": ["access_token"]
    },
    "facebook": {
      "endpoint": "/api/v1/auth/facebook/",
      "method": "POST",
      "required_fields": ["access_token"]
    }
  }
}
```

#### 2. Google Login
```http
POST /api/v1/auth/google/
Content-Type: application/json

{
  "access_token": "google_access_token_here"
}
```

#### 3. Facebook Login
```http
POST /api/v1/auth/facebook/
Content-Type: application/json

{
  "access_token": "facebook_access_token_here"
}
```

### Success Response (Both endpoints)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "pk": 1,
    "username": "user_12345",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Error Response
```json
{
  "non_field_errors": ["Incorrect value"]
}
```

---

## 🔧 Frontend Implementation

### Option 1: React with Google OAuth (Recommended)

#### Step 1: Install Dependencies
```bash
npm install @react-oauth/google
```

#### Step 2: Get Google Client ID
Ask the backend team for the Google OAuth Client ID, or create your own:
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create OAuth 2.0 credentials
- Add authorized JavaScript origins: `http://localhost:3000`

**For Development:** Use this Client ID (ask backend team)

#### Step 3: Implement Google Login

```jsx
// App.jsx or main component
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function App() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: credentialResponse.credential
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Store tokens
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        console.error('Login failed:', data);
        alert('Login failed. Please try again.');
      }
    } catch (error) {
      console.error('Error during login:', error);
      alert('Network error. Please check your connection.');
    }
  };

  const handleGoogleError = () => {
    console.log('Google Login Failed');
    alert('Google login was cancelled or failed.');
  };

  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <div className="login-container">
        <h1>Login to Shopwice</h1>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          useOneTap
        />
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;
```

---

### Option 2: React with Facebook Login

#### Step 1: Install Dependencies
```bash
npm install react-facebook-login
```

#### Step 2: Get Facebook App ID
**For Development:** Use this App ID: `2488059255826311`

**Important:** Make sure `http://localhost:3000` is added to Valid OAuth Redirect URIs in the Facebook app settings.

#### Step 3: Implement Facebook Login

```jsx
import FacebookLogin from 'react-facebook-login/dist/facebook-login-render-props';

function LoginPage() {
  const handleFacebookResponse = async (response) => {
    if (response.accessToken) {
      try {
        const apiResponse = await fetch('http://localhost:8000/api/v1/auth/facebook/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            access_token: response.accessToken
          })
        });

        const data = await apiResponse.json();

        if (apiResponse.ok) {
          // Store tokens
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          
          // Redirect to dashboard
          window.location.href = '/dashboard';
        } else {
          console.error('Login failed:', data);
          alert('Login failed. Please try again.');
        }
      } catch (error) {
        console.error('Error during login:', error);
        alert('Network error. Please check your connection.');
      }
    } else {
      console.log('Facebook login cancelled');
    }
  };

  return (
    <FacebookLogin
      appId="2488059255826311"
      fields="name,email,picture"
      callback={handleFacebookResponse}
      render={renderProps => (
        <button onClick={renderProps.onClick} className="fb-login-btn">
          Login with Facebook
        </button>
      )}
    />
  );
}
```

---

### Option 3: Vanilla JavaScript (No Framework)

#### Google Login
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
  <div id="g_id_onload"
       data-client_id="YOUR_GOOGLE_CLIENT_ID"
       data-callback="handleGoogleLogin">
  </div>
  <div class="g_id_signin" data-type="standard"></div>

  <script>
    function handleGoogleLogin(response) {
      fetch('http://localhost:8000/api/v1/auth/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: response.credential
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          window.location.href = '/dashboard';
        }
      })
      .catch(error => console.error('Error:', error));
    }
  </script>
</body>
</html>
```

#### Facebook Login
```html
<!DOCTYPE html>
<html>
<head>
  <script async defer crossorigin="anonymous" 
    src="https://connect.facebook.net/en_US/sdk.js"></script>
</head>
<body>
  <button onclick="loginWithFacebook()">Login with Facebook</button>

  <script>
    window.fbAsyncInit = function() {
      FB.init({
        appId: '2488059255826311',
        cookie: true,
        xfbml: true,
        version: 'v18.0'
      });
    };

    function loginWithFacebook() {
      FB.login(function(response) {
        if (response.authResponse) {
          const accessToken = response.authResponse.accessToken;
          
          fetch('http://localhost:8000/api/v1/auth/facebook/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              access_token: accessToken
            })
          })
          .then(res => res.json())
          .then(data => {
            if (data.access_token) {
              localStorage.setItem('access_token', data.access_token);
              localStorage.setItem('refresh_token', data.refresh_token);
              window.location.href = '/dashboard';
            }
          })
          .catch(error => console.error('Error:', error));
        }
      }, {scope: 'public_profile,email'});
    }
  </script>
</body>
</html>
```

---

## 🔐 Using JWT Tokens in Frontend

After successful login, use the `access_token` for authenticated API requests:

```javascript
// Example: Fetch user profile
async function getUserProfile() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/v1/users/profile/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });
  
  return response.json();
}

// Example: Refresh token when access token expires
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/v1/auth/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refreshToken
    })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  
  return data.access;
}
```

---

## 🌐 Accessing the Backend

### Development Setup Options

#### Option 1: Run Backend Locally (Recommended for Development)

The backend team should share instructions to run the backend on `localhost:8000`:

1. **Using Docker Compose** (Easiest):
   ```bash
   # Backend team runs this
   cd shopwice-backend
   docker-compose up
   ```
   Backend will be available at: `http://localhost:8000`

2. **Using Python Virtual Environment**:
   ```bash
   # Backend team runs this
   cd shopwice-backend
   python -m venv myenv
   myenv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python manage.py runserver
   ```

**Frontend connects to:** `http://localhost:8000`

---

#### Option 2: Shared Development Backend (For Team Testing)

If backend is deployed to a shared development server (e.g., AWS EC2, DigitalOcean):

**Backend URL:** `http://dev.shopwice.com:8000` (example)

Update your frontend fetch calls:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://dev.shopwice.com:8000';

fetch(`${API_BASE_URL}/api/v1/auth/google/`, {
  // ... rest of the code
});
```

**Note:** Backend team must configure CORS to allow your frontend domain.

---

#### Option 3: Docker Container on Your Machine

If backend team provides a Docker image:

```bash
# Pull the backend image (backend team provides this)
docker pull shopwice/backend:latest

# Run the container
docker run -p 8000:8000 shopwice/backend:latest
```

Backend will be available at: `http://localhost:8000`

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error
```
Access to fetch at 'http://localhost:8000/api/v1/auth/google/' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solution:** Ask backend team to add your frontend URL to `CORS_ALLOWED_ORIGINS` in Django settings.

---

### Issue 2: "Incorrect value" Error
```json
{"non_field_errors": ["Incorrect value"]}
```

**Causes:**
- Invalid or expired access token
- Token from wrong environment (dev vs prod)
- OAuth app not configured correctly

**Solution:**
- Ensure you're using a fresh token
- Check that OAuth redirect URIs match in Google/Facebook console
- Verify you're using the correct App ID/Client ID

---

### Issue 3: Network Error / Connection Refused
```
Failed to fetch
```

**Solution:**
- Ensure backend is running (`docker-compose up` or `python manage.py runserver`)
- Check backend URL is correct (`http://localhost:8000`)
- Verify no firewall blocking port 8000

---

### Issue 4: Token Expires Quickly
Google tokens from the Sign-In button expire in 1 hour.

**Solution:**
- Use the `refresh_token` to get a new `access_token`
- Implement automatic token refresh in your app (see JWT section above)

---

## 📞 Need Help?

### Contact Backend Team For:
- Google Client ID for development
- Facebook App ID (or use: `2488059255826311`)
- Backend deployment URL (if not using localhost)
- CORS configuration issues
- Any 500 Internal Server Error responses

### Testing Credentials:
- **Google:** Use your personal Google account
- **Facebook:** Use test users created in Facebook Developer Console (app is in Development mode)

---

## ✅ Quick Testing Checklist

Before integration:
- [ ] Backend is running and accessible
- [ ] Can access `http://localhost:8000/api/v1/auth/` and get JSON response
- [ ] Have Google Client ID from backend team
- [ ] Have Facebook App ID (2488059255826311 for dev)
- [ ] CORS is configured to allow your frontend origin

After integration:
- [ ] Google login button appears
- [ ] Facebook login button appears
- [ ] Can complete Google login and receive JWT tokens
- [ ] Can complete Facebook login and receive JWT tokens
- [ ] Tokens are stored in localStorage
- [ ] Can use access_token to make authenticated API calls
- [ ] Handle errors gracefully (show user-friendly messages)

---

## 🚀 Next Steps After Integration

1. Test end-to-end login flow with both providers
2. Implement logout functionality (clear localStorage)
3. Add token refresh logic
4. Handle expired tokens (redirect to login)
5. Test account linking (same email, different providers)
6. Add loading states and error messages
7. Test on different browsers

---

**Last Updated:** October 23, 2025  
**Backend Version:** Development  
**Maintainer:** Backend Team - Shopwice
