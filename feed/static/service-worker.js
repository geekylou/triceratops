/*
 Copyright 2016 Google Inc. All Rights Reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

// Names of the two caches used in this version of the service worker.
// Change to v2, etc. when you update any of the local resources, which will
// in turn trigger the install event again.
const PRECACHE = 'precache-v2';
const RUNTIME = 'runtime';

// A list of local resources we always want to be cached.
const PRECACHE_URLS = [
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.min.js',
  '/static/css/bootstrap-theme.min.css',
  '/static/jquery.min.js',
];

// A list of local resources we always want to be cached.
const SECURE_URLS = [
  '/rss/base',
  '/rss/?liked&no_header',
  '/rss/?&no_header',
];

function cacheSecure(cache,url)
{
    fetch(url,
    {
        credentials: 'include'
    }).then(function (response) 
    {
      if (!response.ok) {
        throw new TypeError('bad response status');
      }
      return cache.put(url, response);
    });
}
// The install handler takes care of precaching the resources we always need.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(PRECACHE)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(self.skipWaiting())
  );
});

// The activate handler takes care of cleaning up old caches.
self.addEventListener('activate', event => {
  const currentCaches = [PRECACHE, RUNTIME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
    }).then(cachesToDelete => {
      return Promise.all(cachesToDelete.map(cacheToDelete => {
        return caches.delete(cacheToDelete);
      }));
    }).then(() => self.clients.claim())
  );
});

// The fetch handler serves responses for same-origin resources from a cache.
// If no response is found, it populates the runtime cache with the response
// from the network before returning it to the page.
self.addEventListener('fetch', event => {
  // Skip cross-origin requests, like those for Google Analytics.
  if (event.request.url.startsWith(self.location.origin)) 
  {
    if (event.request.url.startsWith(self.location.origin+'/rss') || event.request.url.startsWith(self.location.origin+'/admin'))
    {
        event.respondWith(
            fetch(event.request).then(response => {
                return caches.open(RUNTIME).then(cache => {
                if (event.request.method=='POST')
                {
                    console.log(event.request.url);
                    if (event.request.url.startsWith(self.location.origin+'/rss'))
                    {
                        SECURE_URLS.forEach(function(url) {
                            cacheSecure(cache,url);
                            console.log(url);
                        });
                    }
                    return response;
                }
                else
                {
                    // Put a copy of the response in the runtime cache.
                    return cache.put(event.request, response.clone()).then(() => {
                        return response;
                    }).catch(e => {
                        console.log(e);
                    });
                }
                });
            }).catch(e => {
                console.log("offline");
                console.log(e);
                if (event.request.url.endsWith('/rss') || event.request.url.endsWith('/rss/'))
                {
                    return caches.match('/rss/base');
                }
                else
                {
                    return caches.match(event.request);
                }
            })
    
        );
    }
    else
    {
        event.respondWith(
          caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }

            return caches.open(RUNTIME).then(cache => {
              return fetch(event.request).then(response => {
                // Put a copy of the response in the runtime cache.
                return cache.put(event.request, response.clone()).then(() => {
                  return response;
                });
              });
            });
          })
        );
    }
  }
});

