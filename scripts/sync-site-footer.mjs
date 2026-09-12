import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sitemap = await readFile(path.join(root, 'sitemap.xml'), 'utf8');
const publicPages = new Set(
  [...sitemap.matchAll(/<loc>https:\/\/blueroll\.app\/?([^<]*)<\/loc>/g)]
    .map(([, pathname]) => pathname.replace(/\/$/, '/index.html') || 'index.html')
);

// These are public self-audit steps reached from /audit/ but intentionally
// omitted from the sitemap to keep the index focused on the audit entry page.
publicPages.add('audit/allergens.html');
publicPages.add('audit/cleanliness.html');
publicPages.add('audit/cross-contamination.html');
publicPages.add('audit/staff-training.html');

const stylesheet = '<link rel="stylesheet" href="/site-footer.css?v=20260813">';
const footer = `<!-- ============ FOOTER ============ -->
<footer class="blueroll-footer" aria-label="Site footer">
  <div class="blueroll-footer__grid">
    <div>
      <a class="blueroll-footer__brand" href="/" aria-label="Blueroll home">
        <img src="/assets/blueroll-logo-v2.svg" alt="">
        <span>Blueroll</span>
      </a>
      <p class="blueroll-footer__intro">Food safety management for restaurants in the UK, US &amp; Europe. One kitchen or an estate.</p>
      <div class="blueroll-footer__badges">
        <a href="https://apps.apple.com/app/id6760937451" aria-label="Download Blueroll on the App Store"><img src="/assets/badge-app-store.svg" alt="Download on the App Store"></a>
        <a href="https://play.google.com/store/apps/details?id=app.blueroll.mobile" aria-label="Get Blueroll on Google Play"><img src="/assets/badge-google-play.svg" alt="Get it on Google Play"></a>
      </div>
      <div class="blueroll-footer__copyright">© 2026 Blueroll · London &amp; New York</div>
    </div>
    <nav class="blueroll-footer__column" aria-label="Product">
      <div class="blueroll-footer__heading">Product</div>
      <a href="/multi-site-food-safety.html" class="blueroll-footer__link">Multisite</a>
      <a href="/haccp-checklists.html" class="blueroll-footer__link">HACCP Checklists</a>
      <a href="/allergen-matrix.html" class="blueroll-footer__link">Allergen Matrix</a>
      <a href="/ai-recipe-import.html" class="blueroll-footer__link">AI Recipe Import</a>
      <a href="/compliance-reports.html" class="blueroll-footer__link">Compliance Reports</a>
    </nav>
    <nav class="blueroll-footer__column" aria-label="Free tools">
      <div class="blueroll-footer__heading">Free tools</div>
      <a href="/audit/" class="blueroll-footer__link">Self-audit</a>
      <a href="/check-food-hygiene-rating.html" class="blueroll-footer__link">Check a rating</a>
      <a href="/free-food-hygiene-rating-badge.html" class="blueroll-footer__link">Rating badge</a>
      <a href="https://chatgpt.com/g/g-6a0c75c897108191956d8c9f3223abb4-blueroll-uk-food-safety-coach" class="blueroll-footer__link">GPT Safety Coach</a>
      <a href="/london-food-hygiene-map.html" class="blueroll-footer__link">London hygiene map</a>
    </nav>
    <nav class="blueroll-footer__column" aria-label="Company">
      <div class="blueroll-footer__heading">Company</div>
      <a href="/#pricing" class="blueroll-footer__link">Pricing</a>
      <a href="/trail-alternative.html" class="blueroll-footer__link">Trail alternative</a>
      <a href="/about.html" class="blueroll-footer__link">About</a>
      <a href="/privacy.html" class="blueroll-footer__link">Privacy</a>
      <a href="/terms.html" class="blueroll-footer__link">Terms</a>
    </nav>
  </div>
</footer>`;

const legacyFooter = /<!-- ============ FOOTER ============ -->[\s\S]*?<a href="\/?terms\.html" class="foot-link">Terms<\/a>\s*<\/div>\s*<\/div>\s*<\/div>/;
const trustFooter = /<footer class="trust-footer">[\s\S]*?<\/footer>/;

let added = 0;
let replaced = 0;

for (const relativePath of [...publicPages].sort()) {
  const filename = path.join(root, relativePath);
  let html = await readFile(filename, 'utf8');

  if (!html.includes('/site-footer.css')) {
    if (!html.includes('</head>')) throw new Error(`Missing </head> in ${relativePath}`);
    html = html.replace('</head>', `${stylesheet}\n</head>`);
  }

  if (legacyFooter.test(html)) {
    html = html.replace(legacyFooter, footer);
    replaced += 1;
  } else if (trustFooter.test(html)) {
    html = html.replace(trustFooter, footer);
    replaced += 1;
  } else if (!html.includes('class="blueroll-footer"')) {
    if (!html.includes('</body>')) throw new Error(`Missing </body> in ${relativePath}`);
    html = html.replace('</body>', `${footer}\n\n</body>`);
    added += 1;
  }

  await writeFile(filename, html);
}

console.log(`Synced ${publicPages.size} public pages: ${added} added, ${replaced} replaced.`);
