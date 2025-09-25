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

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log('WARNING: This server contains intentionally vulnerable endpoints for security testing');
  console.log('Available vulnerable endpoints:');
  console.log('   GET  /user/:id - SQL Injection');
  console.log('   GET  /file/:filename - Path Traversal');
  console.log('   POST /login - LDAP Injection');
});

