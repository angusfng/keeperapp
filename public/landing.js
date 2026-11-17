// Homepage: the swipe demo and scroll reveal.
(function () {
  'use strict';

  // ---------- Scroll reveal ----------
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  // ---------- Swipe demo ----------
  var stack = document.getElementById('demo-stack');
  if (!stack) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Sizes are made up for the demo, in MB.
  var PHOTOS = [
    { src: '1011', caption: 'Lake trip, 2019', mb: 3.1 },
    { src: 'blur1', caption: 'Market, out of focus', mb: 2.4 },
    { src: '237', caption: 'Biscuit, age 1', mb: 2.9 },
    { src: 'blur2', caption: 'Pocket shot', mb: 1.8 },
    { src: '1015', caption: 'Fjord lookout', mb: 4.2 },
    { src: '129', caption: 'Sunset bench', mb: 2.6 },
    { src: '1025', caption: 'Blanket day', mb: 3.4 },
    { src: '49', caption: 'Santorini, 2022', mb: 3.8 }
  ];
  var THRESHOLD = 90;
  var VISIBLE = 3;

  var queue = [], history = [];
  var kept = 0, deleted = 0, freed = 0;
  var els = {
    kept: document.getElementById('tally-kept'),
    deleted: document.getElementById('tally-deleted'),
    freed: document.getElementById('tally-freed'),
    undo: document.getElementById('btn-undo'),
    keep: document.getElementById('btn-keep'),
    del: document.getElementById('btn-delete'),
    done: document.getElementById('demo-done'),
    doneKept: document.getElementById('done-kept'),
    doneDeleted: document.getElementById('done-deleted'),
    reset: document.getElementById('demo-reset')
  };

  var ICON_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#check"/></svg>';
  var ICON_X = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#x"/></svg>';

  function makeCard(photo) {
    var fig = document.createElement('figure');
    fig.className = 'polaroid';
    fig.innerHTML =
      '<img src="/assets/photos/' + photo.src + '.webp" alt="Sample photo: ' + photo.caption + '" width="640" height="640" draggable="false">' +
      '<figcaption>' + photo.caption + '</figcaption>' +
      '<span class="tint keep"></span><span class="tint del"></span>' +
      '<span class="stamp stamp-keep">' + ICON_CHECK + 'KEEP</span>' +
      '<span class="stamp stamp-del">' + ICON_X + 'DELETE</span>';
    fig._photo = photo;
    return fig;
  }

  // A small fixed tilt per depth so the stack reads as a pile of prints.
  var TILTS = [0, -4, 3.5];
  function layout() {
    var cards = stack.querySelectorAll('.polaroid:not(.gone)');
    cards.forEach(function (card, i) {
      var depth = cards.length - 1 - i; // last child is on top
      card.style.zIndex = String(10 - depth);
      card.style.transition = reduceMotion ? 'none' : 'transform .35s cubic-bezier(.2,.8,.2,1)';
      card.style.transform = depth === 0
        ? 'rotate(-1.5deg)'
        : 'translate(' + (depth * 6) + 'px,' + (depth * 10) + 'px) rotate(' + TILTS[depth] + 'deg) scale(' + (1 - depth * 0.04) + ')';
      card.setAttribute('aria-hidden', depth === 0 ? 'false' : 'true');
    });
  }

  function fill() {
    // Keep VISIBLE cards in the DOM, top card last.
    while (stack.querySelectorAll('.polaroid:not(.gone)').length < VISIBLE && queue.length) {
      var count = stack.querySelectorAll('.polaroid:not(.gone)').length;
      var photo = queue[count];
      if (!photo) break;
      stack.insertBefore(makeCard(photo), stack.firstChild);
    }
    layout();
  }

  function render() {
    els.kept.textContent = kept;
    els.deleted.textContent = deleted;
    els.freed.textContent = freed >= 1000 ? (freed / 1000).toFixed(2) + ' GB' : freed.toFixed(1).replace(/\.0$/, '') + ' MB';
    els.undo.disabled = history.length === 0;
    var empty = queue.length === 0;
    els.keep.disabled = empty;
    els.del.disabled = empty;
    els.done.hidden = !empty;
    if (empty) { els.doneKept.textContent = kept; els.doneDeleted.textContent = deleted; }
  }

  function top() {
    var cards = stack.querySelectorAll('.polaroid:not(.gone)');
    return cards[cards.length - 1] || null;
  }

  function setDrag(card, dx, dy) {
    var r = dx / 18;
    card.style.transform = 'translate(' + dx + 'px,' + (dy * 0.4) + 'px) rotate(' + (-1.5 + r) + 'deg)';
    var p = Math.max(-1, Math.min(1, dx / THRESHOLD));
    card.querySelector('.stamp-keep').style.opacity = p > 0 ? p : 0;
    card.querySelector('.tint.keep').style.opacity = p > 0 ? p : 0;
    card.querySelector('.stamp-del').style.opacity = p < 0 ? -p : 0;
    card.querySelector('.tint.del').style.opacity = p < 0 ? -p : 0;
  }

  function decide(dir) {
    var card = top();
    if (!card) return;
    var photo = queue.shift();
    history.push({ photo: photo, dir: dir });
    if (dir > 0) { kept++; } else { deleted++; freed += photo.mb; }
    if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) {} }
    var w = stack.offsetWidth;
    card.classList.add('gone');
    card.style.pointerEvents = 'none';
    card.style.zIndex = '20';
    card.style.transition = reduceMotion ? 'opacity .2s' : 'transform .45s cubic-bezier(.3,.6,.3,1), opacity .45s';
    setDrag(card, dir * THRESHOLD, 0);
    requestAnimationFrame(function () {
      card.style.transform = 'translate(' + (dir * w * 1.6) + 'px,' + (-40) + 'px) rotate(' + (dir * 28) + 'deg)';
      card.style.opacity = '0';
    });
    fill();
    setTimeout(function () { card.remove(); }, reduceMotion ? 200 : 450);
    render();
  }

  function undo() {
    var last = history.pop();
    if (!last) return;
    if (last.dir > 0) { kept--; } else { deleted--; freed = Math.max(0, freed - last.photo.mb); }
    queue.unshift(last.photo);
    // Drop the bottom card if we'd exceed the visible count, then slide the photo back in.
    var cards = stack.querySelectorAll('.polaroid:not(.gone)');
    if (cards.length >= VISIBLE) cards[0].remove();
    var card = makeCard(last.photo);
    card.style.transition = 'none';
    card.style.transform = 'translate(' + (last.dir * stack.offsetWidth * 1.4) + 'px,-30px) rotate(' + (last.dir * 24) + 'deg)';
    stack.appendChild(card);
    card.getBoundingClientRect(); // commit the start position
    layout();
    render();
  }

  // Pointer dragging
  var drag = null;
  stack.addEventListener('pointerdown', function (e) {
    var card = top();
    if (!card || !card.contains(e.target)) return;
    drag = { card: card, x: e.clientX, y: e.clientY, dx: 0, dy: 0, id: e.pointerId };
    card.setPointerCapture(e.pointerId);
    card.style.transition = 'none';
  });
  stack.addEventListener('pointermove', function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    drag.dx = e.clientX - drag.x;
    drag.dy = e.clientY - drag.y;
    setDrag(drag.card, drag.dx, drag.dy);
  });
  function endDrag(e) {
    if (!drag || e.pointerId !== drag.id) return;
    var d = drag; drag = null;
    if (Math.abs(d.dx) > THRESHOLD) {
      decide(d.dx > 0 ? 1 : -1);
    } else {
      d.card.style.transition = 'transform .35s cubic-bezier(.2,.8,.2,1)';
      setDrag(d.card, 0, 0);
      layout();
    }
  }
  stack.addEventListener('pointerup', endDrag);
  stack.addEventListener('pointercancel', endDrag);

  els.keep.addEventListener('click', function () { decide(1); });
  els.del.addEventListener('click', function () { decide(-1); });
  els.undo.addEventListener('click', undo);
  stack.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); decide(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); decide(-1); }
    else if ((e.key === 'z' && (e.metaKey || e.ctrlKey)) || e.key === 'Backspace') { e.preventDefault(); undo(); }
  });

  function start() {
    queue = PHOTOS.slice();
    history = []; kept = 0; deleted = 0; freed = 0;
    stack.innerHTML = '';
    fill();
    render();
  }
  els.reset.addEventListener('click', start);
  start();

  // A gentle nudge so visitors see the card moves, once, when the demo scrolls into view.
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var nudged = false;
    new IntersectionObserver(function (entries, obs) {
      if (nudged || !entries[0].isIntersecting) return;
      nudged = true; obs.disconnect();
      setTimeout(function () {
        var card = top();
        if (!card || drag || history.length) return;
        card.style.transition = 'transform .5s cubic-bezier(.3,.7,.3,1)';
        setDrag(card, 46, 0);
        setTimeout(function () {
          if (drag || history.length || top() !== card) return;
          setDrag(card, 0, 0); layout();
        }, 700);
      }, 900);
    }, { threshold: 0.6 }).observe(stack);
  }
})();
