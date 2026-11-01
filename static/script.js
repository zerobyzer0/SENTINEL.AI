// ============================================================
// SentinelAI — Frontend Script
// Loading Screen, Ambient Particles, and Scroll Animations
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    initLoadingScreen();
    initParticles();
    initScrollAnimations();
    initFormScan();
});

// 1. Loading Screen Animation Sequence
function initLoadingScreen() {
    const loadingTexts = [
        'INITIALIZING SECURITY PROTOCOLS...',
        'LOADING NEURAL NETWORK WEIGHTS...',
        'CALIBRATING ANOMALY DETECTORS...',
        'ESTABLISHING SECURE CHANNELS...',
        'SYSTEM READY.'
    ];

    const progressFill = document.getElementById('progressFill');
    const loaderText = document.getElementById('loaderText');
    const loadingScreen = document.getElementById('loadingScreen');

    if (!loadingScreen) return;

    let progress = 0;
    let textIndex = 0;

    const loadingInterval = setInterval(() => {
        // Increment progress smoothly with a realistic jitter
        progress += Math.random() * 16 + 8;
        if (progress >= 100) progress = 100;

        if (progressFill) {
            progressFill.style.width = progress + '%';
        }

        if (loaderText && progress > (textIndex + 1) * 20 && textIndex < loadingTexts.length - 1) {
            textIndex++;
            loaderText.textContent = loadingTexts[textIndex];
        }

        if (progress >= 100) {
            clearInterval(loadingInterval);
            setTimeout(() => {
                document.body.classList.add('loaded');
                // Ensure loading screen is completely removed from DOM flow after transition
                setTimeout(() => {
                    if (loadingScreen) {
                        loadingScreen.style.display = 'none';
                    }
                }, 650);
            }, 300);
        }
    }, 180);
}

// 2. Floating Cyber Particles Background
function initParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;

    const count = 30;
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.setProperty('--duration', (Math.random() * 7 + 5) + 's');
        particle.style.setProperty('--float-delay', (Math.random() * 4) + 's');
        const size = (Math.random() * 3 + 1.5) + 'px';
        particle.style.width = size;
        particle.style.height = size;
        particlesContainer.appendChild(particle);
    }
}

// 3. Staggered Scroll & Element Entrance Observer
function initScrollAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-up, .fade-left, .fade-right, .scale-in, .table-row-animate').forEach(el => {
        observer.observe(el);
    });
}

// 4. Form Submit Scanning Feedback & Filebox Enhancements
function initFormScan() {
    const scanForm = document.getElementById('scanForm');
    const fileInput = document.getElementById('fileInput');
    const filebox = document.getElementById('filebox');
    const fileboxTitle = document.getElementById('fileboxTitle');
    const fileboxDesc = document.getElementById('fileboxDesc');

    if (fileInput && filebox) {
        // Handle file change
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                filebox.classList.add('has-file');
                if (fileboxTitle) fileboxTitle.textContent = file.name;
                if (fileboxDesc) fileboxDesc.textContent = `Selected CSV · ${sizeMB} MB · Click or drag to change`;
            } else {
                filebox.classList.remove('has-file');
                if (fileboxTitle) fileboxTitle.textContent = 'Select traffic CSV';
                if (fileboxDesc) fileboxDesc.textContent = 'Drag & drop or click to browse · CSV only · up to 100 MB';
            }
        });

        // Drag & drop visual feedback
        ['dragenter', 'dragover'].forEach(eventName => {
            filebox.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                filebox.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            filebox.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                filebox.classList.remove('dragover');
            });
        });
    }

    if (scanForm) {
        scanForm.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                btn.innerHTML = '<span class="spinner"></span> Analyzing Traffic...';
                btn.disabled = true;
            }
        });
    }
}
