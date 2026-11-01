// Runs the Python analyzer (run_analysis.py) as a child process and turns its output into
// a JavaScript object, or an AnalysisError that says what went wrong.

import { spawn } from "node:child_process"; // lets Node start another program (Python) and read its output
import path from "node:path"; // builds file paths that work on Windows and Mac/Linux
import { fileURLToPath } from "node:url"; // converts this file's URL into a normal path

// __dirname = the folder this file is in. ES modules don't provide it automatically, so we build it.
const __dirname = path.dirname(fileURLToPath(import.meta.url));
// the project root (one level up from server/), where run_analysis.py lives
const PROJECT_ROOT = path.join(__dirname, "..");

const PYTHON = process.env.PYTHON || "python"; // on Mac/Linux this is often "python3"

/**
 * An Error that also carries a short machine-readable `code`
 * ("not_found", "timeout", ...) so the route can choose the right HTTP status.
 * `extends Error` = inherit everything a normal Error has (message, stack trace) and add to it.
 */
export class AnalysisError extends Error {
  constructor(message, code) {
    super(message); // run Error's own constructor first, which stores the message
    this.name = "AnalysisError";
    this.code = code;
  }
}

/**
 * Run the Python analyzer for one username.
 * Returns a Promise that resolves with the results object, or rejects with an AnalysisError.
 * timeoutMs: kill Python if it takes longer than this (GitHub rate limits can make it wait a long time).
 */
export function runAnalysis(username, { timeoutMs = 120_000 } = {}) {
  return new Promise((resolve, reject) => {
    // start: python run_analysis.py <username>, inside the project root
    // passing the arguments as an ARRAY (not one string) means no shell is involved,
    //  so a username can never be interpreted as an extra command
    const child = spawn(PYTHON, ["run_analysis.py", username], { cwd: PROJECT_ROOT });

    let stdout = ""; // the JSON result arrives here, possibly in several chunks
    let stderr = ""; // progress messages and Python errors arrive here
    let timedOut = false;

    // a timer that fires once after timeoutMs; if Python is still running then, stop it
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill(); // ends the Python process; the "close" event below still fires afterwards
    }, timeoutMs);

    // "data" events fire every time the child process writes something
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
      process.stderr.write(chunk); // show Python's progress in the server's terminal too
    });

    // "error" fires if the program couldn't even start (for example, Python isn't installed)
    child.on("error", (err) => {
      clearTimeout(timer);
      reject(new AnalysisError(`Could not start ${PYTHON}: ${err.message}`, "server_error"));
    });

    // "close" fires when the Python process has finished; code is its exit code
    child.on("close", (code) => {
      clearTimeout(timer); // finished in time (or was killed): the timer is no longer needed

      if (timedOut) {
        reject(new AnalysisError(`Analysis took longer than ${timeoutMs / 1000} seconds and was stopped.`, "timeout"));
        return;
      }

      let parsed;
      try {
        parsed = JSON.parse(stdout); // text -> JavaScript object
      } catch {
        // stdout wasn't JSON (for example, Python crashed with a traceback before printing anything)
        const lastLine = stderr.trim().split("\n").pop();
        reject(new AnalysisError(`Analyzer crashed (exit code ${code}): ${lastLine}`, "server_error"));
        return;
      }

      if (code === 0) {
        resolve(parsed);
      } else {
        // Python's fail() gave us {"error": ..., "code": ...}
        reject(new AnalysisError(parsed.error || `Analyzer failed with exit code ${code}`, parsed.code || "server_error"));
      }
    });
  });
}
