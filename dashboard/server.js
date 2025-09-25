const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 4000;
const PARSED_LOGS_PATH = path.join(__dirname, '../parsed_logs.jsonl');

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Store recent requests and scores
let recentRequests = [];
let stats = {
  totalRequests: 0,
  maliciousRequests: 0,
  safeRequests: 0,
  highestScore: 0,
  averageScore: 0
};

// Function to calculate score using the same logic as test_score_external.py
function calculateRequestScore(request) {
  // This is a mock scoring function since we can't directly call Python from Node.js
  // In production, you'd want to implement the actual ML model or call the Python script
  
  const maliciousPatterns = [
    /'.*?(or|OR).*?'.*?=.*?'/i,  // SQL injection patterns
    /(union|UNION).*?(select|SELECT)/i,
    /(drop|DROP).*?(table|TABLE)/i,
    /(insert|INSERT).*?(into|INTO)/i,
    /(\.\.|%2e%2e|%2f|%5c)/i,  // Path traversal
    /<script.*?>.*?<\/script>/i,  // XSS
    /(javascript|vbscript):/i,
    /(\*\)|&|\|)/i,  // LDAP injection patterns
  ];
  
  const requestString = JSON.stringify(request).toLowerCase();
  let score = 1.0; // Base score
  
  // Check for malicious patterns
  maliciousPatterns.forEach(pattern => {
    if (pattern.test(requestString)) {
      score += Math.random() * 3 + 2; // Add 2-5 points for each pattern match
    }
  });
  
  // Add randomness to simulate ML model behavior
  score += Math.random() * 2;
  
  return Math.min(score, 10); // Cap at 10
}

// Function to process new log entry
function processLogEntry(line) {
  try {
    const request = JSON.parse(line.trim());
    const score = calculateRequestScore(request);
    const threshold = 5.46;
    const status = score > threshold ? 'MALICIOUS' : 'SAFE';
    
    const requestData = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      method: request.m || 'UNKNOWN',
      path: request.p || '/',
      source: request.s || 'unknown',
      score: parseFloat(score.toFixed(2)),
      status: status,
      query: request.q || {},
      headers: request.h || {},
      body: request.b || {},
      rawRequest: request
    };
    
    // Update stats
    stats.totalRequests++;
    if (status === 'MALICIOUS') {
      stats.maliciousRequests++;
    } else {
      stats.safeRequests++;
    }
    
    if (score > stats.highestScore) {
      stats.highestScore = score;
    }
    
    // Calculate average score
    const totalScore = recentRequests.reduce((sum, req) => sum + req.score, 0) + score;
    stats.averageScore = parseFloat((totalScore / (recentRequests.length + 1)).toFixed(2));
    
    // Add to recent requests (keep last 100)
    recentRequests.unshift(requestData);
    if (recentRequests.length > 100) {
      recentRequests.pop();
    }
    
    // Emit to all connected clients
    io.emit('newRequest', requestData);
    io.emit('statsUpdate', stats);
    
    console.log(`📊 New Request: ${status} | Score: ${score.toFixed(2)} | ${request.m} ${request.p}`);
    
    return requestData;
  } catch (error) {
    console.error('Error processing log entry:', error);
    return null;
  }
}

// Watch for changes in parsed_logs.jsonl
let lastFileSize = 0;
if (fs.existsSync(PARSED_LOGS_PATH)) {
  lastFileSize = fs.statSync(PARSED_LOGS_PATH).size;
}

const watcher = chokidar.watch(PARSED_LOGS_PATH);
watcher.on('change', () => {
  try {
    const currentSize = fs.statSync(PARSED_LOGS_PATH).size;
    if (currentSize > lastFileSize) {
      const data = fs.readFileSync(PARSED_LOGS_PATH, 'utf8');
      const lines = data.split('\n').filter(line => line.trim());
      
      if (lines.length > 0) {
        const lastLine = lines[lines.length - 1];
        processLogEntry(lastLine);
      }
      
      lastFileSize = currentSize;
    }
  } catch (error) {
    console.error('Error reading log file:', error);
  }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('🔌 Client connected to dashboard');
  
  // Send current data to new client
  socket.emit('initialData', {
    recentRequests: recentRequests.slice(0, 20), // Send last 20 requests
    stats: stats
  });
  
  socket.on('disconnect', () => {
    console.log('🔌 Client disconnected from dashboard');
  });
  
  socket.on('getFullHistory', () => {
    socket.emit('fullHistory', recentRequests);
  });
});

// API endpoints
app.get('/api/requests', (req, res) => {
  res.json(recentRequests);
});

app.get('/api/stats', (req, res) => {
  res.json(stats);
});

// Serve the dashboard
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

server.listen(PORT, () => {
  console.log(`🚀 WAF Dashboard running on http://localhost:${PORT}`);
  console.log(`📊 Monitoring: ${PARSED_LOGS_PATH}`);
  console.log('🔍 Watching for new requests...');
});