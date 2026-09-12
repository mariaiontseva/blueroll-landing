import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '..');
const UK_FILE = path.join(root, 'recalls', 'index.html');
const US_FILE = path.join(root, 'recalls-us', 'index.html');
const SITEMAP = path.join(root, 'sitemap.xml');
const START = '<!-- RECALL_FALLBACK_START -->';
const END = '<!-- RECALL_FALLBACK_END -->';

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

function replaceFallback(html, cards) {
  const start = html.indexOf(START);
  const end = html.indexOf(END);
  if (start === -1 || end === -1 || end < start) throw new Error('Recall fallback markers not found');
  return `${html.slice(0, start)}${START}\n${cards}\n      ${html.slice(end)}`;
}

function ukType(item) {
  const types = item.type || [];
  if (types.some(type => /\/(AA|FAFA)$/i.test(type))) return {label:'Allergy alert', cls:'tag-allergy', risk:'risk-allergy', card:'is-allergy', allergy:true};
  if (types.some(type => /\/(PRIN|FAFR)$/i.test(type))) return {label:'Recalled', cls:'tag-recalled', risk:'risk-recall', card:'is-recall', allergy:false};
  return {label:'Alert', cls:'tag-other', risk:'', card:'', allergy:false};
}

function ukProduct(item) {
  return item.productDetails?.[0]?.productName?.trim() || item.shortTitle?.trim() || item.title || 'Food alert';
}

function ukBusiness(item) {
  if (item.reportingBusiness?.commonName) return item.reportingBusiness.commonName;
  return (item.title || '').match(/^(.+?)\s+recalls?\s/i)?.[1] || '';
}

function ukReason(item) {
  const risk = item.problem?.[0]?.riskStatement;
  if (risk) return risk.trim();
  const match = (item.title || '').match(/because (?:of |it )?(.*)/i);
  return match ? match[1] : item.title || '';
}

function ukPack(item) {
  return (item.productDetails || []).flatMap(product => [product.packSizeDescription, product.batchDescription]).filter(Boolean).join(' · ').replace(/\s+/g, ' ').trim();
}

function renderUk(item) {
  const date = new Date(item.created);
  const type = ukType(item);
  const business = ukBusiness(item);
  const pack = ukPack(item);
  const url = item.alertURL || `https://www.food.gov.uk/news-alerts/alert/${String(item.notation || '').toLowerCase()}`;
  const action = type.allergy ? 'Anyone with the listed allergy should not consume this product. Return for a full refund.' : 'Stop selling. Check your stock, remove affected products, and document the action.';
  return `      <a class="recall-card ${type.card}" href="${escapeHtml(url)}" target="_blank" rel="noopener">
        <div class="recall-date"><span class="day">${date.toLocaleDateString('en-GB',{day:'2-digit'})}</span><span class="month">${date.toLocaleDateString('en-GB',{month:'short'}).toUpperCase()}</span></div>
        <div class="recall-body">
          <div class="recall-row"><span class="recall-tag ${type.cls}">${type.label}</span>${business ? `<span class="recall-business">${escapeHtml(business)}</span>` : ''}</div>
          <div class="recall-product">${escapeHtml(ukProduct(item))}</div>
          <div class="recall-risk ${type.risk}">${escapeHtml(ukReason(item))}</div>
          <div class="recall-action"><strong>What to do:</strong> ${action}</div>
          <div class="recall-meta">${pack ? `<strong>${escapeHtml(pack)}</strong>` : ''}<span>FSA · ${escapeHtml(item.notation || '')}</span><span class="recall-meta-cta">Read full notice →</span></div>
        </div>
      </a>`;
}

function fdaDate(value) {
  if (!value || value.length !== 8) return null;
  return new Date(Number(value.slice(0,4)), Number(value.slice(4,6))-1, Number(value.slice(6,8)));
}

function fdaType(classification) {
  const value = String(classification || '').toLowerCase();
  if (value.includes('class i') && !value.includes('class ii') && !value.includes('class iii')) return {num:1,label:'Class I · High risk',cls:'tag-class-1',risk:'risk-class-1',card:'is-class-1'};
  if (value.includes('class ii') && !value.includes('class iii')) return {num:2,label:'Class II',cls:'tag-class-2',risk:'risk-class-2',card:'is-class-2'};
  if (value.includes('class iii')) return {num:3,label:'Class III',cls:'tag-class-3',risk:'risk-class-3',card:'is-class-3'};
  return {num:0,label:'Recall',cls:'tag-class-2',risk:'risk-class-2',card:'is-class-2'};
}

function firstSentence(value, limit=200) {
  const text = String(value || '');
  const match = text.match(/^(.+?[.。!?])\s/);
  return match ? match[1] : text.length > limit ? `${text.slice(0,limit-3)}…` : text;
}

function fdaProduct(item) {
  const text = String(item.product_description || 'Food recall');
  const match = text.match(/^(.+?)[,;]/);
  return match ? match[1].trim() : text.length > 120 ? `${text.slice(0,117)}…` : text;
}

function renderUs(item) {
  const date = fdaDate(item.recall_initiation_date);
  const type = fdaType(item.classification);
  const firm = item.recalling_firm || '';
  const location = [item.city,item.state].filter(Boolean).join(', ');
  const action = type.num === 1 ? 'Stop all use immediately. Check stock, pull affected lots, and document the action.' : type.num === 3 ? 'Review labelling or packaging. Document your check in HACCP records.' : 'Check stock for affected lots, remove if held, and document the action.';
  const url = `https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts?search=${encodeURIComponent(firm)}`;
  const dateHtml = date ? `<span class="day">${date.toLocaleDateString('en-US',{day:'2-digit'})}</span><span class="month">${date.toLocaleDateString('en-US',{month:'short'}).toUpperCase()}</span>` : '<span class="day">—</span><span class="month">No date</span>';
  return `      <a class="recall-card ${type.card}" href="${escapeHtml(url)}" target="_blank" rel="noopener">
        <div class="recall-date">${dateHtml}</div>
        <div class="recall-body">
          <div class="recall-row"><span class="recall-tag ${type.cls}">${type.label}</span>${firm ? `<span class="recall-business">${escapeHtml(firm)}${location ? ` · ${escapeHtml(location)}` : ''}</span>` : ''}</div>
          <div class="recall-product">${escapeHtml(fdaProduct(item))}</div>
          <div class="recall-risk ${type.risk}">${escapeHtml(firstSentence(item.reason_for_recall))}</div>
          <div class="recall-action"><strong>What to do:</strong> ${action}</div>
          <div class="recall-meta">${item.distribution_pattern ? `<strong>Distributed: ${escapeHtml(item.distribution_pattern)}</strong>` : ''}${item.recall_number ? `<span>FDA · ${escapeHtml(item.recall_number)}</span>` : ''}${item.status ? `<span>${escapeHtml(item.status)}</span>` : ''}<span class="recall-meta-cta">Search FDA →</span></div>
        </div>
      </a>`;
}

async function fetchJson(url) {
  const response = await fetch(url, {headers:{'user-agent':'Blueroll recall fallback updater/1.0'}});
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json();
}

async function updateUk() {
  const data = await fetchJson('https://data.food.gov.uk/food-alerts/id?_limit=80&_sort=-created');
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate()-30);
  cutoff.setHours(0,0,0,0);
  const items = (data.items || []).filter(item => item.title && new Date(item.created) >= cutoff).sort((a,b)=>new Date(b.created)-new Date(a.created)).slice(0,8);
  if (!items.length) throw new Error('FSA returned no recent alerts; existing fallback left untouched');
  const html = await readFile(UK_FILE,'utf8');
  await writeFile(UK_FILE, replaceFallback(html, items.map(renderUk).join('\n')), 'utf8');
  return items.length;
}

async function updateUs() {
  const data = await fetchJson('https://api.fda.gov/food/enforcement.json?sort=recall_initiation_date:desc&limit=100');
  const byRecall = new Map();
  for (const item of data.results || []) {
    const key = item.recall_number || item.event_id;
    if (key && !byRecall.has(key)) byRecall.set(key,item);
  }
  const items = [...byRecall.values()].sort((a,b)=>String(b.recall_initiation_date||'').localeCompare(String(a.recall_initiation_date||''))).slice(0,8);
  if (!items.length) throw new Error('FDA returned no recent recalls; existing fallback left untouched');
  const html = await readFile(US_FILE,'utf8');
  await writeFile(US_FILE, replaceFallback(html, items.map(renderUs).join('\n')), 'utf8');
  return items.length;
}

function updateLastmod(xml, pathname, date) {
  const escaped = pathname.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const pattern = new RegExp(`(<loc>https://blueroll\\.app/${escaped}</loc><lastmod>)[^<]+`);
  return xml.replace(pattern, `$1${date}`);
}

const [ukCount,usCount] = await Promise.all([updateUk(),updateUs()]);
const today = new Date().toISOString().slice(0,10);
let sitemap = await readFile(SITEMAP,'utf8');
sitemap = updateLastmod(sitemap,'recalls/',today);
sitemap = updateLastmod(sitemap,'recalls-us/',today);
await writeFile(SITEMAP,sitemap,'utf8');
console.log(`Updated static recall fallbacks: ${ukCount} UK, ${usCount} US (${today})`);
