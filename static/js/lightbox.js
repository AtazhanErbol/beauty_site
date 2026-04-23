/**
 * Lightbox для портфолио.
 * Открывает изображение в полноэкранной модалке с навигацией и клавиатурным управлением.
 */
(function () {
  'use strict';

  const grid = document.getElementById('portfolio-grid');
  const lightbox = document.getElementById('lightbox');
  if (!grid || !lightbox) return;

  const imgEl = document.getElementById('lightbox-image');
  const captionEl = document.getElementById('lightbox-caption');
  const closeBtn = document.getElementById('lightbox-close');
  const prevBtn = document.getElementById('lightbox-prev');
  const nextBtn = document.getElementById('lightbox-next');

  const items = Array.from(grid.querySelectorAll('.portfolio-item'));
  let currentIndex = -1;
  let lastFocused = null;

  function buildCaption(item) {
    const title = item.dataset.title || '';
    const description = item.dataset.description || '';
    let html = '';
    if (title) html += '<h3 class="lightbox-title">' + escapeHtml(title) + '</h3>';
    if (description) html += '<p class="lightbox-description">' + escapeHtml(description) + '</p>';
    return html;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function open(index) {
    if (index < 0 || index >= items.length) return;
    currentIndex = index;
    lastFocused = document.activeElement;
    const item = items[index];
    imgEl.src = item.dataset.src || item.querySelector('img').src;
    imgEl.alt = item.dataset.title || '';
    captionEl.innerHTML = buildCaption(item);
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.classList.add('lightbox-open');
    updateNavButtons();
    // focus close for keyboard users
    setTimeout(function () { closeBtn.focus(); }, 50);
  }

  function close() {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lightbox-open');
    imgEl.src = '';
    currentIndex = -1;
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
  }

  function updateNavButtons() {
    if (items.length <= 1) {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    } else {
      prevBtn.style.display = '';
      nextBtn.style.display = '';
    }
  }

  function prev() {
    if (items.length === 0) return;
    open((currentIndex - 1 + items.length) % items.length);
  }

  function next() {
    if (items.length === 0) return;
    open((currentIndex + 1) % items.length);
  }

  // Click on each figure
  items.forEach(function (item, idx) {
    item.addEventListener('click', function () { open(idx); });
    item.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open(idx);
      }
    });
  });

  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', prev);
  nextBtn.addEventListener('click', next);

  // Click on backdrop closes
  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) close();
  });

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (!lightbox.classList.contains('is-open')) return;
    if (e.key === 'Escape') { close(); }
    else if (e.key === 'ArrowLeft') { prev(); }
    else if (e.key === 'ArrowRight') { next(); }
  });

  // Swipe на мобильных
  let touchStartX = null;
  lightbox.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) return;
    touchStartX = e.touches[0].clientX;
  });
  lightbox.addEventListener('touchend', function (e) {
    if (touchStartX == null) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) {
      if (dx > 0) prev(); else next();
    }
    touchStartX = null;
  });
})();
