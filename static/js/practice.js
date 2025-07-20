// DSA Practice Page JavaScript

// Global timer variables
let timerStartTime = null;
let timerInterval = null;
let timerTotalElapsed = 0;
let timerIsRunning = false;

// Timer functions
function formatTime(milliseconds) {
    const hours = Math.floor(milliseconds / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
    if (!timerIsRunning || !timerStartTime) return;
    
    const currentTime = Date.now();
    const currentSession = currentTime - timerStartTime;
    const totalTime = timerTotalElapsed + currentSession;
    
    const formattedTime = formatTime(totalTime);
    
    // Update the timer display
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = formattedTime;
    }
    
    // jQuery update (fallback)
    if (typeof $ !== 'undefined') {
        $('#timer').text(formattedTime);
    }
}

function startTimer() {
    timerStartTime = Date.now();
    timerIsRunning = true;
    
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateTimerDisplay, 100);
    
    const startBtn = document.getElementById('startTimer');
    const pauseBtn = document.getElementById('pauseTimer');
    const timerCircle = document.querySelector('.timer-circle');
    
    if (startBtn) startBtn.style.display = 'none';
    if (pauseBtn) pauseBtn.style.display = 'inline-flex';
    if (timerCircle) timerCircle.classList.add('timer-running');
}

function pauseTimer() {
    if (timerIsRunning && timerStartTime) {
        const currentTime = Date.now();
        const currentSession = currentTime - timerStartTime;
        timerTotalElapsed += currentSession;
    }
    
    timerIsRunning = false;
    timerStartTime = null;
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    const startBtn = document.getElementById('startTimer');
    const pauseBtn = document.getElementById('pauseTimer');
    const timerCircle = document.querySelector('.timer-circle');
    
    if (startBtn) startBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';
    if (timerCircle) timerCircle.classList.remove('timer-running');
}

function resetTimer() {
    timerIsRunning = false;
    timerStartTime = null;
    timerTotalElapsed = 0;
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    document.getElementById('timer').textContent = '00:00:00';
    document.getElementById('startTimer').style.display = 'inline-flex';
    document.getElementById('pauseTimer').style.display = 'none';
    document.querySelector('.timer-circle').classList.remove('timer-running');
}

// Progress tracking functions
function updateProgress() {
    const totalQuestions = $('.practice-question-item').length;
    const solvedQuestions = $('.practice-question-item .status-solved').length;
    const attemptedQuestions = $('.practice-question-item .status-attempted').length;
    
    const progressPercent = totalQuestions > 0 ? Math.round((solvedQuestions / totalQuestions) * 100) : 0;
    
    $('#progressBar').css('width', progressPercent + '%');
    $('#progressPercent').text(progressPercent + '%');
    $('#solvedCount').text(solvedQuestions);
    $('#attemptedCount').text(attemptedQuestions);
    $('#totalCount').text(totalQuestions);
}

function updateDifficultyBreakdown() {
    const easyQuestions = $('.practice-question-item .difficulty-easy').length;
    const mediumQuestions = $('.practice-question-item .difficulty-medium').length;
    const hardQuestions = $('.practice-question-item .difficulty-hard').length;
    
    $('#easyCount').text(easyQuestions);
    $('#mediumCount').text(mediumQuestions);
    $('#hardCount').text(hardQuestions);
}

function startRandomQuestion() {
    const questions = $('.practice-question-item');
    if (questions.length === 0) return;
    
    const randomIndex = Math.floor(Math.random() * questions.length);
    const randomQuestion = $(questions[randomIndex]);
    const solveBtn = randomQuestion.find('.solve-btn-small');
    
    if (solveBtn.length) {
        solveBtn.click();
    }
}

// Global function to save generated questions
function saveGeneratedQuestion(button, question) {
    // Implementation for saving questions
    console.log('Saving question:', question);
}

function loadQuestionDetails(questionId) {
    $.ajax({
        url: `/dsa/api/question/${questionId}/`,
        method: 'GET',
        success: function(data) {
            if (data.success) {
                const question = data.question;
                $('#modalQuestionTitle').text(question.title);
                
                const detailsHtml = `
                    <div class="question-details">
                        <div class="mb-3">
                            <h6>Problem Description</h6>
                            <p>${question.description}</p>
                        </div>
                        
                        <div class="mb-3">
                            <h6>Examples</h6>
                            <pre class="bg-light p-3 rounded">${question.examples}</pre>
                        </div>
                        
                        <div class="mb-3">
                            <h6>Constraints</h6>
                            <p>${question.constraints}</p>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Time Complexity</h6>
                                <span class="badge badge-info">${question.time_complexity}</span>
                            </div>
                            <div class="col-md-6">
                                <h6>Space Complexity</h6>
                                <span class="badge badge-info">${question.space_complexity}</span>
                            </div>
                        </div>
                        
                        ${question.solution_approach ? `
                            <div class="mt-3">
                                <h6>Solution Approach</h6>
                                <p>${question.solution_approach}</p>
                            </div>
                        ` : ''}
                    </div>
                `;
                
                $('#modalQuestionDetails').html(detailsHtml);
                $('#modalSolveBtn').attr('onclick', `window.open('/dsa/solve/${questionId}/', '_blank')`);
            } else {
                $('#modalQuestionDetails').html('<p class="text-danger">Failed to load question details.</p>');
            }
        },
        error: function() {
            $('#modalQuestionDetails').html('<p class="text-danger">Error loading question details.</p>');
        }
    });
}

function saveSessionState() {
    const sessionState = {
        timer: {
            totalElapsed: timerTotalElapsed,
            isRunning: timerIsRunning
        },
        timestamp: Date.now()
    };
    
    try {
        localStorage.setItem('practiceSessionState', JSON.stringify(sessionState));
    } catch (error) {
        console.error('Failed to save session state:', error);
    }
}

function loadSessionState() {
    try {
        const sessionState = localStorage.getItem('practiceSessionState');
        if (sessionState) {
            const state = JSON.parse(sessionState);
            
            // Load timer state if saved recently (within 1 hour)
            if (Date.now() - state.timestamp < 3600000) {
                timerTotalElapsed = state.timer.totalElapsed || 0;
                updateTimerDisplay();
            }
        }
    } catch (error) {
        console.error('Failed to load session state:', error);
    }
}

function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    });
    
    elements.forEach(el => observer.observe(el));
}

// Initialize when DOM is ready
$(document).ready(function() {
    // Load session state
    loadSessionState();
    
    // Initialize progress tracking
    updateProgress();
    updateDifficultyBreakdown();
    
    // Initialize animations
    animateOnScroll();
    
    // Auto-save session state periodically
    setInterval(saveSessionState, 30000); // Save every 30 seconds
    
    // Event listeners for question details modal
    $(document).on('click', '.view-details', function() {
        const questionId = $(this).data('question-id');
        $('#questionModal').modal('show');
        loadQuestionDetails(questionId);
    });
    
    // Event listeners for question status updates
    $(document).on('click', '.solve-btn-small', function() {
        const questionItem = $(this).closest('.practice-question-item');
        questionItem.find('.status-badge')
            .removeClass('status-pending')
            .addClass('status-attempted')
            .text('In Progress');
        updateProgress();
    });
    
    // Save state when page is unloaded
    $(window).on('beforeunload', function() {
        saveSessionState();
    });
});

// Utility functions
function getCsrfToken() {
    return $('[name=csrfmiddlewaretoken]').val() || '';
}
