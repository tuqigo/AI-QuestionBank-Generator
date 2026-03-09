const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Step 1: Running TypeScript compiler...');
execSync('npx tsc', { stdio: 'inherit' });

console.log('Step 2: Running Vite build...');
execSync('npx vite build', { stdio: 'inherit' });

console.log('Step 3: Building Cloudflare Functions...');
execSync('npx wrangler pages functions build --outdir=dist --external=@cloudflare/workers-types', {
  stdio: 'inherit',
  cwd: process.cwd()
});

// Rename index.js to _worker.js
const distDir = path.join(process.cwd(), 'dist');
const indexJs = path.join(distDir, 'index.js');
const workerJs = path.join(distDir, '_worker.js');

if (fs.existsSync(indexJs)) {
  console.log('Step 4: Renaming index.js to _worker.js...');
  fs.renameSync(indexJs, workerJs);

  // Remove the "@cloudflare/workers-types" import line
  console.log('Step 5: Removing workers-types import...');
  let content = fs.readFileSync(workerJs, 'utf8');
  content = content.replace(/import "@cloudflare\/workers-types";\n?/g, '');
  fs.writeFileSync(workerJs, content, 'utf8');
  console.log('Done! _worker.js created.');
} else {
  console.error('Error: index.js not found in dist directory');
  process.exit(1);
}
