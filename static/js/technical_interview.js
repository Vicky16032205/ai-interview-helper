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
        
        // Simulate AI analysis
        setTimeout(() => {
            showAnalysisResults(code, language, selectedQuestion);
            resetButtonLoading(this, 'Analyze with AI', 'fas fa-brain');
        }, 2000);
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
        
        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            showNotification('File size should be less than 5MB.', 'danger');
            return false;
        }
        
        return true;
    }

    function handleResumeAnalysis() {
        setButtonLoading(this, 'Analyzing Resume...');
        
        // Simulate resume analysis
        setTimeout(() => {
            showResumeAnalysis();
            resetButtonLoading(this, 'Analyze Resume', 'fas fa-search');
        }, 2000);
    }

    function setButtonLoading(button, text) {
        button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${text}`;
        button.disabled = true;
    }

    function resetButtonLoading(button, text, iconClass) {
        button.innerHTML = `<i class="${iconClass} mr-2"></i>${text}`;
        button.disabled = false;
    }

    function showAnalysisResults(code, language, question) {
        const resultsSection = document.getElementById('resultsSection');
        const analysisResults = document.getElementById('analysisResults');
        
        if (!resultsSection || !analysisResults) return;
        
        analysisResults.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-code mr-2"></i>Code Quality</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-success" style="width: 85%"></div>
                    </div>
                    <small class="text-muted">85% - Good structure and readability</small>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-tachometer-alt mr-2"></i>Time Complexity</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-warning" style="width: 70%"></div>
                    </div>
                    <small class="text-muted">70% - Can be optimized further</small>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6><i class="fas fa-lightbulb mr-2"></i>Suggestions</h6>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-check text-success mr-2"></i>Good use of ${language} conventions</li>
                        <li><i class="fas fa-info text-info mr-2"></i>Consider edge cases for empty inputs</li>
                        <li><i class="fas fa-exclamation text-warning mr-2"></i>Algorithm complexity could be improved</li>
                    </ul>
                </div>
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showResumeAnalysis() {
        const resultsSection = document.getElementById('resultsSection');
        const analysisResults = document.getElementById('analysisResults');
        
        if (!resultsSection || !analysisResults) return;
        
        analysisResults.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <h6><i class="fas fa-user-graduate mr-2"></i>Experience Level</h6>
                    <div class="badge badge-primary">Mid-Level</div>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-code mr-2"></i>Top Skills</h6>
                    <div class="d-flex flex-wrap">
                        <span class="badge badge-secondary mr-1 mb-1">Python</span>
                        <span class="badge badge-secondary mr-1 mb-1">JavaScript</span>
                        <span class="badge badge-secondary mr-1 mb-1">System Design</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-chart-line mr-2"></i>Match Score</h6>
                    <div class="progress">
                        <div class="progress-bar bg-success" style="width: 90%"></div>
                    </div>
                    <small class="text-muted">90% match for technical roles</small>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6><i class="fas fa-question-circle mr-2"></i>Recommended Questions</h6>
                    <div class="list-group">
                        <div class="list-group-item">Database optimization strategies</div>
                        <div class="list-group-item">RESTful API design patterns</div>
                        <div class="list-group-item">Microservices communication</div>
                    </div>
                </div>
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Use the showNotification function from main.js if available
    if (typeof showNotification === 'undefined') {
        window.showNotification = function(message, type) {
            alert(message);
        };
    }
});