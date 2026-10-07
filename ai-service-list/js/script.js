// 필터·검색·모달 기능 (데이터는 services.js)
const PRICE = {
  free: { label: '무료', cls: 'free' },
  freemium: { label: '무료+유료', cls: 'freemium' },
  paid: { label: '유료', cls: 'paid' },
};

// 분야별 은은한 색조 (hue)
const HUES = [28, 215, 262, 330, 8, 190, 150, 100, 340, 45, 175, 285, 235, 20];
const hueOf = (cat) => HUES[CATEGORIES.indexOf(cat) % HUES.length];

const state = { cat: '전체', price: 'all', q: '' };

const $ = (id) => document.getElementById(id);
const grid = $('grid');
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
};

function domainOf(url) {
  try { return new URL(url).hostname; } catch { return ''; }
}

// 로고: 파비콘 서비스 사용, 실패하면 첫 글자로 대체
function makeLogo(s, size) {
  const wrap = el('span', 'logo');
  const img = new Image();
  img.alt = '';
  img.loading = 'lazy';
  img.decoding = 'async';
  img.src = `https://www.google.com/s2/favicons?domain=${domainOf(s.url)}&sz=${size || 128}`;
  img.addEventListener('error', () => {
    img.remove();
    wrap.classList.add('fallback');
    wrap.textContent = s.name.trim().charAt(0).toUpperCase();
  });
  img.addEventListener('load', () => {
    // 아주 작은 기본 아이콘(지구본)이 오면 첫 글자로 대체
    if (img.naturalWidth && img.naturalWidth < 24) img.dispatchEvent(new Event('error'));
  });
  wrap.appendChild(img);
  return wrap;
}

function badge(type) {
  const p = PRICE[type];
  return el('span', `badge ${p.cls}`, p.label);
}

function matches(s) {
  if (state.cat !== '전체' && !s.categories.includes(state.cat)) return false;
  if (state.price !== 'all' && s.priceType !== state.price) return false;
  if (state.q) {
    const hay = [s.name, s.desc, s.useCase, ...s.categories, ...s.pros].join(' ').toLowerCase();
    if (!state.q.split(/\s+/).every((w) => hay.includes(w))) return false;
  }
  return true;
}

function makeCard(s, i) {
  const hue = hueOf(s.categories[0]);
  const card = el('article', 'card');
  card.style.setProperty('--h', hue);
  card.tabIndex = 0;
  card.setAttribute('role', 'button');
  card.setAttribute('aria-label', `${s.name} 상세 보기`);

  const top = el('div', 'card-top');
  const link = el('a', 'logo-link');
  link.href = s.url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.title = `${s.name} 공식 사이트 열기`;
  link.setAttribute('aria-label', `${s.name} 공식 사이트 열기`);
  link.appendChild(makeLogo(s));
  link.addEventListener('click', (e) => e.stopPropagation());
  top.append(link, badge(s.priceType));

  const name = el('h3', 'card-name', s.name);
  const cats = el('p', 'card-cats', s.categories.join(' · '));
  const desc = el('p', 'card-desc', s.desc);
  const use = el('p', 'card-use');
  use.append(el('span', null, '추천'), document.createTextNode(s.useCase));

  card.append(top, name, cats, desc, use);
  card.addEventListener('click', () => openModal(s, card));
  card.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target === card) {
      e.preventDefault();
      openModal(s, card);
    }
  });
  return card;
}

// 스크롤 등장: 화면에 들어온 카드를 순서대로 띄움
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const revealer = ('IntersectionObserver' in window && !reduceMotion)
  ? new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach((e, k) => {
        const card = e.target;
        revealer.unobserve(card);
        card.style.transitionDelay = `${k * 55}ms`;
        card.classList.add('in');
        setTimeout(() => { card.style.transitionDelay = ''; }, 900);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 })
  : null;

let renderTimer = 0;
function render() {
  const list = services.filter(matches);
  const paint = () => {
    grid.classList.remove('out');
    const cards = list.map(makeCard);
    grid.replaceChildren(...cards);
    cards.forEach((c) => (revealer ? revealer.observe(c) : c.classList.add('in')));
    $('empty').hidden = list.length > 0;
    $('count').textContent = `${list.length}개 서비스`;
  };
  clearTimeout(renderTimer);
  if (reduceMotion || !grid.children.length) return paint();
  grid.classList.add('out'); // 기존 카드가 먼저 사라진 뒤 새 카드가 등장
  renderTimer = setTimeout(paint, 160);
}

function fillList(ul, items) {
  ul.replaceChildren(...items.map((t) => el('li', null, t)));
}

let lastFocus = null;
function openModal(s, from) {
  lastFocus = from || document.activeElement;
  const m = $('modal');
  m.style.setProperty('--h', hueOf(s.categories[0]));
  $('m-logo').replaceChildren(makeLogo(s, 128));
  $('m-name').textContent = s.name;
  const meta = $('m-meta');
  meta.replaceChildren(badge(s.priceType), ...s.categories.map((c) => el('span', 'tag', c)));
  $('m-desc').textContent = s.desc;
  fillList($('m-price'), s.priceDetail.length ? s.priceDetail : ['요금 정보를 확인 중이에요']);
  fillList($('m-pros'), s.pros);
  $('m-use').textContent = s.useCase;
  $('m-link').href = s.url;
  m.hidden = false;
  document.body.classList.add('lock');
  m.querySelector('.sheet').scrollTop = 0;
  m.querySelector('.close').focus();
}

function closeModal() {
  $('modal').hidden = true;
  document.body.classList.remove('lock');
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}

function buildFilters() {
  const box = $('categories');
  ['전체', ...CATEGORIES].forEach((c) => {
    const b = el('button', 'chip', c);
    b.type = 'button';
    b.dataset.cat = c;
    if (c !== '전체') b.style.setProperty('--h', hueOf(c));
    b.setAttribute('aria-pressed', c === state.cat);
    b.addEventListener('click', () => {
      state.cat = c;
      syncActive();
      render();
    });
    box.appendChild(b);
  });
  const seg = $('prices');
  [['all', '전체'], ['free', '무료'], ['freemium', '무료+유료'], ['paid', '유료']].forEach(([k, label]) => {
    const b = el('button', null, label);
    b.type = 'button';
    b.dataset.price = k;
    b.setAttribute('aria-pressed', k === state.price);
    b.addEventListener('click', () => {
      state.price = k;
      syncActive();
      render();
    });
    seg.appendChild(b);
  });
}

function syncActive() {
  document.querySelectorAll('.chip').forEach((b) => b.setAttribute('aria-pressed', b.dataset.cat === state.cat));
  document.querySelectorAll('#prices button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.price === state.price));
  const active = document.querySelector('.chip[aria-pressed="true"]');
  if (active) active.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
}

// 마우스로 잡아끌어 분야 칩 가로 스크롤 (터치는 기본 스와이프 사용)
function enableDragScroll(box) {
  let down = false, moved = false, startX = 0, startLeft = 0;
  box.addEventListener('pointerdown', (e) => {
    if (e.pointerType !== 'mouse' || e.button !== 0) return;
    down = true; moved = false;
    startX = e.clientX; startLeft = box.scrollLeft;
  });
  window.addEventListener('pointermove', (e) => {
    if (!down) return;
    const dx = e.clientX - startX;
    if (!moved && Math.abs(dx) > 5) { moved = true; box.classList.add('dragging'); }
    if (moved) box.scrollLeft = startLeft - dx;
  });
  window.addEventListener('pointerup', () => {
    if (!down) return;
    down = false;
    box.classList.remove('dragging');
  });
  // 드래그 직후에는 칩 클릭이 일어나지 않도록 막음
  box.addEventListener('click', (e) => {
    if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; }
  }, true);
}

function init() {
  $('stats').textContent = `${services.length}개 서비스 · ${CATEGORIES.length}개 분야`;
  buildFilters();
  enableDragScroll($('categories'));
  render();

  $('search').addEventListener('input', (e) => {
    state.q = e.target.value.trim().toLowerCase();
    render();
  });
  $('reset').addEventListener('click', () => {
    state.cat = '전체';
    state.price = 'all';
    state.q = '';
    $('search').value = '';
    syncActive();
    render();
  });
  $('modal').addEventListener('click', (e) => {
    if (e.target.closest('[data-close]')) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !$('modal').hidden) closeModal();
  });
}

init();
