// We're importing Express (to build the server), Google AI (to talk to Gemini),
// dotenv (.env file), and cors (to let our frontend talk to us)
const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
const cors = require('cors');

// --- 2. CONFIGURE YOUR TOOLS ---
dotenv.config(); // Load the .env file

const app = express(); // Create your Express app
app.use(express.json()); // Tell Express to understand JSON
app.use(cors()); // Allow your frontend to make requests

// Configure the Google AI
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.0-pro" });

// --- 3. CREATE YOUR "DOORS" (API ENDPOINTS) ---

// === DOOR #1: GET A NEW QUESTION ===
app.post('/get-question', async (req, res) => {
  try {
    // Get the job role from the frontend's request
    const { role } = req.body;

    if (!role) {
      return res.status(400).send("Error: 'role' is required.");
    }

    // This is our instruction for the AI
    const prompt = `You are an AI hiring manager.
      Your task is to generate one interview question for a "${role}" position.
      - The question should be challenging but fair.
      - Do NOT add any extra text like "Here is your question:".
      - Just return the question text itself.`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const question = response.text();

    // Send the single question back to the frontend
    res.json({ question: question });

  } catch (error) {
    console.error("Error in /get-question:", error);
    res.status(500).send("Error generating question.");
  }
});

// === DOOR #2: GET FEEDBACK ON AN ANSWER ===
app.post('/get-feedback', async (req, res) => {
  try {
    // Get the question and answer from the frontend's request
    const { question, answer } = req.body;

    if (!question || !answer) {
      return res.status(400).send("Error: 'question' and 'answer' are required.");
    }

    // This is our instruction for the AI
    const prompt = `You are an expert, encouraging interview coach.
      A user was practicing for an interview.
      
      The question was: "${question}"
      The user's answer was: "${answer}"

      Please provide constructive feedback for this answer.
      Structure your feedback in two parts:
      1. **What Went Well:** (Start with 1-2 positive points).
      2. **How to Improve:** (Give 2-3 specific, actionable bullet points for improvement).
      Keep the tone friendly and helpful.`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const feedback = response.text();

    // Send the detailed feedback back to the frontend
    res.json({ feedback: feedback });

  } catch (error) {
    console.error("Error in /get-feedback:", error);
    res.status(500).send("Error generating feedback.");
  }
});

// --- 4. START THE SERVER ---
// We'll run our server on port 5000
const port = 5000;
app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
  console.log("Backend is ready. You can now test it.");
});
