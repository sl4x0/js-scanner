// Test file 2: GitHub token (fake)
const axios = require('axios');

// FAKE GitHub Personal Access Token - DO NOT USE
const GITHUB_TOKEN = 'ghp_1234567890abcdefghijklmnopqrstuvwxyz';
const GITHUB_API = 'https://api.github.com';

async function createGist(content, description) {
    const headers = {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
    };
    
    const data = {
        description: description,
        public: false,
        files: {
            'test.txt': {
                content: content
            }
        }
    };
    
    try {
        const response = await axios.post(
            `${GITHUB_API}/gists`,
            data,
            { headers }
        );
        return response.data;
    } catch (error) {
        console.error('Error creating gist:', error);
        throw error;
    }
}

// API endpoints
const endpoints = {
    repos: '/api/repos',
    issues: '/api/issues',
    pullRequests: '/api/pull-requests'
};

module.exports = { createGist, endpoints };
