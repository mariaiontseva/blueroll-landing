import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ignored = new Set(['node_modules','.git']);

async function htmlFiles(dir) {
  const entries = await readdir(dir,{withFileTypes:true});
  const files = [];
  for (const entry of entries) {
    if (ignored.has(entry.name)) continue;
    const full = path.join(dir,entry.name);
    if (entry.isDirectory()) files.push(...await htmlFiles(full));
    else if (entry.isFile() && entry.name.endsWith('.html')) files.push(full);
  }
  return files;
}

const links = '<a href="/best-food-safety-apps-uk.html">Compare Apps</a><a href="/about.html">About &amp; Standards</a><a href="/evidence.html">Evidence</a><a href="/security.html">Security</a>';
let changed = 0;

for (const file of await htmlFiles(root)) {
  let html = await readFile(file,'utf8');
  if (!html.includes('bx-foot-col') || /href=["']\/?about\.html["']/.test(html)) continue;
  const privacy = /<a href=["']\/?privacy\.html["']>Privacy Policy<\/a>/;
  if (!privacy.test(html)) continue;
  html = html.replace(privacy, `${links}$&`);
  await writeFile(file,html,'utf8');
  changed += 1;
}
console.log(`Added trust links to ${changed} shared footers`);
