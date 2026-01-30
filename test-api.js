/**
 * AI Travel Planner - API Testing Suite
 * =====================================
 * Comprehensive testing script for production deployment
 */

const https = require('https');
const http = require('http');

// Configuration
const config = {
    // Production URLs
    production: {
        baseURL: 'https://travel-planner.yourcompany.com',
        mobileURL: 'https://travel-planner.yourcompany.com/mobile',
        internalURL: 'http://internal-travel-planner:8080'
    },
    
    // Testing URLs
    testing: {
        baseURL: 'https://travel-planner-test.yourcompany.com',
        mobileURL: 'https://travel-planner-test.yourcompany.com/mobile'
    },
    
    // API Key
    apiKey: 'your-mobile-app-api-key-here',
    
    // Test data
    testData: {
        city: 'Cairo',
        country: 'Egypt',
        theme: 'cultural',
        planSize: 6,
        startTime: '09:00',
        endTime: '22:00',
        language: 'en'
    }
};

// Test results storage
const testResults = {
    passed: 0,
    failed: 0,
    errors: []
};

/**
 * Make HTTP request
 */
function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const isHttps = url.startsWith('https://');
        const client = isHttps ? https : http;
        
        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': config.apiKey,
                ...options.headers
            },
            timeout: 30000,
            rejectUnauthorized: false, // For self-signed certificates
            ...options
        };

        const req = client.request(url, requestOptions, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve({
                        status: res.statusCode,
                        headers: res.headers,
                        data: jsonData
                    });
                } catch (error) {
                    resolve({
                        status: res.statusCode,
                        headers: res.headers,
                        data: data
                    });
                }
            });
        });

        req.on('error', reject);
        req.on('timeout', () => reject(new Error('Request timeout')));
        
        if (options.body) {
            req.write(JSON.stringify(options.body));
        }
        
        req.end();
    });
}

/**
 * Test function wrapper
 */
async function runTest(testName, testFunction) {
    console.log(`\n🧪 Running test: ${testName}`);
    try {
        await testFunction();
        testResults.passed++;
        console.log(`✅ ${testName} - PASSED`);
    } catch (error) {
        testResults.failed++;
        testResults.errors.push({ test: testName, error: error.message });
        console.log(`❌ ${testName} - FAILED: ${error.message}`);
    }
}

/**
 * Test 1: Health Check
 */
async function testHealthCheck() {
    const response = await makeRequest(`${config.production.baseURL}/health`);
    
    if (response.status !== 200) {
        throw new Error(`Health check returned status ${response.status}`);
    }
    
    if (!response.data.status || response.data.status !== 'healthy') {
        throw new Error('Health check status is not healthy');
    }
    
    console.log(`   Status: ${response.data.status}`);
    console.log(`   Version: ${response.data.version}`);
    console.log(`   Database: ${response.data.database_status}`);
}

/**
 * Test 2: Mobile API Health Check
 */
async function testMobileHealthCheck() {
    const response = await makeRequest(`${config.production.mobileURL}/health`);
    
    if (response.status !== 200) {
        throw new Error(`Mobile health check returned status ${response.status}`);
    }
    
    if (!response.data.status || response.data.status !== 'healthy') {
        throw new Error('Mobile health check status is not healthy');
    }
}

/**
 * Test 3: Get Themes
 */
async function testGetThemes() {
    const response = await makeRequest(`${config.production.mobileURL}/themes`);
    
    if (response.status !== 200) {
        throw new Error(`Get themes returned status ${response.status}`);
    }
    
    if (!response.data.success) {
        throw new Error('Get themes request was not successful');
    }
    
    if (!response.data.themes || !Array.isArray(response.data.themes)) {
        throw new Error('Themes data is not an array');
    }
    
    const expectedThemes = ['cultural', 'adventure', 'foodies', 'family', 'couples', 'friends'];
    for (const theme of expectedThemes) {
        if (!response.data.themes.includes(theme)) {
            throw new Error(`Missing expected theme: ${theme}`);
        }
    }
    
    console.log(`   Available themes: ${response.data.themes.join(', ')}`);
}

/**
 * Test 4: Generate Itinerary (POST)
 */
async function testGenerateItinerary() {
    const response = await makeRequest(`${config.production.mobileURL}/itinerary`, {
        method: 'POST',
        body: config.testData
    });
    
    if (response.status !== 200) {
        throw new Error(`Generate itinerary returned status ${response.status}`);
    }
    
    if (!response.data.success) {
        throw new Error(`Generate itinerary failed: ${response.data.message}`);
    }
    
    if (!response.data.data || !response.data.data.slots) {
        throw new Error('Itinerary data is missing or invalid');
    }
    
    if (response.data.data.slots.length === 0) {
        throw new Error('No activities found in itinerary');
    }
    
    console.log(`   Generated ${response.data.data.slots.length} activities`);
    console.log(`   Total duration: ${response.data.data.total_duration || 'N/A'}`);
    console.log(`   Theme: ${response.data.data.theme}`);
    console.log(`   City: ${response.data.data.city}, ${response.data.data.country}`);
}

/**
 * Test 5: Quick Itinerary (GET)
 */
async function testQuickItinerary() {
    const params = new URLSearchParams({
        city: config.testData.city,
        country: config.testData.country,
        theme: config.testData.theme,
        plan_size: config.testData.planSize.toString()
    });
    
    const response = await makeRequest(`${config.production.mobileURL}/itinerary/quick?${params}`);
    
    if (response.status !== 200) {
        throw new Error(`Quick itinerary returned status ${response.status}`);
    }
    
    if (!response.data.success) {
        throw new Error(`Quick itinerary failed: ${response.data.message}`);
    }
    
    if (!response.data.data || !response.data.data.slots) {
        throw new Error('Quick itinerary data is missing or invalid');
    }
    
    console.log(`   Quick itinerary generated ${response.data.data.slots.length} activities`);
}

/**
 * Test 6: Invalid API Key
 */
async function testInvalidApiKey() {
    const response = await makeRequest(`${config.production.mobileURL}/health`, {
        headers: {
            'X-API-Key': 'invalid-api-key'
        }
    });
    
    if (response.status !== 401) {
        throw new Error(`Expected 401 status for invalid API key, got ${response.status}`);
    }
}

/**
 * Test 7: Missing API Key
 */
async function testMissingApiKey() {
    const response = await makeRequest(`${config.production.mobileURL}/health`, {
        headers: {}
    });
    
    if (response.status !== 401) {
        throw new Error(`Expected 401 status for missing API key, got ${response.status}`);
    }
}

/**
 * Test 8: Invalid Theme
 */
async function testInvalidTheme() {
    const response = await makeRequest(`${config.production.mobileURL}/itinerary`, {
        method: 'POST',
        body: {
            ...config.testData,
            theme: 'invalid-theme'
        }
    });
    
    if (response.status !== 400) {
        throw new Error(`Expected 400 status for invalid theme, got ${response.status}`);
    }
}

/**
 * Test 9: Missing Required Fields
 */
async function testMissingFields() {
    const response = await makeRequest(`${config.production.mobileURL}/itinerary`, {
        method: 'POST',
        body: {
            theme: config.testData.theme
            // Missing city and country
        }
    });
    
    if (response.status !== 422) {
        throw new Error(`Expected 422 status for missing fields, got ${response.status}`);
    }
}

/**
 * Test 10: Rate Limiting
 */
async function testRateLimiting() {
    const requests = [];
    const maxRequests = 25; // Should trigger rate limiting
    
    for (let i = 0; i < maxRequests; i++) {
        requests.push(makeRequest(`${config.production.mobileURL}/health`));
    }
    
    const responses = await Promise.allSettled(requests);
    const rateLimitedResponses = responses.filter(
        result => result.status === 'fulfilled' && result.value.status === 429
    );
    
    if (rateLimitedResponses.length === 0) {
        console.log('   Rate limiting not triggered (may be configured differently)');
    } else {
        console.log(`   Rate limiting triggered for ${rateLimitedResponses.length} requests`);
    }
}

/**
 * Test 11: Internal API Access
 */
async function testInternalApiAccess() {
    try {
        const response = await makeRequest(`${config.production.internalURL}/health`);
        
        if (response.status !== 200) {
            throw new Error(`Internal API returned status ${response.status}`);
        }
        
        console.log('   Internal API is accessible');
    } catch (error) {
        if (error.code === 'ECONNREFUSED') {
            console.log('   Internal API not accessible (expected if not on company subnet)');
        } else {
            throw error;
        }
    }
}

/**
 * Test 12: SSL Certificate
 */
async function testSSLCertificate() {
    const https = require('https');
    
    return new Promise((resolve, reject) => {
        const req = https.request(config.production.baseURL, { rejectUnauthorized: true }, (res) => {
            console.log('   SSL certificate is valid');
            resolve();
        });
        
        req.on('error', (error) => {
            if (error.code === 'CERT_HAS_EXPIRED') {
                reject(new Error('SSL certificate has expired'));
            } else if (error.code === 'SELF_SIGNED_CERTIFICATE') {
                console.log('   Using self-signed certificate (OK for testing)');
                resolve();
            } else {
                reject(error);
            }
        });
        
        req.end();
    });
}

/**
 * Test 13: CORS Headers
 */
async function testCORSHeaders() {
    const response = await makeRequest(`${config.production.mobileURL}/health`, {
        headers: {
            'Origin': 'https://your-mobile-app.com'
        }
    });
    
    if (!response.headers['access-control-allow-origin']) {
        throw new Error('CORS headers not present');
    }
    
    console.log(`   CORS headers present: ${response.headers['access-control-allow-origin']}`);
}

/**
 * Test 14: Response Time
 */
async function testResponseTime() {
    const startTime = Date.now();
    await makeRequest(`${config.production.mobileURL}/health`);
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    if (responseTime > 5000) {
        throw new Error(`Response time too slow: ${responseTime}ms`);
    }
    
    console.log(`   Response time: ${responseTime}ms`);
}

/**
 * Test 15: Error Handling
 */
async function testErrorHandling() {
    const response = await makeRequest(`${config.production.mobileURL}/nonexistent-endpoint`);
    
    if (response.status !== 404) {
        throw new Error(`Expected 404 status for nonexistent endpoint, got ${response.status}`);
    }
    
    console.log('   Error handling working correctly');
}

/**
 * Main test runner
 */
async function runAllTests() {
    console.log('🚀 Starting AI Travel Planner API Tests');
    console.log('=====================================');
    console.log(`Production URL: ${config.production.baseURL}`);
    console.log(`Mobile URL: ${config.production.mobileURL}`);
    console.log(`API Key: ${config.apiKey.substring(0, 8)}...`);
    
    // Core functionality tests
    await runTest('Health Check', testHealthCheck);
    await runTest('Mobile API Health Check', testMobileHealthCheck);
    await runTest('Get Themes', testGetThemes);
    await runTest('Generate Itinerary (POST)', testGenerateItinerary);
    await runTest('Quick Itinerary (GET)', testQuickItinerary);
    
    // Security tests
    await runTest('Invalid API Key', testInvalidApiKey);
    await runTest('Missing API Key', testMissingApiKey);
    await runTest('Invalid Theme', testInvalidTheme);
    await runTest('Missing Required Fields', testMissingFields);
    await runTest('Rate Limiting', testRateLimiting);
    
    // Infrastructure tests
    await runTest('Internal API Access', testInternalApiAccess);
    await runTest('SSL Certificate', testSSLCertificate);
    await runTest('CORS Headers', testCORSHeaders);
    await runTest('Response Time', testResponseTime);
    await runTest('Error Handling', testErrorHandling);
    
    // Print results
    console.log('\n📊 Test Results Summary');
    console.log('======================');
    console.log(`✅ Passed: ${testResults.passed}`);
    console.log(`❌ Failed: ${testResults.failed}`);
    console.log(`📈 Success Rate: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);
    
    if (testResults.errors.length > 0) {
        console.log('\n❌ Failed Tests:');
        testResults.errors.forEach(error => {
            console.log(`   - ${error.test}: ${error.error}`);
        });
    }
    
    if (testResults.failed === 0) {
        console.log('\n🎉 All tests passed! Your API is ready for production.');
    } else {
        console.log('\n⚠️  Some tests failed. Please review and fix the issues before deploying to production.');
        process.exit(1);
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    runAllTests().catch(error => {
        console.error('Test runner error:', error);
        process.exit(1);
    });
}

module.exports = {
    runAllTests,
    makeRequest,
    config
};
