(() => {
  const root = document.querySelector('.lineup');
  if (!root) return;

  const exhibit = root.querySelector('.lineup-exhibit');
  const stage = exhibit.querySelector('.lineup-stage');
  const credits = exhibit.querySelector('.lineup-credits');
  const counter = exhibit.querySelector('.lineup-count b');
  const announcement = exhibit.querySelector('.lineup-sr');
  const details = [...root.querySelectorAll('.lineup-detail')];
  const indexLinks = [...root.querySelectorAll('.lineup-index a')];
  const wrap = value => (value % details.length + details.length) % details.length;
  let current = 0;

  // Reuse the same images and source credits as the fully readable static edition.
  const plates = details.map(detail => {
    const photo = detail.querySelector('.lineup-photo');
    const title = detail.querySelector('h2').textContent;
    const credit = photo.querySelector('.lineup-credit');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'lineup-machine';
    button.setAttribute('aria-label', 'Show ' + title);
    button.tabIndex = -1; // The category index provides an equivalent keyboard target for every plate.
    button.append(photo.querySelector('img'));
    stage.append(button);
    credits.append(credit);
    photo.remove();
    return { button, credit, title };
  });

  function select(value) {
    const previousDetail = details[current];
    const focusedAction = [...previousDetail.querySelectorAll('.actions a')].indexOf(document.activeElement);
    current = wrap(value);
    plates.forEach(({ button, credit }, i) => {
      const active = i === current;
      button.dataset.slot = wrap(i - current);
      button.setAttribute('aria-pressed', String(active));
      details[i].hidden = !active;
      credit.hidden = !active;
      if (active) indexLinks[i].setAttribute('aria-current', 'true');
      else indexLinks[i].removeAttribute('aria-current');
    });
    counter.textContent = String(current + 1).padStart(2, '0');
    announcement.textContent = ' · ' + plates[current].title;
    if (focusedAction !== -1) details[current].querySelectorAll('.actions a')[focusedAction].focus({ preventScroll: true });
  }

  exhibit.querySelector('.lineup-controls').addEventListener('click', event => {
    const arrow = event.target.closest('[data-step]');
    if (arrow) select(current + Number(arrow.dataset.step));
  });
  indexLinks.forEach((link, i) => link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    select(i);
    if (matchMedia('(max-width: 820px)').matches) stage.scrollIntoView({ block: 'start' });
  }));
  document.addEventListener('keydown', event => {
    if (event.target !== document.body && !root.contains(event.target)) return;
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    select(current + (event.key === 'ArrowRight' ? 1 : -1));
  });

  let gesture = null;
  let suppressClick = false;
  stage.addEventListener('pointerdown', event => {
    if (!event.isPrimary || event.button !== 0) return;
    suppressClick = false;
    gesture = { id: event.pointerId, x: event.clientX, y: event.clientY, horizontal: false };
  });
  stage.addEventListener('dragstart', event => event.preventDefault());
  stage.addEventListener('pointermove', event => {
    if (gesture?.id !== event.pointerId || gesture.horizontal) return;
    const dx = Math.abs(event.clientX - gesture.x);
    const dy = Math.abs(event.clientY - gesture.y);
    if (dy > 10 && dy > dx) {
      gesture = null;
      suppressClick = true;
    } else if (dx > 10 && dx > 1.25 * dy) {
      gesture.horizontal = true;
      suppressClick = true;
      stage.setPointerCapture(event.pointerId);
    }
  });
  window.addEventListener('pointerup', event => {
    if (gesture?.id !== event.pointerId) return;
    const dx = event.clientX - gesture.x;
    if (gesture.horizontal && Math.abs(dx) >= 32) select(current + (dx < 0 ? 1 : -1));
    gesture = null;
  });
  stage.addEventListener('pointercancel', () => { gesture = null; });
  stage.addEventListener('click', event => {
    if (suppressClick && event.detail) return;
    const button = event.target.closest('.lineup-machine');
    if (button) select(plates.findIndex(plate => plate.button === button));
  });

  // Category links also resolve when opened in a new tab or with scripting disabled.
  const fromFragment = () => {
    const index = details.findIndex(detail => '#' + detail.id === location.hash);
    select(Math.max(0, index));
  };
  fromFragment();
  window.addEventListener('hashchange', fromFragment);
  root.classList.add('lineup-ready');
  exhibit.hidden = false;
})();
