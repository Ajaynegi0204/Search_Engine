const express = require("express");
const { spawn } = require("child_process");
const path = require("path");
const {verifyToken} = require("../controllers/middleware");
const router = express.Router();

const QUERY_TIMEOUT = process.env.QUERY_TIMEOUT || 120000;

function runQuery(query) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.resolve(__dirname, "../../query/query.py");
    const python = spawn("python3", [scriptPath]);

    const timeoutId = setTimeout(() => {
      python.kill();
      reject(new Error(`Query timed out after ${QUERY_TIMEOUT/1000} seconds`));
    }, QUERY_TIMEOUT);

    let result = "";
    let error = "";

    python.stdout.on("data", (data) => {
      result += data.toString();
    });

    python.stderr.on("data", (data) => {
      error += data.toString();
    });

    python.on("close", (code) => {
      clearTimeout(timeoutId);
      if (code === 0) {
        try {
          const parsed = JSON.parse(result);
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse output: ${err.message}`));
        }
      } else {
        reject(new Error(`Script failed: ${error || 'Unknown error'}`));
      }
    });

    python.on("error", (err) => {
      clearTimeout(timeoutId);
      reject(new Error(`Script execution failed: ${err.message}`));
    });

    python.stdin.write(JSON.stringify({ query }));
    python.stdin.end();
  });
}

router.post("/", verifyToken,async (req, res) => {
  const { query, filters } = req.body;

  if (!query || typeof query !== "string") {
    return res.status(400).json({
      error: "Invalid request",
      details: "Query parameter must be a string"
    });
  }

  try {
    res.setTimeout(QUERY_TIMEOUT + 5000);

    const result = await runQuery(query);
    const platformFilter = filters?.platform?.toLowerCase().trim();

    const filtered = platformFilter
      ? result.filter(p => (p.platform || "").toLowerCase().trim() === platformFilter)
      : result;

    res.json(filtered);
  } catch (err) {
    console.error("Query processing error:", err);
    res.status(500).json({
      error: "Search processing failed",
      details: err.message,
      timeout: QUERY_TIMEOUT
    });
  }
});

module.exports = router;