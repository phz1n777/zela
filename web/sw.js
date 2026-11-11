// Service worker do Zela: guarda só a "casca" do app para abrir com internet fraca.
// Respostas da API (/api, /robo) nunca entram no cache: status e fotos sempre vêm do servidor.
const VERSAO = "zela-v1";
const CASCA = ["/", "/index.html", "/painel.html", "/estilo.css", "/comum.js", "/app.js", "/painel.js", "/icone.svg", "/manifest.webmanifest"];

self.addEventListener("install", (ev) => {
  ev.waitUntil(caches.open(VERSAO).then((c) => c.addAll(CASCA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (ev) => {
  ev.waitUntil(
    caches.keys()
      .then((chaves) => Promise.all(chaves.filter((k) => k !== VERSAO).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (ev) => {
  const url = new URL(ev.request.url);
  if (ev.request.method !== "GET" || url.origin !== location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/robo/") || url.pathname === "/metrics") return;
  // Rede primeiro (versão nova), cache como reserva quando estiver offline.
  ev.respondWith(
    fetch(ev.request)
      .then((resp) => {
        if (resp.ok) {
          const copia = resp.clone();
          caches.open(VERSAO).then((c) => c.put(ev.request, copia));
        }
        return resp;
      })
      .catch(() => caches.match(ev.request).then((r) => r || caches.match("/"))),
  );
});
