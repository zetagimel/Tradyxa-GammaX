const CACHE_VERSION = 'v2-aztryx';
const CACHE_NAME = `aztryx-${CACHE_VERSION}`;

// Assets to cache on install
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Caching static assets');
      return cache.addAll(ASSETS_TO_CACHE).catch(() => {
        console.log('[SW] Some assets failed to cache (expected for dynamic files)');
      });
    })
  );
  self.skipWaiting();
});

// Fetch event - use network-first for data, cache-first for assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Always fetch fresh data files - never use cache
  if (url.pathname.startsWith('/data/')) {
    event.respondWith(
      fetch(request, { cache: 'no-store' })
        .then((response) => {
          // Only cache successful responses
          if (response && response.status === 200) {
            const clonedResponse = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, clonedResponse);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              console.log('[SW] Serving cached response for offline:', url.pathname);
              return cachedResponse;
            }
            return new Response('No cached data available', { status: 503 });
          });
        })
    );
    return;
  }

  // Cache-first for static assets (HTML, CSS, JS)
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(request, { cache: 'default' }).then((response) => {
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }
        const clonedResponse = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, clonedResponse);
        });
        return response;
      });
    }).catch(() => {
      // Return offline page or cached response
      return caches.match('/index.html');
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name.startsWith('aztryx-'))
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// Background sync for offline updates (optional enhancement)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(
      fetch('/data/ticker/NIFTY.json', { cache: 'no-store' })
        .then(() => {
          console.log('[SW] Background sync completed');
        })
        .catch(console.error)
    );
  }
});
