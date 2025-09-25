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

let recentRequests = [];
let stats = {
  totalRequests: 0,
  maliciousRequests: 0,
  safeRequests: 0,
  highestScore: 0,
  averageScore: 0
};

function calculateRequestScore(request) {
  const maliciousPatterns = [
    /'.*?(or|OR).*?'.*?=.*?'/i,
    /(union|UNION).*?(select|SELECT)/i,
    /(drop|DROP).*?(table|TABLE)/i,
    /(insert|INSERT).*?(into|INTO)/i,
    /(\.\.|%2e%2e|%2f|%5c)/i,
    /<script.*?>.*?<\/script>/i,
    /(javascript|vbscript):/i,
    /(\*\)|&|\|)/i,
  ];
  
  const requestString = JSON.stringify(request).toLowerCase();
  let score = 1.0;
  
  maliciousPatterns.forEach(pattern => {
    if (pattern.test(requestString)) {
      score += Math.random() * 3 + 2;
    }
  });
  
  score += Math.random() * 2;
  
  return Math.min(score, 10);
}


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
    
    stats.totalRequests++;
    if (status === 'MALICIOUS') {
      stats.maliciousRequests++;
    } else {
      stats.safeRequests++;
    }
    
    if (score > stats.highestScore) {
      stats.highestScore = score;
    }
    
    const totalScore = recentRequests.reduce((sum, req) => sum + req.score, 0) + score;
    stats.averageScore = parseFloat((totalScore / (recentRequests.length + 1)).toFixed(2));
    
    recentRequests.unshift(requestData);
    if (recentRequests.length > 100) {
      recentRequests.pop();
    }
    io.emit('newRequest', requestData);
    io.emit('statsUpdate', stats);
    
    console.log(`📊 New Request: ${status} | Score: ${score.toFixed(2)} | ${request.m} ${request.p}`);
    
    return requestData;
  } catch (error) {
    console.error('Error processing log entry:', error);
    return null;
  }
}
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

io.on('connection', (socket) => {
  console.log('🔌 Client connected to dashboard');
  
  socket.emit('initialData', {
    recentRequests: recentRequests.slice(0, 20),
    stats: stats
  });
  
  socket.on('disconnect', () => {
    console.log('🔌 Client disconnected from dashboard');
  });
  
  socket.on('getFullHistory', () => {
    socket.emit('fullHistory', recentRequests);
  });
});
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