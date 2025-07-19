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
    
    updateTimerDisplay();
}

function pauseTimer() {
    if (!timerIsRunning) return;
    
    timerTotalElapsed += Date.now() - timerStartTime;
    timerIsRunning = false;
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    document.getElementById('startTimer').style.display = 'inline-flex';
    document.getElementById('pauseTimer').style.display = 'none';
    document.querySelector('.timer-circle').classList.remove('timer-running');
}

function resetTimer() {
    timerIsRunning = false;
    timerTotalElapsed = 0;
    timerStartTime = null;
    
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
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.showLoadingState();

        try {
            // Generate 5 diverse questions with retry logic
            const questions = [];
            const questionVariations = this.createQuestionVariations(difficulty, category);
            
            for (let i = 0; i < 5; i++) {
                // Use different variations for each question
                const variation = questionVariations[i % questionVariations.length];
                
                // Retry logic for API calls
                const question = await this.generateQuestionWithRetry(variation, i + 1);
                
                if (question) {
                    questions.push(question);
                } else {
                    console.log(`Failed to generate question ${i + 1} after retries`);
                }
                
                // Add a longer delay between requests to allow for more variation
                if (i < 4) {
                    await this.delay(1000 + (i * 200)); // Progressive delay: 1000ms, 1200ms, 1400ms, 1600ms
                }
            }

            // Replace existing questions with new ones
            if (questions.length > 0) {
                this.replaceQuestionsInList(questions);
            } else {
                throw new Error('Failed to generate any questions');
            }
            
        } catch (error) {
            console.error('Error generating questions:', error);
            this.showErrorMessage('Failed to generate new questions. The AI service might be busy. Please try again in a few minutes.');
        } finally {
            this.isGenerating = false;
            this.hideLoadingState();
        }
    }

    async generateQuestionWithRetry(variation, questionNumber, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(`Generating question ${questionNumber}, attempt ${attempt}`);
                
                const response = await fetch(this.apiBaseUrl + 'generate-question/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        difficulty: variation.difficulty,
                        category: variation.category,
                        save_to_db: false,
                        variation_seed: Math.random().toString(36).substr(2, 9),
                        context: variation.context,
                        problemType: variation.problemType,
                        avoidPatterns: variation.avoidPatterns,
                        uniqueConstraint: variation.uniqueConstraint,
                        requestIndex: questionNumber,
                        timestamp: Date.now(),
                        diversityHint: `Generate a ${variation.problemType} that is completely different from typical ${variation.category} problems`
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success && data.question) {
                    console.log(`Successfully generated question ${questionNumber} on attempt ${attempt}`);
                    return data.question;
                } else {
                    console.log('Question generation failed:', data);
                    throw new Error('Failed to generate question');
                }
                
            } catch (error) {
                console.error(`Question ${questionNumber} attempt ${attempt} failed:`, error);
                
                if (attempt === maxRetries) {
                    console.error(`Failed to generate question ${questionNumber} after ${maxRetries} attempts`);
                    return null;
                }
                
                // Wait before retrying (exponential backoff)
                const waitTime = Math.min(2000 * Math.pow(2, attempt - 1), 10000); // 2s, 4s, 8s, max 10s
                console.log(`Waiting ${waitTime}ms before retry...`);
                await this.delay(waitTime);
            }
        }
        
        return null;
    }

    async generateAdaptiveQuestions() {
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.showLoadingState();

        try {
            // Generate 5 diverse adaptive questions with retry logic
            const questions = [];
            for (let i = 0; i < 5; i++) {
                const question = await this.generateAdaptiveQuestionWithRetry(i + 1);
                
                if (question) {
                    questions.push(question);
                } else {
                    console.log(`Failed to generate adaptive question ${i + 1} after retries`);
                }
                
                // Add a small delay between requests to allow for more variation
                if (i < 4) {
                    await this.delay(1000 + (i * 300)); // Progressive delay: 1000ms, 1300ms, 1600ms, 1900ms
                }
            }

            // Replace existing questions with new ones
            if (questions.length > 0) {
                this.replaceQuestionsInList(questions);
            } else {
                throw new Error('Failed to generate any adaptive questions');
            }
            
        } catch (error) {
            console.error('Error generating adaptive questions:', error);
            this.showErrorMessage('Failed to generate adaptive questions. The AI service might be busy. Please try again in a few minutes.');
        } finally {
            this.isGenerating = false;
            this.hideLoadingState();
        }
    }

    async generateAdaptiveQuestionWithRetry(questionNumber, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(`Generating adaptive question ${questionNumber}, attempt ${attempt}`);
                
                const response = await fetch(this.apiBaseUrl + 'adaptive-question/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        variation_seed: Math.random().toString(36).substr(2, 9),
                        request_index: questionNumber,
                        timestamp: Date.now()
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success && data.question) {
                    console.log(`Successfully generated adaptive question ${questionNumber} on attempt ${attempt}`);
                    return data.question;
                } else {
                    throw new Error('Failed to generate adaptive question');
                }
                
            } catch (error) {
                console.error(`Adaptive question ${questionNumber} attempt ${attempt} failed:`, error);
                
                if (attempt === maxRetries) {
                    console.error(`Failed to generate adaptive question ${questionNumber} after ${maxRetries} attempts`);
                    return null;
                }
                
                // Wait before retrying (exponential backoff)
                const waitTime = Math.min(2000 * Math.pow(2, attempt - 1), 10000); // 2s, 4s, 8s, max 10s
                console.log(`Waiting ${waitTime}ms before retry...`);
                await this.delay(waitTime);
            }
        }
        
        return null;
    }

    createQuestionVariations(baseDifficulty, baseCategory) {
        const difficulties = ['easy', 'medium', 'hard'];
        const categories = ['array', 'string', 'tree', 'graph', 'dynamic-programming', 'sorting', 'searching', 'hash-table', 'two-pointers', 'sliding-window', 'stack', 'queue', 'heap', 'linked-list', 'binary-search'];
        
        // Much more diverse problem types and contexts
        const problemTypes = [
            'optimization problem',
            'counting problem', 
            'search problem',
            'sorting problem',
            'graph traversal',
            'tree manipulation',
            'string processing',
            'mathematical calculation',
            'pattern matching',
            'data structure design'
        ];
        
        const contexts = [
            'Focus on algorithmic thinking and optimization',
            'Emphasize data structure manipulation', 
            'Consider edge cases and boundary conditions',
            'Think about time and space complexity trade-offs',
            'Explore different approaches and patterns',
            'Design efficient algorithms for large datasets',
            'Implement creative solutions using advanced techniques',
            'Solve real-world application problems',
            'Focus on mathematical and logical reasoning',
            'Create problems involving multiple data structures'
        ];

        const variations = [];
        
        // Create 5 VERY different variations
        for (let i = 0; i < 5; i++) {
            let difficulty = baseDifficulty;
            let category = baseCategory;
            
            // Much higher chance to change difficulty (50% chance)
            if (Math.random() < 0.5) {
                difficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
            }
            
            // Much higher chance to change category (70% chance)
            if (Math.random() < 0.7) {
                category = categories[Math.floor(Math.random() * categories.length)];
            }
            
            // Add completely different problem types
            const problemType = problemTypes[Math.floor(Math.random() * problemTypes.length)];
            const context = contexts[i % contexts.length];
            
            variations.push({
                difficulty: difficulty,
                category: category,
                context: context,
                problemType: problemType,
                avoidPatterns: i > 0 ? ['subarray', 'longest', 'binary array'] : [], // Avoid common patterns after first question
                uniqueConstraint: `variation_${i}_${Math.random().toString(36).substr(2, 5)}`
            });
        }
        
        return variations;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    removeDuplicateQuestions(questions) {
        const seen = new Set();
        const uniqueQuestions = [];
        
        for (const question of questions) {
            const title = question.title?.toLowerCase() || '';
            let questionId = null;
            
            // Extract LeetCode question number from title
            // Pattern: "Problem Name - 123" or "Problem Name (123)" or "123. Problem Name"
            const leetcodePatterns = [
                /- (\d+)$/,           // "Problem Name - 123"
                /\((\d+)\)$/,         // "Problem Name (123)"
                /^(\d+)\./,           // "123. Problem Name"
                /\s-\s(\d+)$/,        // "Problem Name - 123"
                /leetcode\s*(\d+)/i,  // "LeetCode 123" or "leetcode123"
                /#(\d+)/              // "Problem Name #123"
            ];
            
            // Try to extract question number
            for (const pattern of leetcodePatterns) {
                const match = title.match(pattern);
                if (match) {
                    questionId = match[1];
                    break;
                }
            }
            
            // If we found a LeetCode number, use it as primary identifier
            if (questionId) {
                const identifier = `leetcode_${questionId}`;
                
                if (!seen.has(identifier)) {
                    seen.add(identifier);
                    uniqueQuestions.push(question);
                } else {
                    console.log('Duplicate LeetCode question detected and removed:', question.title, `(#${questionId})`);
                }
            } else {
                // Fallback: use exact title match for non-LeetCode problems
                const identifier = `title_${title}`;
                
                if (!seen.has(identifier)) {
                    seen.add(identifier);
                    uniqueQuestions.push(question);
                } else {
                    console.log('Duplicate title detected and removed:', question.title);
                }
            }
        }
        
        return uniqueQuestions;
    }

    removeDuplicatesLessStrict(questions) {
        const seen = new Set();
        const uniqueQuestions = [];
        
        for (const question of questions) {
            const title = question.title?.toLowerCase() || '';
            
            // Extract LeetCode number if present
            const leetcodeMatch = title.match(/(?:- (\d+)$|\((\d+)\)$|^(\d+)\.|leetcode\s*(\d+)|#(\d+))/i);
            const questionId = leetcodeMatch ? (leetcodeMatch[1] || leetcodeMatch[2] || leetcodeMatch[3] || leetcodeMatch[4] || leetcodeMatch[5]) : null;
            
            const identifier = questionId ? `leetcode_${questionId}` : `title_${title}`;
            
            if (!seen.has(identifier)) {
                seen.add(identifier);
                uniqueQuestions.push(question);
            } else {
                console.log('Exact duplicate detected and removed:', question.title);
            }
        }
        
        return uniqueQuestions;
    }

    addQuestionToList(question) {
        console.log('Adding question to list:', question);
        
        const questionsGrid = $('.questions-grid');
        console.log('Questions grid found:', questionsGrid.length);
        
        if (questionsGrid.length === 0) {
            console.error('Questions grid not found!');
            return;
        }

        const questionCount = $('.practice-question-item').length + 1;
        console.log('Question count:', questionCount);
        const questionHtml = `
            <div class="practice-question-item animate__animated animate__fadeInUp" data-question-id="${question.id || 'generated'}">
                <div class="question-number">${questionCount}</div>
                <div class="question-content">
                    <h6 class="question-title">${question.title || 'Generated Question'}</h6>
                    <p class="question-description">${question.description || question.question_text || ''}</p>
                    <div class="question-tags">
                        <span class="difficulty-tag difficulty-${question.difficulty || 'medium'}">
                            ${(question.difficulty || 'medium').charAt(0).toUpperCase() + (question.difficulty || 'medium').slice(1)}
                        </span>
                        <span class="category-tag">
                            <i class="fas fa-tag mr-1"></i>${question.category || 'Algorithm'}
                        </span>
                        <span class="complexity-tag">
                            <i class="fas fa-clock mr-1"></i>${question.time_complexity || 'O(n)'}
                        </span>
                        <span class="generated-badge">AI Generated</span>
                    </div>
                </div>
                <div class="question-actions">
                    <button class="action-btn-small view-details" data-question-id="${question.id || 'generated'}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="solve-btn-small" title="Solve Challenge" onclick="alert('This is a generated question. Try implementing the solution!')">
                        <i class="fas fa-code mr-1"></i>Solve
                    </button>
                    <button class="save-btn-small" title="Save Question" onclick="saveGeneratedQuestion(this, ${JSON.stringify(question).replace(/"/g, '&quot;')})">
                        <i class="fas fa-save"></i>
                    </button>
                </div>
                <div class="question-status">
                    <span class="status-badge status-pending">Not Started</span>
                </div>
            </div>
        `;
        
        questionsGrid.append(questionHtml);
        updateProgress();
    }

    replaceQuestionsInList(questions) {
        console.log('Replacing questions in list:', questions);
        
        // Remove duplicate questions
        let uniqueQuestions = this.removeDuplicateQuestions(questions);
        console.log(`Filtered ${questions.length} questions to ${uniqueQuestions.length} unique questions`);
        
        // Fallback: If we have fewer than 2 unique questions, be less strict
        if (uniqueQuestions.length < 2 && questions.length > 2) {
            console.log('Too few unique questions, using less strict filtering...');
            uniqueQuestions = this.removeDuplicatesLessStrict(questions);
        }
        
        const questionsGrid = $('.questions-grid');
        if (questionsGrid.length === 0) {
            console.error('Questions grid not found!');
            return;
        }

        // Clear existing questions
        questionsGrid.empty();

        // Add each unique question
        uniqueQuestions.forEach((question, index) => {
            const questionCount = index + 1;
            const questionHtml = `
                <div class="practice-question-item animate__animated animate__fadeInUp" data-question-id="${question.id || 'generated-' + questionCount}">
                    <div class="question-number">${questionCount}</div>
                    <div class="question-content">
                        <h6 class="question-title">${question.title || 'Generated Question'}</h6>
                        <p class="question-description">${question.description || question.question_text || ''}</p>
                        <div class="question-tags">
                            <span class="difficulty-tag difficulty-${question.difficulty || 'medium'}">
                                ${(question.difficulty || 'medium').charAt(0).toUpperCase() + (question.difficulty || 'medium').slice(1)}
                            </span>
                            <span class="category-tag">
                                <i class="fas fa-tag mr-1"></i>${question.category || 'Algorithm'}
                            </span>
                            <span class="complexity-tag">
                                <i class="fas fa-clock mr-1"></i>${question.time_complexity || 'O(n)'}
                            </span>
                            <span class="generated-badge">AI Generated</span>
                        </div>
                    </div>
                    <div class="question-actions">
                        <button class="action-btn-small view-details" data-question-id="${question.id || 'generated-' + questionCount}" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="solve-btn-small" title="Solve Challenge" onclick="alert('This is a generated question. Try implementing the solution!')">
                            <i class="fas fa-code mr-1"></i>Solve
                        </button>
                        <button class="save-btn-small" title="Save Question" onclick="saveGeneratedQuestion(this, ${JSON.stringify(question).replace(/"/g, '&quot;')})">
                            <i class="fas fa-save"></i>
                        </button>
                    </div>
                    <div class="question-status">
                        <span class="status-badge status-pending">Not Started</span>
                    </div>
                </div>
            `;
            
            questionsGrid.append(questionHtml);
        });

        // Update progress after adding all questions
        updateProgress();
        
        // Show success message
        console.log(`Successfully replaced with ${uniqueQuestions.length} new questions`);
        
        // Show success notification
        const message = uniqueQuestions.length < questions.length 
            ? `Successfully generated ${uniqueQuestions.length} unique questions (${questions.length - uniqueQuestions.length} duplicates removed)!`
            : `Successfully generated ${uniqueQuestions.length} new questions!`;
        this.showSuccessMessage(message);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    showLoadingState() {
        $('.dynamic-question-btn, .adaptive-question-btn').prop('disabled', true).addClass('loading');
        
        // Show loading message
        const questionsGrid = $('.questions-grid');
        if (questionsGrid.length > 0) {
            questionsGrid.prepend(`
                <div class="loading-message animate__animated animate__fadeIn" style="text-align: center; padding: 20px;">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-3">Generating 5 new questions... Please wait.</p>
                    <small class="text-muted">This may take a moment if the AI service is busy.</small>
                </div>
            `);
        }
    }

    hideLoadingState() {
        $('.dynamic-question-btn, .adaptive-question-btn').prop('disabled', false).removeClass('loading');
        
        // Remove loading message
        $('.loading-message').remove();
    }

    showErrorMessage(message) {
        console.error('Error:', message);
        
        // Create a more informative error notification
        const errorNotification = `
            <div class="alert alert-warning alert-dismissible fade show animate__animated animate__fadeIn" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                <strong>API Service Issue</strong><br>
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        
        $('body').append(errorNotification);
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            $('.alert-warning').fadeOut();
        }, 8000);
    }

    showSuccessMessage(message) {
        console.log('Success:', message);
        
        // Create a temporary success notification
        const notification = `
            <div class="alert alert-success alert-dismissible fade show animate__animated animate__fadeIn" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;">
                <i class="fas fa-check-circle mr-2"></i>${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        
        $('body').append(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            $('.alert-success').fadeOut();
        }, 5000);
    }
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
    
    updateDifficultyBreakdown();
}

function updateDifficultyBreakdown() {
    const questions = $('.practice-question-item');
    let easyTotal = 0, mediumTotal = 0, hardTotal = 0;
    let easySolved = 0, mediumSolved = 0, hardSolved = 0;
    
    questions.each(function() {
        const difficulty = $(this).find('.difficulty-easy').length > 0 ? 'easy' :
                         $(this).find('.difficulty-medium').length > 0 ? 'medium' : 'hard';
        const isSolved = $(this).find('.status-solved').length > 0;
        
        if (difficulty === 'easy') {
            easyTotal++;
            if (isSolved) easySolved++;
        } else if (difficulty === 'medium') {
            mediumTotal++;
            if (isSolved) mediumSolved++;
        } else {
            hardTotal++;
            if (isSolved) hardSolved++;
        }
    });
    
    $('#easyProgress').text(`${easySolved}/${easyTotal}`);
    $('#mediumProgress').text(`${mediumSolved}/${mediumTotal}`);
    $('#hardProgress').text(`${hardSolved}/${hardTotal}`);
}

// Quick action functions
function startRandomQuestion() {
    const questionItems = $('.practice-question-item');
    if (questionItems.length > 0) {
        const randomIndex = Math.floor(Math.random() * questionItems.length);
        const randomQuestion = questionItems.eq(randomIndex);
        const questionId = randomQuestion.data('question-id');
        
        // Add highlight animation before navigation
        randomQuestion.addClass('animate__animated animate__pulse');
        setTimeout(() => {
            window.location.href = `/dsa/solve/${questionId}/`;
        }, 500);
    }
}

function showHints() {
    const hintModal = `
        <div class="modal fade" id="hintModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-info text-white">
                        <h5 class="modal-title"><i class="fas fa-lightbulb mr-2"></i>Practice Hints</h5>
                        <button type="button" class="close text-white" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="hint-content">
                            <div class="hint-item">
                                <i class="fas fa-check-circle text-success"></i>
                                <span>Start with easier problems to build confidence</span>
                            </div>
                            <div class="hint-item">
                                <i class="fas fa-clock text-warning"></i>
                                <span>Set time limits for each problem</span>
                            </div>
                            <div class="hint-item">
                                <i class="fas fa-code text-primary"></i>
                                <span>Focus on understanding the algorithm first</span>
                            </div>
                            <div class="hint-item">
                                <i class="fas fa-repeat text-info"></i>
                                <span>Practice similar problems to reinforce concepts</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(hintModal);
    $('#hintModal').modal('show');
    $('#hintModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Global function to save generated questions
function saveGeneratedQuestion(button, question) {
    alert('Save functionality will be implemented soon!');
}

// Question details modal functions
function loadQuestionDetails(questionId) {
    console.log('Loading question details for ID:', questionId); // Debug log
    $('#questionModal').modal('show');
    $('#modalQuestionDetails').html(`
        <div class="loading-state">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3">Loading question details...</p>
        </div>
    `);
    
    $.ajax({
        url: `/dsa/api/question/${questionId}/`,
        method: 'GET',
        success: function(data) {
            console.log('Question details loaded:', data); // Debug log
            if (data.success) {
                const q = data.question;
                $('#modalQuestionTitle').text(q.title);
                
                let detailsHtml = `
                    <div class="question-detail-content">
                        <div class="detail-header">
                            <div class="detail-badges">
                                <span class="difficulty-badge difficulty-${q.difficulty}">${q.difficulty}</span>
                                <span class="category-badge">${q.category}</span>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h6><i class="fas fa-info-circle text-primary mr-2"></i>Description</h6>
                            <p class="detail-text">${q.description}</p>
                        </div>
                `;
                
                if (q.examples) {
                    detailsHtml += `
                        <div class="detail-section">
                            <h6><i class="fas fa-lightbulb text-warning mr-2"></i>Examples</h6>
                            <pre class="detail-code">${q.examples}</pre>
                        </div>
                    `;
                }
                
                if (q.constraints) {
                    detailsHtml += `
                        <div class="detail-section">
                            <h6><i class="fas fa-exclamation-triangle text-danger mr-2"></i>Constraints</h6>
                            <p class="detail-text">${q.constraints}</p>
                        </div>
                    `;
                }
                
                if (q.time_complexity || q.space_complexity) {
                    detailsHtml += `
                        <div class="detail-section">
                            <h6><i class="fas fa-tachometer-alt text-success mr-2"></i>Complexity Analysis</h6>
                            <div class="complexity-grid">
                                <div class="complexity-item">
                                    <div class="complexity-icon">
                                        <i class="fas fa-clock"></i>
                                    </div>
                                    <div>
                                        <div class="complexity-label">Time Complexity</div>
                                        <code class="complexity-value">${q.time_complexity || 'N/A'}</code>
                                    </div>
                                </div>
                                <div class="complexity-item">
                                    <div class="complexity-icon">
                                        <i class="fas fa-memory"></i>
                                    </div>
                                    <div>
                                        <div class="complexity-label">Space Complexity</div>
                                        <code class="complexity-value">${q.space_complexity || 'N/A'}</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                detailsHtml += '</div>';
                $('#modalQuestionDetails').html(detailsHtml);
            } else {
                $('#modalQuestionDetails').html(`
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle text-danger"></i>
                        <h5>Error Loading Question</h5>
                        <p>${data.error || 'Unable to load question details.'}</p>
                    </div>
                `);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', xhr, status, error); // Debug log
            $('#modalQuestionDetails').html(`
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle text-danger"></i>
                    <h5>Error Loading Question</h5>
                    <p>Unable to load question details. Please try again.</p>
                    <small class="text-muted">Error: ${error}</small>
                </div>
            `);
        }
    });
}

// Session state management
function saveSessionState() {
    const sessionData = {
        startTime: timerStartTime,
        totalElapsed: timerTotalElapsed,
        isRunning: timerIsRunning,
        progress: {
            solved: $('.practice-question-item .status-solved').length,
            attempted: $('.practice-question-item .status-attempted').length
        }
    };
    localStorage.setItem('dsaSessionState', JSON.stringify(sessionData));
}

function loadSessionState() {
    const savedState = localStorage.getItem('dsaSessionState');
    if (savedState) {
        try {
            const sessionData = JSON.parse(savedState);
            if (sessionData.startTime && sessionData.isRunning) {
                timerStartTime = sessionData.startTime;
                timerTotalElapsed = sessionData.totalElapsed || 0;
                timerIsRunning = true;
                timerInterval = setInterval(updateTimerDisplay, 100);
                $('#startTimer').hide();
                $('#pauseTimer').show();
                $('.timer-circle').addClass('timer-running');
            }
        } catch (e) {
            console.error('Error loading session state:', e);
        }
    }
}

// Scroll animation
function animateOnScroll() {
    $('.animate-on-scroll').each(function() {
        const elementTop = $(this).offset().top;
        const elementBottom = elementTop + $(this).outerHeight();
        const viewportTop = $(window).scrollTop();
        const viewportBottom = viewportTop + $(window).height();

        if (elementBottom > viewportTop && elementTop < viewportBottom) {
            $(this).addClass('animated');
        }
    });
}

// Initialize everything when DOM is ready
$(document).ready(function() {
    let currentModalQuestionId = null;
    
    // Initialize timer
    const elements = {
        timer: document.getElementById('timer'),
        startTimer: document.getElementById('startTimer'),
        pauseTimer: document.getElementById('pauseTimer'),
        resetTimer: document.getElementById('resetTimer')
    };
    
    let allElementsFound = true;
    for (const [name, element] of Object.entries(elements)) {
        if (!element) {
            allElementsFound = false;
        }
    }
    
    if (allElementsFound) {
        // Attach event listeners
        elements.startTimer.addEventListener('click', startTimer);
        elements.pauseTimer.addEventListener('click', pauseTimer);
        elements.resetTimer.addEventListener('click', resetTimer);
        
        // Force initial display update
        elements.timer.style.display = 'block';
        elements.timer.style.visibility = 'visible';
        elements.timer.style.color = '#333';
        elements.timer.style.fontSize = '1.5rem';
        elements.timer.textContent = '00:00:00';
    }
    
    // Initialize dynamic question manager
    const questionManager = new DynamicQuestionManager();

    // Event handlers for dynamic question buttons
    $('.dynamic-question-btn').click(function() {
        const difficulty = $(this).data('difficulty');
        const category = $(this).data('category');
        questionManager.generateQuestion(difficulty, category);
    });

    $('.adaptive-question-btn').click(function() {
        questionManager.generateAdaptiveQuestions();
    });
    
    // Modal solve button handler
    $('#modalSolveBtn').click(function() {
        if (currentModalQuestionId) {
            window.location.href = `/dsa/solve/${currentModalQuestionId}/`;
        }
    });
    
    // View details button handler (for the eye icon)
    $(document).on('click', '.view-details', function(e) {
        e.preventDefault();
        console.log('View details clicked'); // Debug log
        const questionId = $(this).data('question-id');
        console.log('Question ID:', questionId); // Debug log
        if (questionId) {
            currentModalQuestionId = questionId;
            loadQuestionDetails(questionId);
            $('#questionModal').modal('show');
        } else {
            console.error('No question ID found');
        }
    });
    
    // Initialize progress
    updateProgress();
    
    // Enhanced question item interactions
    $('.practice-question-item').hover(
        function() {
            $(this).addClass('question-hover');
        },
        function() {
            $(this).removeClass('question-hover');
        }
    );
    
    // Enhanced keyboard shortcuts
    $(document).keydown(function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.which) {
                case 32: // Ctrl+Space - Start/Pause timer
                    e.preventDefault();
                    if ($('#startTimer').is(':visible')) {
                        $('#startTimer').click();
                    } else {
                        $('#pauseTimer').click();
                    }
                    break;
                case 82: // Ctrl+R - Reset timer
                    e.preventDefault();
                    $('#resetTimer').click();
                    break;
                case 78: // Ctrl+N - New session
                    e.preventDefault();
                    location.reload();
                    break;
                case 191: // Ctrl+/ - Show hints
                    e.preventDefault();
                    showHints();
                    break;
            }
        }
    });
    
    // Load session state on page load
    loadSessionState();
    
    // Auto-save session state
    setInterval(saveSessionState, 30000);
    
    // Save on page unload
    $(window).on('beforeunload', function() {
        saveSessionState();
    });
    
    // Scroll animation
    $(window).on('scroll', animateOnScroll);
    animateOnScroll();
});

// Make functions available globally
window.startRandomQuestion = startRandomQuestion;
window.showHints = showHints;
window.saveGeneratedQuestion = saveGeneratedQuestion;
