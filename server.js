const express = require('express');
const app = express();
const PORT = 3000;

// Endpoint 1: A simple status check
app.get('/api/status', (req, res) => {
    res.json({ status: "success", message: "The request loop is working!" });
});

// Endpoint 2: Some dummy data
app.get('/api/data', (req, res) => {
    res.json({ project: "mini-backend", language: "Node.js", endpoints: 2 });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
});