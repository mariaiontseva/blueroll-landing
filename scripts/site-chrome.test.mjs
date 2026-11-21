import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { Script } from 'node:vm';
import test from 'node:test';
import { defaultPages, sharedMarkup, syncPage } from './sync-site-chrome.mjs';

const require = createRequire(import.meta.url);
const { JSDOM } = require('jsdom');
const runtime = readFileSync(new URL('../site-chrome.js', import.meta.url), 'utf8');
const styles = readFileSync(new URL('../site-chrome.css', import.meta.url), 'utf8');
const home = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const shared = sharedMarkup(home);

function setup(file = 'index.html') {
  const html = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
  const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://blueroll.app/' + file });
  let desktopChange;
  dom.window.matchMedia = () => ({ matches: false, addEventListener(type, handler) { desktopChange = handler; } });
  dom.window.eval(runtime);
  return { dom, window: dom.window, document: dom.window.document, button: dom.window.document.getElementById('nav-burger'), menu: dom.window.document.getElementById('mobile-menu'), resizeDesktop: () => desktopChange({ matches: true }) };
}

test('all eight pages have identical homepage chrome and root-relative internal links', () => {
  const reference = setup().document;
  for (const file of defaultPages) {
    const s = setup(file);
    for (const selector of ['#br-site-header', '#mobile-menu', '#br-site-footer']) {
      assert.equal(s.document.querySelectorAll(selector).length, 1, file + ' ' + selector);
      assert.equal(s.document.querySelector(selector).outerHTML, reference.querySelector(selector).outerHTML, file + ' ' + selector);
    }
    const chrome = [...s.document.querySelectorAll('.br-site-chrome')];
    for (const node of chrome.flatMap(x => [...x.querySelectorAll('[href], [src]')])) {
      for (const attr of ['href', 'src']) if (node.hasAttribute(attr)) assert.match(node.getAttribute(attr), /^(?:\/|https?:|mailto:|tel:)/, file + ': ' + node.getAttribute(attr));
    }
    assert.equal(s.document.querySelectorAll('script[src="/site-chrome.js"]').length, 1, file);
    assert.equal(s.document.querySelectorAll('link[href="/site-chrome.css"]').length, 1, file);
    assert.equal(s.document.querySelectorAll('#br-site-header .dd').length, 3, file);
    assert.ok(s.document.querySelector('#br-site-header a[href="/#audiences"]'), file);
    assert.ok(s.document.querySelector('#br-site-header a[href="/#pricing"]'), file);
    assert.ok(s.document.querySelector('#br-site-header a[href="/#faq"]'), file);
    assert.ok(s.document.querySelector('#br-site-footer a[href="https://apps.apple.com/app/id6760937451"] img[src="/assets/badge-app-store.svg"]'), file);
    assert.ok(s.document.querySelector('#br-site-footer a[href^="https://play.google.com/"] img[src="/assets/badge-google-play.svg"]'), file);
    assert.equal(s.button.getAttribute('aria-controls'), 'mobile-menu', file);
    s.dom.window.close();
  }
});

test('mobile toggle opens and closes once on every page, including repeated runtime evaluation', () => {
  for (const file of defaultPages) {
    const s = setup(file);
    s.window.eval(runtime);
    assert.equal(s.menu.hidden, true, file);
    s.button.click();
    assert.equal(s.menu.hidden, false, file);
    assert.equal(s.button.getAttribute('aria-expanded'), 'true', file);
    assert.equal(s.document.body.classList.contains('mm-lock'), true, file);
    s.button.click();
    assert.equal(s.menu.hidden, true, file);
    assert.equal(s.button.getAttribute('aria-expanded'), 'false', file);
    assert.equal(s.document.body.classList.contains('mm-lock'), false, file);
    s.dom.window.close();
  }
});

test('Escape closes mobile navigation and restores the menu button focus', () => {
  const s = setup('kitchen-cleaning-schedule-generator.html');
  s.button.click();
  s.menu.querySelector('a').focus();
  s.document.dispatchEvent(new s.window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }));
  assert.equal(s.menu.hidden, true);
  assert.equal(s.button.getAttribute('aria-expanded'), 'false');
  assert.equal(s.document.activeElement, s.button);
  assert.equal(s.document.body.classList.contains('mm-lock'), false);
  s.dom.window.close();
});

test('following a navigation link closes the drawer and releases body scroll', () => {
  const s = setup('guides/uk/index.html');
  s.button.click();
  const link = s.menu.querySelector('a');
  link.addEventListener('click', event => event.preventDefault());
  link.click();
  assert.equal(s.menu.hidden, true);
  assert.equal(s.document.body.classList.contains('mm-lock'), false);
  assert.equal(s.button.getAttribute('aria-expanded'), 'false');
  s.dom.window.close();
});

test('returning to the desktop layout closes an open drawer', () => {
  const s = setup('sfbb-app.html');
  s.button.click();
  s.resizeDesktop();
  assert.equal(s.menu.hidden, true);
  assert.equal(s.document.body.classList.contains('mm-lock'), false);
  s.dom.window.close();
});

test('sync is idempotent and leaves content scripts with no duplicate menu bindings', () => {
  for (const file of defaultPages) {
    const html = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
    assert.equal(syncPage(html, shared), html, file);
    for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
      if (match[1].includes('application/ld+json')) continue;
      assert.ok(!match[2].includes("document.getElementById('nav-burger')"), file);
      new Script(match[2], { filename: file });
    }
  }
  assert.match(home, /FAQPage/);
  assert.match(home, /document\.getElementById\('faq-list'\)/);
  const generator = readFileSync(new URL('../kitchen-cleaning-schedule-generator.html', import.meta.url), 'utf8');
  assert.match(generator, /src="\/cleaning-schedule-generator\.js"/);
  assert.match(generator, /id="print-area"/);
  assert.match(styles, /@media print[\s\S]*#br-site-header[\s\S]*#br-site-footer[\s\S]*display: none !important/);
});

test('legacy fixed nav positioning cannot override the shared primary navigation', () => {
  for (const file of ['sfbb-app.html', 'guides/uk/index.html']) {
    const s = setup(file);
    const style = s.document.createElement('style');
    style.textContent = styles;
    s.document.head.appendChild(style);
    assert.equal(s.window.getComputedStyle(s.document.querySelector('#br-site-header .nav-links')).position, 'static', file);
    assert.equal(s.document.querySelector('#br-site-footer .footer-grid').style.gridTemplateColumns, '2fr 1fr 1fr 1fr', file);
    s.dom.window.close();
  }
});
