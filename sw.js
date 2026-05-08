const SHARE_CACHE = 'facturas-shared-files-v1';

self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.endsWith('/share-target') && event.request.method === 'POST') {
    event.respondWith(handleShare(event.request));
    return;
  }
  if (url.pathname.includes('/shared/')) {
    event.respondWith(caches.open(SHARE_CACHE).then(cache => cache.match(event.request)));
  }
});

async function handleShare(request) {
  const formData = await request.formData();
  const files = formData.getAll('files').filter(file => file && file.size);
  const id = String(Date.now());
  const cache = await caches.open(SHARE_CACHE);
  const manifest = { id, files: [] };

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const safeName = sanitizeName(file.name || `invoice-${i + 1}`);
    const url = `shared/${id}/${i}-${safeName}`;
    await cache.put(url, new Response(file, {
      headers: {
        'Content-Type': file.type || guessType(safeName),
        'X-File-Name': encodeURIComponent(safeName)
      }
    }));
    manifest.files.push({ name: safeName, type: file.type || guessType(safeName), url });
  }

  await cache.put(`shared/${id}/manifest.json`, new Response(JSON.stringify(manifest), {
    headers: { 'Content-Type': 'application/json; charset=utf-8' }
  }));

  return Response.redirect(`online.html?shared=${id}`, 303);
}

function sanitizeName(name) {
  return String(name).replace(/[\\/:*?"<>|]+/g, '_').slice(0, 140);
}

function guessType(name) {
  const lower = String(name).toLowerCase();
  if (lower.endsWith('.pdf')) return 'application/pdf';
  if (lower.endsWith('.png')) return 'image/png';
  return 'image/jpeg';
}
