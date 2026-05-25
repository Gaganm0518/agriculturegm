/**
 * Notifications Logic
 * Handles polling, dropdown UI, and toast notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) return; // Not logged in

    // 1. Setup UI
    setupNotificationUI();

    // 2. Initial fetch & poll
    fetchNotifications();
    setInterval(fetchNotifications, 30000); // Poll every 30 seconds
});

function setupNotificationUI() {
    const userMenu = document.querySelector('.user-menu');
    if (!userMenu) return;

    // Inject bell icon and dropdown if not present
    if (!document.getElementById('notif-bell')) {
        const notifWrapper = document.createElement('div');
        notifWrapper.className = 'notif-wrapper';
        notifWrapper.style.position = 'relative';
        notifWrapper.style.marginRight = '20px';
        notifWrapper.style.cursor = 'pointer';

        notifWrapper.innerHTML = `
            <div id="notif-bell" style="font-size: 1.2rem; color: var(--gray-600);">
                <i class="fas fa-bell"></i>
                <span id="notif-badge" style="display:none; position:absolute; top:-5px; right:-8px; background:red; color:white; font-size:0.6rem; font-weight:bold; padding:2px 5px; border-radius:50%;">0</span>
            </div>
            <div id="notif-dropdown" class="notif-dropdown shadow-md" style="display:none; position:absolute; right:0; top:35px; width:300px; background:white; border-radius:8px; z-index:1000; border:1px solid var(--gray-200);">
                <div style="padding:10px; border-bottom:1px solid var(--gray-200); display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-size:1rem; color:var(--dark-green);">Notifications</h4>
                    <button id="mark-all-read" style="background:none; border:none; color:var(--primary-green); cursor:pointer; font-size:0.8rem;">Mark all read</button>
                </div>
                <div id="notif-list" style="max-height:300px; overflow-y:auto; padding:0;">
                    <div style="padding:15px; text-align:center; color:var(--gray-500); font-size:0.9rem;">Loading...</div>
                </div>
            </div>
        `;

        userMenu.insertBefore(notifWrapper, userMenu.firstChild);

        // Toggle logic
        const bell = document.getElementById('notif-bell');
        const dropdown = document.getElementById('notif-dropdown');
        
        bell.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        });

        document.addEventListener('click', (e) => {
            if (!notifWrapper.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });

        document.getElementById('mark-all-read').addEventListener('click', markAllRead);
    }

    // Setup Toast Container
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = 'position:fixed; bottom:20px; right:20px; z-index:9999; display:flex; flex-direction:column; gap:10px;';
        document.body.appendChild(toastContainer);
    }
}

async function fetchNotifications() {
    try {
        const res = await apiGet('/notifications/');
        if (res && res.success) {
            updateBadge(res.data.unread_count);
            renderDropdown(res.data.notifications);
        }
    } catch (err) {
        console.error("Failed to fetch notifications", err);
    }
}

function updateBadge(count) {
    const badge = document.getElementById('notif-badge');
    if (!badge) return;

    if (count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

function renderDropdown(notifications) {
    const list = document.getElementById('notif-list');
    if (!list) return;

    list.innerHTML = '';

    if (notifications.length === 0) {
        list.innerHTML = '<div style="padding:15px; text-align:center; color:var(--gray-500); font-size:0.9rem;">No notifications.</div>';
        return;
    }

    // Show last 5
    notifications.slice(0, 5).forEach(n => {
        const item = document.createElement('div');
        item.style.cssText = `padding: 12px 15px; border-bottom: 1px solid var(--gray-100); cursor: pointer; transition: background 0.2s; ${n.is_read ? 'opacity: 0.7;' : 'background: #f0fdf4;'}`;
        
        let icon = '<i class="fas fa-info-circle text-blue-500"></i>';
        if (n.type === 'prediction') icon = '<i class="fas fa-check-circle" style="color:var(--primary-green);"></i>';

        const date = new Date(n.created_at).toLocaleString();

        item.innerHTML = `
            <div style="display:flex; gap:10px; align-items:start;">
                <div style="margin-top:2px;">${icon}</div>
                <div>
                    <div style="font-size:0.85rem; color:var(--text-dark); margin-bottom:4px; ${n.is_read ? '' : 'font-weight:600;'}">${n.message}</div>
                    <div style="font-size:0.7rem; color:var(--gray-500);">${date}</div>
                </div>
            </div>
        `;

        item.addEventListener('click', async () => {
            if (!n.is_read) {
                await apiPut(`/notifications/${n.id}/read`, {});
                fetchNotifications();
            }
            window.location.href = '/history.html';
        });

        list.appendChild(item);
    });
}

async function markAllRead() {
    try {
        await apiPut('/notifications/read-all', {});
        fetchNotifications();
    } catch (err) {
        console.error("Failed to mark all as read");
    }
}

window.showToast = function(message, type='success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColor = type === 'error' ? '#dc2626' : 'var(--primary-green)';
    
    toast.style.cssText = `
        background: ${bgColor}; 
        color: white; 
        padding: 12px 20px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 10px;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    `;

    toast.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);

    // Remove after 4s
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};
