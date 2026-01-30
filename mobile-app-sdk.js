/**
 * AI Travel Planner - Mobile App SDK
 * ==================================
 * JavaScript SDK for easy integration with mobile web apps
 */

class TravelPlannerSDK {
    constructor(config) {
        this.baseURL = config.baseURL || 'https://travel-planner.yourcompany.com/mobile';
        this.apiKey = config.apiKey;
        this.timeout = config.timeout || 30000;
        this.retryAttempts = config.retryAttempts || 3;
        this.retryDelay = config.retryDelay || 1000;
        
        if (!this.apiKey) {
            throw new Error('API key is required');
        }
    }

    /**
     * Make HTTP request with retry logic
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey,
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        let lastError;
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, requestOptions);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                lastError = error;
                if (attempt < this.retryAttempts) {
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
                }
            }
        }
        
        throw lastError;
    }

    /**
     * Check API health
     */
    async healthCheck() {
        return await this.makeRequest('/health');
    }

    /**
     * Get available travel themes
     */
    async getThemes() {
        return await this.makeRequest('/themes');
    }

    /**
     * Generate travel itinerary
     */
    async generateItinerary(params) {
        const {
            city,
            country,
            theme = 'cultural',
            planSize = 6,
            startTime = '09:00',
            endTime = '22:00',
            language = 'en'
        } = params;

        if (!city || !country) {
            throw new Error('City and country are required');
        }

        return await this.makeRequest('/itinerary', {
            method: 'POST',
            body: JSON.stringify({
                city,
                country,
                theme,
                plan_size: planSize,
                start_time: startTime,
                end_time: endTime,
                language
            })
        });
    }

    /**
     * Quick itinerary generation with query parameters
     */
    async quickItinerary(city, country, theme = 'cultural', planSize = 6) {
        const params = new URLSearchParams({
            city,
            country,
            theme,
            plan_size: planSize.toString()
        });

        return await this.makeRequest(`/itinerary/quick?${params}`);
    }

    /**
     * Validate theme
     */
    async validateTheme(theme) {
        const themes = await this.getThemes();
        return themes.themes.includes(theme);
    }

    /**
     * Get itinerary with error handling and validation
     */
    async getItinerary(params) {
        try {
            // Validate theme if provided
            if (params.theme) {
                const isValidTheme = await this.validateTheme(params.theme);
                if (!isValidTheme) {
                    throw new Error(`Invalid theme: ${params.theme}`);
                }
            }

            // Generate itinerary
            const result = await this.generateItinerary(params);
            
            if (!result.success) {
                throw new Error(result.message || 'Failed to generate itinerary');
            }

            return result;
        } catch (error) {
            console.error('Error generating itinerary:', error);
            throw error;
        }
    }
}

/**
 * React Hook for Travel Planner SDK
 */
function useTravelPlanner(config) {
    const [sdk] = useState(() => new TravelPlannerSDK(config));
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const generateItinerary = useCallback(async (params) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await sdk.getItinerary(params);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [sdk]);

    const getThemes = useCallback(async () => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await sdk.getThemes();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [sdk]);

    const healthCheck = useCallback(async () => {
        try {
            return await sdk.healthCheck();
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [sdk]);

    return {
        generateItinerary,
        getThemes,
        healthCheck,
        loading,
        error,
        sdk
    };
}

/**
 * Vue.js Plugin for Travel Planner SDK
 */
const TravelPlannerPlugin = {
    install(app, config) {
        const sdk = new TravelPlannerSDK(config);
        app.config.globalProperties.$travelPlanner = sdk;
        app.provide('travelPlanner', sdk);
    }
};

/**
 * Angular Service for Travel Planner SDK
 */
class TravelPlannerService {
    private sdk: TravelPlannerSDK;

    constructor() {
        this.sdk = new TravelPlannerSDK({
            baseURL: 'https://travel-planner.yourcompany.com/mobile',
            apiKey: 'your-mobile-app-api-key-here'
        });
    }

    async generateItinerary(params: any) {
        return await this.sdk.generateItinerary(params);
    }

    async getThemes() {
        return await this.sdk.getThemes();
    }

    async healthCheck() {
        return await this.sdk.healthCheck();
    }
}

/**
 * Utility functions
 */
const TravelPlannerUtils = {
    /**
     * Format time duration
     */
    formatDuration(startTime, endTime) {
        const start = new Date(`2000-01-01T${startTime}`);
        const end = new Date(`2000-01-01T${endTime}`);
        const diffMs = end - start;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        
        if (diffHours > 0) {
            return `${diffHours}h ${diffMinutes}m`;
        }
        return `${diffMinutes}m`;
    },

    /**
     * Calculate total itinerary duration
     */
    calculateTotalDuration(slots) {
        if (!slots || slots.length === 0) return '0m';
        
        const firstSlot = slots[0];
        const lastSlot = slots[slots.length - 1];
        
        return this.formatDuration(firstSlot.start, lastSlot.end);
    },

    /**
     * Group activities by category
     */
    groupByCategory(slots) {
        return slots.reduce((groups, slot) => {
            const category = slot.category || 'other';
            if (!groups[category]) {
                groups[category] = [];
            }
            groups[category].push(slot);
            return groups;
        }, {});
    },

    /**
     * Get theme emoji
     */
    getThemeEmoji(theme) {
        const emojis = {
            cultural: '🏛️',
            adventure: '🏔️',
            foodies: '🍽️',
            family: '👨‍👩‍👧‍👦',
            couples: '💕',
            friends: '👥'
        };
        return emojis[theme] || '🗺️';
    },

    /**
     * Validate city and country
     */
    validateLocation(city, country) {
        if (!city || typeof city !== 'string' || city.trim().length === 0) {
            throw new Error('City is required and must be a non-empty string');
        }
        
        if (!country || typeof country !== 'string' || country.trim().length === 0) {
            throw new Error('Country is required and must be a non-empty string');
        }
        
        return true;
    }
};

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    // CommonJS
    module.exports = {
        TravelPlannerSDK,
        useTravelPlanner,
        TravelPlannerPlugin,
        TravelPlannerService,
        TravelPlannerUtils
    };
} else if (typeof define === 'function' && define.amd) {
    // AMD
    define([], function() {
        return {
            TravelPlannerSDK,
            useTravelPlanner,
            TravelPlannerPlugin,
            TravelPlannerService,
            TravelPlannerUtils
        };
    });
} else {
    // Browser global
    window.TravelPlannerSDK = TravelPlannerSDK;
    window.useTravelPlanner = useTravelPlanner;
    window.TravelPlannerPlugin = TravelPlannerPlugin;
    window.TravelPlannerService = TravelPlannerService;
    window.TravelPlannerUtils = TravelPlannerUtils;
}
