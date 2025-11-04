// server.js
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

// --- Mock interview questions ---
const interviewQuestions = {
  "Frontend Developer": [
    "What is the difference between CSS Grid and Flexbox?",
    "Explain the virtual DOM in React."
  ],
  "Backend Developer": [
    "What is RESTful API?",
    "Explain SQL vs NoSQL databases."
  ],
  "Full Stack Developer": [
    "Describe a full-stack application you've built.",
    "How do you handle authentication?"
  ],
  "AI Engineer": [
    "What is overfitting in machine learning?",
    "Difference between supervised and unsupervised learning?"
  ]
};

// --- Routes ---

// Simple test route
app.get("/", (req, res) => {
  res.send("AI Mock Interview Backend is running!");
});

// Get questions by role
app.get("/api/interviews/:role", (req, res) => {
  const role = req.params.role;
  const questions = interviewQuestions[role];
  if (!questions) return res.status(404).json({ error: "Role not found" });
  res.json({ role, questions });
});

// AI evaluation route
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.post("/api/interviews/answer", async (req, res) => {
  const { question, answer } = req.body;

  if (!question || !answer) {
    return res.status(400).json({ error: "Question and answer required" });
  }

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are an interview evaluator." },
        {
          role: "user",
          content: `Question: ${question}\nCandidate answer: ${answer}\nProvide detailed feedback and score 1-10.`,
        },
      ],
    });

    const feedback = response.choices[0].message.content;
    res.json({ feedback });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "AI evaluation failed" });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
