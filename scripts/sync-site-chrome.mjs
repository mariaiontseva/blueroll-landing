import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// Use explicit paths for additional pages. Unknown layouts fail before any write.
export const defaultPages = ['index.html', 'tools.html', 'guides/uk/index.html', 'kitchen-cleaning-schedule-template.html', 'haccp-checklists.html', 'sfbb-app.html', 'free-food-hygiene-rating-badge.html', 'kitchen-cleaning-schedule-generator.html'];
const root = fileURLToPath(new URL('../', import.meta.url));
const beginHeader = '<!-- BEGIN SHARED SITE HEADER -->';
const endHeader = '<!-- END SHARED SITE HEADER -->';
const beginFooter = '<!-- BEGIN SHARED SITE FOOTER -->';
const endFooter = '<!-- END SHARED SITE FOOTER -->';

function elementEnd(html, start) {
  const opening = html.slice(start).match(/^<(\w+)\b[^>]*>/);
  if (!opening) throw new Error('Expected element at ' + start);
  const tag = opening[1];
  const tokens = new RegExp('<\\/?' + tag + '\\b[^>]*>', 'g');
  tokens.lastIndex = start;
  let depth = 0, match;
  while ((match = tokens.exec(html))) {
    depth += match[0].startsWith('</') ? -1 : 1;
    if (!depth) return tokens.lastIndex;
  }
  throw new Error('Unclosed ' + tag + ' element');
}

function markedRange(html, begin, end) {
  const start = html.indexOf(begin);
  if (start < 0) return null;
  const finish = html.indexOf(end, start);
  if (finish < 0) throw new Error('Unclosed shared chrome marker');
  return [start, finish + end.length];
}

function legacyHeaderRange(html) {
  const marker = html.indexOf('<!-- ============ NAV ============ -->');
  if (marker >= 0) {
    const start = html.indexOf('<div', marker);
    const mobile = html.indexOf('<div class="mobile-menu" id="mobile-menu">', start);
    if (start < 0 || mobile < 0 || !html.slice(start, start + 100).includes('position: sticky')) throw new Error('Unrecognised navigation layout');
    return [marker, elementEnd(html, mobile)];
  }
  const generator = html.indexOf('<header class="site-header">');
  if (generator >= 0) return [generator, elementEnd(html, generator)];
  throw new Error('No recognised navigation to replace');
}

function legacyFooterRange(html) {
  const marker = html.indexOf('<!-- ============ FOOTER ============ -->');
  if (marker >= 0) {
    const start = html.indexOf('<div style="background: #14161b; color: #9aa0a8;">', marker);
    if (start < 0) throw new Error('Unrecognised footer layout');
    return [marker, elementEnd(html, start)];
  }
  const generator = html.indexOf('<footer class="site-footer wrap">');
  if (generator >= 0) return [generator, elementEnd(html, generator)];
  throw new Error('No recognised footer to replace');
}

function rootPaths(markup) {
  return markup.replace(/\b(href|src)="([^"]+)"/g, (all, attr, value) => {
    if (value.startsWith('/') || /^[a-z][a-z\d+.-]*:/i.test(value)) return all;
    return attr + '="/' + value + '"';
  });
}

export function sharedMarkup(home) {
  const hr = markedRange(home, beginHeader, endHeader) || legacyHeaderRange(home);
  const fr = markedRange(home, beginFooter, endFooter) || legacyFooterRange(home);
  let header = home.slice(...hr);
  let footer = home.slice(...fr);
  if (!header.startsWith(beginHeader)) {
    header = header.replace('<!-- ============ NAV ============ -->', '').trim();
    const outerEnd = elementEnd(header, 0);
    const outer = header.slice(0, outerEnd).replace(/^<div /, '<header id="br-site-header" class="br-site-chrome" ').replace(/<\/div>$/, '</header>');
    header = outer + header.slice(outerEnd);
    header = header.replace('<div class="mobile-menu" id="mobile-menu">', '<div class="mobile-menu br-site-chrome" id="mobile-menu" role="navigation" aria-label="Mobile navigation" hidden>');
    header = header.replace('id="nav-burger" aria-label="Menu"', 'id="nav-burger" type="button" aria-controls="mobile-menu" aria-label="Menu"');
    header = beginHeader + '\n' + header + '\n' + endHeader;
  }
  if (!footer.startsWith(beginFooter)) {
    footer = footer.replace('<!-- ============ FOOTER ============ -->', '').trim();
    footer = footer.replace(/^<div /, '<footer id="br-site-footer" class="br-site-chrome" ').replace(/<\/div>$/, '</footer>');
    footer = beginFooter + '\n' + footer + '\n' + endFooter;
  }
  return { header: rootPaths(header), footer: rootPaths(footer) };
}

function removeLegacyMenuListeners(html) {
  return html.replace(/<script(\s[^>]*)?>([\s\S]*?)<\/script>/g, (tag, attrs = '', body) => {
    if (attrs.includes('src=') || attrs.includes('application/ld+json')) return tag;
    let updated = body;
    const declaration = String.raw`  var btn = document\.getElementById\('nav-burger'\), menu = document\.getElementById\('mobile-menu'\);\n`;
    updated = updated.replace(new RegExp(declaration + String.raw`  if \(btn && menu\) \{\n[\s\S]*?^  \}\n`, 'gm'), '');
    updated = updated.replace(new RegExp(declaration + String.raw`  if \(!btn \|\| !menu\) return;\n[\s\S]*?^  menu\.querySelectorAll\('a'\).*?\n`, 'gm'), '');
    updated = updated.replace(/\/\/ Мобильное меню\n/g, '').replace(/\(function\s*\(\)\s*\{\s*\}\)\(\);\s*/g, '');
    return updated.trim() ? '<script' + attrs + '>' + updated + '</script>' : '';
  });
}

export function syncPage(html, shared) {
  const headerRange = markedRange(html, beginHeader, endHeader) || legacyHeaderRange(html);
  html = html.slice(0, headerRange[0]) + shared.header + html.slice(headerRange[1]);
  const footerRange = markedRange(html, beginFooter, endFooter) || legacyFooterRange(html);
  html = html.slice(0, footerRange[0]) + shared.footer + html.slice(footerRange[1]);
  html = removeLegacyMenuListeners(html);
  html = html.replace(/<link rel="stylesheet" href="\/site-footer\.css\?v=20260813">\n?/g, '');
  if (!html.includes('href="/site-chrome.css"')) html = html.replace('</head>', '<link rel="stylesheet" href="/site-chrome.css">\n<script src="/site-chrome.js" defer></script>\n</head>');
  if (!html.includes('family=Geist:')) html = html.replace('</head>', '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">\n</head>');
  return html;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const check = args.includes('--check');
  const pages = args.filter(x => !x.startsWith('--'));
  const targets = pages.length ? pages : defaultPages;
  const shared = sharedMarkup(readFileSync(resolve(root, 'index.html'), 'utf8'));
  const results = targets.map(page => {
    const path = resolve(root, page);
    if (!path.startsWith(root)) throw new Error('Path is outside the repository: ' + page);
    const original = readFileSync(path, 'utf8');
    const updated = syncPage(original, shared);
    return { page, path, original, updated };
  });
  // Validate every target before writing any of them.
  for (const result of results) {
    if (check && result.original !== result.updated) throw new Error('Shared site chrome differs: ' + result.page);
    if (!check && result.original !== result.updated) writeFileSync(result.path, result.updated);
    console.log((check ? 'checked ' : 'synced ') + result.page);
  }
}
