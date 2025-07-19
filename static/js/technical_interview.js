// Technical Interview JavaScript - Updated for new structure

document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    const difficultyButtons = document.querySelectorAll('.difficulty-btn');
    const questionItems = document.querySelectorAll('.question-item');
    const codeEditor = document.getElementById('codeEditor');
    const languageSelect = document.getElementById('languageSelect');
    const analyzeButton = document.getElementById('analyzeCode');
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFile');
    const analyzeResumeBtn = document.getElementById('analyzeResume');
    
    let selectedQuestion = null;
    let selectedDifficulty = 'medium';

    // Initialize
    init();

    function init() {
        if (analyzeButton) analyzeButton.disabled = true;
        updateCodePlaceholder('python');
        
        // Debug logging to check if elements exist
        console.log('Elements found:');
        console.log('- difficultyButtons:', difficultyButtons.length);
        console.log('- questionItems:', questionItems.length);
        console.log('- codeEditor:', !!codeEditor);
        console.log('- languageSelect:', !!languageSelect);
        console.log('- analyzeButton (code):', !!analyzeButton);
        console.log('- uploadArea:', !!uploadArea);
        console.log('- fileInput:', !!fileInput);
        console.log('- analyzeResumeBtn:', !!analyzeResumeBtn);
        
        setupEventListeners();
    }

    function setupEventListeners() {
        // Difficulty selection
        difficultyButtons.forEach(btn => {
            btn.addEventListener('click', handleDifficultyChange);
        });

        // Question selection
        questionItems.forEach(item => {
            item.addEventListener('click', handleQuestionSelection);
        });

        // Language change
        if (languageSelect) {
            languageSelect.addEventListener('change', handleLanguageChange);
        }

        // Code analysis
        if (analyzeButton) {
            analyzeButton.addEventListener('click', handleCodeAnalysis);
        }

        // File upload
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
            fileInput.addEventListener('change', handleFileSelect);
        }

        // Resume analysis
        if (analyzeResumeBtn) {
            analyzeResumeBtn.addEventListener('click', handleResumeAnalysis);
        }
    }

    function handleDifficultyChange() {
        difficultyButtons.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedDifficulty = this.getAttribute('data-difficulty');
        console.log('Selected difficulty:', selectedDifficulty);
    }

    function handleQuestionSelection() {
        questionItems.forEach(q => q.classList.remove('selected'));
        this.classList.add('selected');
        selectedQuestion = this.getAttribute('data-question');
        console.log('Selected question:', selectedQuestion);
        
        // Enable code analysis
        if (analyzeButton) {
            analyzeButton.disabled = false;
        }
    }

    function handleLanguageChange() {
        const language = this.value;
        updateCodePlaceholder(language);
    }

    function updateCodePlaceholder(language) {
        if (!codeEditor) return;
        
        const placeholders = {
            python: `# Write your Python code here
def solution():
    """
    Your implementation here
    Consider time complexity and edge cases
    """
    pass`,
            javascript: `// Write your JavaScript code here
function solution() {
    /*
    Your implementation here
    Consider time complexity and edge cases
    */
}`,
            java: `// Write your Java code here
public class Solution {
    public void solution() {
        /*
        Your implementation here
        Consider time complexity and edge cases
        */
    }
}`,
            cpp: `// Write your C++ code here
#include <iostream>
using namespace std;

class Solution {
public:
    void solution() {
        /*
        Your implementation here
        Consider time complexity and edge cases
        */
    }
};`,
            go: `// Write your Go code here
package main

import "fmt"

func solution() {
    /*
    Your implementation here
    Consider time complexity and edge cases
    */
}`
        };
        
        codeEditor.placeholder = placeholders[language] || placeholders.python;
    }

    function handleCodeAnalysis() {
        const code = codeEditor.value.trim();
        const language = languageSelect.value;
        
        if (!code) {
            showNotification('Please write some code first!', 'warning');
            return;
        }
        
        if (!selectedQuestion) {
            showNotification('Please select a question first!', 'warning');
            return;
        }
        
        // Show loading state
        setButtonLoading(this, 'Analyzing...');
        
        // Make actual API call
        fetch('/interview/api/analyze-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                code: code,
                language: language,
                question: selectedQuestion
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showCodeAnalysisResults(data.feedback);
            } else {
                showNotification(data.error || 'Error analyzing code', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error analyzing code. Please try again.', 'danger');
        })
        .finally(() => {
            resetButtonLoading(this, 'Analyze with AI', 'fas fa-brain');
        });
    }

    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave() {
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    }

    function handleFileSelect() {
        if (this.files.length > 0) {
            handleFileUpload(this.files[0]);
        }
    }

    function handleFileUpload(file) {
        if (!validateFile(file)) {
            return;
        }
        
        // Update upload area
        uploadArea.innerHTML = `
            <div class="upload-content">
                <i class="fas fa-file-check fa-3x text-success mb-3"></i>
                <h5>${file.name}</h5>
                <p class="text-muted">File ready for analysis</p>
            </div>
        `;
        
        if (analyzeResumeBtn) {
            analyzeResumeBtn.style.display = 'inline-flex';
        }
    }

    function validateFile(file) {
        const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            showNotification('Please upload a PDF, DOC, DOCX, or TXT file.', 'danger');
            return false;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB limit to match backend
            showNotification('File size should be less than 10MB.', 'danger');
            return false;
        }
        
        return true;
    }

    function handleResumeAnalysis() {
        const fileInput = document.getElementById('resumeFile');
        const analyzeButton = document.getElementById('analyzeResume');
        
        // Debug logging
        console.log('File input element:', fileInput);
        console.log('Analyze button:', analyzeButton);
        
        if (!fileInput) {
            showNotification('File input not found. Please refresh the page and try again.', 'danger');
            return;
        }
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showNotification('Please select a resume file first!', 'warning');
            return;
        }
        
        const file = fileInput.files[0];
        console.log('Selected file:', file.name);
        
        const formData = new FormData();
        formData.append('resume', file);
        
        if (analyzeButton) {
            setButtonLoading(analyzeButton, 'Analyzing Resume...');
        }
        
        fetch('/interview/api/upload-resume/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showResumeAnalysisResults(data.feedback);
                // After resume analysis, generate custom questions
                generateCustomQuestions(file);
            } else {
                showNotification(data.error || 'Error analyzing resume', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error analyzing resume. Please try again.', 'danger');
        })
        .finally(() => {
            if (analyzeButton) {
                resetButtonLoading(analyzeButton, 'Analyze Resume', 'fas fa-search');
            }
        });
    }
    
    function generateCustomQuestions(file) {
        const formData = new FormData();
        formData.append('resume', file);
        formData.append('difficulty', selectedDifficulty);
        
        fetch('/interview/api/generate-questions/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateQuestionsDisplay(data.questions);
                showNotification('Custom questions generated based on your resume!', 'success');
            } else {
                console.error('Question generation failed:', data.error);
            }
        })
        .catch(error => {
            console.error('Error generating questions:', error);
        });
    }

    function setButtonLoading(button, text) {
        button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${text}`;
        button.disabled = true;
    }

    function resetButtonLoading(button, text, iconClass) {
        button.innerHTML = `<i class="${iconClass} mr-2"></i>${text}`;
        button.disabled = false;
    }

    function showCodeAnalysisResults(feedback) {
        const resultsSection = document.getElementById('resultsSection');
        const analysisResults = document.getElementById('analysisResults');
        
        if (!resultsSection || !analysisResults) return;
        
        analysisResults.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-code mr-2"></i>Code Quality Score</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-${getScoreColor(feedback.score)}" style="width: ${feedback.score * 10}%"></div>
                    </div>
                    <small class="text-muted">${feedback.score}/10</small>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-exclamation-triangle mr-2"></i>Issues Found</h6>
                    <span class="badge badge-${feedback.issues.length > 0 ? 'warning' : 'success'}">
                        ${feedback.issues.length} issues
                    </span>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <h6><i class="fas fa-lightbulb mr-2"></i>Suggestions</h6>
                    <ul class="list-unstyled">
                        ${feedback.suggestions.map(suggestion => `
                            <li><i class="fas fa-check text-info mr-2"></i>${suggestion}</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-star mr-2"></i>Best Practices</h6>
                    <ul class="list-unstyled">
                        ${feedback.best_practices.map(practice => `
                            <li><i class="fas fa-check text-success mr-2"></i>${practice}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            ${feedback.issues.length > 0 ? `
            <div class="row mt-3">
                <div class="col-12">
                    <h6><i class="fas fa-bug mr-2"></i>Critical Issues</h6>
                    <ul class="list-unstyled">
                        ${feedback.issues.map(issue => `
                            <li><i class="fas fa-exclamation text-warning mr-2"></i>${issue}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            ` : ''}
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showResumeAnalysisResults(feedback) {
        const resultsSection = document.getElementById('resultsSection');
        const analysisResults = document.getElementById('analysisResults');
        
        if (!resultsSection || !analysisResults) return;
        
        analysisResults.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <h6><i class="fas fa-chart-line mr-2"></i>Overall Score</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-${getScoreColor(feedback.score)}" style="width: ${feedback.score * 10}%"></div>
                    </div>
                    <small class="text-muted">${feedback.score}/10</small>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-robot mr-2"></i>ATS Score</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-${getATSScoreColor(feedback.ats_score)}" style="width: ${feedback.ats_score}%"></div>
                    </div>
                    <small class="text-muted">${feedback.ats_score}/100</small>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-user-graduate mr-2"></i>Experience Level</h6>
                    <span class="badge badge-primary">${feedback.experience_level || 'Mid-Level'}</span>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <h6><i class="fas fa-thumbs-up mr-2"></i>Strengths</h6>
                    <ul class="list-unstyled">
                        ${feedback.strengths.map(strength => `
                            <li><i class="fas fa-check text-success mr-2"></i>${strength}</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-tools mr-2"></i>Areas for Improvement</h6>
                    <ul class="list-unstyled">
                        ${feedback.improvements.map(improvement => `
                            <li><i class="fas fa-arrow-up text-warning mr-2"></i>${improvement}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            ${feedback.skills_identified && feedback.skills_identified.length > 0 ? `
            <div class="row mt-3">
                <div class="col-12">
                    <h6><i class="fas fa-code mr-2"></i>Skills Identified</h6>
                    <div class="d-flex flex-wrap">
                        ${feedback.skills_identified.map(skill => `
                            <span class="badge badge-secondary mr-1 mb-1">${skill}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
            ` : ''}
            <div class="row mt-3">
                <div class="col-12">
                    <h6><i class="fas fa-lightbulb mr-2"></i>Recommendations</h6>
                    <ul class="list-unstyled">
                        ${feedback.recommendations.map(rec => `
                            <li><i class="fas fa-star text-info mr-2"></i>${rec}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    function updateQuestionsDisplay(questions) {
        const questionsContainer = document.getElementById('questionsContainer');
        if (!questionsContainer || !questions || questions.length === 0) return;
        
        questionsContainer.innerHTML = questions.map((q, index) => `
            <div class="question-item" data-question="custom_${index}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${q.category}</h6>
                        <p class="mb-0 text-muted">${q.question}</p>
                        <small class="text-info">${q.explanation}</small>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Re-attach event listeners to new question items
        const newQuestionItems = questionsContainer.querySelectorAll('.question-item');
        newQuestionItems.forEach(item => {
            item.addEventListener('click', handleQuestionSelection);
        });
    }
    
    function getScoreColor(score) {
        if (score >= 8) return 'success';
        if (score >= 6) return 'warning';
        return 'danger';
    }
    
    function getATSScoreColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    // Use the showNotification function from main.js if available
    if (typeof showNotification === 'undefined') {
        window.showNotification = function(message, type) {
            alert(message);
        };
    }
    
    // CSRF token helper function
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
});