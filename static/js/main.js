// Main JavaScript file for general functionality

$(document).ready(function() {
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });

    // Add animation class to elements when they come into view
    const animateElements = function() {
        $('.animate-on-scroll').each(function() {
            const elementTop = $(this).offset().top;
            const elementBottom = elementTop + $(this).outerHeight();
            const viewportTop = $(window).scrollTop();
            const viewportBottom = viewportTop + $(window).height();

            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('animate__animated animate__fadeInUp');
            }
        });
    };

    $(window).on('scroll', animateElements);
    animateElements(); // Check on load

    // Custom file input
    $('.custom-file-input').on('change', function() {
        const fileName = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName || 'Choose file');
    });

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Initialize popovers
    $('[data-toggle="popover"]').popover();
});

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999;">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(() => {
        notification.alert('close');
    }, 5000);
}

// API call utility function
function apiCall(url, method = 'GET', data = null) {
    const options = {
        url: url,
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };

    if (data) {
        options.data = JSON.stringify(data);
    }

    return $.ajax(options);
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Format feedback display
function formatFeedback(feedback) {
    let html = '<div class="feedback-content">';
    
    if (feedback.score !== undefined) {
        const scoreColor = feedback.score >= 8 ? 'success' : feedback.score >= 6 ? 'warning' : 'danger';
        html += `<div class="text-center mb-4">
                    <div class="feedback-score text-${scoreColor}" style="font-size: 3rem; font-weight: bold;">${feedback.score}/10</div>
                    <p class="text-muted">Overall Score</p>
                 </div>`;
    }
    
    // HR Interview specific sections
    if (feedback.transcription !== undefined && feedback.transcription !== null) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-microphone text-info mr-2"></i>Audio Transcription</h6>
                    <div class="alert alert-light border">
                        <p class="mb-2"><strong>What we heard:</strong></p>
                        <p class="mb-0 font-italic">"${feedback.transcription}"</p>
                        <small class="text-muted">✓ Transcribed using AssemblyAI</small>
                    </div>
                 </div>`;
    }
    
    if (feedback.communication !== undefined && feedback.communication !== null) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-comments text-primary mr-2"></i>Communication Assessment</h6>
                    <p class="mb-0">${feedback.communication}</p>
                 </div>`;
    }
    
    if (feedback.star_usage !== undefined && feedback.star_usage !== null) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-list text-info mr-2"></i>STAR Method Usage</h6>
                    <p class="mb-0">${feedback.star_usage}</p>
                 </div>`;
    }
    
    if (feedback.tone_delivery !== undefined && feedback.tone_delivery !== null) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-volume-up text-secondary mr-2"></i>Tone & Delivery</h6>
                    <p class="mb-0">${feedback.tone_delivery}</p>
                 </div>`;
    }
    
    // Display different feedback sections
    const sections = [
        { key: 'issues', title: 'Issues Found', icon: 'fa-exclamation-triangle', color: 'danger' },
        { key: 'suggestions', title: 'Suggestions', icon: 'fa-lightbulb', color: 'info' },
        { key: 'best_practices', title: 'Best Practices', icon: 'fa-check-circle', color: 'success' },
        { key: 'strengths', title: 'Key Strengths', icon: 'fa-star', color: 'success' },
        { key: 'improvements', title: 'Areas for Improvement', icon: 'fa-arrow-up', color: 'warning' },
        { key: 'recommendations', title: 'Recommendations', icon: 'fa-thumbs-up', color: 'primary' }
    ];
    
    sections.forEach(section => {
        if (feedback[section.key] && Array.isArray(feedback[section.key]) && feedback[section.key].length > 0) {
            html += `<div class="mb-3">
                        <h6><i class="fas ${section.icon} text-${section.color} mr-2"></i>${section.title}</h6>
                        <ul class="mb-0">`;
            feedback[section.key].forEach(item => {
                if (item && item.trim() !== '') {
                    html += `<li>${item}</li>`;
                }
            });
            html += '</ul></div>';
        }
    });
    
    // Add special sections for resume analysis
    if (feedback.ats_score !== undefined) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-robot text-info mr-2"></i>ATS Compatibility</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-info" style="width: ${feedback.ats_score}%"></div>
                    </div>
                    <p class="mb-0">${feedback.ats_score}/100 - Your resume is ${feedback.ats_score >= 80 ? 'well' : feedback.ats_score >= 60 ? 'moderately' : 'poorly'} optimized for ATS systems</p>
                 </div>`;
    }
    
    if (feedback.formatting_score !== undefined) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-format-text text-secondary mr-2"></i>Formatting Quality</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-secondary" style="width: ${feedback.formatting_score * 10}%"></div>
                    </div>
                    <p class="mb-0">${feedback.formatting_score}/10</p>
                 </div>`;
    }
    
    if (feedback.content_score !== undefined) {
        html += `<div class="mb-3">
                    <h6><i class="fas fa-file-text text-success mr-2"></i>Content Quality</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-success" style="width: ${feedback.content_score * 10}%"></div>
                    </div>
                    <p class="mb-0">${feedback.content_score}/10</p>
                 </div>`;
    }
    
    // Add any additional feedback fields, excluding HR-specific ones we already handled
    const excludedKeys = [
        'score', 'issues', 'suggestions', 'best_practices', 'strengths', 'improvements', 
        'recommendations', 'error', 'ats_score', 'formatting_score', 'content_score', 
        'missing_sections', 'communication', 'star_usage', 'tone_delivery'
    ];
    
    Object.keys(feedback).forEach(key => {
        if (!excludedKeys.includes(key) && feedback[key] !== null && feedback[key] !== undefined) {
            const displayValue = Array.isArray(feedback[key]) ? 
                feedback[key].join(', ') : feedback[key];
                
            if (displayValue && displayValue.toString().trim() !== '') {
                html += `<div class="mb-3">
                            <h6><i class="fas fa-info-circle text-secondary mr-2"></i>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
                            <p class="mb-0">${displayValue}</p>
                         </div>`;
            }
        }
    });
    
    // Show error message if present
    if (feedback.error) {
        html += `<div class="alert alert-danger mt-3">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    <strong>Analysis Error:</strong> ${feedback.error}
                 </div>`;
    }
    
    html += '</div>';
    return html;
}