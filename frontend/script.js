// --- CONFIGURATION ---
// Ensure your Flask API is running at this address (http://127.0.0.1:5000)
const API_BASE_URL = 'http://127.0.0.1:5000/api';
const APP_ELEMENT = document.getElementById('app');

// Global state object to track the logged-in user
let user = { isAuthenticated: false, role: null, username: null };

// --- CORE APPLICATION ROUTING ---

/**
 * Determines whether to show the Login Screen or the Dashboard.
 */
function renderApp() {
  if (user.isAuthenticated) {
    renderDashboard();
  } else {
    renderLogin();
  }
}

/**
 * Clears the user state and returns to the login screen.
 */
function handleLogout() {
  user = { isAuthenticated: false, role: null, username: null };
  localStorage.removeItem('hotel_user'); // Clear user data from browser storage
  renderApp();
}

// --- 1. LOGIN SCREEN ---

function renderLogin() {
  APP_ELEMENT.innerHTML = `
        <div class="flex items-center justify-center min-h-screen">
            <div class="w-full max-w-md p-8 bg-white rounded-xl shadow-2xl border border-gray-100">
                <h2 class="text-3xl font-extrabold text-gray-800 mb-2 text-center">
                    Welcome to Hotel PMS
                </h2>
                <p class="text-sm text-gray-500 mb-6 text-center">
                    Sign in with your staff credentials.
                </p>
                <form id="loginForm" class="space-y-6">
                    <div>
                        <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
                        <input type="text" id="username" name="username" placeholder="e.g., receptionist" 
                            class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" required />
                    </div>
                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                        <input type="password" id="password" name="password" placeholder="securepwd123"
                            class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" required />
                    </div>
                    <div id="loginMessage" class="text-center text-sm"></div>
                    <button type="submit" id="loginButton"
                        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors">
                        Sign In
                    </button>
                </form>
                <p class="text-xs text-gray-400 mt-4 text-center">Test users created: sysadmin, manager, reception, housekeeping</p>
            </div>
        </div>
    `;

  // Attach event listener to the form upon rendering
  document.getElementById('loginForm').addEventListener('submit', handleLoginSubmit);
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const messageEl = document.getElementById('loginMessage');
  const loginButton = document.getElementById('loginButton');

  messageEl.innerHTML = '<span class="text-blue-500">Authenticating...</span>';
  loginButton.disabled = true;

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Success: Update global user state
      user = {
        staffID: data.staffID,
        username: data.username,
        role: data.role,
        isAuthenticated: true,
      };
      localStorage.setItem('hotel_user', JSON.stringify(user));
      renderApp(); // Redirect to dashboard
    } else {
      // Failure: Display error message
      messageEl.innerHTML = `<span class="text-red-600">${data.error || 'Login failed.'}</span>`;
    }
  } catch (err) {
    messageEl.innerHTML = `<span class="text-red-600">Network error. Is the Flask API running?</span>`;
    console.error("Login Network Error:", err);
  } finally {
    loginButton.disabled = false;
  }
}

// --- 2. DASHBOARD LAYOUT AND ROLE-BASED ROUTING ---

function renderHeader() {
  return `
        <header class="bg-white shadow-md p-4 flex justify-between items-center sticky top-0 z-10">
            <h1 class="text-2xl font-extrabold text-gray-800">Hotel PMS</h1>
            <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-600 font-medium">Logged in as: ${user.username} (<span class="font-bold text-indigo-600">${user.role}</span>)</span>
                <button id="logoutButton"
                    class="px-3 py-1 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors">
                    Logout
                </button>
            </div>
        </header>
    `;
}

/**
 * Returns the correct content based on the user's role.
 */
function renderRoleContent() {
  switch (user.role) {
    case 'Admin':
      return `
                <div class="p-8">
                    <h2 class="text-3xl font-bold mb-4 text-red-700">System Administration Dashboard</h2>
                    <p class="text-gray-600">Welcome, Admin. You have full access to User Management, Pricing, and System Configuration.</p>
                    <div class="mt-8 p-6 border-l-4 border-red-500 bg-red-50 rounded-lg">
                        <p class="font-semibold text-red-800">Admin View: Placeholder</p>
                        <p class="text-sm text-red-600">Staff CRUD, Room Types, and Services interfaces will be built here.</p>
                    </div>
                </div>
            `;
    case 'Manager':
      return `
                <div class="p-8">
                    <h2 class="text-3xl font-bold mb-4 text-green-700">Financial & Operational Oversight</h2>
                    <p class="text-gray-600">Welcome, Manager. Access is granted for Billing, Payments, and Room Audits.</p>
                    <div class="mt-8 p-6 border-l-4 border-green-500 bg-green-50 rounded-lg">
                        <p class="font-semibold text-green-800">Manager View: Placeholder</p>
                        <p class="text-sm text-green-600">Financial audit and status monitoring tools will be displayed here.</p>
                    </div>
                </div>
            `;
    case 'Receptionist':
    case 'Housekeeping':
      return `
                <div class="p-8">
                    <h2 class="text-3xl font-bold mb-4 text-blue-700">Guests & Reservations Console</h2>
                    <p class="text-gray-600">Welcome, ${user.role}. Your primary functions are guest check-in/out and new bookings.</p>
                    <div class="mt-8 p-6 border-l-4 border-blue-500 bg-blue-50 rounded-lg">
                        <p class="font-semibold text-blue-800">Receptionist View: Placeholder</p>
                        <p class="text-sm text-blue-600">The functional Guest List and Reservation Form will be built here.</p>
                    </div>
                </div>
            `;
    default:
      return `
                <div class="p-8 text-center">
                    <h2 class="text-3xl font-bold text-yellow-600">Access Denied</h2>
                    <p class="text-lg text-gray-500">Your role (${user.role}) is not recognized or authorized to view this dashboard.</p>
                </div>
            `;
  }
}

function renderDashboard() {
  APP_ELEMENT.innerHTML = renderHeader() + `
        <main class="container mx-auto p-4">
            ${renderRoleContent()}
        </main>
    `;

  // Attach event listener to the logout button
  document.getElementById('logoutButton').addEventListener('click', handleLogout);
}

// --- 3. INITIALIZATION ---

function initializeApp() {
  // Check for previous session data in localStorage
  const storedUser = localStorage.getItem('hotel_user');
  if (storedUser) {
    user = JSON.parse(storedUser);
  }
  renderApp();
}

// Start the application when the script loads
initializeApp();
