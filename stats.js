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
  function getCount(path) {
    return fetch(GC + '/counter/' + encodeURIComponent(path) + '.json')
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

  // 👁 views (this page)
  getCount(location.pathname).then(function (n) {
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
