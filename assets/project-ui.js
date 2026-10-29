(() => {
  const assetBase = new URL('.', document.currentScript.src);
  let manifestPromise;
  const getManifest = () => manifestPromise ||= fetch(new URL('document-index.json', assetBase)).then(response => { if (!response.ok) throw new Error('Document index unavailable'); return response.json(); });
  const dialog = document.createElement('dialog');
  dialog.className = 'pdf-dialog';
  dialog.setAttribute('aria-labelledby', 'pdf-dialog-title');
  dialog.innerHTML = '<div class="pdf-toolbar"><h2 id="pdf-dialog-title">Document preview</h2><div class="pdf-actions"><a class="btn pdf-open" target="_blank" rel="noopener">Open full PDF ↗</a><a class="btn pdf-download" download>Download PDF ↓</a><button type="button" class="btn pdf-close" aria-label="Close document preview">Close ×</button></div></div><div class="pdf-controls"><button class="btn pdf-prev" type="button">← Previous</button><span class="pdf-page-status" role="status">Loading…</span><button class="btn pdf-next" type="button">Next →</button><label>Zoom <select class="pdf-zoom" aria-label="Document zoom"><option value="100">Fit width</option><option value="150">150%</option><option value="200">200%</option></select></label></div><div class="pdf-reader" tabindex="0" aria-label="Document page"><div class="pdf-sheet"><img class="pdf-page-image" alt=""></div></div><p class="pdf-mobile-help">Use Previous / Next to read every page. Zoom in for detail, or download the original PDF.</p>';
  document.body.append(dialog);
  const image = dialog.querySelector('.pdf-page-image');
  const reader = dialog.querySelector('.pdf-reader');
  const sheet = dialog.querySelector('.pdf-sheet');
  const status = dialog.querySelector('.pdf-page-status');
  const prev = dialog.querySelector('.pdf-prev');
  const next = dialog.querySelector('.pdf-next');
  let trigger, currentDoc, currentPage = 1, title, request = 0;
  function render() {
    image.src = new URL(`document-previews/${currentDoc.id}/page-${String(currentPage).padStart(3, '0')}.jpg`, assetBase).href;
    image.alt = `${title}, page ${currentPage} of ${currentDoc.pages}`;
    status.textContent = `Page ${currentPage} of ${currentDoc.pages}`;
    prev.disabled = currentPage <= 1;
    next.disabled = currentPage >= currentDoc.pages;
    reader.scrollTo(0, 0);
  }
  document.addEventListener('click', async event => {
    const button = event.target.closest('[data-pdf]');
    if (!button) return;
    trigger = button;
    const href = button.dataset.pdf;
    title = button.dataset.title || 'Document preview';
    dialog.querySelector('h2').textContent = title;
    dialog.querySelector('.pdf-open').href = href;
    dialog.querySelector('.pdf-download').href = href;
    dialog.querySelector('.pdf-download').setAttribute('download', href.split('/').pop());
    dialog.querySelector('.pdf-zoom').value = '100';
    sheet.style.width = '100%';
    image.removeAttribute('src');
    currentDoc = null;
    prev.disabled = next.disabled = true;
    status.textContent = 'Loading document…';
    const id = ++request;
    dialog.showModal();
    document.body.classList.add('preview-open');
    try {
      const manifest = await getManifest();
      if (id !== request || !dialog.open) return;
      currentDoc = manifest[decodeURIComponent(href.split('/').pop())];
      if (!currentDoc) throw new Error('Document preview unavailable');
      currentPage = Math.min(currentDoc.pages, Math.max(1, Number(button.dataset.page) || 1));
      render();
    } catch (error) {
      status.textContent = 'Preview unavailable. Use Open full PDF or Download PDF.';
    }
  });
  prev.addEventListener('click', () => { if (currentDoc && currentPage > 1) { currentPage--; render(); } });
  next.addEventListener('click', () => { if (currentDoc && currentPage < currentDoc.pages) { currentPage++; render(); } });
  dialog.querySelector('.pdf-zoom').addEventListener('change', event => { sheet.style.width = event.target.value + '%'; });
  dialog.querySelector('.pdf-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    request++;
    image.removeAttribute('src');
    document.body.classList.remove('preview-open');
    trigger?.focus();
  });
})();

// Image zoom: an "Enlarge" button on every content image, opening a full-screen viewer.
(() => {
  const imgs = [...document.querySelectorAll('main figure img, main .lab > img')]
    .filter(img => !img.closest('.document-cover'));
  if (!imgs.length) return;
  const dlg = document.createElement('dialog');
  dlg.className = 'zoom-dialog';
  dlg.setAttribute('aria-label', 'Enlarged image');
  dlg.innerHTML = '<div class="zoom-bar"><span class="zoom-cap"></span><span class="btns"><button type="button" class="btn zoom-toggle">Actual size</button><button type="button" class="btn zoom-close" aria-label="Close enlarged image">Close ×</button></span></div><div class="zoom-stage"><img alt=""></div>';
  document.body.append(dlg);
  const stage = dlg.querySelector('.zoom-stage'), big = stage.querySelector('img'), toggle = dlg.querySelector('.zoom-toggle');
  let opener;
  const setFull = on => { stage.classList.toggle('full', on); toggle.textContent = on ? 'Fit to screen' : 'Actual size'; };
  function open(img) {
    opener = img;
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    const cap = img.closest('figure')?.querySelector('figcaption')?.textContent || img.alt || '';
    dlg.querySelector('.zoom-cap').textContent = cap;
    setFull(false);
    dlg.showModal();
    document.body.classList.add('preview-open');
  }
  imgs.forEach(img => {
    img.classList.add('zoomable');
    const wrap = document.createElement('span');
    wrap.className = 'zoom-wrap';
    img.parentNode.insertBefore(wrap, img);
    wrap.append(img);
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'zoom-btn';
    b.textContent = '⤢ Enlarge';
    b.setAttribute('aria-label', 'Enlarge image' + (img.alt ? ': ' + img.alt : ''));
    wrap.append(b);
    b.addEventListener('click', () => open(img));
    img.addEventListener('click', () => open(img));
  });
  toggle.addEventListener('click', () => setFull(!stage.classList.contains('full')));
  big.addEventListener('click', () => setFull(!stage.classList.contains('full')));
  dlg.querySelector('.zoom-close').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => { if (e.target === dlg || e.target === stage) dlg.close(); });
  dlg.addEventListener('close', () => { document.body.classList.remove('preview-open'); opener?.focus?.(); });
})();
