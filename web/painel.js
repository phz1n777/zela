import { CATEGORIAS, STATUS, textoSugestao, dataHora, api, el } from "/comum.js";

const $ = (id) => document.getElementById(id);
const CHAVE_TOKEN = "zela-operador";

function lerToken() {
  try { return sessionStorage.getItem(CHAVE_TOKEN) || ""; } catch { return ""; }
}
function gravarToken(valor) {
  try { valor ? sessionStorage.setItem(CHAVE_TOKEN, valor) : sessionStorage.removeItem(CHAVE_TOKEN); } catch { /* sem storage */ }
}
let token = lerToken();

function atualizarEstadoToken() {
  $("estado-token").textContent = token ? "Token em uso nesta aba." : "Sem token: o painel fica só para leitura.";
}

for (const [v, r] of Object.entries(STATUS)) $("f-status").append(el("option", { value: v }, r));
for (const [v, r] of Object.entries(CATEGORIAS)) $("f-categoria").append(el("option", { value: v }, r));

$("form-token").addEventListener("submit", (ev) => {
  ev.preventDefault();
  token = $("token").value.trim();
  gravarToken(token);
  $("token").value = "";
  atualizarEstadoToken();
  carregar();
});

$("filtros").addEventListener("submit", (ev) => { ev.preventDefault(); carregar(); });

async function mudarStatus(id, status, botao) {
  botao.disabled = true;
  try {
    await api(`/api/reports/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", "x-operador-token": token },
      body: JSON.stringify({ status }),
    });
    await carregar(`Relato ${id} agora está como ${STATUS[status].toLowerCase()}.`);
  } catch (e) {
    $("estado-lista").textContent = e.status === 401 ? "Token de operador inválido." : e.message;
    botao.disabled = false;
  }
}

function cartao(r) {
  const acoes = [];
  if (token && r.status === "recebido") {
    acoes.push(el("button", { type: "button", class: "botao", onclick: (e) => mudarStatus(r.id, "em_triagem", e.currentTarget) }, "Iniciar triagem"));
  }
  if (token && (r.status === "recebido" || r.status === "em_triagem")) {
    acoes.push(el("button", { type: "button", class: "botao perigo", onclick: (e) => mudarStatus(r.id, "descartado", e.currentTarget) }, "Descartar"));
  }
  const confirmacao = r.cv_reviewed ? "Confirmada pelo cidadão" : "Ainda não confirmada";
  return el("li", { class: "cartao relato" },
    el("img", { src: `/api/reports/${r.id}/image`, alt: `Foto do relato ${r.id}`, loading: "lazy" }),
    el("h3", {}, `Protocolo ${r.id} · ${CATEGORIAS[r.category] ?? r.category}`),
    el("div", {},
      el("span", { class: `selo ${r.status}` }, STATUS[r.status]), " ",
      r.source === "demo" ? el("span", { class: "selo demo" }, "demonstração") : null,
    ),
    el("dl", {},
      el("dt", {}, "Local"), el("dd", {}, r.location),
      el("dt", {}, "Enviado"), el("dd", {}, dataHora(r.created_at)),
      el("dt", {}, "Sugestão"), el("dd", {}, textoSugestao(r)),
      el("dt", {}, "Categoria"), el("dd", {}, confirmacao),
      r.description ? [el("dt", {}, "Descrição"), el("dd", {}, r.description)] : null,
      r.service_order ? [el("dt", {}, "Ordem"), el("dd", {}, r.service_order)] : null,
    ),
    acoes.length ? el("div", { class: "acoes" }, acoes) : null,
  );
}

async function carregar(aviso = "") {
  const params = new URLSearchParams();
  if ($("f-status").value) params.set("status", $("f-status").value);
  if ($("f-categoria").value) params.set("category", $("f-categoria").value);
  if ($("f-origem").value) params.set("source", $("f-origem").value);
  $("estado-lista").textContent = "Carregando…";
  try {
    const [relatos, todos] = await Promise.all([api(`/api/reports?${params}`), api("/api/reports?limit=500")]);
    $("lista").replaceChildren(...relatos.map(cartao));
    const total = relatos.length ? `${relatos.length} relato(s).` : "Nenhum relato com esses filtros.";
    $("estado-lista").textContent = aviso ? `${aviso} ${total}` : total;
    const contagem = Object.fromEntries(Object.keys(STATUS).map((s) => [s, 0]));
    for (const r of todos) contagem[r.status] = (contagem[r.status] ?? 0) + 1;
    $("resumo").replaceChildren(
      el("li", {}, el("strong", {}, String(todos.length)), "no total"),
      ...Object.entries(STATUS).map(([s, rot]) => el("li", {}, el("strong", {}, String(contagem[s])), rot)),
    );
  } catch (e) {
    $("estado-lista").textContent = e.message;
  }
}

atualizarEstadoToken();
carregar();
