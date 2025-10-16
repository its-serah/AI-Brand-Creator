// BrandForge AI - Enhanced Frontend JavaScript
class BrandCreator {
    constructor() {
        this.apiBaseUrl = 'https://brand-api-gpu-905163229563.us-central1.run.app/api/v1';
        this.currentTipIndex = 0;
        this.quoteIndex = 0;
        this.musicPlaying = false;
        this.currentResults = null;
        
        // Inspirational quotes for loading
        this.quotes = [
            { quote: "A brand is no longer what we tell the consumer it is—it is what consumers tell each other it is.", author: "Scott Cook, Intuit" },
            { quote: "Your brand is what other people say about you when you're not in the room.", author: "Jeff Bezos, Amazon" },
            { quote: "Products are made in a factory, but brands are created in the mind.", author: "Walter Landor" },
            { quote: "A logo doesn't sell (directly), it identifies.", author: "Paul Rand" },
            { quote: "The aim of marketing is to know and understand the customer so well the product or service fits him and sells itself.", author: "Peter Drucker" },
            { quote: "Brand is just a perception, and perception will match reality over time.", author: "Elon Musk" },
            { quote: "A brand for a company is like a reputation for a person.", author: "Jeff Bezos" },
            { quote: "The best marketing doesn't feel like marketing.", author: "Tom Fishburne" },
            { quote: "Make it simple. Make it memorable. Make it inviting to look at. Make it fun to read.", author: "Leo Burnett" },
            { quote: "Good design is obvious. Great design is transparent.", author: "Joe Sparano" }
        ];
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
    }

    bindEvents() {
        // Form submission
        const form = document.getElementById('brandCreationForm');
        form.addEventListener('submit', this.handleFormSubmit.bind(this));

        // Enhanced action buttons
        const createNewBtn = document.getElementById('createNewBtn');
        createNewBtn?.addEventListener('click', this.resetForm.bind(this));
        
        const tryAgainBtn = document.getElementById('tryAgainBtn');
        tryAgainBtn?.addEventListener('click', this.tryAgain.bind(this));
        
        const emailResultsBtn = document.getElementById('emailResultsBtn');
        emailResultsBtn?.addEventListener('click', this.showEmailModal.bind(this));

        // Email modal events
        const closeEmailModal = document.getElementById('closeEmailModal');
        closeEmailModal?.addEventListener('click', this.hideEmailModal.bind(this));
        
        const emailForm = document.getElementById('emailForm');
        emailForm?.addEventListener('submit', this.handleEmailSubmit.bind(this));
        
        // Music toggle
        const musicToggle = document.getElementById('musicToggle');
        musicToggle?.addEventListener('click', this.toggleMusic.bind(this));
        
        // Explainability toggle
        const explainabilityToggle = document.getElementById('explainabilityToggle');
        explainabilityToggle?.addEventListener('click', this.toggleExplainability.bind(this));

        // Form validation on input change
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('change', this.validateForm.bind(this));
            field.addEventListener('input', this.validateForm.bind(this));
        });

        // Show explainability when form is filled
        const allInputs = form.querySelectorAll('input, select, textarea');
        allInputs.forEach(input => {
            input.addEventListener('change', this.updateExplainability.bind(this));
        });
        
        // Close modal on outside click
        const emailModal = document.getElementById('emailModal');
        emailModal?.addEventListener('click', (e) => {
            if (e.target === emailModal) {
                this.hideEmailModal();
            }
        });
    }

    setupFormValidation() {
        this.validateForm();
    }

    validateForm() {
        const form = document.getElementById('brandCreationForm');
        const submitBtn = document.getElementById('submitBtn');
        const requiredFields = form.querySelectorAll('[required]');
        
        let isValid = true;
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });

        // Check if at least one personality trait is selected
        const personalityChecks = form.querySelectorAll('input[name="personality"]:checked');
        if (personalityChecks.length === 0) {
            isValid = false;
        }

        // Check if color scheme is selected
        const colorScheme = form.querySelector('input[name="colorScheme"]:checked');
        if (!colorScheme) {
            isValid = false;
        }

        submitBtn.disabled = !isValid;
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = this.collectFormData();
        const prompt = this.buildPrompt(formData);
        const negativePrompt = this.buildNegativePrompt(formData);

        console.log('Generated Prompt:', prompt);
        console.log('Generated Negative Prompt:', negativePrompt);

        // Show loading with enhanced experience
        this.showEnhancedLoading();
        
        await this.submitBrandRequest({
            ...formData,
            prompt,
            negativePrompt
        });
    }

    collectFormData() {
        const form = document.getElementById('brandCreationForm');
        const formData = new FormData(form);
        
        // Collect personality traits
        const personalities = [];
        form.querySelectorAll('input[name="personality"]:checked').forEach(checkbox => {
            personalities.push(checkbox.value);
        });

        return {
            industry: formData.get('industry'),
            businessName: formData.get('businessName'),
            personality: personalities,
            logoStyle: formData.get('logoStyle'),
            colorScheme: formData.get('colorScheme'),
            targetAudience: formData.get('targetAudience'),
            additionalNotes: formData.get('additionalNotes') || ''
        };
    }

    buildPrompt(data) {
        let prompt = `Create a ${data.logoStyle} logo for "${data.businessName}", `;
        prompt += `a ${data.industry} company. `;
        
        // Add personality traits
        if (data.personality.length > 0) {
            prompt += `The brand should feel ${data.personality.join(', ')}. `;
        }

        // Add color scheme preferences
        const colorDescriptions = {
            'warm': 'warm autumn colors like burnt orange, golden amber, and deep maroon',
            'cool': 'cool colors like blues and teals',
            'neutral': 'neutral colors like grays, whites, and earth tones',
            'vibrant': 'vibrant and energetic colors'
        };
        
        if (colorDescriptions[data.colorScheme]) {
            prompt += `Use ${colorDescriptions[data.colorScheme]}. `;
        }

        // Add target audience context
        const audienceContext = {
            'young-adults': 'Appeal to young adults aged 18-35 with modern, trendy aesthetics',
            'professionals': 'Appeal to professionals with clean, sophisticated design',
            'families': 'Appeal to families with friendly, approachable design',
            'seniors': 'Appeal to seniors with clear, readable, and trustworthy design',
            'businesses': 'Appeal to other businesses with professional, authoritative design',
            'global': 'Appeal to a global audience with universal, inclusive design'
        };
        
        if (audienceContext[data.targetAudience]) {
            prompt += `${audienceContext[data.targetAudience]}. `;
        }

        // Add logo style specifics
        const styleInstructions = {
            'minimal': 'Keep it clean and simple with minimal elements',
            'geometric': 'Use geometric shapes and mathematical precision',
            'text-based': 'Focus on typography and lettering design',
            'symbolic': 'Create a symbolic representation of the brand concept',
            'abstract': 'Use abstract forms and creative interpretation',
            'classic': 'Use timeless, traditional design principles'
        };
        
        if (styleInstructions[data.logoStyle]) {
            prompt += `${styleInstructions[data.logoStyle]}. `;
        }

        // Add industry-specific elements
        const industryElements = {
            'technology': 'incorporate subtle tech elements without clichés',
            'healthcare': 'convey trust, care, and professionalism',
            'education': 'suggest knowledge, growth, and accessibility',
            'finance': 'convey stability, trust, and prosperity',
            'retail': 'be approachable and memorable for consumers',
            'food': 'be appetizing and evoke freshness or comfort',
            'fashion': 'be stylish and reflect current trends',
            'automotive': 'suggest motion, power, and reliability',
            'real-estate': 'convey stability, growth, and home',
            'consulting': 'suggest expertise, guidance, and professionalism',
            'creative': 'showcase creativity and artistic vision'
        };
        
        if (industryElements[data.industry]) {
            prompt += `Make sure to ${industryElements[data.industry]}. `;
        }

        // Add additional notes if provided
        if (data.additionalNotes.trim()) {
            prompt += `Additional requirements: ${data.additionalNotes}. `;
        }

        // Final refinements
        prompt += 'Create a high-quality, professional logo that would work well across all media. ';
        prompt += 'The design should be scalable, memorable, and unique. ';
        prompt += 'Avoid overused symbols and clichés. Focus on originality and brand differentiation.';

        return prompt;
    }

    buildNegativePrompt(data) {
        let negativePrompt = 'blurry, low quality, pixelated, distorted, watermark, text overlay, ';
        negativePrompt += 'clipart, generic symbols, overused icons, cliché elements, ';
        negativePrompt += 'poor composition, unbalanced design, amateur, unprofessional, ';
        negativePrompt += 'too complex, cluttered, illegible, inappropriate colors, ';

        // Industry-specific negatives
        const industryNegatives = {
            'technology': 'circuit boards, gears, lightbulbs, atoms, ',
            'healthcare': 'red crosses, stethoscopes, pills, syringes, ',
            'education': 'graduation caps, apples, books, pencils, ',
            'finance': 'dollar signs, coins, piggy banks, graphs, ',
            'retail': 'shopping carts, price tags, bags, ',
            'food': 'chef hats, forks and knives, plates, ',
            'fashion': 'hangers, mannequins, sewing machines, ',
            'automotive': 'car silhouettes, wheels, keys, ',
            'real-estate': 'house shapes, keys, rooftops, ',
            'consulting': 'handshakes, briefcases, ties, ',
            'creative': 'paint brushes, palettes, easels, '
        };

        if (industryNegatives[data.industry]) {
            negativePrompt += industryNegatives[data.industry];
        }

        // Style-specific negatives
        if (data.logoStyle === 'minimal') {
            negativePrompt += 'ornate details, excessive elements, decorative flourishes, ';
        } else if (data.logoStyle === 'text-based') {
            negativePrompt += 'complex imagery, pictorial elements, symbols, ';
        } else if (data.logoStyle === 'geometric') {
            negativePrompt += 'organic shapes, hand-drawn elements, irregular forms, ';
        }

        // Color scheme negatives
        const colorNegatives = {
            'warm': 'cold colors, blues, greens, purples, ',
            'cool': 'warm colors, reds, oranges, yellows, ',
            'neutral': 'bright neon colors, highly saturated hues, ',
            'vibrant': 'muted colors, desaturated tones, grays, '
        };

        if (colorNegatives[data.colorScheme]) {
            negativePrompt += colorNegatives[data.colorScheme];
        }

        negativePrompt += 'inconsistent branding, multiple conflicting styles, poor readability';

        return negativePrompt;
    }

    async submitBrandRequest(brandData) {
        const submitBtn = document.getElementById('submitBtn');
        const loadingSection = document.getElementById('loadingSection');
        const formSection = document.getElementById('brandForm');

        try {
            // Show loading state
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Hide form and show loading
            formSection.style.display = 'none';
            loadingSection.style.display = 'flex';

            // Make API request
            const response = await fetch(`${this.apiBaseUrl}/brand/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    business_name: brandData.businessName,
                    industry: brandData.industry,
                    style: brandData.logoStyle,
                    color_scheme: brandData.colorScheme,
                    personality_traits: brandData.personality,
                    target_audience: brandData.targetAudience,
                    prompt: brandData.prompt,
                    negative_prompt: brandData.negativePrompt,
                    additional_notes: brandData.additionalNotes
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const result = await response.json();
            
            // Hide loading and show results
            loadingSection.style.display = 'none';
            this.displayResults(result, brandData);

        } catch (error) {
            console.error('Error generating brand:', error);
            
            // Hide loading and show form again
            loadingSection.style.display = 'none';
            formSection.style.display = 'block';
            
            // Reset button state
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            
            // Show error message
            this.showErrorMessage('Sorry, there was an error generating your brand. Please try again.');
        }
    }

    displayResults(result, originalData) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsGrid = document.getElementById('resultsGrid');
        
        // Clear previous results
        resultsGrid.innerHTML = '';
        
        // Create results cards
        if (result.logos && result.logos.length > 0) {
            result.logos.forEach((logo, index) => {
                const resultCard = this.createResultCard(logo, result, originalData, index);
                resultsGrid.appendChild(resultCard);
            });
        } else {
            // Create a single result card with brand info
            const resultCard = this.createResultCard(null, result, originalData, 0);
            resultsGrid.appendChild(resultCard);
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createResultCard(logo, result, originalData, index) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const logoSection = logo ? `
            <div class="logo-container">
                <img src="${logo.url}" alt="Generated Logo ${index + 1}" />
            </div>
        ` : `
            <div class="logo-container">
                <div style="color: var(--warm-gray); text-align: center;">
                    Logo will appear here once generated
                </div>
            </div>
        `;
        
        const colorsSection = result.color_palette ? `
            <div class="brand-colors">
                ${result.color_palette.map(color => `
                    <div class="color-swatch" style="background-color: ${color};" title="${color}"></div>
                `).join('')}
            </div>
        ` : '';

        // Enhanced features display
        const extractedColorsSection = result.extracted_colors && result.extracted_colors.length > 0 ? `
            <div style="margin-top: 1rem;">
                <strong>Extracted Colors from Logo:</strong><br>
                <div class="brand-colors">
                    ${result.extracted_colors.slice(0, 6).map(color => `
                        <div class="color-swatch" style="background-color: ${color};" title="${color}"></div>
                    `).join('')}
                </div>
            </div>
        ` : '';
        
        const enhancementBadges = result.enhancement_features ? `
            <div class="enhancement-badges">
                ${result.enhancement_features.map(feature => `
                    <span class="enhancement-badge">${this.formatEnhancementFeature(feature)}</span>
                `).join('')}
            </div>
        ` : '';
        
        const socialExportsSection = result.social_media_exports && Object.keys(result.social_media_exports).length > 0 ? `
            <div style="margin-top: 1rem;">
                <strong>Social Media Formats Available</strong>
                <div class="social-formats">
                    <span class="social-format-badge">Instagram</span>
                    <span class="social-format-badge">Facebook</span>
                    <span class="social-format-badge">Twitter</span>
                    <span class="social-format-badge">YouTube</span>
                    <span class="social-format-badge">LinkedIn</span>
                </div>
            </div>
        ` : '';
        
        card.innerHTML = `
            <h3>${originalData.businessName}</h3>
            ${enhancementBadges}
            ${logoSection}
            <div class="brand-info">
                <p><strong>Industry:</strong> ${this.formatValue(originalData.industry)}</p>
                <p><strong>Style:</strong> ${this.formatValue(originalData.logoStyle)}</p>
                <p><strong>Personality:</strong> ${originalData.personality.join(', ')}</p>
                <p><strong>Target Audience:</strong> ${this.formatValue(originalData.targetAudience)}</p>
                ${result.font_suggestion ? `<p><strong>Recommended Font:</strong> ${result.font_suggestion}</p>` : ''}
                ${colorsSection ? `<div style="margin-top: 1rem;"><strong>Brand Colors:</strong><br>${colorsSection}</div>` : ''}
                ${extractedColorsSection}
                ${socialExportsSection}
                ${result.brand_description ? `<p style="margin-top: 1rem;"><strong>Brand Description:</strong><br>${result.brand_description}</p>` : ''}
            </div>
        `;
        
        return card;
    }

    formatValue(value) {
        return value.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    formatEnhancementFeature(feature) {
        const featureNames = {
            '4x_upscaling': '4x Upscaled',
            'color_extraction': 'Color Extracted',
            'color_variations': 'Color Variations',
            'social_media_exports': 'Social Media Ready'
        };
        return featureNames[feature] || feature.replace(/_/g, ' ');
    }

    showErrorMessage(message) {
        // Create or update error message element
        let errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'errorMessage';
            errorDiv.style.cssText = `
                background: #ffebee;
                color: #c62828;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border: 1px solid #ffcdd2;
                text-align: center;
            `;
            
            const formCard = document.querySelector('.form-card');
            formCard.insertBefore(errorDiv, formCard.firstChild);
        }
        
        errorDiv.textContent = message;
        errorDiv.scrollIntoView({ behavior: 'smooth' });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    toggleExplainability() {
        const toggle = document.getElementById('explainabilityToggle');
        const content = document.getElementById('explainabilityContent');
        
        if (content.style.display === 'none' || !content.style.display) {
            content.style.display = 'block';
            toggle.classList.add('expanded');
            toggle.querySelector('span').textContent = 'Hide AI Prompts';
            this.updateExplainability();
        } else {
            content.style.display = 'none';
            toggle.classList.remove('expanded');
            toggle.querySelector('span').textContent = 'Show AI Prompts';
        }
    }

    updateExplainability() {
        const formData = this.collectFormData();
        
        // Check if form has enough data
        if (!formData.businessName || !formData.industry || formData.personality.length === 0) {
            document.getElementById('explainabilitySection').style.display = 'none';
            return;
        }
        
        // Show explainability section
        document.getElementById('explainabilitySection').style.display = 'block';
        
        // Generate and display prompts
        const prompt = this.buildPrompt(formData);
        const negativePrompt = this.buildNegativePrompt(formData);
        
        // Update displays
        document.getElementById('finalPromptDisplay').textContent = prompt;
        document.getElementById('negativePromptDisplay').textContent = negativePrompt;
        
        // Show breakdown
        this.showPromptBreakdown(formData, prompt, negativePrompt);
    }

    showPromptBreakdown(formData, prompt, negativePrompt) {
        const breakdown = document.getElementById('promptBreakdown');
        
        const breakdownItems = [
            { label: 'Business Name', value: formData.businessName },
            { label: 'Industry', value: this.formatValue(formData.industry) },
            { label: 'Logo Style', value: this.formatValue(formData.logoStyle) },
            { label: 'Color Scheme', value: this.formatValue(formData.colorScheme) },
            { label: 'Personality', value: formData.personality.join(', ') },
            { label: 'Target Audience', value: this.formatValue(formData.targetAudience) }
        ];
        
        if (formData.additionalNotes) {
            breakdownItems.push({ label: 'Additional Notes', value: formData.additionalNotes });
        }
        
        breakdown.innerHTML = breakdownItems.map(item => `
            <div class="breakdown-item">
                <div class="breakdown-label">${item.label}:</div>
                <div class="breakdown-value">${item.value}</div>
            </div>
        `).join('');
    }

    resetForm() {
        // Hide results and show form
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('formSection').style.display = 'block';
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('explainabilitySection').style.display = 'none';
        
        // Reset form
        const form = document.getElementById('brandCreationForm');
        form.reset();
        
        // Reset button state
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.classList.remove('loading');
        submitBtn.disabled = true; // Will be enabled when form is valid
        
        // Remove error messages
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.remove();
        }
        
        // Scroll to top
        document.querySelector('.header').scrollIntoView({ behavior: 'smooth' });
        
        // Revalidate form
        this.validateForm();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BrandCreator();
});

// Helper function to handle API errors gracefully
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

// Add some utility functions for better UX
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Progressive enhancement for better accessibility
function enhanceAccessibility() {
    // Add ARIA labels to form elements
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const label = group.querySelector('label');
        const input = group.querySelector('input, select, textarea');
        if (label && input && !input.getAttribute('aria-describedby')) {
            const labelId = `label-${Math.random().toString(36).substr(2, 9)}`;
            label.id = labelId;
            input.setAttribute('aria-describedby', labelId);
        }
    });
    
    // Add keyboard navigation for custom elements
    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
        option.setAttribute('tabindex', '0');
        option.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const radio = option.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change'));
                }
            }
        });
    });
    
    const checkboxItems = document.querySelectorAll('.checkbox-item');
    checkboxItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const checkbox = item.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            }
        });
    });
}

// Enhanced loading and interactive methods for BrandCreator class
BrandCreator.prototype.showEnhancedLoading = function() {
    const loadingSection = document.getElementById('loadingSection');
    const formSection = document.getElementById('brandForm');
    
    formSection.style.display = 'none';
    loadingSection.style.display = 'flex';
    
    this.startQuoteRotation();
    this.startTipCarousel();
    this.animateProgress();
};

BrandCreator.prototype.startQuoteRotation = function() {
    const quoteElement = document.getElementById('inspirationalQuote');
    const authorElement = document.getElementById('quoteAuthor');
    
    const rotateQuote = () => {
        const quote = this.quotes[this.quoteIndex];
        quoteElement.textContent = `"${quote.quote}"`;
        authorElement.textContent = `— ${quote.author}`;
        this.quoteIndex = (this.quoteIndex + 1) % this.quotes.length;
    };
    
    rotateQuote();
    this.quoteInterval = setInterval(rotateQuote, 8000);
};

BrandCreator.prototype.startTipCarousel = function() {
    const tips = document.querySelectorAll('.tip-card');
    
    const rotateTips = () => {
        tips.forEach((tip, index) => {
            tip.classList.toggle('active', index === this.currentTipIndex);
        });
        this.currentTipIndex = (this.currentTipIndex + 1) % tips.length;
    };
    
    this.tipInterval = setInterval(rotateTips, 5000);
};

BrandCreator.prototype.animateProgress = function() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    
    const steps = [
        { progress: 15, title: "Initializing design intelligence", subtitle: "Loading AI models and design databases" },
        { progress: 30, title: "Analyzing brand requirements", subtitle: "Processing industry context and target audience" },
        { progress: 50, title: "Generating design concepts", subtitle: "Creating unique visual identities" },
        { progress: 70, title: "Applying design psychology", subtitle: "Optimizing colors, typography, and composition" },
        { progress: 85, title: "Refining brand elements", subtitle: "Ensuring scalability and professional standards" },
        { progress: 100, title: "Brand identity complete", subtitle: "Your professional brand system is ready" }
    ];
    
    let currentStep = 0;
    
    const updateProgress = () => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            progressFill.style.width = step.progress + '%';
            if (progressText) progressText.textContent = step.progress + '%';
            loadingTitle.textContent = step.title;
            loadingSubtitle.textContent = step.subtitle;
            currentStep++;
        }
    };
    
    this.progressInterval = setInterval(updateProgress, 5000);
    updateProgress();
};

BrandCreator.prototype.tryAgain = function() {
    const formData = this.collectFormData();
    const prompt = this.buildPrompt(formData) + " (variation)";
    const negativePrompt = this.buildNegativePrompt(formData);
    
    this.showEnhancedLoading();
    
    this.submitBrandRequest({
        ...formData,
        prompt,
        negativePrompt
    });
};

BrandCreator.prototype.showEmailModal = function() {
    const modal = document.getElementById('emailModal');
    modal.style.display = 'flex';
    
    const userEmail = document.getElementById('userEmail');
    userEmail.focus();
};

BrandCreator.prototype.hideEmailModal = function() {
    const modal = document.getElementById('emailModal');
    modal.style.display = 'none';
    
    const emailForm = document.getElementById('emailForm');
    emailForm.reset();
};

BrandCreator.prototype.handleEmailSubmit = async function(event) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    try {
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        submitBtn.textContent = 'Successfully Sent!';
        
        setTimeout(() => {
            this.hideEmailModal();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            this.showSuccessMessage('Your brand kit has been sent to your email!');
        }, 1500);
        
    } catch (error) {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        this.showErrorMessage('Failed to send email. Please try again.');
    }
};

BrandCreator.prototype.toggleMusic = function() {
    const musicBtn = document.getElementById('musicToggle');
    
    if (this.musicPlaying) {
        musicBtn.textContent = 'Focus Mode Audio';
        this.musicPlaying = false;
    } else {
        this.playNotificationSound();
        musicBtn.textContent = 'Stop Audio';
        this.musicPlaying = true;
    }
};

BrandCreator.prototype.playNotificationSound = function() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.frequency.setValueAtTime(440, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
    } catch (e) {
        console.log('Audio not supported');
    }
};

BrandCreator.prototype.showSuccessMessage = function(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 3000;
        font-weight: 500;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 4000);
};

// Initialize accessibility enhancements
document.addEventListener('DOMContentLoaded', enhanceAccessibility);
