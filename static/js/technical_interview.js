// Technical Interview JavaScript - Enhanced with Resume Upload
class TechnicalInterview {
    constructor() {
        this.resumeAnalysis = null;
        this.currentQuestions = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeElements();
        this.setupOriginalFunctionality();
    }    setupEventListeners() {
        console.log('Setting up event listeners...');
        // Resume upload - handle both interfaces
        const resumeInput = document.getElementById('resume-upload');
        const resumeFile = document.getElementById('resumeFile');
        const uploadArea = document.getElementById('uploadArea');
        const analyzeResumeBtn = document.getElementById('analyzeResume');

        console.log('Elements found:', {
            resumeInput: !!resumeInput,
            resumeFile: !!resumeFile,
            uploadArea: !!uploadArea,
            analyzeResumeBtn: !!analyzeResumeBtn
        });

        // New interface (Step 1)
        if (resumeInput) {
            console.log('Adding change listener to resume-upload');
            resumeInput.addEventListener('change', this.handleResumeUpload.bind(this));
        }

        // Original drag-and-drop interface
        if (resumeFile) {
            resumeFile.addEventListener('change', this.handleResumeUpload.bind(this));
        }

        // Make upload area clickable
        if (uploadArea) {
            uploadArea.addEventListener('click', () => {
                if (resumeFile) {
                    resumeFile.click();
                }
            });

            // Handle drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleResumeUploadDirect(files[0]);
                }
            });
        }

        // Analyze resume button (original interface)
        if (analyzeResumeBtn) {
            analyzeResumeBtn.addEventListener('click', () => {
                if (resumeFile && resumeFile.files.length > 0) {
                    this.handleResumeUploadDirect(resumeFile.files[0]);
                }
            });
        }

        // Generate questions button
        const generateBtn = document.getElementById('generate-questions-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', this.generateQuestions.bind(this));
        }

        // Start interview button
        const startBtn = document.getElementById('start-interview-btn');
        if (startBtn) {
            startBtn.addEventListener('click', this.startInterview.bind(this));
        }
    }

    initializeElements() {
        // Check which interface is being used
        const stepUpload = document.getElementById('step-upload');
        const uploadArea = document.getElementById('uploadArea');
        
        if (stepUpload) {
            // New step-based interface
            this.showStep('upload');
        } else if (uploadArea) {
            // Original drag-and-drop interface
            console.log('Using original drag-and-drop interface');
        }
    }

    async handleResumeUpload(event) {
        console.log('Resume upload triggered:', event.target.id);
        const file = event.target.files[0];
        if (!file) {
            console.log('No file selected');
            return;
        }
        
        console.log('File selected:', file.name, 'Size:', file.size);
        this.handleResumeUploadDirect(file);
    }

    async handleResumeUploadDirect(file) {
        console.log('handleResumeUploadDirect called with file:', file.name);
        this.showLoading('Analyzing resume...');

        // Determine which interface we're using
        const isStepInterface = document.getElementById('step-upload') !== null;
        console.log('Using step interface:', isStepInterface);
        
        if (!isStepInterface) {
            // Show analyze button for original interface
            const analyzeBtn = document.getElementById('analyzeResume');
            if (analyzeBtn) {
                analyzeBtn.style.display = 'inline-block';
            }

            // Update upload area text to show file selected
            const uploadArea = document.getElementById('uploadArea');
            if (uploadArea) {
                const uploadContent = uploadArea.querySelector('.upload-content');
                if (uploadContent) {
                    uploadContent.innerHTML = `
                        <i class="fas fa-file-check fa-3x text-success mb-3"></i>
                        <h5>${file.name}</h5>
                        <p class="text-muted">File selected. Click "Analyze Resume" to proceed.</p>
                    `;
                }
            }
        } else {
            // For step interface, show file name in the card
            const stepUploadCard = document.querySelector('#step-upload .card-body');
            if (stepUploadCard) {
                const existingStatus = stepUploadCard.querySelector('.file-status');
                if (existingStatus) {
                    existingStatus.remove();
                }
                
                const statusDiv = document.createElement('div');
                statusDiv.className = 'file-status alert alert-info mt-2';
                statusDiv.innerHTML = `<i class="fas fa-file-check mr-2"></i>File selected: <strong>${file.name}</strong> - Analyzing...`;
                stepUploadCard.appendChild(statusDiv);
            }
        }

        const formData = new FormData();
        formData.append('resume', file);

        try {
            const response = await fetch('/interview/upload-resume/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                console.log('Resume upload successful, analysis data:', data.analysis);
                try {
                    this.resumeAnalysis = JSON.parse(data.analysis);
                    console.log('Parsed analysis:', this.resumeAnalysis);
                    
                    // Display the analysis in the dedicated section
                    this.displayResumeAnalysis();
                    
                    // Update status in step interface
                    if (isStepInterface) {
                        console.log('Updating step interface status');
                        const stepUploadCard = document.querySelector('#step-upload .card-body');
                        if (stepUploadCard) {
                            const statusDiv = stepUploadCard.querySelector('.file-status');
                            if (statusDiv) {
                                statusDiv.className = 'file-status alert alert-success mt-2';
                                statusDiv.innerHTML = `<i class="fas fa-check-circle mr-2"></i>Resume analyzed successfully! Check the detailed analysis below.`;
                            }
                        }
                        // Also show the questions step
                        this.showStep('questions');
                    }
                    
                    // For original interface, show results section
                    const resultsSection = document.getElementById('resultsSection');
                    if (resultsSection && !isStepInterface) {
                        console.log('Showing original results section');
                        resultsSection.style.display = 'block';
                        resultsSection.scrollIntoView({ behavior: 'smooth' });
                    }
                } catch (parseError) {
                    console.error('JSON Parse Error:', parseError);
                    console.error('Analysis data:', data.analysis);
                    this.showError('Error parsing resume analysis. Please try again.');
                }
            } else {
                this.showError(data.error || 'Failed to analyze resume');
            }
        } catch (error) {
            this.showError('Error uploading resume: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayResumeAnalysis() {
        console.log('displayResumeAnalysis called');
        
        // Try to find the dedicated analysis results section first
        let analysisDiv = document.getElementById('resume-analysis-results');
        let contentDiv = document.getElementById('resume-analysis-content');
        let isStepInterface = true;
        let isOriginalInterface = false;
        
        // Fallback to other sections if needed
        if (!analysisDiv) {
            analysisDiv = document.getElementById('resume-analysis'); // Step-based interface
            contentDiv = analysisDiv;
        }
        
        if (!analysisDiv) {
            analysisDiv = document.getElementById('analysisResults'); // Original interface
            contentDiv = analysisDiv;
            isStepInterface = false;
            isOriginalInterface = true;
        }
        
        console.log('Analysis div found:', !!analysisDiv, 'Content div:', !!contentDiv);
        console.log('Resume analysis data:', this.resumeAnalysis);
        
        if (!analysisDiv || !this.resumeAnalysis) {
            console.error('Analysis container not found or no analysis data', {
                analysisDiv: !!analysisDiv,
                resumeAnalysis: !!this.resumeAnalysis
            });
            return;
        }

        // Populate Technical Skills
        const technicalSkillsDiv = document.getElementById('technical-skills');
        if (technicalSkillsDiv && this.resumeAnalysis.technical_skills) {
            technicalSkillsDiv.innerHTML = this.resumeAnalysis.technical_skills.map(skill => 
                `<span class="skill-tag">${skill}</span>`
            ).join('');
        }

        // Populate Programming Languages  
        const programmingLanguagesDiv = document.getElementById('programming-languages');
        if (programmingLanguagesDiv && this.resumeAnalysis.programming_languages) {
            programmingLanguagesDiv.innerHTML = this.resumeAnalysis.programming_languages.map(lang => 
                `<span class="skill-tag">${lang}</span>`
            ).join('');
        }

        // Populate Experience Level
        const experienceLevelDiv = document.getElementById('experience-level');
        if (experienceLevelDiv && this.resumeAnalysis.experience_level) {
            experienceLevelDiv.innerHTML = `<span class="experience-badge">${this.resumeAnalysis.experience_level}</span>`;
        }

        // Populate Experience Highlights
        const experienceHighlightsDiv = document.getElementById('experience-highlights');
        if (experienceHighlightsDiv && this.resumeAnalysis.key_experience) {
            experienceHighlightsDiv.innerHTML = this.resumeAnalysis.key_experience.map(exp => `
                <div class="highlight-item">
                    <div class="highlight-title">
                        <i class="fas fa-briefcase"></i>
                        ${exp.title}
                    </div>
                    <p class="highlight-description">${exp.description}</p>
                </div>
            `).join('');
        }

        // Populate Focus Areas
        const focusAreasDiv = document.getElementById('focus-areas');
        if (focusAreasDiv && this.resumeAnalysis.recommended_focus) {
            focusAreasDiv.innerHTML = this.resumeAnalysis.recommended_focus.map((focus, index) => {
                // Extract a meaningful title from the focus area text
                let title = 'Focus Area';
                if (focus.toLowerCase().includes('project')) title = 'Project Deep Dive';
                else if (focus.toLowerCase().includes('technical') || focus.toLowerCase().includes('skill')) title = 'Technical Skills';
                else if (focus.toLowerCase().includes('problem') || focus.toLowerCase().includes('solving')) title = 'Problem Solving';
                else if (focus.toLowerCase().includes('team') || focus.toLowerCase().includes('collaboration')) title = 'Teamwork & Collaboration';
                else if (focus.toLowerCase().includes('ai') || focus.toLowerCase().includes('ml') || focus.toLowerCase().includes('concept')) title = 'AI/ML Concepts';
                else if (focus.toLowerCase().includes('programming') || focus.toLowerCase().includes('language')) title = 'Programming Languages';
                else if (focus.toLowerCase().includes('software') || focus.toLowerCase().includes('engineering')) title = 'Software Engineering';
                else title = `Focus Area ${index + 1}`;
                
                return `
                    <div class="focus-area-card">
                        <div class="focus-area-title">
                            <i class="fas fa-arrow-right"></i>
                            ${title}
                        </div>
                        <p class="focus-area-description">${focus}</p>
                    </div>
                `;
            }).join('');
        }

        // Show Analysis Complete message
        const analysisCompleteDiv = document.getElementById('analysis-complete');
        if (analysisCompleteDiv) {
            analysisCompleteDiv.style.display = 'block';
        }
        
        // Show the dedicated analysis section if using it
        if (analysisDiv.id === 'resume-analysis-results') {
            console.log('Making resume-analysis-results visible');
            analysisDiv.style.display = 'block';
            console.log('Display style set to block');
            
            // Smooth scroll to the analysis section
            setTimeout(() => {
                console.log('Scrolling to analysis section');
                analysisDiv.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        } else {
            console.log('Not using dedicated analysis section, using:', analysisDiv.id);
            // For original interface, create fallback HTML
            if (isOriginalInterface) {
                const analysisHtml = `
                    <div class="resume-analysis-container">
                        <div class="analysis-header">
                            <div class="header-content">
                                <div class="header-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="header-text">
                                    <h3 class="mb-1">Resume Analysis Results</h3>
                                    <p class="mb-0">AI-powered insights from your resume</p>
                                </div>
                            </div>
                        </div>
                        <div class="analysis-content">
                            <div class="analysis-section">
                                <div class="section-header">
                                    <i class="fas fa-cogs section-icon"></i>
                                    <h5>Technical Skills</h5>
                                </div>
                                <div class="skills-grid">
                                    ${this.resumeAnalysis.technical_skills.map(skill => 
                                        `<span class="skill-tag">${skill}</span>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="analysis-section">
                                <div class="section-header">
                                    <i class="fas fa-code section-icon"></i>
                                    <h5>Programming Languages</h5>
                                </div>
                                <div class="skills-grid">
                                    ${this.resumeAnalysis.programming_languages.map(lang => 
                                        `<span class="skill-tag">${lang}</span>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="analysis-section full-width">
                                <div class="section-header">
                                    <i class="fas fa-star section-icon"></i>
                                    <h5>Key Experience Highlights</h5>
                                </div>
                                <div class="experience-highlights">
                                    ${this.resumeAnalysis.key_experience.map(exp => `
                                        <div class="highlight-item">
                                            <div class="highlight-title">
                                                <i class="fas fa-briefcase"></i>
                                                ${exp.title}
                                            </div>
                                            <p class="highlight-description">${exp.description}</p>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="analysis-complete">
                                <div class="success-icon">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                                <div class="success-content">
                                    <h6>Analysis Complete!</h6>
                                    <p>Your resume has been successfully analyzed. Generate personalized interview questions.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                contentDiv.innerHTML = analysisHtml;
            }
        }
        
        console.log('Resume analysis display complete');
    }

    async generateQuestions() {
        if (!this.resumeAnalysis) {
            this.showError('Please upload and analyze a resume first');
            return;
        }

        this.showLoading('Generating interview questions...');

        const requestData = {
            skills: this.resumeAnalysis.technical_skills,
            experience_level: this.resumeAnalysis.experience_level,
            count: 10  // Generate 10 questions for full interview
        };

        try {
            const response = await fetch('/interview/generate-questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                try {
                    this.currentQuestions = JSON.parse(data.questions);
                    this.displayQuestions();
                    this.showStep('interview');
                } catch (parseError) {
                    console.error('JSON Parse Error:', parseError);
                    console.error('Questions data:', data.questions);
                    this.showError('Error parsing generated questions. Please try again.');
                }
            } else {
                this.showError(data.error || 'Failed to generate questions');
            }
        } catch (error) {
            this.showError('Error generating questions: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayQuestions() {
        const questionsDiv = document.getElementById('interview-questions');
        if (!questionsDiv || !this.currentQuestions.length) return;

        const html = `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-list-ol mr-2"></i>
                        Your Technical Interview Questions (${this.currentQuestions.length} Questions)
                    </h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-info mb-4">
                        <i class="fas fa-info-circle mr-2"></i>
                        <strong>Instructions:</strong> You'll have ${this.currentQuestions.length} questions to answer. 
                        You can answer via text or voice recording. Take your time to provide detailed, thoughtful responses.
                    </div>
                    
                    <div class="questions-preview">
                        ${this.currentQuestions.map((q, index) => `
                            <div class="question-preview-item mb-3 p-3 border rounded">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="mb-0">
                                        <span class="badge badge-primary mr-2">${index + 1}</span>
                                        <span class="badge badge-${this.getDifficultyColor(q.difficulty)} mr-2">${q.difficulty}</span>
                                        <span class="badge badge-outline-secondary">${q.type}</span>
                                    </h6>
                                    <small class="text-muted">
                                        <i class="fas fa-clock mr-1"></i>${q.expected_duration}
                                    </small>
                                </div>
                                <p class="mb-0 text-dark">${q.question}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="interview-start-section mt-4 p-4 bg-light rounded text-center">
                        <h5 class="text-primary mb-3">
                            <i class="fas fa-play-circle mr-2"></i>Ready to Start Your Interview?
                        </h5>
                        <p class="text-muted mb-4">
                            You'll be taken to a dedicated interview session where you can focus entirely on answering questions.
                            The session will track your progress and generate a comprehensive report at the end.
                        </p>
                        <button id="start-interview-btn" class="btn btn-success btn-lg px-5">
                            <i class="fas fa-rocket mr-2"></i>Start Interview Session
                        </button>
                    </div>
                </div>
            </div>
        `;

        questionsDiv.innerHTML = html;
        
        // Re-attach event listener for start button (since we replaced the HTML)
        const startBtn = document.getElementById('start-interview-btn');
        if (startBtn) {
            startBtn.addEventListener('click', this.startInterview.bind(this));
        }
    }

    getDifficultyColor(difficulty) {
        switch (difficulty.toLowerCase()) {
            case 'easy': return 'success';
            case 'medium': return 'warning';
            case 'hard': return 'danger';
            default: return 'secondary';
        }
    }

    startInterview() {
        // Store questions in session storage for the interview session page
        if (this.currentQuestions && this.currentQuestions.length > 0) {
            sessionStorage.setItem('interview_questions', JSON.stringify(this.currentQuestions));
            // Navigate to the interview session page
            window.location.href = '/interview/interview-session/';
        } else {
            this.showError('No questions available. Please generate questions first.');
        }
    }

    showStep(step) {
        // Hide all steps
        document.querySelectorAll('.interview-step').forEach(el => {
            el.style.display = 'none';
        });

        // Show current step
        const currentStep = document.getElementById(`step-${step}`);
        if (currentStep) {
            currentStep.style.display = 'block';
        }
    }

    showLoading(message) {
        // Show loading indicator
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.innerHTML = `<div class="text-center"><i class="fa fa-spinner fa-spin"></i> ${message}</div>`;
            loadingDiv.style.display = 'block';
        }
    }

    hideLoading() {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }

    showError(message) {
        // Show error message
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
            errorDiv.style.display = 'block';
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Original functionality preserved
    setupOriginalFunctionality() {
        const difficultyButtons = document.querySelectorAll('.difficulty-btn');
        const questionItems = document.querySelectorAll('.question-item');
        
        let selectedQuestion = null;
        let selectedDifficulty = 'medium';

        // Difficulty selection
        difficultyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                difficultyButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedDifficulty = btn.dataset.difficulty;
                this.filterQuestionsByDifficulty(selectedDifficulty);
            });
        });

        // Question selection
        questionItems.forEach(item => {
            item.addEventListener('click', (e) => {
                questionItems.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                selectedQuestion = item.dataset.question;
                this.showQuestionDetails(selectedQuestion);
            });
        });
    }

    filterQuestionsByDifficulty(difficulty) {
        // Implementation for filtering questions by difficulty
        console.log('Filtering questions by difficulty:', difficulty);
    }

    showQuestionDetails(questionId) {
        // Implementation for showing question details
        console.log('Showing question details for:', questionId);
    }

    async generateQuestionsForOriginalInterface() {
        if (!this.resumeAnalysis) {
            this.showError('Please upload and analyze a resume first');
            return;
        }

        this.showLoading('Generating personalized interview questions...');

        const requestData = {
            skills: this.resumeAnalysis.technical_skills,
            experience_level: this.resumeAnalysis.experience_level,
            count: 5
        };

        try {
            const response = await fetch('/interview/generate-questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                try {
                    this.currentQuestions = JSON.parse(data.questions);
                    this.displayQuestionsInOriginalInterface();
                } catch (parseError) {
                    console.error('JSON Parse Error:', parseError);
                    console.error('Questions data:', data.questions);
                    this.showError('Error parsing generated questions. Please try again.');
                }
            } else {
                this.showError(data.error || 'Failed to generate questions');
            }
        } catch (error) {
            this.showError('Error generating questions: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayQuestionsInOriginalInterface() {
        const analysisDiv = document.getElementById('analysisResults');
        if (!analysisDiv || !this.currentQuestions.length) return;

        const questionsHtml = `
            <div class="card mt-3">
                <div class="card-header">
                    <h5><i class="fas fa-question-circle mr-2"></i>Personalized Interview Questions</h5>
                </div>
                <div class="card-body">
                    ${this.currentQuestions.map((q, index) => `
                        <div class="question-item mb-4 p-3 border rounded">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="mb-0">Question ${index + 1}</h6>
                                <div>
                                    <span class="badge badge-${this.getDifficultyColor(q.difficulty)} mr-2">${q.difficulty}</span>
                                    <span class="badge badge-secondary">${q.type}</span>
                                </div>
                            </div>
                            <p class="mb-2">${q.question}</p>
                            <small class="text-muted">
                                <i class="fas fa-clock mr-1"></i>Expected Duration: ${q.expected_duration}
                            </small>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Append questions to the existing analysis
        analysisDiv.innerHTML += questionsHtml;
    }
}

// Global function to skip resume upload
function skipResumeUpload() {
    const technicalInterview = new TechnicalInterview();
    technicalInterview.showStep('question-selection');
}

// Global function to test upload
function testUpload() {
    console.log('Test upload clicked');
    const resumeInput = document.getElementById('resume-upload');
    console.log('Resume input element:', resumeInput);
    console.log('Files:', resumeInput ? resumeInput.files : 'No input found');
    
    if (resumeInput && resumeInput.files.length > 0) {
        console.log('File found, triggering upload');
        // Get the existing technicalInterview instance
        if (window.technicalInterviewInstance) {
            window.technicalInterviewInstance.handleResumeUploadDirect(resumeInput.files[0]);
        } else {
            console.error('No technicalInterview instance found');
        }
    } else {
        console.log('No file selected, please select a file first');
        alert('Please select a file first, then click Test Upload');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.technicalInterviewInstance = new TechnicalInterview();
});
