// Photo gallery pages (SHP, MSK…): tap a photo to view it full screen; ‹ › or swipe to move, ✕ to close.
(function () {
  var items = Array.prototype.slice.call(document.querySelectorAll('.g-item'));
  var box = document.getElementById('lightbox');
  if (!items.length || !box) return;
  var img = document.getElementById('lb-img'), cap = document.getElementById('lb-cap'), cur = 0;

  function show(i) {
    cur = (i + items.length) % items.length;
    img.src = items[cur].getAttribute('data-full');
    cap.textContent = items[cur].getAttribute('data-cap') || '';
    box.hidden = false;
  }
  function close() { box.hidden = true; img.removeAttribute('src'); items[cur].focus(); }

  items.forEach(function (b, i) { b.addEventListener('click', function () { show(i); }); });
  document.getElementById('lb-close').addEventListener('click', close);
  document.getElementById('lb-prev').addEventListener('click', function () { show(cur - 1); });
  document.getElementById('lb-next').addEventListener('click', function () { show(cur + 1); });
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(cur - 1);
    if (e.key === 'ArrowRight') show(cur + 1);
  });
  var x0 = null;  // swipe left/right on phones
  box.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1));
  });
})();
