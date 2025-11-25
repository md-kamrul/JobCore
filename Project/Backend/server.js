import express from "express";
import multer from "multer";
import fs from "fs";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));


const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});


const storage = multer.diskStorage({
  destination: "uploads/",
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
});
const upload = multer({ storage });




app.post("/api/interview/start", (req, res) => {
  const { name, role } = req.body;
  res.json({
    message: `Interview started for ${role}`,
    user: name,
  });
});

app.get("/api/interview/question", async (req, res) => {
  try {
    const { role } = req.query;
    const prompt = `Give one ${role} interview question.`;

    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
    });

    const question = completion.choices[0].message.content; 
    res.json({ question });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

//  Upload Audio & Transcribe
app.post("/api/interview/upload", upload.single("audio"), async (req, res) => {
  try {
    const audioPath = req.file.path;

    const transcription = await client.audio.transcriptions.create({
      model: "whisper-1",
      file: fs.createReadStream(audioPath),
    });

    res.json({
      transcript: transcription.text,
      message: "Audio transcribed successfully",
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

//  Analyze Response
app.post("/api/interview/analyze", async (req, res) => {
  try {
    const { question, transcript } = req.body;

    const prompt = `
    Analyze the following mock interview response.
    Question: ${question}
    Answer: ${transcript}

    Provide feedback including:
    - Communication (out of 10)
    - Confidence (out of 10)
    - Accuracy (out of 10)
    - Suggestion for improvement.
    `;

    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
    });

    const analysis = completion.choices[0].message.content;
    res.json({ feedback: analysis });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

//SERVER RUN
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
