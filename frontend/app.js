const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

// Environment configuration
const API_URL = process.env.API_URL || "http://localhost:8000";
const PORT = process.env.PORT || 3000;

// Axios instance with timeout
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 5000
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: "ok" });
});

// Submit job
app.post('/submit', async (req, res) => {
  try {
    const response = await apiClient.post('/jobs');
    res.json(response.data);
  } catch (err) {
    console.error("Submit error:", err.message);
    res.status(500).json({ error: "Failed to submit job" });
  }
});

// Check job status
app.get('/status/:id', async (req, res) => {
  try {
    const response = await apiClient.get(`/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    console.error("Status error:", err.message);
    res.status(500).json({ error: "Failed to fetch job status" });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});