// ==================== DARK MODE TOGGLE ====================
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeText = document.getElementById('darkModeText');
    const darkModeIcon = darkModeToggle ? darkModeToggle.querySelector('i') : null;
    
    // Check for saved dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Apply saved preference
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        if (darkModeIcon) {
            darkModeIcon.classList.remove('fa-moon');
            darkModeIcon.classList.add('fa-sun');
        }
        if (darkModeText) {
            darkModeText.textContent = 'Light';
        }
    }
    
    // Toggle dark mode
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('dark-mode');
            const isNowDark = document.body.classList.contains('dark-mode');
            
            // Update icon and text
            if (darkModeIcon) {
                if (isNowDark) {
                    darkModeIcon.classList.remove('fa-moon');
                    darkModeIcon.classList.add('fa-sun');
                    darkModeText.textContent = 'Light';
                } else {
                    darkModeIcon.classList.remove('fa-sun');
                    darkModeIcon.classList.add('fa-moon');
                    darkModeText.textContent = 'Dark';
                }
            }
            
            // Save preference
            localStorage.setItem('darkMode', isNowDark);
            
            // Show toast
            showToast(isNowDark ? 'Dark mode enabled 🌙' : 'Light mode enabled ☀️', 'info');
        });
    }
});

// ==================== MOBILE MENU TOGGLE ====================
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger to X
            const spans = hamburger.querySelectorAll('span');
            if (navMenu.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                const spans = hamburger.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    }
});

// ==================== FLASH MESSAGE AUTO-DISMISS ====================
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== SMOOTH SCROLLING ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ==================== FORM VALIDATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.style.borderColor = 'var(--danger)';
                showValidationError(this, 'Please enter a valid email address');
            } else {
                this.style.borderColor = 'var(--gray-300)';
                removeValidationError(this);
            }
        });
    });
    
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.name === 'password' && input.closest('form').querySelector('[name="confirm_password"]')) {
            input.addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                showPasswordStrength(this, strength);
            });
        }
    });
});

function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    return strength;
}

function showPasswordStrength(input, strength) {
    let indicator = input.parentElement.querySelector('.password-strength');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength';
        input.parentElement.appendChild(indicator);
    }
    
    const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColor = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981'];
    
    indicator.innerHTML = `
        <div style="display: flex; gap: 4px; margin-top: 8px;">
            ${[1,2,3,4,5].map(i => `
                <div style="flex: 1; height: 4px; background: ${i <= strength ? strengthColor[strength-1] : '#e5e7eb'}; border-radius: 2px;"></div>
            `).join('')}
        </div>
        <small style="font-size: 0.75rem; color: ${strengthColor[strength-1] || '#6b7280'}; margin-top: 4px; display: block;">
            ${strength > 0 ? strengthText[strength-1] : 'Enter password'}
        </small>
    `;
}

function showValidationError(input, message) {
    removeValidationError(input);
    const error = document.createElement('small');
    error.className = 'validation-error';
    error.style.color = 'var(--danger)';
    error.style.fontSize = '0.875rem';
    error.style.marginTop = '0.25rem';
    error.style.display = 'block';
    error.textContent = message;
    input.parentElement.appendChild(error);
}

function removeValidationError(input) {
    const error = input.parentElement.querySelector('.validation-error');
    if (error) {
        error.remove();
    }
}

// ==================== DYNAMIC DATE FORMATTING ====================
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function getRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

// ==================== LOADING STATES ====================
function showLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
}

function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

// ==================== CONFIRMATION DIALOGS ====================
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==================== COPY TO CLIPBOARD ====================
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
        }
        document.body.removeChild(textarea);
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    let container = document.querySelector('.flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== DEBOUNCE UTILITY ====================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== SCROLL TO TOP ====================
document.addEventListener('DOMContentLoaded', function() {
    // Create scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.setAttribute('aria-label', 'Scroll to top');
    
    document.body.appendChild(scrollBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'flex';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    
    // Scroll to top on click
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    scrollBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    scrollBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// ==================== PROGRESS BAR ANIMATION ====================
document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    // Animate progress bars on page load
    setTimeout(() => {
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }, 300);
});

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search (if exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) searchInput.focus();
    }
    
    // Escape: Close modals/menus
    if (e.key === 'Escape') {
        const navMenu = document.getElementById('navMenu');
        if (navMenu && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
        }
    }
});

// ==================== ANALYTICS TRACKING (Placeholder) ====================
function trackEvent(category, action, label) {
    console.log('Event tracked:', { category, action, label });
    // Add your analytics code here
}

// ==================== INITIALIZE ====================
console.log('%c🚀 SkillTracker JavaScript loaded successfully!', 'color: #4f46e5; font-size: 16px; font-weight: bold;');

// Clear any cached quote data on page load
if (window.performance && performance.navigation.type === 1) {
    console.log('Page refreshed - clearing quote cache');
}

// Expose useful functions globally
window.SkillTracker = {
    showToast,
    copyToClipboard,
    formatDate,
    getRelativeTime,
    showLoading,
    hideLoading,
    confirmAction,
    trackEvent
};