const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// MongoDB connection
const mongoURI = 'mongodb+srv://jbg1793:4cYNIv0dRhHUkPhb@spotifywrapped.0gq7x.mongodb.net/?retryWrites=true&w=majority&appName=SpotifyWrapped'; // replace with your connection string
mongoose.connect(mongoURI)
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.error('MongoDB connection error:', err));

// Define a simple schema and model (customize based on your needs)
const wrappedSchema = new mongoose.Schema({
    period: String,
    data: Object, // replace with your data structure
});

const Wrapped = mongoose.model('Wrapped', wrappedSchema);

// Endpoint to save Spotify Wrapped data
app.post('/api/wrapped', async (req, res) => {
    try {
        const { period, data } = req.body;
        const newWrapped = new Wrapped({ period, data });
        await newWrapped.save();
        res.status(201).send(newWrapped);
    } catch (error) {
        res.status(400).send(error);
    }
});

// Endpoint to fetch all Spotify Wrapped data
app.get('/api/wrapped', async (req, res) => {
    try {
        const wrappedData = await Wrapped.find();
        res.send(wrappedData);
    } catch (error) {
        res.status(500).send(error);
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

