(() => {
  'use strict';

  const sources = [
    [/^(?:www\.)?chatgpt\.com$|^chat\.openai\.com$/, 'chatgpt'],
    [/^(?:www\.)?perplexity\.ai$/, 'perplexity'],
    [/^copilot\.(?:microsoft\.com|cloud\.microsoft)$/, 'microsoft_copilot'],
    [/^gemini\.google\.com$/, 'google_gemini'],
    [/^(?:www\.)?claude\.ai$/, 'claude'],
    [/^(?:www\.)?poe\.com$/, 'poe'],
    [/^(?:www\.)?you\.com$/, 'you']
  ];

  try {
    const params = new URLSearchParams(window.location.search);
    const tagged = (params.get('utm_source') || '').toLowerCase();
    const referrerHost = document.referrer ? new URL(document.referrer).hostname.toLowerCase() : '';
    let entrySource = '';

    for (const [pattern, name] of sources) {
      if (pattern.test(referrerHost) || pattern.test(tagged)) {
        entrySource = name;
        break;
      }
    }

    if (entrySource) window.sessionStorage.setItem('blueroll_ai_source', entrySource);
    const sessionSource = entrySource || window.sessionStorage.getItem('blueroll_ai_source') || '';

    const sendEvent = (name, eventParams) => {
      window.dataLayer = window.dataLayer || [];
      if (typeof window.gtag === 'function') {
        window.gtag('event', name, eventParams);
      } else {
        window.dataLayer.push({ event: name, ...eventParams });
      }
    };

    if (entrySource) {
      const eventKey = `blueroll_ai_referral:${entrySource}:${window.location.pathname}`;
      if (!window.sessionStorage.getItem(eventKey)) {
        window.sessionStorage.setItem(eventKey, '1');
        sendEvent('ai_referral_landing', {
          ai_source: entrySource,
          landing_page: window.location.pathname,
          referrer_host: referrerHost || '(utm-tagged)'
        });
      }
    }

    const trialClickKey = 'blueroll_trial_click';

    // A trial click followed by a browser-back arrival here means the visitor left onboarding.
    // Any other kind of page load clears the marker, so later back navigation on the site is not counted.
    window.addEventListener('pageshow', event => {
      try {
        const stored = window.sessionStorage.getItem(trialClickKey);
        if (!stored) return;
        window.sessionStorage.removeItem(trialClickKey);

        const navigation = window.performance?.getEntriesByType?.('navigation')?.[0];
        if (!event.persisted && navigation?.type !== 'back_forward') return;

        const { time } = JSON.parse(stored);
        sendEvent('onboarding_back_return', {
          ai_source: sessionSource || '(not_ai_referred)',
          landing_page: window.location.pathname,
          seconds: Math.max(0, Math.round((Date.now() - time) / 1000))
        });
      } catch (error) {
        // Analytics must never interfere with page use.
      }
    });

    document.addEventListener('click', event => {
      const link = event.target.closest?.('a[href]');
      if (!link) return;

      const href = link.getAttribute('href') || '';
      let eventName = '';
      let destination = '';

      if (/^https:\/\/app\.blueroll\.app(?:\/|$)/i.test(href)) {
        // "Sign in" links share the app URL; keep returning customers out of the trial count.
        eventName = /^\s*sign in\s*$/i.test(link.textContent || '') ? 'sign_in_click' : 'trial_start_click';
        destination = 'app.blueroll.app';
      } else if (/^mailto:hello@blueroll\.app/i.test(href) && /demo/i.test(href)) {
        eventName = 'demo_request_click';
        destination = 'email';
      } else if (/apps\.apple\.com|play\.google\.com/i.test(href)) {
        eventName = 'app_store_click';
        destination = href.includes('apple.com') ? 'apple_app_store' : 'google_play';
      } else if (link.hasAttribute('data-proof-link')) {
        eventName = 'proof_link_click';
        destination = link.getAttribute('data-proof-link') || new URL(link.href, window.location.href).hostname;
      }

      if (!eventName) return;
      sendEvent(eventName, {
        ai_source: sessionSource || '(not_ai_referred)',
        landing_page: window.location.pathname,
        destination,
        transport_type: 'beacon'
      });

      // Remember a same-tab trial click so a browser-back return from the app can be counted.
      const sameTab = event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey &&
        (link.getAttribute('target') || '_self') === '_self';
      if (eventName === 'trial_start_click' && sameTab) {
        try {
          window.sessionStorage.setItem(trialClickKey, JSON.stringify({ time: Date.now() }));
        } catch (error) {
          // Storage can be blocked; the click itself has already been recorded.
        }
      }
    }, { capture: true });

    document.querySelectorAll('details.ms-faq').forEach((item, index) => {
      item.addEventListener('toggle', () => {
        if (!item.open) return;
        sendEvent('faq_open', {
          ai_source: sessionSource || '(not_ai_referred)',
          landing_page: window.location.pathname,
          faq_position: index + 1,
          faq_question: item.querySelector('summary')?.textContent?.trim() || '(unknown)'
        });
      });
    });
  } catch (error) {
    // Analytics must never interfere with page use, storage restrictions included.
  }
})();
