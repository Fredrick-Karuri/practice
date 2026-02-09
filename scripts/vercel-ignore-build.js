#!/usr/bin/env node

/**
 * This script prevents Vercel from building when changes don't affect this project
 * Returns exit code 0 to skip build, 1 to proceed with build
 */

const { execSync } = require('child_process');

const projectPath = process.env.VERCEL_GIT_COMMIT_REF === 'main' 
  ? process.cwd().split('/').slice(-2).join('/')
  : '';

if (!projectPath) {
  console.log('Not on main branch, proceeding with build');
  process.exit(1);
}

try {
  // Get changed files between HEAD and previous commit
  const changedFiles = execSync('git diff --name-only HEAD~1 HEAD')
    .toString()
    .trim()
    .split('\n');

  const hasChanges = changedFiles.some(file => 
    file.startsWith(projectPath) || 
    file.includes('package.json') ||
    file.includes('.github/workflows')
  );

  if (hasChanges) {
    console.log('✅ Changes detected in this project or CI config');
    process.exit(1); // Build
  } else {
    console.log('⏭️  No changes in this project, skipping build');
    process.exit(0); // Skip
  }
} catch (error) {
  console.log('Error checking changes, proceeding with build:', error.message);
  process.exit(1); // Build on error to be safe
}