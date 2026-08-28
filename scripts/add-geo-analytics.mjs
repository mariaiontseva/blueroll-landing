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

let changed = 0;
let removed = 0;
for (const file of await htmlFiles(root)) {
  let html = await readFile(file,'utf8');
  const isPublic = /<link rel=["']canonical["']/.test(html) && !/<meta name=["']robots["'][^>]*noindex/i.test(html);
  if (!isPublic && html.includes('<script src="/geo-analytics.js" defer></script>')) {
    html = html.replace('<script src="/geo-analytics.js" defer></script>\n','');
    await writeFile(file,html,'utf8');
    removed += 1;
    continue;
  }
  if (!isPublic || html.includes('src="/geo-analytics.js"') || !html.includes('</head>')) continue;
  const next = html.replace('</head>','<script src="/geo-analytics.js" defer></script>\n</head>');
  await writeFile(file,next,'utf8');
  changed += 1;
}
console.log(`Added AI referral measurement to ${changed} public HTML files; removed it from ${removed} non-public files`);
