/**
 * AI Travel Planner - API Testing for ai2.trekio.net
 * ===================================================
 * Test script specifically for your server deployment
 */

const https = require('https');
const http = require('http');

// Configuration for ai2.trekio.net
const config = {
    baseURL: 'https://ai2.trekio.net',
    mobileURL: 'https://ai2.trekio.net/mobile',
    apiKey: 'your-mobile-app-api-key-here', // Update this with your actual API key
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

// Test results
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
            rejectUnauthorized: false, // For testing
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
    const response = await makeRequest(`${config.baseURL}/health`);
    
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
    const response = await makeRequest(`${config.mobileURL}/health`);
    
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
    const response = await makeRequest(`${config.mobileURL}/themes`);
    
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
    const response = await makeRequest(`${config.mobileURL}/itinerary`, {
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
    
    // Log first activity for verification
    if (response.data.data.slots.length > 0) {
        const firstActivity = response.data.data.slots[0];
        console.log(`   First activity: ${firstActivity.name} (${firstActivity.start} - ${firstActivity.end})`);
    }
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
    
    const response = await makeRequest(`${config.mobileURL}/itinerary/quick?${params}`);
    
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
 * Test 6: SSL Certificate
 */
async function testSSLCertificate() {
    const https = require('https');
    
    return new Promise((resolve, reject) => {
        const req = https.request(config.baseURL, { rejectUnauthorized: true }, (res) => {
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
 * Test 7: Response Time
 */
async function testResponseTime() {
    const startTime = Date.now();
    await makeRequest(`${config.mobileURL}/health`);
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    if (responseTime > 10000) {
        throw new Error(`Response time too slow: ${responseTime}ms`);
    }
    
    console.log(`   Response time: ${responseTime}ms`);
}

/**
 * Test 8: CORS Headers
 */
async function testCORSHeaders() {
    const response = await makeRequest(`${config.mobileURL}/health`, {
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
 * Main test runner
 */
async function runAllTests() {
    console.log('🚀 Testing AI Travel Planner API on ai2.trekio.net');
    console.log('==================================================');
    console.log(`Base URL: ${config.baseURL}`);
    console.log(`Mobile URL: ${config.mobileURL}`);
    console.log(`API Key: ${config.apiKey.substring(0, 8)}...`);
    
    // Core functionality tests
    await runTest('Health Check', testHealthCheck);
    await runTest('Mobile API Health Check', testMobileHealthCheck);
    await runTest('Get Themes', testGetThemes);
    await runTest('Generate Itinerary (POST)', testGenerateItinerary);
    await runTest('Quick Itinerary (GET)', testQuickItinerary);
    
    // Infrastructure tests
    await runTest('SSL Certificate', testSSLCertificate);
    await runTest('Response Time', testResponseTime);
    await runTest('CORS Headers', testCORSHeaders);
    
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
        console.log('\n🎉 All tests passed! Your API is ready for mobile app integration.');
        console.log('\n📱 Mobile App Integration URLs:');
        console.log(`   Base URL: ${config.mobileURL}`);
        console.log(`   Health Check: ${config.mobileURL}/health`);
        console.log(`   Generate Itinerary: ${config.mobileURL}/itinerary`);
        console.log(`   Get Themes: ${config.mobileURL}/themes`);
    } else {
        console.log('\n⚠️  Some tests failed. Please review and fix the issues.');
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
