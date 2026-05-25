/**
 * Multi-language Support (i18n)
 */

let translations = {};
let currentLang = localStorage.getItem('appLang') || 'en';

/**
 * Load language JSON file
 */
async function loadLanguage(lang) {
    try {
        const response = await fetch(`/static/i18n/${lang}.json`);
        if (!response.ok) {
            throw new Error(`Failed to load ${lang} translations`);
        }
        translations = await response.json();
        currentLang = lang;
        localStorage.setItem('appLang', lang);
        
        // Update DOM elements
        applyTranslations();
        
        // Update language selector dropdown if exists
        const langSelect = document.getElementById('lang-selector');
        if (langSelect) {
            langSelect.value = lang;
        }
        
    } catch (error) {
        console.error('i18n loading error:', error);
    }
}

/**
 * Get translated string for a key
 */
function t(key, defaultText = '') {
    return translations[key] || defaultText || key;
}

/**
 * Update all DOM elements with data-i18n attribute
 */
function applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        
        // Handle input placeholders
        if (el.tagName === 'INPUT' && el.type !== 'button' && el.type !== 'submit') {
            const translated = t(key);
            if (translated !== key) {
                el.placeholder = translated;
            }
        } else {
            // Check if element has an icon child to preserve it
            const icon = el.querySelector('i');
            const translated = t(key);
            
            if (translated !== key) {
                if (icon) {
                    el.innerHTML = '';
                    el.appendChild(icon);
                    el.appendChild(document.createTextNode(' ' + translated));
                } else {
                    el.textContent = translated;
                }
            }
        }
    });
}

/**
 * Initialize language selector dropdown in the topnav
 */
function initLanguageSelector() {
    const userMenu = document.querySelector('.user-menu');
    if (!userMenu) return;
    
    // Check if already injected
    if (document.getElementById('lang-selector')) return;
    
    const wrapper = document.createElement('div');
    wrapper.style.marginRight = '15px';
    wrapper.innerHTML = `
        <select id="lang-selector" class="form-control" style="width: 100px; padding: 4px 8px; height: 30px; font-size: 0.85rem;">
            <option value="en">English</option>
            <option value="kn">ಕನ್ನಡ</option>
            <option value="hi">हिंदी</option>
        </select>
    `;
    
    userMenu.insertBefore(wrapper, userMenu.firstChild);
    
    const select = document.getElementById('lang-selector');
    select.value = currentLang;
    
    select.addEventListener('change', (e) => {
        loadLanguage(e.target.value);
    });
}

// Automatically load default or saved language on page load
document.addEventListener('DOMContentLoaded', () => {
    initLanguageSelector();
    loadLanguage(currentLang);
});
