// Home page: slow cross-fade slideshow on the plant-exhibition tile.
// Each plant photo shows for SHOW_MS, then fades (CSS transition) into the next one.
// Pauses while the page is hidden; stays still if the visitor prefers reduced motion.
(function () {
  var SHOW_MS = 4000;
  var box = document.getElementById('plant-slides');
  var dataEl = document.getElementById('slides-data');
  if (!box || !dataEl) return;
  var slides = JSON.parse(dataEl.textContent);
  if (slides.length < 2) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var imgs = box.querySelectorAll('img.slide');
  var nameEl = document.getElementById('slide-name');
  var cur = 0, front = 0, timer = null;

  function next() {
    var i = (cur + 1) % slides.length, back = 1 - front;
    var loader = new Image();
    loader.onload = function () {           // switch only once the next photo is ready
      imgs[back].src = slides[i].src;
      imgs[back].classList.add('on');
      imgs[front].classList.remove('on');
      if (nameEl) nameEl.textContent = slides[i].name;
      front = back; cur = i;
      schedule();
    };
    loader.onerror = function () { cur = i; schedule(); };  // skip a photo that fails to load
    loader.src = slides[i].src;
  }
  function schedule() { clearTimeout(timer); if (!document.hidden) timer = setTimeout(next, SHOW_MS); }
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) clearTimeout(timer); else schedule();
  });
  schedule();
})();
