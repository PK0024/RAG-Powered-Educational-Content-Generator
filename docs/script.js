/**
 * RAG-Powered Educational Content Generator
 * Professional Portfolio - Interactive JavaScript
 * Academic Project - Northeastern University
 */

// ===== Smooth Scroll Navigation =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));

        if (target) {
            const navHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = target.offsetTop - navHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ===== Navbar Scroll Effect =====
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    // Add shadow on scroll
    if (currentScroll > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
});

// ===== Intersection Observer for Fade-in Animations =====
const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -100px 0px'
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');

            // Stop observing once animated
            fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all major elements
const elementsToAnimate = document.querySelectorAll(
    '.feature-card, .impl-card, .resource-card, .tech-category-card, ' +
    '.achievement-card, .architecture-layer, .results-category'
);

elementsToAnimate.forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(30px)';
    fadeInObserver.observe(element);
});

// ===== Active Navigation Link =====
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (window.pageYOffset >= (sectionTop - 200)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').substring(1) === current) {
            link.classList.add('active');
        }
    });
});

// ===== Dynamic Counter Animation =====
const animateCounter = (element, target) => {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 30);
};

// Animate metrics when they come into view
const metricObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const metricValue = entry.target.querySelector('.metric-value');
            if (metricValue && !metricValue.classList.contains('animated')) {
                const targetValue = parseInt(metricValue.textContent);
                if (!isNaN(targetValue)) {
                    metricValue.classList.add('animated');
                    animateCounter(metricValue, targetValue);
                }
            }

            const statNumber = entry.target.querySelector('.stat-number');
            if (statNumber && !statNumber.classList.contains('animated')) {
                const targetValue = parseInt(statNumber.textContent);
                if (!isNaN(targetValue)) {
                    statNumber.classList.add('animated');
                    animateCounter(statNumber, targetValue);
                }
            }
        }
    });
}, { threshold: 0.5 });

// Observe all metric items
document.querySelectorAll('.metric-item, .stat-card').forEach(item => {
    metricObserver.observe(item);
});

// ===== Pipeline Step Sequential Animation =====
const pipelineSteps = document.querySelectorAll('.pipeline-step');

const pipelineObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            pipelineSteps.forEach((step, index) => {
                setTimeout(() => {
                    step.style.opacity = '1';
                    step.style.transform = 'translateY(0)';
                }, index * 100);
            });
            pipelineObserver.disconnect();
        }
    });
}, { threshold: 0.3 });

if (pipelineSteps.length > 0) {
    pipelineSteps.forEach(step => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(20px)';
        step.style.transition = 'all 0.5s ease-out';
    });

    pipelineObserver.observe(document.querySelector('.pipeline-flow'));
}

// ===== Table Row Highlight Effect =====
document.querySelectorAll('.results-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', function () {
        this.style.backgroundColor = '#e3f2fd';
        this.style.transition = 'background-color 0.2s ease';
    });

    row.addEventListener('mouseleave', function () {
        this.style.backgroundColor = '';
    });
});

// ===== Copy Code Snippets (if any code blocks exist) =====
document.querySelectorAll('pre code').forEach(block => {
    const button = document.createElement('button');
    button.textContent = 'Copy';
    button.className = 'copy-btn';

    button.addEventListener('click', () => {
        navigator.clipboard.writeText(block.textContent).then(() => {
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        });
    });

    block.parentElement.style.position = 'relative';
    block.parentElement.appendChild(button);
});

// ===== External Link Icon Addition =====
document.querySelectorAll('a[target="_blank"]').forEach(link => {
    if (!link.querySelector('svg')) {
        const icon = document.createElement('span');
        icon.innerHTML = ' ↗';
        icon.style.fontSize = '0.875em';
        icon.style.opacity = '0.7';
        link.appendChild(icon);
    }
});

// ===== Loading State Handler =====
window.addEventListener('load', () => {
    document.body.classList.add('loaded');

    // Trigger hero animation
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(30px)';
        heroContent.style.transition = 'all 0.8s ease-out';

        setTimeout(() => {
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        }, 100);
    }
});

// ===== Scroll Progress Indicator =====
const createScrollIndicator = () => {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    indicator.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #1976d2, #42a5f5);
        z-index: 9999;
        transition: width 0.1s ease-out;
    `;
    document.body.appendChild(indicator);

    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.pageYOffset / windowHeight) * 100;
        indicator.style.width = scrolled + '%';
    });
};

// Initialize scroll indicator
createScrollIndicator();

// ===== Performance Metrics Animation =====
const animatePercentage = (element) => {
    const text = element.textContent;
    const match = text.match(/(\d+)%/);

    if (match) {
        const target = parseInt(match[1]);
        let current = 0;
        const increment = target / 30;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = text;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + '%';
            }
        }, 40);
    }
};

// Animate achievement percentages
const achievementObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const strongElement = entry.target.querySelector('strong');
            if (strongElement && strongElement.textContent.includes('%') && !strongElement.classList.contains('animated')) {
                strongElement.classList.add('animated');
                animatePercentage(strongElement);
            }
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.achievement-card').forEach(card => {
    achievementObserver.observe(card);
});

// ===== Console Easter Egg for Developers =====
console.log('%c🎓 RAG-Powered Educational Content Generator', 'font-size: 20px; font-weight: bold; color: #1976d2;');
console.log('%cAcademic Project - Northeastern University', 'font-size: 14px; color: #666;');
console.log('%cBuilt with: FastAPI • Streamlit • LlamaIndex • Pinecone • OpenAI', 'font-size: 12px; color: #999;');
console.log('%cInterested in the code? Check out: https://github.com/PK0024/RAG-Educational-Content-Generator', 'font-size: 12px; color: #1976d2;');

// ===== Parallax Effect on Hero =====
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');

    if (hero && scrolled < hero.offsetHeight) {
        hero.style.transform = `translateY(${scrolled * 0.4}px)`;
        hero.style.opacity = 1 - (scrolled / hero.offsetHeight) * 0.5;
    }
});

// ===== Feature Card Tilt Effect (Optional) =====
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});

// ===== Auto-update Copyright Year =====
const currentYear = new Date().getFullYear();
document.querySelectorAll('.footer-bottom p').forEach(p => {
    if (p.textContent.includes('2024')) {
        p.textContent = p.textContent.replace('2024', currentYear);
    }
});

// ===== Lazy Loading for Images (if added later) =====
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ===== Accessibility: Skip to Content Link =====
const createSkipLink = () => {
    const skipLink = document.createElement('a');
    skipLink.href = '#abstract';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Skip to content';
    skipLink.style.cssText = `
        position: absolute;
        top: -100px;
        left: 0;
        background: var(--blue-primary);
        color: white;
        padding: 1rem 2rem;
        text-decoration: none;
        z-index: 10000;
        transition: top 0.3s;
    `;

    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });

    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-100px';
    });

    document.body.prepend(skipLink);
};

createSkipLink();

// ===== Initialize on DOM Load =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('RAG Educational Content Generator - Portfolio Loaded');

    // Add initial load animation class
    document.body.classList.add('loaded');

    // Log page load time for optimization
    if (window.performance) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    }
});