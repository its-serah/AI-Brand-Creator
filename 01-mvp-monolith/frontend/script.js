// Brand Creator Frontend JavaScript
class BrandCreator {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
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

        // Create new brand button
        const createNewBtn = document.getElementById('createNewBtn');
        createNewBtn?.addEventListener('click', this.resetForm.bind(this));

        // Form validation on input change
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('change', this.validateForm.bind(this));
            field.addEventListener('input', this.validateForm.bind(this));
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

        card.innerHTML = `
            <h3>${originalData.businessName}</h3>
            ${logoSection}
            <div class="brand-info">
                <p><strong>Industry:</strong> ${this.formatValue(originalData.industry)}</p>
                <p><strong>Style:</strong> ${this.formatValue(originalData.logoStyle)}</p>
                <p><strong>Personality:</strong> ${originalData.personality.join(', ')}</p>
                <p><strong>Target Audience:</strong> ${this.formatValue(originalData.targetAudience)}</p>
                ${result.font_suggestion ? `<p><strong>Recommended Font:</strong> ${result.font_suggestion}</p>` : ''}
                ${colorsSection ? `<div style="margin-top: 1rem;"><strong>Brand Colors:</strong><br>${colorsSection}</div>` : ''}
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

    resetForm() {
        // Hide results and show form
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('formSection').style.display = 'block';
        document.getElementById('loadingSection').style.display = 'none';
        
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

// Initialize accessibility enhancements
document.addEventListener('DOMContentLoaded', enhanceAccessibility);
