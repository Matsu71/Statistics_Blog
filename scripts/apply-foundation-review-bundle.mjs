// Apply UTF-8 source changes transferred through the connector as a compressed JSON bundle.
// No code is evaluated. Every overwrite verifies its original and replacement content hash.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const bundlePath = path.join(root, '.github/review-bundles/foundation-release.json');
const hash = data => createHash('sha256').update(data).digest('hex');
let raw;
try { raw = await readFile(bundlePath, 'utf8'); }
catch (error) { if(error.code==='ENOENT') { console.log('No pending source bundle.'); process.exit(0); } throw error; }
const envelope = JSON.parse(raw);
if(envelope.encoding!=='gzip-base64-json-v1') throw new Error('Unsupported source bundle');
const compressed = Buffer.from(envelope.payload, 'base64');
if(hash(compressed)!==envelope.sha256) throw new Error('Bundle integrity mismatch');
const decoded = gunzipSync(compressed, { maxOutputLength: 5_000_000 });
const entries = JSON.parse(decoded.toString('utf8'));
if(!Array.isArray(entries)||entries.length>120) throw new Error('Invalid source manifest');
const targets = new Set();
for (const entry of entries) {
  if(typeof entry.path!=='string'||typeof entry.content!=='string'||entry.path.includes('..')||entry.path.includes('\\')||path.isAbsolute(entry.path)) throw new Error('Invalid source path');
  if(!/^(src\/|scripts\/|project-docs\/learning-platform-design\/|astro\.config\.mjs$)/.test(entry.path)) throw new Error('Path outside reviewed source scope');
  if(targets.has(entry.path))throw new Error('Duplicate source path');
  targets.add(entry.path);
  if(hash(entry.content)!==entry.sha256)throw new Error(`Replacement hash mismatch: ${entry.path}`);
  const target=path.join(root,entry.path);
  let existing=null;
  try { existing=hash(await readFile(target)); } catch(e) { if(e.code!=='ENOENT')throw e; }
  if(existing!==entry.base_sha256&&existing!==entry.sha256)throw new Error(`Concurrent edit detected: ${entry.path}`);
}
for (const entry of entries) {
  const target=path.join(root,entry.path);
  await mkdir(path.dirname(target),{recursive:true});
  await writeFile(target,entry.content,'utf8');
}
console.log(`Applied ${entries.length} integrity-checked UTF-8 source files. Review the resulting normal source files, not the transport encoding.`);
