/**
 * Shared Layout Component
 * Dynamically injects the Sidebar and Top Navigation across all pages.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Only apply if the body has dashboard-layout
    if (!document.body.classList.contains('dashboard-layout')) return;

    // Remove existing hardcoded sidebars/navs if they exist
    const existingSidebar = document.querySelector('.sidebar');
    const existingTopnav = document.querySelector('.topnav');
    if (existingSidebar) existingSidebar.remove();
    if (existingTopnav) existingTopnav.remove();

    // Determine current path for active state
    const currentPath = window.location.pathname;

    const sidebarHTML = `
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <i class="fas fa-seedling"></i>
                <span>SmartAgri</span>
            </div>
            <nav class="sidebar-nav">
                <a href="/dashboard.html" class="nav-item ${currentPath.includes('dashboard') ? 'active' : ''}">
                    <i class="fas fa-home"></i><span data-i18n="nav.dashboard"> Dashboard</span>
                </a>
                <a href="/input-form.html" class="nav-item ${currentPath.includes('input-form') || currentPath.includes('crop-result') ? 'active' : ''}">
                    <i class="fas fa-leaf"></i><span data-i18n="dash.card.crop"> Crop Recommendation</span>
                </a>
                <a href="/disease-detect.html" class="nav-item ${currentPath.includes('disease') ? 'active' : ''}">
                    <i class="fas fa-bug"></i><span data-i18n="nav.disease_detection"> Disease Detection</span>
                </a>
                <a href="/yield-prediction.html" class="nav-item ${currentPath.includes('yield') ? 'active' : ''}">
                    <i class="fas fa-chart-line"></i><span data-i18n="nav.yield_prediction"> Yield Prediction</span>
                </a>
                <a href="/fertilizer-recommend.html" class="nav-item ${currentPath.includes('fertilizer') ? 'active' : ''}">
                    <i class="fas fa-vial"></i><span data-i18n="nav.fertilizer_recs"> Fertilizer Recs</span>
                </a>
                <a href="/weather.html" class="nav-item ${currentPath.includes('weather') ? 'active' : ''}">
                    <i class="fas fa-cloud-sun"></i><span data-i18n="nav.weather"> Weather Insights</span>
                </a>
                <a href="/market.html" class="nav-item ${currentPath.includes('market') ? 'active' : ''}">
                    <i class="fas fa-rupee-sign"></i><span> Market Prices</span>
                </a>
                <a href="/history.html" class="nav-item ${currentPath.includes('history') ? 'active' : ''}">
                    <i class="fas fa-history"></i><span data-i18n="nav.history"> My History</span>
                </a>
                <a href="/admin-dashboard.html" class="nav-item ${currentPath.includes('admin') ? 'active' : ''}" id="admin-nav-link" style="display: none;">
                    <i class="fas fa-shield-alt"></i><span data-i18n="nav.admin_panel"> Admin Panel</span>
                </a>
            </nav>
            
            <!-- Bottom Tab Bar (Mobile Only) -->
            <nav class="mobile-bottom-nav">
                <a href="/dashboard.html" class="mobile-nav-item ${currentPath.includes('dashboard') ? 'active' : ''}"><i class="fas fa-home"></i></a>
                <a href="/input-form.html" class="mobile-nav-item ${currentPath.includes('input-form') || currentPath.includes('crop-result') ? 'active' : ''}"><i class="fas fa-leaf"></i></a>
                <a href="/disease-detect.html" class="mobile-nav-item ${currentPath.includes('disease') ? 'active' : ''}"><i class="fas fa-bug"></i></a>
                <a href="/yield-prediction.html" class="mobile-nav-item ${currentPath.includes('yield') ? 'active' : ''}"><i class="fas fa-chart-line"></i></a>
                <a href="/market.html" class="mobile-nav-item ${currentPath.includes('market') ? 'active' : ''}"><i class="fas fa-rupee-sign"></i></a>
                <a href="/history.html" class="mobile-nav-item ${currentPath.includes('history') ? 'active' : ''}"><i class="fas fa-history"></i></a>
            </nav>
        </aside>
    `;

    const topnavHTML = `
        <header class="topnav">
            <!-- Hamburger menu for mobile header -->
            <button class="menu-toggle" id="menu-toggle">
                <i class="fas fa-bars"></i>
            </button>
            <div style="flex: 1;"></div>
            <div class="user-menu">
                <span class="user-name" id="user-name-display">Loading...</span>
                <button id="logout-btn" class="btn btn-secondary btn-sm" style="margin-left: 10px;">
                    <i class="fas fa-sign-out-alt"></i><span data-i18n="nav.logout"> Logout</span>
                </button>
            </div>
        </header>
    `;

    // Insert into DOM
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
    
    // Find main content area to prepend topnav
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertAdjacentHTML('afterbegin', topnavHTML);
    } else {
        // Fallback
        document.body.insertAdjacentHTML('beforeend', topnavHTML);
    }

    // --- Re-attach Event Listeners ---
    
    // Menu Toggle (for smaller screens but not bottom-tab size, e.g. tablets)
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            if (typeof logout === 'function') {
                await logout();
            } else {
                if (typeof removeToken === 'function') removeToken();
                else localStorage.removeItem('agri_token');
                window.location.href = '/login.html';
            }
        });
    }

    // Initialize language selector if i18n is loaded
    if (typeof initLanguageSelector === 'function') {
        initLanguageSelector();
    }

    // Apply translations if i18n is loaded
    if (typeof applyTranslations === 'function') {
        applyTranslations();
    }
    
    // Check if user is admin to show admin link and update name
    async function updateUserInfo() {
        let user = null;
        try {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                user = JSON.parse(userStr);
            }
        } catch (e) {}

        const nameDisplay = document.getElementById('user-name-display');
        
        // If no user in localStorage but we are authenticated, fetch it
        if (!user && typeof isAuthenticated === 'function' && isAuthenticated()) {
            if (typeof apiGet === 'function') {
                const userRes = await apiGet('/auth/me');
                if (userRes && userRes.success) {
                    user = userRes.data.user;
                    localStorage.setItem('user', JSON.stringify(user));
                }
            }
        }

        if (user) {
            if (user.role === 'admin') {
                const adminLink = document.getElementById('admin-nav-link');
                if (adminLink) adminLink.style.display = 'flex';
            }
            if (nameDisplay) nameDisplay.textContent = user.name;
            
            // Also update welcome name on dashboard if it exists
            const welcomeName = document.getElementById('welcome-name');
            if (welcomeName) welcomeName.textContent = user.name.split(' ')[0];
        } else {
            // Fallback
            if (nameDisplay) nameDisplay.textContent = 'Farmer';
        }
    }
    
    updateUserInfo();
});
