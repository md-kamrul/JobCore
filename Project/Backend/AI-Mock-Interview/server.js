// server.js
const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const OpenAI = require("openai");

// Load variables from .env
const path = require("path");
dotenv.config({ path: path.join(__dirname, ".env.local") });

// Create Express app
const app = express();
const PORT = process.env.PORT || 5000;

// OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Middlewares
app.use(cors());           // allow requests from frontend
app.use(express.json());  // parse JSON bodies

// Simple test route
app.get("/", (req, res) => {
  res.send("Welcome to the AI Mock Interview API 🚀");
});

app.get("/health", (req, res) => {
  res.send("Server is running");
});

// 1) Route: Get an interview question
app.post("/api/interview/question", async (req, res) => {
  try {
    const { role, level } = req.body;

    const userPrompt = `
You are an expert interviewer.
Generate ONE interview question for a ${level} ${role}.
Return only the question text, no explanation.
`;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a helpful interview assistant." },
        { role: "user", content: userPrompt },
      ],
    });

    const question = completion.choices[0].message.content.trim();

    res.json({ question });
  } catch (error) {
    console.error("Error generating question:", error);
    res.status(500).json({ error: "Failed to generate question" });
  }
});

// 2) Route: Evaluate an answer
app.post("/api/interview/evaluate", async (req, res) => {
  try {
    const { role, level, question, answer } = req.body;

    const userPrompt = `
You are an interviewer.
Role: ${role}
Level: ${level}

Interview Question: "${question}"
Candidate Answer: "${answer}"

1) Give a score out of 10.
2) Give very short feedback (2-3 lines).
3) Suggest how to improve.

Respond in clear text.
`;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a strict but fair interviewer." },
        { role: "user", content: userPrompt },
      ],
    });

    const evaluation = completion.choices[0].message.content.trim();

    res.json({ evaluation });
  } catch (error) {
    console.error("Error evaluating answer:", error);
    res.status(500).json({ error: "Failed to evaluate answer" });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(` Server listening at http://localhost:${PORT}`);
});
