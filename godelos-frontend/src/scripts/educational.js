/**
 * Educational Features Module
 * Provides educational and learning support functionality
 */

class EducationalFeatures {
    constructor() {
        this.isInitialized = false;
        this.currentLesson = null;
        this.userProgress = new Map();
        this.eventListeners = new Map();
        this.tutorials = new Map();
        this.assessments = new Map();
        
        console.log('📚 Educational Features module loaded');
        this.init();
    }

    /**
     * Initialize the educational features system
     */
    async init() {
        try {
            this.setupTutorials();
            this.setupAssessments();
            this.loadUserProgress();
            this.setupEventHandlers();
            this.isInitialized = true;
            console.log('✅ Educational Features initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize Educational Features:', error);
        }
    }

    /**
     * Setup available tutorials
     */
    setupTutorials() {
        this.tutorials.set('cognitive_architecture', {
            id: 'cognitive_architecture',
            title: 'Understanding Cognitive Architecture',
            description: 'Learn about the layers and components of cognitive systems',
            difficulty: 'beginner',
            modules: [
                'Introduction to Cognitive Systems',
                'Perception and Attention',
                'Memory and Learning',
                'Reasoning and Decision Making',
                'Metacognition and Self-Awareness'
            ],
            estimatedTime: '30 minutes'
        });

        this.tutorials.set('transparency_features', {
            id: 'transparency_features',
            title: 'Cognitive Transparency Features',
            description: 'Explore how to understand AI reasoning processes',
            difficulty: 'intermediate',
            modules: [
                'What is Cognitive Transparency?',
                'Reasoning Visualization',
                'Knowledge Graph Exploration',
                'Uncertainty Analysis',
                'Provenance Tracking'
            ],
            estimatedTime: '45 minutes'
        });

        this.tutorials.set('advanced_querying', {
            id: 'advanced_querying',
            title: 'Advanced Query Techniques',
            description: 'Master complex querying and interaction patterns',
            difficulty: 'advanced',
            modules: [
                'Query Optimization',
                'Multi-step Reasoning',
                'Context Management',
                'Error Handling',
                'Performance Tuning'
            ],
            estimatedTime: '60 minutes'
        });

        console.log('📚 Tutorials configured:', Array.from(this.tutorials.keys()));
    }

    /**
     * Setup assessments
     */
    setupAssessments() {
        this.assessments.set('basic_concepts', {
            id: 'basic_concepts',
            title: 'Basic Concepts Assessment',
            questions: [
                {
                    type: 'multiple_choice',
                    question: 'What is the primary purpose of the attention layer?',
                    options: ['Memory storage', 'Focus management', 'Pattern recognition', 'Decision making'],
                    correct: 1
                },
                {
                    type: 'true_false',
                    question: 'Metacognition involves thinking about thinking.',
                    correct: true
                }
            ]
        });

        this.assessments.set('transparency_understanding', {
            id: 'transparency_understanding',
            title: 'Transparency Features Assessment',
            questions: [
                {
                    type: 'multiple_choice',
                    question: 'What does provenance tracking help you understand?',
                    options: ['System performance', 'Data origins', 'User preferences', 'Network latency'],
                    correct: 1
                }
            ]
        });

        console.log('📚 Assessments configured:', Array.from(this.assessments.keys()));
    }

    /**
     * Load user progress from storage
     */
    loadUserProgress() {
        try {
            const stored = localStorage.getItem('godelOS_educational_progress');
            if (stored) {
                const progress = JSON.parse(stored);
                this.userProgress = new Map(Object.entries(progress));
                console.log('📚 User progress loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load user progress:', error);
        }
    }

    /**
     * Save user progress to storage
     */
    saveUserProgress() {
        try {
            const progress = Object.fromEntries(this.userProgress);
            localStorage.setItem('godelOS_educational_progress', JSON.stringify(progress));
            console.log('📚 User progress saved');
        } catch (error) {
            console.warn('⚠️ Could not save user progress:', error);
        }
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        this.on('lessonStarted', (data) => {
            this.handleLessonStarted(data);
        });

        this.on('lessonCompleted', (data) => {
            this.handleLessonCompleted(data);
        });

        this.on('assessmentCompleted', (data) => {
            this.handleAssessmentCompleted(data);
        });
    }

    /**
     * Start a tutorial
     */
    startTutorial(tutorialId) {
        if (this.tutorials.has(tutorialId)) {
            const tutorial = this.tutorials.get(tutorialId);
            this.currentLesson = {
                type: 'tutorial',
                id: tutorialId,
                startTime: Date.now(),
                currentModule: 0
            };
            
            this.emit('lessonStarted', {
                type: 'tutorial',
                tutorial: tutorial,
                timestamp: Date.now()
            });
            
            console.log(`📚 Started tutorial: ${tutorial.title}`);
            return tutorial;
        } else {
            console.warn(`⚠️ Tutorial not found: ${tutorialId}`);
            return null;
        }
    }

    /**
     * Complete a tutorial module
     */
    completeModule(tutorialId, moduleIndex) {
        if (this.currentLesson && this.currentLesson.id === tutorialId) {
            this.currentLesson.currentModule = moduleIndex + 1;
            
            // Update progress
            const progressKey = `tutorial_${tutorialId}`;
            const currentProgress = this.userProgress.get(progressKey) || { completed: 0, modules: [] };
            currentProgress.modules[moduleIndex] = true;
            currentProgress.completed = currentProgress.modules.filter(Boolean).length;
            this.userProgress.set(progressKey, currentProgress);
            
            this.saveUserProgress();
            console.log(`📚 Completed module ${moduleIndex} of tutorial ${tutorialId}`);
        }
    }

    /**
     * Start an assessment
     */
    startAssessment(assessmentId) {
        if (this.assessments.has(assessmentId)) {
            const assessment = this.assessments.get(assessmentId);
            this.currentLesson = {
                type: 'assessment',
                id: assessmentId,
                startTime: Date.now(),
                answers: []
            };
            
            console.log(`📚 Started assessment: ${assessment.title}`);
            return assessment;
        } else {
            console.warn(`⚠️ Assessment not found: ${assessmentId}`);
            return null;
        }
    }

    /**
     * Submit assessment answer
     */
    submitAnswer(questionIndex, answer) {
        if (this.currentLesson && this.currentLesson.type === 'assessment') {
            this.currentLesson.answers[questionIndex] = answer;
            console.log(`📚 Answer submitted for question ${questionIndex}`);
        }
    }

    /**
     * Complete an assessment
     */
    completeAssessment() {
        if (this.currentLesson && this.currentLesson.type === 'assessment') {
            const assessment = this.assessments.get(this.currentLesson.id);
            const score = this.calculateScore(assessment, this.currentLesson.answers);
            
            const result = {
                assessmentId: this.currentLesson.id,
                score: score,
                answers: this.currentLesson.answers,
                completedAt: Date.now()
            };
            
            // Save result
            const progressKey = `assessment_${this.currentLesson.id}`;
            this.userProgress.set(progressKey, result);
            this.saveUserProgress();
            
            this.emit('assessmentCompleted', result);
            console.log(`📚 Assessment completed with score: ${score.percentage}%`);
            
            this.currentLesson = null;
            return result;
        }
        return null;
    }

    /**
     * Calculate assessment score
     */
    calculateScore(assessment, answers) {
        let correct = 0;
        const total = assessment.questions.length;
        
        assessment.questions.forEach((question, index) => {
            const userAnswer = answers[index];
            if (question.type === 'multiple_choice' && userAnswer === question.correct) {
                correct++;
            } else if (question.type === 'true_false' && userAnswer === question.correct) {
                correct++;
            }
        });
        
        return {
            correct: correct,
            total: total,
            percentage: Math.round((correct / total) * 100)
        };
    }

    /**
     * Get user's learning progress
     */
    getUserProgress() {
        return Object.fromEntries(this.userProgress);
    }

    /**
     * Get recommended next lesson
     */
    getRecommendedLesson() {
        // Simple recommendation logic
        const completedTutorials = Array.from(this.userProgress.keys())
            .filter(key => key.startsWith('tutorial_'))
            .map(key => key.replace('tutorial_', ''));
        
        const availableTutorials = Array.from(this.tutorials.keys());
        const nextTutorial = availableTutorials.find(id => !completedTutorials.includes(id));
        
        if (nextTutorial) {
            return {
                type: 'tutorial',
                id: nextTutorial,
                tutorial: this.tutorials.get(nextTutorial)
            };
        }
        
        return null;
    }

    /**
     * Handle lesson started event
     */
    handleLessonStarted(data) {
        console.log('📚 Lesson started event:', data);
    }

    /**
     * Handle lesson completed event
     */
    handleLessonCompleted(data) {
        console.log('📚 Lesson completed event:', data);
    }

    /**
     * Handle assessment completed event
     */
    handleAssessmentCompleted(data) {
        console.log('📚 Assessment completed event:', data);
    }

    /**
     * Event emitter functionality
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Get educational metrics
     */
    getMetrics() {
        return {
            totalTutorials: this.tutorials.size,
            totalAssessments: this.assessments.size,
            userProgress: this.getUserProgress(),
            currentLesson: this.currentLesson,
            isInitialized: this.isInitialized
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.saveUserProgress();
        this.eventListeners.clear();
        this.tutorials.clear();
        this.assessments.clear();
        this.userProgress.clear();
        this.currentLesson = null;
        this.isInitialized = false;
        console.log('📚 Educational Features destroyed');
    }
}

// Make the class available globally
window.EducationalFeatures = EducationalFeatures;

console.log('✅ Educational Features module loaded and available as window.EducationalFeatures');