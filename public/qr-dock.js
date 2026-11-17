// Shows a small App Store QR card to desktop visitors after they scroll a little.
(function () {
  'use strict';
  if (!window.matchMedia('(min-width: 1024px) and (hover: hover)').matches) return;
  try { if (sessionStorage.getItem('keeper-qr-dismissed')) return; } catch (e) {}
  var dock = document.createElement('aside');
  dock.className = 'qr-dock';
  dock.setAttribute('aria-label', 'Get Keeper on your iPhone');
  dock.innerHTML =
    '<img src="/assets/qr-app-store.svg" alt="QR code that opens Keeper on the App Store" width="84" height="84">' +
    '<p><strong>Get Keeper</strong>Scan with your iPhone camera</p>' +
    '<button type="button" aria-label="Close">×</button>';
  document.body.appendChild(dock);
  dock.querySelector('button').addEventListener('click', function () {
    dock.classList.remove('show');
    try { sessionStorage.setItem('keeper-qr-dismissed', '1'); } catch (e) {}
    window.removeEventListener('scroll', onScroll);
  });
  function onScroll() { dock.classList.toggle('show', window.scrollY > 600); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
