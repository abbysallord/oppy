#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if python3 is installed on target environment
try {
  execSync('python3 --version', { stdio: 'ignore' });
} catch (e) {
  console.error('\x1b[31mError: python3 is not installed or not found in system PATH.\x1b[0m');
  console.error('OppScout requires Python 3.8+ to run its crawlers and parsing logic.');
  process.exit(1);
}

// Auto-check and install python package dependencies (like feedparser)
try {
  execSync('python3 -c "import feedparser"', { stdio: 'ignore' });
} catch (e) {
  console.log('\x1b[33mWarning: Python dependency "feedparser" is missing. Attempting automatic installation...\x1b[0m');
  try {
    execSync('python3 -m pip install feedparser', { stdio: 'inherit' });
    console.log('\x1b[32mSuccessfully installed feedparser.\x1b[0m\n');
  } catch (err) {
    console.error('\x1b[31mError: Failed to install feedparser automatically.\x1b[0m');
    console.error('Please run: pip install feedparser');
    process.exit(1);
  }
}

// Resolve absolute path to python scan script
const scanScriptPath = path.join(__dirname, '..', 'scan.py');

if (!fs.existsSync(scanScriptPath)) {
  console.error(`\x1b[31mInternal Error: scan.py not found at ${scanScriptPath}\x1b[0m`);
  process.exit(1);
}

// Spawn child process for python3 scan.py
const pythonProcess = spawn('python3', [scanScriptPath, ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: process.env
});

pythonProcess.on('close', (code) => {
  process.exit(code);
});
