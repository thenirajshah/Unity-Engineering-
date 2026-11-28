(() => {
  const root = document.querySelector('.lineup');
  if (!root) return;
  const stage = root.querySelector('.lineup-stage');
  const cards = [...stage.querySelectorAll('.lineup-machine')];
  const details = [...root.querySelectorAll('.lineup-detail')];
  const controls = root.querySelector('.lineup-controls');
  const count = cards.length;
  const wrap = n => ((n % count) + count) % count;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let position = 0, target = 0, selected = -1;
  let frame = 0, previous = 0, wheelTimer;
  let pointer = null, startX, startPosition, dragged = false;

  function draw() {
    cards.forEach((card, i) => {
      let depth = wrap(i - position);
      if (depth > count - 1) depth -= count;
      const scale = Math.pow(.74, depth);
      const left = depth < 0 ? 3 + depth * 56 : 3 + 94 * (1 - Math.pow(.62, depth));
      card.style.transform = 'translate(' + left / .47 + '%, ' + (-depth * 3.6) + '%) scale(' + scale + ')';
      card.style.filter = 'blur(' + Math.max(0, depth * .8) + 'px)';
      const fade = depth < 0 ? Math.min(1, 4 * (1 + depth)) : 1 - depth / (count - 1);
      card.style.opacity = String(fade);
      card.style.pointerEvents = fade < .08 ? 'none' : '';
      card.style.zIndex = String(100 - Math.round(depth * 10));
    });
    const active = wrap(Math.round(position));
    if (active === selected) return;
    selected = active;
    details.forEach((detail, i) => { detail.hidden = i !== active; });
  }

  function animate(now) {
    const dt = Math.min(now - previous, 50);
    previous = now;
    position += (target - position) * (1 - Math.exp(-dt * .0072));
    if (reduce.matches || Math.abs(position - target) < .0004) position = target;
    draw();
    frame = position === target ? 0 : requestAnimationFrame(animate);
  }

  function move(value) {
    target = value;
    if (!frame) {
      previous = performance.now();
      frame = requestAnimationFrame(animate);
    }
  }

  function step(amount) {
    clearTimeout(wheelTimer);
    move(Math.round(target) + amount);
  }

  controls.addEventListener('click', event => {
    const button = event.target.closest('[data-step]');
    if (button) step(Number(button.dataset.step));
  });
  root.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    step(event.key === 'ArrowRight' ? 1 : -1);
  });
  stage.addEventListener('pointerdown', event => {
    if (!event.isPrimary || event.button !== 0) return;
    pointer = event.pointerId;
    clearTimeout(wheelTimer);
    startX = event.clientX;
    startPosition = target;
    dragged = false;
  });
  stage.addEventListener('pointermove', event => {
    if (pointer !== event.pointerId) return;
    const dx = startX - event.clientX;
    if (!dragged && Math.abs(dx) < 6) return;
    if (!dragged) stage.setPointerCapture(pointer);
    dragged = true;
    move(startPosition + dx / Math.max(110, stage.clientWidth * .22));
  });
  function release(event) {
    if (event.pointerId !== pointer) return;
    pointer = null;
    if (dragged) move(Math.round(target));
  }
  window.addEventListener('pointerup', release);
  window.addEventListener('pointercancel', release);
  stage.addEventListener('dragstart', event => event.preventDefault());
  stage.addEventListener('click', event => {
    const card = event.target.closest('.lineup-machine');
    if (!card || (event.detail && dragged)) return;
    const base = Math.round(position);
    move(base + wrap(cards.indexOf(card) - base));
  });
  stage.addEventListener('wheel', event => {
    if (event.ctrlKey) return;
    event.preventDefault();
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? stage.clientHeight : 1;
    const delta = (event.deltaX + event.deltaY) * unit;
    move(target + Math.max(-120, Math.min(120, delta)) / 180);
    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(() => move(Math.round(target)), 150);
  }, { passive: false });

  root.classList.add('lineup-ready');
  controls.hidden = false;
  cards.forEach(card => { card.tabIndex = -1; });
  draw();
})();
