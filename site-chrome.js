/* One shared listener set for the homepage navigation on public pages. */
(function () {
  var header = document.getElementById('br-site-header');
  var button = document.getElementById('nav-burger');
  var menu = document.getElementById('mobile-menu');
  if (!header || !button || !menu || header.dataset.chromeReady === 'true') return;
  header.dataset.chromeReady = 'true';

  function setOpen(open, restoreFocus) {
    menu.hidden = !open;
    menu.classList.toggle('open', open);
    document.body.classList.toggle('mm-lock', open);
    button.setAttribute('aria-expanded', String(open));
    if (restoreFocus) button.focus();
  }

  setOpen(false, false);
  button.addEventListener('click', function () {
    setOpen(button.getAttribute('aria-expanded') !== 'true', false);
  });
  menu.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false, false);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      event.preventDefault();
      setOpen(false, true);
    }
  });
  if (window.matchMedia) {
    var desktop = window.matchMedia('(min-width: 961px)');
    var closeOnDesktop = function (event) { if (event.matches) setOpen(false, false); };
    if (desktop.addEventListener) desktop.addEventListener('change', closeOnDesktop);
    else if (desktop.addListener) desktop.addListener(closeOnDesktop);
  }
})();
