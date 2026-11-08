// Visiting-hours tile on the home page: live India-time clock, open/closed colour, and a
// pop-up weekly timetable. Settings (opening time, closing time, holidays) come from
// build.py via the <script id="hours-config"> JSON block.
(function () {
  var cfgEl = document.getElementById('hours-config');
  var tile = document.getElementById('st-tile');
  if (!cfgEl || !tile) return;
  var cfg = JSON.parse(cfgEl.textContent);

  var DAYS = { Sun: 'ஞாயிறு', Mon: 'திங்கள்', Tue: 'செவ்வாய்', Wed: 'புதன்', Thu: 'வியாழன்', Fri: 'வெள்ளி', Sat: 'சனி' };
  var ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  var icon = document.getElementById('st-icon'), label = document.getElementById('st-label');
  var clock = document.getElementById('st-clock'), next = document.getElementById('st-next');
  var overlay = document.getElementById('hours-overlay'), table = document.getElementById('hours-table');

  // Line-drawn door icons (colour comes from CSS currentColor)
  var DOOR_OPEN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">' +
    '<path d="M3.5 21.5h17"/><path d="M6 21.5V3h12v18.5"/>' +
    '<path d="M6 3l7.5 2.3v17.2L6 21.5z" fill="currentColor" fill-opacity=".18"/>' +
    '<circle cx="11.6" cy="13.2" r=".9" fill="currentColor" stroke="none"/></svg>';
  var DOOR_CLOSED = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">' +
    '<path d="M3.5 21.5h17"/><rect x="6" y="3" width="12" height="18.5" rx=".6" fill="currentColor" fill-opacity=".14"/>' +
    '<rect x="9.6" y="11.2" width="4.8" height="4" rx=".7" fill="currentColor" stroke="none"/>' +
    '<path d="M10.6 11.2V9.9a1.4 1.4 0 0 1 2.8 0v1.3"/></svg>';

  function mins(s) { var a = s.split(':'); return +a[0] * 60 + +a[1]; }
  // "16:00" -> "மாலை 4:00"
  function tamilTime(hhmm) {
    var a = hhmm.split(':'), h = +a[0], part = h < 12 ? 'காலை' : (h < 16 ? 'மதியம்' : 'மாலை');
    var h12 = h % 12 === 0 ? 12 : h % 12;
    return part + ' ' + h12 + ':' + a[1];
  }
  var FROM = tamilTime(cfg.from), UNTIL = tamilTime(cfg.until);

  // Current date/time parts in India time, optionally shifted by whole days.
  function ist(dayOffset) {
    var d = new Date(Date.now() + (dayOffset || 0) * 86400000), p = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata', weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    }).formatToParts(d).forEach(function (x) { p[x.type] = x.value; });
    p.date = p.year + '-' + p.month + '-' + p.day;
    p.h = +p.hour % 24;
    return p;
  }
  function isWorkDay(p) { return p.weekday !== 'Sun' && cfg.holidays.indexOf(p.date) === -1; }

  function nextOpening(now) {
    if (isWorkDay(now) && now.h * 60 + +now.minute < mins(cfg.from)) return 'இன்று ' + FROM + ' மணிக்கு';
    for (var i = 1; i <= 14; i++) {
      var d = ist(i);
      if (isWorkDay(d)) return (i === 1 ? 'நாளை' : DAYS[d.weekday]) + ' ' + FROM + ' மணிக்கு';
    }
    return '';
  }

  function update() {
    var now = ist(0), t = now.h * 60 + +now.minute;
    var open = isWorkDay(now) && t >= mins(cfg.from) && t < mins(cfg.until);
    tile.classList.toggle('is-open', open);
    tile.classList.toggle('is-closed', !open);
    var want = open ? 'open' : 'closed';
    if (icon.getAttribute('data-door') !== want) {   // only redraw when the state changes
      icon.innerHTML = open ? DOOR_OPEN : DOOR_CLOSED;
      icon.setAttribute('data-door', want);
    }
    label.textContent = open ? 'திறந்துள்ளது' : 'மூடப்பட்டுள்ளது';
    var h12 = now.h % 12 === 0 ? 12 : now.h % 12;
    clock.textContent = DAYS[now.weekday] + ' · ' + h12 + ':' + now.minute + ':' + now.second + (now.h < 12 ? ' AM' : ' PM');
    next.textContent = open ? UNTIL + ' வரை' : nextOpening(now);
    return now;
  }

  function fillTable() {
    var today = ist(0).weekday, rows = '';
    ORDER.forEach(function (k) {
      var time = k === 'Sun' ? '<b class="off">விடுமுறை</b>' : '<b>' + FROM + ' – ' + UNTIL + '</b>';
      rows += '<div class="hours-row' + (k === today ? ' today' : '') + '"><span>' + DAYS[k] +
        (k === today ? ' <small>(இன்று)</small>' : '') + '</span>' + time + '</div>';
    });
    table.innerHTML = rows;
  }

  function openPanel() { fillTable(); overlay.hidden = false; document.getElementById('hours-close').focus(); }
  function closePanel() { overlay.hidden = true; tile.focus(); }
  tile.addEventListener('click', openPanel);
  document.getElementById('hours-close').addEventListener('click', closePanel);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) closePanel(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) closePanel(); });

  try { update(); setInterval(update, 1000); } catch (e) { /* keep the static fallback text */ }
})();
