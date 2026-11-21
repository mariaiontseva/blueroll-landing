import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import test from 'node:test';

const source = readFileSync(new URL('../geo-analytics.js', import.meta.url), 'utf8');

function setup({ blocked = false, referrer = '', navigation = 'navigate' } = {}) {
  const events = [];
  const values = new Map();
  const listeners = {};
  const access = fn => (...args) => {
    if (blocked) throw new Error('Storage denied');
    return fn(...args);
  };
  const window = {
    location: { href: 'https://blueroll.app/', pathname: '/', search: '' },
    sessionStorage: {
      getItem: access(key => values.get(key) || null),
      setItem: access((key, value) => values.set(key, value)),
      removeItem: access(key => values.delete(key))
    },
    performance: { getEntriesByType: () => [{ type: navigation }] },
    gtag: (...event) => events.push(event),
    addEventListener: (name, handler) => { listeners[name] = handler; }
  };
  const document = {
    referrer,
    addEventListener: (name, handler) => { listeners[name] = handler; },
    querySelectorAll: () => []
  };
  runInNewContext(source, { window, document, URL, URLSearchParams });
  function click({ href = 'https://app.blueroll.app/onboarding', text = 'Start for free', placement = 'hero', target, metaKey = false } = {}) {
    const link = {
      textContent: text,
      getAttribute: key => ({ href, target })[key] || null,
      hasAttribute: () => false,
      closest: selector => selector === '[data-cta-location]'
        ? (placement ? { getAttribute: () => placement } : null)
        : { id: 'pricing', tagName: 'SECTION' }
    };
    listeners.click({ target: { closest: () => link }, button: 0, metaKey });
  }
  return { events, values, listeners, click };
}

test('a trial click remains measurable when session storage is blocked', () => {
  const s = setup({ blocked: true });
  s.click();
  assert.equal(s.events[0][1], 'trial_start_click');
  assert.equal(s.events[0][2].cta_location, 'hero');
});

test('an AI referral does not disable click tracking when storage is blocked', () => {
  const s = setup({ blocked: true, referrer: 'https://chatgpt.com/' });
  s.click();
  assert.deepEqual(s.events.map(event => event[1]), ['ai_referral_landing', 'trial_start_click']);
  assert.equal(s.events[1][2].ai_source, 'chatgpt');
});

test('the direct login route and legacy sign-in label are excluded from trial clicks', () => {
  const s = setup();
  s.click({ href: 'https://app.blueroll.app/login', text: 'Log in' });
  s.click({ href: 'https://app.blueroll.app/', text: 'Sign in' });
  assert.deepEqual(s.events.map(event => event[1]), ['sign_in_click', 'sign_in_click']);
  assert.equal(s.values.has('blueroll_trial_click'), false);
});

test('CTA location falls back to the surrounding page section', () => {
  const s = setup();
  s.click({ placement: null });
  assert.equal(s.events[0][2].cta_location, 'pricing');
});

test('modified or new-tab clicks do not create a browser-back marker', () => {
  const s = setup();
  s.click({ metaKey: true });
  s.click({ target: '_blank' });
  assert.equal(s.events.length, 2);
  assert.equal(s.values.has('blueroll_trial_click'), false);
});

test('a browser-back return after a same-tab trial click is counted once', () => {
  const s = setup({ navigation: 'back_forward' });
  s.click();
  s.listeners.pageshow({ persisted: false });
  s.listeners.pageshow({ persisted: false });
  assert.deepEqual(s.events.map(event => event[1]), ['trial_start_click', 'onboarding_back_return']);
});
