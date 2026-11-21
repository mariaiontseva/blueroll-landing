import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext, Script } from 'node:vm';
import test from 'node:test';

const html = readFileSync(new URL('../free-haccp-template.html', import.meta.url), 'utf8');
const start = html.indexOf("document.querySelectorAll('[data-gate]').forEach");
const end = html.indexOf('// Email links land here', start);
assert.ok(start >= 0 && end > start);
const source = html.slice(start, end);

function setup() {
  const events = [];
  const deliveries = [];
  function node() {
    return {
      style: {}, attributes: {}, handlers: {}, hidden: true, textContent: '', value: '',
      focus() { this.focused = true; },
      setAttribute(key, value) { this.attributes[key] = value; },
      addEventListener(name, handler) { this.handlers[name] = handler; }
    };
  }
  const nodes = Object.fromEntries(['idle', 'form', 'sent', 'email', 'send', 'open', 'error', 'setup'].map(name => [name, node()]));
  const gate = { getAttribute: () => 'hero', querySelector: selector => nodes[selector.replace('.g-', '')] };
  const document = { querySelectorAll: () => [gate], querySelector: () => null };
  runInNewContext(source, {
    document,
    setTimeout: callback => callback(),
    track: (name, params) => events.push({ name, params }),
    deliver: (email, placement) => deliveries.push({ email, placement })
  });
  return { nodes, events, deliveries };
}

test('an invalid email explains the error and never delivers a template', () => {
  const s = setup();
  s.nodes.open.handlers.click();
  s.nodes.email.value = 'invalid';
  s.nodes.send.handlers.click();
  assert.equal(s.deliveries.length, 0);
  assert.equal(s.nodes.error.hidden, false);
  assert.match(s.nodes.error.textContent, /valid email address/);
  assert.equal(s.nodes.email.attributes['aria-invalid'], 'true');
  assert.equal(s.nodes.email.focused, true);
  assert.deepEqual(s.events.map(event => event.name), ['haccp_form_open', 'haccp_form_error']);
  assert.equal(s.events[1].params.reason, 'invalid_email');
});

test('editing clears the error and a valid submission preserves delivery', () => {
  const s = setup();
  s.nodes.email.value = '';
  s.nodes.send.handlers.click();
  s.nodes.email.value = ' chef@example.test ';
  s.nodes.email.handlers.input();
  assert.equal(s.nodes.error.hidden, true);
  assert.equal(s.nodes.error.textContent, '');
  assert.equal(s.nodes.email.attributes['aria-invalid'], 'false');
  s.nodes.send.handlers.click();
  assert.deepEqual(s.deliveries, [{ email: 'chef@example.test', placement: 'hero' }]);
  assert.equal(s.nodes.form.style.display, 'none');
  assert.equal(s.nodes.sent.style.display, 'block');
  const event = s.events.find(event => event.name === 'haccp_form_submit');
  assert.deepEqual(Object.keys(event.params), ['placement']);
  assert.equal(event.params.placement, 'hero');
});

test('Enter still submits the template form without a page reload', () => {
  const s = setup();
  s.nodes.email.value = 'chef@example.test';
  let prevented = false;
  s.nodes.email.handlers.keydown({ key: 'Enter', preventDefault: () => { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(s.deliveries.length, 1);
});

test('all generated templates expose four correctly linked accessible errors', () => {
  for (const file of ['free-haccp-template.html', 'haccp-template-cafe.html', 'haccp-template-takeaway.html', 'haccp-template-bakery.html', 'haccp-template-food-truck.html', 'haccp-template-scotland.html']) {
    const page = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
    const ids = [...page.matchAll(/<div class="g-error" id="([^"]+)" role="alert" hidden/g)].map(match => match[1]);
    const references = [...page.matchAll(/<input class="g-email"[^>]*aria-describedby="([^"]+)"/g)].map(match => match[1]);
    assert.equal(ids.length, 4, file);
    assert.equal(new Set(ids).size, 4, file);
    assert.deepEqual(references, ids, file);
    for (const match of page.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
      if (!/type="application\/ld\+json"/.test(match[1])) new Script(match[2], { filename: file });
    }
  }
});
