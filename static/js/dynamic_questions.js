// Dynamic Question Generation for DSA Practice
class DynamicQuestionManager {
    constructor() {
        // Use relative URLs that work in both development and production
        this.apiBaseUrl = '/dsa/api/';
        this.userPerformanceHistory = this.loadUserHistory();
        this.currentQuestions = [];
        this.isGenerating = false;
        
        // Comprehensive DSA categories array for varied generation
        this.dsaCategories = [
            'array', 'string', 'linked_list', 'stack', 'queue',
            'tree', 'graph', 'heap', 'hash_table', 'dynamic_programming',
            'greedy', 'backtracking', 'binary_search', 'sorting',
            'two_pointers', 'sliding_window', 'divide_conquer',
            'trie', 'segment_tree', 'disjoint_set', 'bit_manipulation',
            'recursion', 'math', 'geometry', 'game_theory'
        ];
        
        // Load or initialize the current category index for round-robin generation
        this.currentCategoryIndex = this.loadCategoryIndex();
        
        // Track recently generated question concepts to avoid immediate repetition
        this.recentQuestionConcepts = this.loadRecentConcepts();
    }

    // Generate new questions using variety-based round-robin approach
    async generateNewQuestions(options = {}) {
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.showLoadingState();

        try {
            const {
                difficulty = 'medium',
                count = 5,
                adaptive = false
            } = options;

            let questions = [];

            if (adaptive) {
                // Generate adaptive questions based on user performance
                questions = await this.generateAdaptiveQuestions(count);
            } else {
                // Use the variety-based generation (only method)
                questions = await this.generateVariedQuestions(count, difficulty);
            }

            this.currentQuestions = questions;
            this.displayQuestions(questions);
            this.saveQuestionsToSession(questions);

        } catch (error) {
            console.error('Error generating questions:', error);
            this.showErrorState('Failed to generate new questions. Please try again.');
        } finally {
            this.isGenerating = false;
            this.hideLoadingState();
        }
    }

    // Generate varied questions using batch generation for efficiency
    async generateVariedQuestions(count, difficulty) {
        const questions = [];
        
        // Get the categories that will be used for this generation
        const startIndex = this.getRandomStartIndex();
        const categoriesToUse = [];
        for (let i = 0; i < count; i++) {
            const categoryIndex = (startIndex + i) % this.dsaCategories.length;
            categoriesToUse.push(this.dsaCategories[categoryIndex]);
        }
        
        // Show loading with category information
        const categoryDisplay = categoriesToUse.join(', ');
        const difficultyBadge = `<span class="badge badge-${this.getDifficultyColor(difficulty)} mr-2">${difficulty.toUpperCase()}</span>`;
        this.showLoadingState(`${difficultyBadge}🎯 ${categoryDisplay}`);
        
        console.log(`🎯 Batch generating ${count} questions with ${difficulty} difficulty`);
        console.log(`🏷️ Categories to use: ${categoryDisplay}`);
        
        try {
            // Generate all questions in a single batch request
            const batchQuestions = await this.generateBatchQuestions(count, difficulty, categoriesToUse);
            
            if (batchQuestions && batchQuestions.length > 0) {
                // Filter out any potential duplicates (just in case)
                const uniqueQuestions = this.filterUniqueQuestions(batchQuestions);
                
                // Track all concepts as recently generated
                uniqueQuestions.forEach(question => {
                    this.addRecentConcept(question);
                });
                
                questions.push(...uniqueQuestions);
                console.log(`✅ Successfully generated ${uniqueQuestions.length} unique questions in batch`);
            } else {
                console.warn('⚠️ Batch generation returned no questions, falling back to individual generation');
                // Fallback to individual generation if batch fails
                return await this.generateVariedQuestionsIndividually(count, difficulty, categoriesToUse);
            }
        } catch (error) {
            console.error('❌ Batch generation failed:', error);
            // Fallback to individual generation
            return await this.generateVariedQuestionsIndividually(count, difficulty, categoriesToUse);
        }
        
        // Update the current index for next generation session
        this.currentCategoryIndex = (startIndex + count) % this.dsaCategories.length;
        this.saveCategoryIndex();
        
        console.log(`🎯 Next session will start from category index: ${this.currentCategoryIndex}`);
        console.log(`✅ Final result: Generated ${questions.length} unique questions`);
        
        return questions;
    }

    // Generate multiple questions in a single API call
    async generateBatchQuestions(count, difficulty, categories) {
        console.log(`🚀 Making batch API call for ${count} questions`);
        
        const avoidPatterns = this.getRecentConceptPatterns();
        const categoriesText = categories.join(', ');
        
        // Create comprehensive prompt for batch generation
        const batchPrompt = this.createBatchPrompt(count, difficulty, categories, avoidPatterns);
        
        try {
            const response = await fetch(this.apiBaseUrl + 'generate-batch-questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    count: count,
                    difficulty: difficulty,
                    categories: categories,
                    batch_prompt: batchPrompt,
                    avoid_patterns: avoidPatterns,
                    ensure_diversity: true,
                    save_to_db: false
                })
            });

            console.log(`📡 Batch response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(`✅ Batch response received`);
            
            if (data.success && data.questions && Array.isArray(data.questions)) {
                // Add metadata to each question
                return data.questions.map((question, index) => ({
                    ...question,
                    verified_category: categories[index] || categories[0],
                    generated_timestamp: Date.now(),
                    batch_generated: true,
                    batch_index: index
                }));
            } else {
                throw new Error('Invalid batch response format');
            }
        } catch (error) {
            console.error(`❌ Batch API Error:`, error);
            throw error;
        }
    }

    // Create a comprehensive prompt for batch generation
    createBatchPrompt(count, difficulty, categories, avoidPatterns) {
        const categoryRequirements = categories.map((category, index) => {
            const specificReq = this.getCategorySpecificRequirements(category);
            return `${index + 1}. ${category.replace('_', ' ').toUpperCase()}: ${specificReq}`;
        }).join('\n');

        return `Generate exactly ${count} COMPLETELY DIFFERENT coding problems with ${difficulty} difficulty level.

STRICT REQUIREMENTS:
- Each problem must be from a different category and completely unique
- No similar titles, descriptions, or core concepts
- Avoid these patterns: ${avoidPatterns.join(', ')}

CATEGORIES AND REQUIREMENTS:
${categoryRequirements}

IMPORTANT CONSTRAINTS:
1. Each problem must have a unique title and concept
2. Problems should cover different algorithmic approaches
3. Avoid common LeetCode patterns like "Find Target", "Two Sum", "Subarray Sum"
4. Ensure variety in problem types within each category
5. Use creative and uncommon problem scenarios

FORMAT: Return exactly ${count} problems as a JSON array, each with:
- title: Unique descriptive title
- description: Clear problem description
- examples: Array of input/output examples
- constraints: Problem constraints
- time_complexity: Expected time complexity
- category: The assigned category
- difficulty: "${difficulty}"

Make each problem distinctly different from the others!`;
    }

    // Filter unique questions from batch results
    filterUniqueQuestions(questions) {
        const unique = [];
        
        for (const question of questions) {
            const isDuplicate = this.isDuplicateQuestion(question, unique);
            if (!isDuplicate) {
                unique.push(question);
            } else {
                console.log(`🔄 Filtered out duplicate from batch: ${question.title}`);
            }
        }
        
        return unique;
    }

    // Fallback: Generate questions individually (old method as backup)
    async generateVariedQuestionsIndividually(count, difficulty, categories) {
        console.log(`🔄 Falling back to individual generation`);
        const questions = [];
        const maxRetries = 3;
        
        for (let i = 0; i < count && i < categories.length; i++) {
            const category = categories[i];
            console.log(`🔄 Individual generation ${i + 1}: category '${category}'`);
            
            let questionGenerated = false;
            let retryCount = 0;
            
            while (!questionGenerated && retryCount < maxRetries) {
                try {
                    const question = await this.generateSingleQuestion(difficulty, category, retryCount);
                    
                    if (question && !this.isDuplicateQuestion(question, questions)) {
                        questions.push(question);
                        questionGenerated = true;
                        this.addRecentConcept(question);
                        console.log(`✅ Individual success: ${question.title}`);
                    } else {
                        retryCount++;
                        console.warn(`⚠️ Individual retry ${retryCount}/${maxRetries}`);
                    }
                } catch (error) {
                    retryCount++;
                    console.error(`❌ Individual error (attempt ${retryCount}):`, error);
                }
            }
        }
        
        return questions;
    }

    // Check if a question is a duplicate based on multiple criteria
    isDuplicateQuestion(newQuestion, existingQuestions) {
        const newConcept = this.extractCoreConcept(newQuestion.title?.toLowerCase() || '');
        const newDescription = newQuestion.description?.toLowerCase() || '';
        const newTitle = newQuestion.title?.toLowerCase() || '';
        
        // Check against existing questions in current batch
        if (existingQuestions.length) {
            for (const existing of existingQuestions) {
                const existingTitle = existing.title?.toLowerCase() || '';
                const existingDescription = existing.description?.toLowerCase() || '';
                const existingConcept = this.extractCoreConcept(existingTitle);
                
                // 1. Check for exact title match (case insensitive)
                if (newTitle === existingTitle) {
                    console.log(`🔄 Exact title match detected: '${newTitle}'`);
                    return true;
                }
                
                // 2. Check for exact concept match
                if (newConcept === existingConcept && newConcept.length > 3) {
                    console.log(`🔄 Duplicate concept detected: '${newConcept}'`);
                    return true;
                }
                
                // 3. Check for high similarity in description (more strict)
                const descriptionSimilarity = this.calculateSimilarity(newDescription, existingDescription);
                if (descriptionSimilarity > 0.5) { // Even more strict threshold
                    console.log(`🔄 High description similarity detected: ${(descriptionSimilarity * 100).toFixed(1)}%`);
                    return true;
                }
                
                // 4. Check for similar problem patterns
                if (this.hasSimilarPattern(newDescription, existingDescription)) {
                    console.log(`🔄 Similar problem pattern detected`);
                    return true;
                }
                
                // 5. Check for similar titles with different numbers
                const newTitleNormalized = this.normalizeTitle(newTitle);
                const existingTitleNormalized = this.normalizeTitle(existingTitle);
                if (newTitleNormalized === existingTitleNormalized && newTitleNormalized.length > 10) {
                    console.log(`🔄 Similar title pattern detected: '${newTitleNormalized}'`);
                    return true;
                }
            }
        }
        
        // 6. Check against recently generated concepts
        if (this.isRecentConcept(newConcept)) {
            console.log(`🔄 Concept '${newConcept}' was recently generated, considering as duplicate`);
            return true;
        }
        
        return false;
    }

    // Normalize title by removing numbers and extra words
    normalizeTitle(title) {
        return title
            .replace(/\s*-\s*\d+$/, '') // Remove trailing numbers
            .replace(/\d+/g, '') // Remove all numbers
            .replace(/\s+/g, ' ') // Normalize spaces
            .trim();
    }

    // Check for similar problem patterns
    hasSimilarPattern(desc1, desc2) {
        const patterns = [
            /given.*array.*target/i,
            /find.*target.*sorted/i,
            /word.*ladder/i,
            /trapping.*rain.*water/i,
            /subarray.*sum.*equals/i,
            /longest.*substring/i,
            /maximum.*subarray/i,
            /valid.*parentheses/i
        ];
        
        for (const pattern of patterns) {
            if (pattern.test(desc1) && pattern.test(desc2)) {
                return true;
            }
        }
        return false;
    }

    // Extract core concept from question title
    extractCoreConcept(title) {
        // Remove numbers, common words, and normalize
        return title
            .replace(/\s*-\s*\d+$/, '') // Remove trailing numbers like "- 4", "- 96"
            .replace(/\d+/g, '') // Remove any numbers
            .replace(/\b(the|a|an|in|on|at|for|with|by)\b/g, '') // Remove common words
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
    }

    // Calculate similarity between two strings (simple implementation)
    calculateSimilarity(str1, str2) {
        if (!str1 || !str2) return 0;
        
        const words1 = str1.split(/\s+/);
        const words2 = str2.split(/\s+/);
        
        const commonWords = words1.filter(word => 
            word.length > 3 && words2.includes(word)
        );
        
        const totalWords = Math.max(words1.length, words2.length);
        return totalWords > 0 ? commonWords.length / totalWords : 0;
    }

    // Get a random starting index for variety
    getRandomStartIndex() {
        return Math.floor(Math.random() * this.dsaCategories.length);
    }

    // Load category index from localStorage
    loadCategoryIndex() {
        try {
            const index = localStorage.getItem('dsaCategoryIndex');
            return index ? parseInt(index, 10) : 0;
        } catch {
            return 0;
        }
    }

    // Save category index to localStorage
    saveCategoryIndex() {
        try {
            localStorage.setItem('dsaCategoryIndex', this.currentCategoryIndex.toString());
        } catch (error) {
            console.error('Failed to save category index:', error);
        }
    }

    // Get information about the current rotation status
    getCategoryRotationInfo() {
        const currentCategory = this.dsaCategories[this.currentCategoryIndex];
        const totalCategories = this.dsaCategories.length;
        const progress = Math.round((this.currentCategoryIndex / totalCategories) * 100);
        
        return {
            currentCategory,
            currentIndex: this.currentCategoryIndex,
            totalCategories,
            progress,
            allCategories: this.dsaCategories
        };
    }

    // Reset category rotation to start from beginning
    resetCategoryRotation() {
        this.currentCategoryIndex = 0;
        this.saveCategoryIndex();
        console.log('🔄 Category rotation reset to beginning');
    }

    // Load recent question concepts from localStorage
    loadRecentConcepts() {
        try {
            const concepts = localStorage.getItem('recentQuestionConcepts');
            return concepts ? JSON.parse(concepts) : [];
        } catch {
            return [];
        }
    }

    // Save recent question concepts to localStorage
    saveRecentConcepts() {
        try {
            localStorage.setItem('recentQuestionConcepts', JSON.stringify(this.recentQuestionConcepts));
        } catch (error) {
            console.error('Failed to save recent concepts:', error);
        }
    }

    // Add a question concept to recent list
    addRecentConcept(question) {
        const concept = this.extractCoreConcept(question.title?.toLowerCase() || '');
        if (concept && concept.length > 3) {
            this.recentQuestionConcepts.push({
                concept: concept,
                category: question.category || question.verified_category,
                timestamp: Date.now()
            });
            
            // Keep only last 20 concepts and concepts from last 24 hours
            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
            this.recentQuestionConcepts = this.recentQuestionConcepts
                .filter(item => item.timestamp > oneDayAgo)
                .slice(-20);
                
            this.saveRecentConcepts();
        }
    }

    // Check if a concept was recently generated
    isRecentConcept(concept) {
        return this.recentQuestionConcepts.some(item => item.concept === concept);
    }

    // Generate single question via API with enhanced category specificity and LeetCode-style prompting
    async generateSingleQuestion(difficulty, category, retryCount = 0) {
        console.log(`🚀 Making API call to: ${this.apiBaseUrl}generate-question/`);
        console.log(`📝 Request data:`, { difficulty, category, retry: retryCount });
        
        // Generate a unique LeetCode-style number and get specific requirements
        const leetcodeNumber = this.generateUniqueLeetCodeNumber();
        const categorySpecificRequirements = this.getCategorySpecificRequirements(category);
        const avoidPatterns = this.getRecentConceptPatterns();
        
        // Make requirements stricter on retries
        const strictnessLevel = retryCount > 0 ? `RETRY ${retryCount}: MUST BE COMPLETELY DIFFERENT. ` : '';
        const uniqueConstraint = `${strictnessLevel}Create a COMPLETELY UNIQUE ${category.replace('_', ' ')} problem different from common patterns. Number: ${leetcodeNumber}. AVOID: ${avoidPatterns.join(', ')}`;
        
        try {
            const response = await fetch(this.apiBaseUrl + 'generate-question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    difficulty: difficulty,
                    category: category,
                    leetcode_number: leetcodeNumber,
                    specific_requirements: categorySpecificRequirements,
                    avoid_patterns: avoidPatterns,
                    unique_constraint: uniqueConstraint,
                    retry_count: retryCount,
                    force_unique: retryCount > 0,
                    ensure_variety: true,
                    save_to_db: false
                })
            });

            console.log(`📡 Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(`✅ Response data:`, data);
            
            if (data.success && data.question) {
                // Add category verification and unique identifiers
                data.question.verified_category = category;
                data.question.leetcode_number = leetcodeNumber;
                data.question.generated_timestamp = Date.now();
                data.question.retry_count = retryCount;
                return data.question;
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error(`❌ API Error:`, error);
            throw error;
        }
    }

    // Generate a unique LeetCode-style number
    generateUniqueLeetCodeNumber() {
        // Generate a number between 1000-9999 to avoid conflicts with real LeetCode problems
        const baseNumber = 1000 + Math.floor(Math.random() * 8999);
        const timestamp = Date.now().toString().slice(-3); // Last 3 digits of timestamp
        return parseInt(baseNumber.toString() + timestamp.slice(-1)); // Combine for uniqueness
    }

    // Get patterns to avoid based on recent concepts
    getRecentConceptPatterns() {
        const patterns = this.recentQuestionConcepts.map(item => item.concept);
        return patterns.length > 0 ? patterns : ['avoid common leetcode patterns'];
    }

    // Get Bootstrap color class for difficulty
    getDifficultyColor(difficulty) {
        const colors = {
            'easy': 'success',
            'medium': 'warning', 
            'hard': 'danger'
        };
        return colors[difficulty.toLowerCase()] || 'primary';
    }

    // Get specific requirements for each category to ensure variety
    getCategorySpecificRequirements(category) {
        const requirements = {
            'array': [
                'Array rotation and cyclic shifts',
                'Maximum subarray problems (Kadane variants)',
                'Array rearrangement and partitioning',
                'Peak finding in arrays',
                'Array intersection and union',
                'Majority element detection',
                'Next greater/smaller element',
                'Array compression and encoding'
            ],
            'string': [
                'String compression and decompression',
                'Palindrome variations and checks',
                'String matching and pattern search',
                'Anagram detection and grouping',
                'String transformation problems',
                'Parentheses balancing variations',
                'String permutation generation',
                'Longest common subsequence variants'
            ],
            'linked_list': [
                'Linked list cycle detection variants',
                'Merging sorted linked lists',
                'Linked list reversal in groups',
                'Remove nth node variations',
                'Linked list intersection detection',
                'Add numbers represented as linked lists',
                'Flatten multilevel linked lists',
                'Copy linked list with random pointers'
            ],
            'stack': [
                'Stack-based expression evaluation',
                'Largest rectangle in histogram variants',
                'Valid parentheses with multiple types',
                'Stack sorting problems',
                'Minimum stack implementation',
                'Stack-based backtracking',
                'Monotonic stack applications',
                'Stack-based graph traversal'
            ],
            'queue': [
                'Circular queue implementation',
                'Queue using stacks',
                'Sliding window maximum',
                'Level order traversal variants',
                'Queue-based scheduling',
                'Priority queue applications',
                'Deque operations',
                'Queue reversal problems'
            ],
            'tree': [
                'Binary tree construction from traversals',
                'Tree diameter and path problems',
                'Binary search tree validation',
                'Tree serialization and deserialization',
                'Lowest common ancestor variants',
                'Tree pruning and trimming',
                'Binary tree to linked list conversion',
                'Tree isomorphism checking'
            ],
            'graph': [
                'Graph coloring problems',
                'Topological sorting variants',
                'Strongly connected components',
                'Graph reconstruction problems',
                'Minimum spanning tree variations',
                'Graph bipartition checking',
                'Course scheduling problems',
                'Island counting variants'
            ],
            'dynamic_programming': [
                'Unique path counting problems',
                'Coin change variations',
                'Longest increasing subsequence variants',
                'Edit distance problems',
                'Knapsack problem variations',
                'Matrix chain multiplication',
                'Palindrome partitioning',
                'Stock trading with constraints'
            ],
            'greedy': [
                'Activity selection problems',
                'Huffman coding variations',
                'Gas station circuit problems',
                'Meeting room scheduling',
                'Minimum number of platforms',
                'Job sequencing problems',
                'Fractional knapsack variants',
                'Candy distribution problems'
            ]
        };
        
        const categoryRequirements = requirements[category] || [`Unique ${category.replace('_', ' ')} problem`];
        const randomRequirement = categoryRequirements[Math.floor(Math.random() * categoryRequirements.length)];
        
        return `Create a unique problem focusing on: ${randomRequirement}. Make it distinctly different from common LeetCode patterns.`;
    }

    // Generate adaptive questions based on user performance
    async generateAdaptiveQuestions(count) {
        const questions = [];
        
        for (let i = 0; i < count; i++) {
            const response = await fetch(this.apiBaseUrl + 'adaptive-question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    performance_history: this.userPerformanceHistory
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    questions.push(data.question);
                }
            }
        }

        return questions;
    }

    // Display generated questions in the UI
    displayQuestions(questions) {
        const container = document.querySelector('.questions-grid');
        if (!container) return;

        container.innerHTML = ''; // Clear existing questions

        questions.forEach((question, index) => {
            const questionElement = this.createQuestionElement(question, index);
            container.appendChild(questionElement);
        });

        // Add animations
        this.addQuestionAnimations();
    }

    // Create question element for display
    createQuestionElement(question, index) {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'practice-question-item animate__animated animate__fadeInUp';
        questionDiv.style.animationDelay = `${index * 100}ms`;
        questionDiv.dataset.questionId = question.id;

        questionDiv.innerHTML = `
            <div class="question-number">${index + 1}</div>
            <div class="question-content">
                <h6 class="question-title">${question.title}</h6>
                <p class="question-description">${this.truncateText(question.description, 20)}</p>
                <div class="question-tags">
                    <span class="difficulty-tag difficulty-${question.difficulty}">
                        ${question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                    </span>
                    <span class="category-tag">
                        <i class="fas fa-tag mr-1"></i>${question.category.replace('_', ' ').toUpperCase()}
                    </span>
                    <span class="complexity-tag">
                        <i class="fas fa-clock mr-1"></i>${question.time_complexity || 'O(n)'}
                    </span>
                    ${question.generated ? `<span class="generated-badge"><i class="fas fa-robot mr-1"></i>Gemini AI</span>` : ''}
                    ${question.fallback ? `<span class="fallback-badge"><i class="fas fa-tools mr-1"></i>Template</span>` : ''}
                </div>
            </div>
            <div class="question-actions">
                <button class="action-btn-small view-details" data-question-id="${question.id}" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="solve-btn-small" onclick="solveGeneratedQuestion('${question.id}')" title="Solve Challenge">
                    <i class="fas fa-code mr-1"></i>Solve
                </button>
                <button class="save-btn-small" onclick="saveGeneratedQuestion('${question.id}')" title="Save Question">
                    <i class="fas fa-save"></i>
                </button>
            </div>
            <div class="question-status">
                <span class="status-badge status-pending">Not Started</span>
            </div>
        `;

        return questionDiv;
    }

    // Show loading state with category information
    showLoadingState(categoryInfo = null) {
        const container = document.querySelector('.questions-grid');
        if (container) {
            const categoryDisplay = categoryInfo ? 
                `<p class="text-info"><i class="fas fa-tags mr-2"></i>Categories: ${categoryInfo}</p>` : 
                '';
                
            container.innerHTML = `
                <div class="loading-questions">
                    <div class="loading-spinner">
                        <i class="fas fa-robot fa-spin fa-3x text-primary"></i>
                    </div>
                    <h5 class="mt-3">Generating New Questions with Gemini AI...</h5>
                    <p class="text-muted">Creating personalized coding challenges just for you</p>
                    ${categoryDisplay}
                    <div class="progress mt-3" style="height: 6px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 100%"></div>
                    </div>
                </div>
            `;
        }
    }

    // Hide loading state
    hideLoadingState() {
        const loadingElement = document.querySelector('.loading-questions');
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    // Show error state
    showErrorState(message) {
        const container = document.querySelector('.questions-grid');
        if (container) {
            container.innerHTML = `
                <div class="error-questions">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle fa-3x text-danger"></i>
                    </div>
                    <h5 class="mt-3">Generation Failed</h5>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-refresh mr-2"></i>Try Again
                    </button>
                </div>
            `;
        }
    }

    // Save user performance for adaptive generation
    recordQuestionAttempt(questionId, solved, timeSpent, category) {
        const attempt = {
            questionId: questionId,
            solved: solved,
            timeSpent: timeSpent,
            category: category,
            timestamp: Date.now()
        };

        this.userPerformanceHistory.push(attempt);
        
        // Keep only last 50 attempts
        if (this.userPerformanceHistory.length > 50) {
            this.userPerformanceHistory = this.userPerformanceHistory.slice(-50);
        }

        this.saveUserHistory();
    }

    // Load user performance history from localStorage
    loadUserHistory() {
        try {
            const history = localStorage.getItem('dsaPerformanceHistory');
            return history ? JSON.parse(history) : [];
        } catch {
            return [];
        }
    }

    // Save user performance history to localStorage
    saveUserHistory() {
        try {
            localStorage.setItem('dsaPerformanceHistory', JSON.stringify(this.userPerformanceHistory));
        } catch (error) {
            console.error('Failed to save user history:', error);
        }
    }

    // Save questions to session storage
    saveQuestionsToSession(questions) {
        try {
            sessionStorage.setItem('currentGeneratedQuestions', JSON.stringify(questions));
        } catch (error) {
            console.error('Failed to save questions to session:', error);
        }
    }

    // Utility functions
    truncateText(text, wordCount) {
        const words = text.split(' ');
        return words.length > wordCount 
            ? words.slice(0, wordCount).join(' ') + '...'
            : text;
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    addQuestionAnimations() {
        const questions = document.querySelectorAll('.practice-question-item');
        questions.forEach((question, index) => {
            question.style.animationDelay = `${index * 100}ms`;
        });
    }
}

// Global instance
const dynamicQuestionManager = new DynamicQuestionManager();

// Global functions for button actions
window.generateNewQuestions = function(options = {}) {
    dynamicQuestionManager.generateNewQuestions(options);
};

window.generateAdaptiveQuestions = function() {
    dynamicQuestionManager.generateNewQuestions({ adaptive: true });
};

// Function for generating varied questions with specific count
window.generateVariedQuestions = function(count = 5, difficulty = 'medium') {
    dynamicQuestionManager.generateNewQuestions({
        count: count,
        difficulty: difficulty
    });
};

window.solveGeneratedQuestion = function(questionId) {
    // For generated questions, we need to handle them differently
    // since they might not be in the database
    const questions = JSON.parse(sessionStorage.getItem('currentGeneratedQuestions') || '[]');
    const question = questions.find(q => q.id === questionId);
    
    if (question) {
        // Store question data for the solve page
        sessionStorage.setItem('currentSolveQuestion', JSON.stringify(question));
        // Navigate to a special solve page for generated questions
        window.location.href = `/dsa/solve/generated/${questionId}/`;
    }
};

window.saveGeneratedQuestion = async function(questionId) {
    const questions = JSON.parse(sessionStorage.getItem('currentGeneratedQuestions') || '[]');
    const question = questions.find(q => q.id === questionId);
    
    if (question) {
        try {
            const response = await fetch('/dsa/api/generate-question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': dynamicQuestionManager.getCsrfToken()
                },
                body: JSON.stringify({
                    ...question,
                    save_to_db: true
                })
            });

            if (response.ok) {
                alert('Question saved successfully!');
            } else {
                alert('Failed to save question');
            }
        } catch (error) {
            console.error('Error saving question:', error);
            alert('Error saving question');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add dynamic generation controls to the page
    // Initialize UI enhancements 
    // NOTE: Buttons are now in HTML template, no need to create them dynamically
});

// Initialize when DOM is ready
$(document).ready(function() {
    // Initialize the dynamic question manager
    const questionManager = new DynamicQuestionManager();
    
    // Add event listeners for the dynamic question buttons
    $('.dynamic-question-btn').on('click', function() {
        const difficulty = $(this).data('difficulty') || 'medium';
        const count = $(this).data('count') || 5;
        
        console.log(`🎯 User clicked: ${difficulty.toUpperCase()} difficulty button`);
        console.log(`📊 Generating ${count} varied questions with '${difficulty}' difficulty...`);
        
        questionManager.generateNewQuestions({
            difficulty: difficulty,
            count: count
        });
    });
    
    $('.adaptive-question-btn').on('click', function() {
        const count = $(this).data('count') || 5;
        
        console.log('🧠 User clicked: ADAPTIVE questions button');
        console.log(`📊 Generating ${count} adaptive questions based on performance history...`);
        
        questionManager.generateNewQuestions({
            adaptive: true,
            count: count
        });
    });
    
    // Add event listener for variety generation button (if exists)
    $('.variety-question-btn').on('click', function() {
        const difficulty = $(this).data('difficulty') || 'medium';
        const count = $(this).data('count') || 5;
        
        console.log(`Generating ${count} varied questions with ${difficulty} difficulty...`);
        
        questionManager.generateNewQuestions({
            difficulty: difficulty,
            count: count
        });
    });
    
    // Make questionManager globally available for debugging
    window.questionManager = questionManager;
});

// Global helper functions for backward compatibility
function generateNewQuestions(options = {}) {
    if (window.questionManager) {
        window.questionManager.generateNewQuestions(options);
    }
}

function generateAdaptiveQuestions() {
    if (window.questionManager) {
        window.questionManager.generateNewQuestions({adaptive: true});
    }
}

// Helper function for variety generation
function generateVariedQuestions(count = 5, difficulty = 'medium') {
    if (window.questionManager) {
        window.questionManager.generateNewQuestions({
            count: count,
            difficulty: difficulty
        });
    }
}

// Utility functions for category rotation management
window.getCategoryRotationInfo = function() {
    return window.questionManager ? window.questionManager.getCategoryRotationInfo() : null;
};

window.resetCategoryRotation = function() {
    if (window.questionManager) {
        window.questionManager.resetCategoryRotation();
    }
};

window.logRotationStatus = function() {
    const info = window.getCategoryRotationInfo();
    if (info) {
        console.log(`📊 Category Rotation Status:
        Current: ${info.currentCategory} (${info.currentIndex}/${info.totalCategories})
        Progress: ${info.progress}%
        All Categories: ${info.allCategories.join(', ')}`);
    }
};

// Utility function to clear recent concepts cache
window.clearRecentConcepts = function() {
    if (window.questionManager) {
        window.questionManager.recentQuestionConcepts = [];
        window.questionManager.saveRecentConcepts();
        console.log('🧹 Recent question concepts cache cleared');
    }
};

// Utility function to view recent concepts
window.viewRecentConcepts = function() {
    if (window.questionManager) {
        console.log('📝 Recent Question Concepts:', window.questionManager.recentQuestionConcepts);
    }
};

// Utility function to force clear all caches and start fresh
window.resetAllCaches = function() {
    if (window.questionManager) {
        window.questionManager.recentQuestionConcepts = [];
        window.questionManager.saveRecentConcepts();
        window.questionManager.currentCategoryIndex = 0;
        window.questionManager.saveCategoryIndex();
        localStorage.removeItem('currentGeneratedQuestions');
        sessionStorage.removeItem('currentGeneratedQuestions');
        console.log('🧹 All caches cleared - fresh start!');
    }
};

// Utility function to add problematic patterns to avoid list
window.avoidPattern = function(pattern) {
    if (window.questionManager && pattern) {
        window.questionManager.recentQuestionConcepts.push({
            concept: pattern.toLowerCase(),
            category: 'blocked',
            timestamp: Date.now()
        });
        window.questionManager.saveRecentConcepts();
        console.log(`🚫 Added '${pattern}' to avoid list`);
    }
};
