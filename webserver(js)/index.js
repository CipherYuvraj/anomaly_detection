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


app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

