const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;


app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to the Express server'
  });
});

app.post('/data', (req, res) => {
  const data = req.body;
  res.json({
    message: 'Data received successfully',
    data: data
  });
});




app.get('/user/:id', (req, res) => {
  const userId = req.params.id;
  const fakeQuery = `SELECT * FROM users WHERE id = ${userId}`;
  
  res.json({
    message: 'User lookup',
    query: fakeQuery,
    user_id: userId,
    warning: 'This endpoint is vulnerable to SQL injection for testing purposes'
  });
});

app.get('/file/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = `/var/www/uploads/${filename}`;
  
  res.json({
    message: 'File access',
    requested_file: filename,
    full_path: filePath,
    warning: 'This endpoint is vulnerable to path traversal for testing purposes'
  });
});


app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const ldapQuery = `(&(uid=${username})(password=${password}))`;
  
  res.json({
    message: 'Login attempt',
    ldap_query: ldapQuery,
    username: username,
    warning: 'This endpoint is vulnerable to LDAP injection for testing purposes'
  });
});

// ============= HIGH-RISK ATTACK ENDPOINTS FOR MODEL TESTING =============

// 1. Extremely Malicious SQL Injection Endpoint
app.get('/admin/bypass/:token', (req, res) => {
  const token = req.params.token;
  const maliciousQuery = `SELECT * FROM admin_users WHERE token = '${token}' OR '1'='1' UNION SELECT password,credit_card FROM sensitive_data; DROP TABLE audit_logs; --`;
  
  res.json({
    message: '🚨 CRITICAL VULNERABILITY DETECTED',
    executed_query: maliciousQuery,
    attack_type: 'Advanced SQL Injection + Union Attack + Table Drop',
    risk_level: 'CRITICAL',
    token: token,
    warning: '⚠️ This endpoint contains multiple attack vectors for high-score testing'
  });
});

// 2. Severe Path Traversal with System Access
app.get('/system/read/:path', (req, res) => {
  const path = req.params.path;
  const systemPaths = [
    `../../../../etc/passwd`,
    `../../../../etc/shadow`, 
    `../../../../../../windows/system32/config/sam`,
    `../../../var/log/auth.log`,
    `../../../../home/user/.ssh/id_rsa`
  ];
  
  res.json({
    message: '🚨 SYSTEM FILE ACCESS ATTEMPT',
    requested_path: path,
    full_path: `/var/www/html/${path}`,
    system_files_targeted: systemPaths,
    attack_type: 'Directory Traversal + System File Access',
    risk_level: 'CRITICAL',
    warning: '⚠️ This endpoint simulates severe path traversal attacks'
  });
});

// 3. Multi-Vector Attack Endpoint (XSS + Command Injection + LDAP)
app.post('/execute/command', (req, res) => {
  const { cmd, user, script } = req.body;
  
  const maliciousCommands = [
    `${cmd}; rm -rf /; cat /etc/passwd`,
    `${script}<script>alert('XSS Attack')</script>`,
    `(&(uid=${user})(|(password=*))(cn=*))`
  ];
  
  res.json({
    message: '🚨 MULTI-VECTOR ATTACK DETECTED',
    command_injection: maliciousCommands[0],
    xss_payload: maliciousCommands[1], 
    ldap_injection: maliciousCommands[2],
    attack_types: ['Command Injection', 'XSS', 'LDAP Injection'],
    risk_level: 'EXTREME',
    input_data: { cmd, user, script },
    warning: '⚠️ This endpoint combines multiple attack vectors for maximum threat score'
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log('⚠️ WARNING: This server contains intentionally vulnerable endpoints for security testing');
  console.log('📋 Available vulnerable endpoints:');
  console.log('   GET  /user/:id - SQL Injection');
  console.log('   GET  /file/:filename - Path Traversal');
  console.log('   POST /login - LDAP Injection');
  console.log('');
  console.log('🚨 HIGH-RISK ATTACK ENDPOINTS (for model testing):');
  console.log('   GET  /admin/bypass/:token - Advanced SQL Injection');
  console.log('   GET  /system/read/:path - Severe Path Traversal');
  console.log('   POST /execute/command - Multi-Vector Attack');
});

