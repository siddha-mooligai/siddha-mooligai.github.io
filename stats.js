// View counter (👁) and "useful?" button (👍) for plant pages, backed by GoatCounter.
// Page views are recorded by GoatCounter's count.js; likes are recorded as events "like-<id>".
// If GoatCounter is unreachable or blocked, the numbers stay hidden and the page still works.
(function () {
  var GC = 'https://siddha-mooligai.goatcounter.com';
  var like = document.getElementById('like');
  var views = document.getElementById('views');
  if (!like) return;
  var id = like.getAttribute('data-id');
  var likePath = 'like-' + id;
  var key = 'liked-' + id;
  var btn = like.querySelector('button');
  var countEl = like.querySelector('.like-count');
  var likes = null;

  function num(s) { return parseInt(String(s).replace(/[^\d]/g, ''), 10) || 0; }
  function fmt(n) { return n.toLocaleString('en-IN'); }
  // GoatCounter caches each counter answer for ~4 hours, keyed on path + start/end.
  // A far-future "end" date that changes every 10 minutes gives a fresh count (≤10 min old);
  // any end date after today counts all visits, so the number itself is unaffected.
  function freshEnd() {
    var slot = Math.floor(Date.now() / 600000) - 2990000;   // 10-minute slots since 7 Nov 2026
    return new Date(Date.UTC(2030, 0, 1) + Math.max(slot, 0) * 86400000).toISOString().slice(0, 10);
  }
  function getCount(path) {
    return fetch(GC + '/counter/' + encodeURIComponent(path) + '.json?end=' + freshEnd())
      .then(function (r) {
        if (r.status === 404) return 0;          // no hits recorded yet
        if (!r.ok) throw new Error(r.status);
        return r.json().then(function (j) { return num(j.count); });
      });
  }
  function storedLiked() { try { return localStorage.getItem(key) === '1'; } catch (e) { return false; } }
  function markLiked() {
    btn.disabled = true;
    btn.textContent = '👍 நன்றி!';
  }
  function showLikes() {
    if (likes === null) return;
    countEl.textContent = likes > 0 ? fmt(likes) + ' பேர் விரும்பினர்' : '';
  }

  // 👁 views (this page). Visits are recorded without the trailing slash (see build.py);
  // GoatCounter also treats "/plants/x/" and "/plants/x" as the same page.
  getCount(location.pathname.replace(/\/+$/, '')).then(function (n) {
    // the current visit may not be counted yet; never show 0 to someone who is viewing it
    views.querySelector('span').textContent = fmt(Math.max(n, 1));
    views.hidden = false;
  }).catch(function () {});

  // 👍 likes
  if (storedLiked()) markLiked();
  getCount(likePath).then(function (n) { likes = n; showLikes(); }).catch(function () {});

  btn.addEventListener('click', function () {
    if (storedLiked()) return;
    try { localStorage.setItem(key, '1'); } catch (e) {}
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: likePath, title: 'Like: ' + id, event: true });
    }
    markLiked();
    if (likes !== null) { likes += 1; showLikes(); }
  });
})();
