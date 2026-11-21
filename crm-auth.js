/* Admin token for the Blueroll CRM API (web-production-54cc.up.railway.app).
 *
 * For the internal pages only (db.html, fsa.html, email.html and the rest).
 * Loaded before the page's own scripts, it adds an X-Admin-Token header to
 * every fetch that goes to the CRM. The token is asked for once and kept in
 * this browser's localStorage. If the API refuses it (401), it is asked for
 * again and the request is retried once.
 *
 * To forget the token on this browser: crmAuth.forget() in the console.
 */
(function () {
  var script = document.currentScript;
  var ORIGIN = (script && script.dataset.crmOrigin) || 'https://web-production-54cc.up.railway.app';
  var KEY = 'blueroll_crm_admin_token';
  var HEADER = 'X-Admin-Token';
  var nativeFetch = window.fetch.bind(window);
  var memory = '';        // if localStorage is unavailable
  var declined = false;   // cancelled the prompt: don't ask again until reload

  function stored() {
    try { return localStorage.getItem(KEY) || memory; } catch (e) { return memory; }
  }

  function store(token) {
    memory = token;
    try {
      if (token) localStorage.setItem(KEY, token);
      else localStorage.removeItem(KEY);
    } catch (e) { /* memory only */ }
  }

  function ask(message) {
    if (declined) return '';
    var token = (window.prompt(message) || '').trim();
    if (!token) { declined = true; return ''; }
    store(token);
    return token;
  }

  function goesToCrm(input) {
    var url = typeof input === 'string' ? input : (input && input.url) || String(input);
    return url === ORIGIN || url.indexOf(ORIGIN + '/') === 0;
  }

  function send(input, init, token) {
    var opts = Object.assign({}, init);
    var headers = new Headers(opts.headers || (input instanceof Request ? input.headers : undefined));
    if (token) headers.set(HEADER, token);
    opts.headers = headers;
    return nativeFetch(input, opts);
  }

  window.fetch = function (input, init) {
    if (!goesToCrm(input)) return nativeFetch(input, init);

    var used = stored() || ask('Blueroll CRM: paste the admin token');
    return send(input, init, used).then(function (res) {
      if (res.status !== 401) return res;

      // Another request on this page may already have got a new token.
      var now = stored();
      if (now && now !== used) return send(input, init, now);

      store('');
      var fresh = ask('Blueroll CRM did not accept the token. Paste the current admin token');
      return fresh ? send(input, init, fresh) : res;
    });
  };

  window.crmAuth = {
    forget: function () { store(''); declined = false; }
  };
})();
