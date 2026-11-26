const navigation = document.querySelector('#navigation');
const menu = document.querySelector('.menu-button');
const mega = document.querySelector('.mega');

function closeMenu() {
  navigation.classList.remove('open');
  menu.setAttribute('aria-expanded', 'false');
  mega.open = false;
}
menu.addEventListener('click', () => {
  if (navigation.classList.contains('open')) {
    closeMenu();
    return;
  }
  navigation.classList.add('open');
  menu.setAttribute('aria-expanded', 'true');
});
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  if (mega.open) {
    mega.open = false;
    mega.querySelector('summary').focus();
  } else if (navigation.classList.contains('open')) {
    closeMenu();
    menu.focus();
  }
});
document.addEventListener('click', (event) => {
  if (!event.target.closest('.nav')) closeMenu();
});

const search = document.querySelector('#search');
const category = document.querySelector('#category');
const grid = document.querySelector('#product-grid');

if (grid) {
  const count = document.querySelector('#count');
  const empty = document.querySelector('#no-results');
  const cards = [...grid.querySelectorAll('.card')];
  const normalize = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

  function filter() {
    const terms = normalize(search.value).split(' ');
    let total = 0;
    for (const card of cards) {
      const matchesCategory = category.value === '' || card.dataset.category === category.value;
      const copy = normalize(card.dataset.search);
      const found = matchesCategory && terms.every((term) => copy.includes(term));
      card.hidden = !found;
      if (found) total += 1;
    }
    count.textContent = total === 1 ? '1 equipment entry' : `${total} equipment entries`;
    empty.hidden = total !== 0;
  }
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);

  const dialog = document.querySelector('#preview-dialog');
  for (const button of grid.querySelectorAll('.preview')) {
    button.hidden = false;
    button.addEventListener('click', () => {
      const card = button.closest('.card');
      const source = card.querySelector('img');
      const image = dialog.querySelector('img');
      image.src = source.src;
      image.alt = source.alt;
      dialog.querySelector('h2').textContent = button.dataset.title;
      dialog.querySelector('p').textContent = button.dataset.detail;
      dialog.querySelector('.detail-link').href = card.querySelector('.card-image').href;
      dialog.querySelector('.quote-link').href = card.querySelector('[href^="/quotation/"]').href;
      dialog.showModal();
    });
  }
}

const enquiry = document.querySelector('#enquiry');
if (enquiry) {
  const category = enquiry.elements.category;
  const equipment = enquiry.elements.equipment;
  const status = document.querySelector('#form-status');
  const named = new URLSearchParams(location.search).get('equipment');
  const selected = [...equipment.options].find((option) => option.value === named && named);

  function filterEquipment() {
    if (category.value && equipment.selectedOptions[0]?.dataset.category !== category.value) {
      equipment.value = '';
    }
    for (const option of equipment.options) {
      option.hidden = Boolean(option.value && category.value && option.dataset.category !== category.value);
      option.disabled = option.hidden;
    }
  }
  if (selected) {
    equipment.value = selected.value;
    category.value = selected.dataset.category;
  }
  category.addEventListener('change', filterEquipment);
  equipment.addEventListener('change', () => {
    const selected = equipment.selectedOptions[0];
    if (selected.value) category.value = selected.dataset.category;
    filterEquipment();
  });
  filterEquipment();
  enquiry.addEventListener('submit', (event) => {
    event.preventDefault();
    const fields = [
      ['name', 'Name'], ['company', 'Company'], ['email', 'Email'], ['phone', 'Mobile'],
      ['category', 'Equipment category'], ['equipment', 'Equipment name'], ['capacity', 'Capacity'],
      ['material', 'Material'], ['pressure', 'Design pressure'], ['temperature', 'Design temperature'],
      ['requirements', 'Project requirements']
    ];
    const lines = ['Hello Unity Engineering,', '', 'I would like to request a quotation.', ''];
    for (const [field, label] of fields) {
      const input = enquiry.elements[field];
      const value = input.tagName === 'SELECT' && input.value ? input.selectedOptions[0].text : input.value.trim();
      if (value) lines.push(label + ': ' + value);
    }
    const body = encodeURIComponent(lines.join('\n'));
    if (event.submitter?.value === 'whatsapp') {
      window.open('https://wa.me/919934969351?text=' + body, '_blank', 'noopener,noreferrer');
      status.textContent = 'Review and send the draft in WhatsApp.';
    } else {
      const email = document.createElement('a');
      email.href = 'mailto:Nirajkumarshah17@gmail.com?subject=Unity%20Engineering%20equipment%20enquiry&body=' + body;
      status.textContent = 'Review and send the draft in your email app.';
      email.click();
    }
  });
  for (const button of enquiry.querySelectorAll('button[type="submit"]')) button.disabled = false;
}

const models = new Map();
async function loadModel(kind) {
  if (!models.has(kind)) {
    const response = await fetch('/assets/models/' + kind + '.glb');
    if (!response.ok) throw new Error('Equipment model unavailable');
    const file = await response.arrayBuffer();
    const header = new DataView(file);
    if (header.getUint32(0, true) !== 0x46546c67 || header.getUint32(4, true) !== 2) {
      throw new Error('Invalid equipment model');
    }
    const length = header.getUint32(12, true);
    const data = JSON.parse(new TextDecoder().decode(new Uint8Array(file, 20, length)));
    const offset = 28 + length;
    const indexView = data.bufferViews[1];
    const Index = data.accessors[3].componentType === 5125 ? Uint32Array : Uint16Array;
    models.set(kind, {
      vertices: new Float32Array(file, offset, data.bufferViews[0].byteLength / 4),
      indices: new Index(file, offset + indexView.byteOffset, data.accessors[3].count)
    });
  }
  return models.get(kind);
}

let engine;
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
for (const viewer of document.querySelectorAll('[data-viewer]')) {
  const canvas = viewer.querySelector('canvas');
  const fallback = viewer.querySelector('img');
  const launch = viewer.querySelector('.launch');
  const controls = viewer.querySelector('.viewer-controls');
  const status = viewer.querySelector('.viewer-status');
  const components = viewer.nextElementSibling?.matches('.components') ? viewer.nextElementSibling : null;
  const hero = viewer.dataset.hero === 'true';
  let model;
  launch.hidden = false;
  launch.addEventListener('click', async () => {
    launch.disabled = true;
    status.textContent = 'Loading equipment model…';
    canvas.hidden = false;
    try {
      engine ??= import('/assets/engine.js');
      const [, data] = await Promise.all([engine, loadModel(viewer.dataset.kind)]);
      model = window.Unity3D.viewer(canvas, viewer.dataset.kind, { data, auto: hero && !reduced.matches });
      if (!model) throw new Error('WebGL is unavailable');
      viewer.classList.add('running');
      if (fallback) fallback.hidden = true;
      launch.hidden = true;
      controls.hidden = false;
      if (components) components.hidden = false;
      controls.querySelector('[data-control="rotate"]').setAttribute('aria-pressed', String(hero && !reduced.matches));
      status.textContent = '';
      canvas.focus({ preventScroll: true });
    } catch {
      canvas.hidden = true;
      launch.hidden = true;
      status.textContent = 'Interactive 3D is unavailable. Showing the concept image.';
    }
  });
  canvas.addEventListener('webglcontextlost', () => {
    model?.dispose();
    model = null;
    viewer.classList.remove('running');
    canvas.hidden = true;
    controls.hidden = true;
    if (components) components.hidden = true;
    if (fallback) fallback.hidden = false;
    status.textContent = 'Interactive 3D is unavailable. Showing the concept image.';
  });
  components?.addEventListener('click', (event) => {
    const target = event.target.closest('[data-component]');
    if (!target || !model) return;
    for (const button of components.querySelectorAll('button')) {
      button.setAttribute('aria-pressed', String(button === target));
    }
    model.focus(Number(target.dataset.yaw), Number(target.dataset.pitch));
    controls.querySelector('[data-control="rotate"]').setAttribute('aria-pressed', 'false');
    components.nextElementSibling.textContent = target.dataset.note;
  });
  controls.addEventListener('click', async (event) => {
    const control = event.target.closest('[data-control]');
    if (!control || !model) return;
    switch (control.dataset.control) {
      case 'rotate': control.setAttribute('aria-pressed', String(model.toggle())); break;
      case 'in': model.zoom(-0.45); break;
      case 'out': model.zoom(0.45); break;
      case 'reset': model.reset(); break;
      case 'cutaway':
      case 'exploded': {
        const showing = control.getAttribute('aria-pressed') === 'true';
        const mode = control.dataset.control;
        const variants = [...controls.querySelectorAll('[data-control="cutaway"], [data-control="exploded"]')];
        for (const button of variants) button.disabled = true;
        status.textContent = 'Loading equipment view…';
        try {
          const next = await loadModel(showing ? 'exchanger' : 'exchanger-' + mode);
          if (!model) return;
          model.replace(next);
          for (const button of variants) button.setAttribute('aria-pressed', String(button === control && !showing));
          status.textContent = showing ? '' : mode === 'cutaway'
            ? 'Concept cutaway · Shell omitted to expose tubes and support rings.'
            : 'Concept exploded assembly · Channel heads separated from the bundle.';
        } catch {
          status.textContent = 'The selected view could not be loaded.';
        } finally {
          for (const button of variants) button.disabled = false;
        }
        break;
      }
      case 'fullscreen':
        try {
          if (document.fullscreenElement) await document.exitFullscreen();
          else await viewer.requestFullscreen();
        } catch {
          status.textContent = 'Fullscreen is unavailable in this browser.';
        }
        break;
    }
  });
}
