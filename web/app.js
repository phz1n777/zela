import { CATEGORIAS, STATUS, EXPLICA_STATUS, textoSugestao, dataHora, api, el } from "/comum.js";

const $ = (id) => document.getElementById(id);
const passos = { relato: $("passo-relato"), confirmar: $("passo-confirmar"), protocolo: $("passo-protocolo") };
let relatoAtual = null; // resposta do POST, com o confirm_token (só em memória)
let coordenadas = null;

function mostrar(nome) {
  for (const [k, sec] of Object.entries(passos)) sec.classList.toggle("escondido", k !== nome);
  passos[nome].focus?.();
  passos[nome].scrollIntoView({ behavior: "smooth", block: "start" });
}

function erro(alvo, mensagem) {
  const caixa = $(alvo);
  caixa.textContent = mensagem || "";
  caixa.classList.toggle("escondido", !mensagem);
}

// Categorias do formulário de envio
for (const [valor, rotulo] of Object.entries(CATEGORIAS)) {
  $("categoria").append(el("option", { value: valor }, rotulo));
}

// Prévia da foto
$("foto").addEventListener("change", () => {
  const arquivo = $("foto").files[0];
  const previa = $("previa");
  if (previa.src) URL.revokeObjectURL(previa.src);
  if (arquivo) {
    previa.src = URL.createObjectURL(arquivo);
    previa.classList.remove("escondido");
  } else {
    previa.classList.add("escondido");
  }
});

// Localização (opcional): só as coordenadas, sem guardar no aparelho
$("usar-gps").addEventListener("click", () => {
  const estado = $("gps-estado");
  if (!("geolocation" in navigator)) {
    estado.textContent = "Este aparelho não informa a localização. Digite o endereço acima.";
    return;
  }
  estado.textContent = "Obtendo localização…";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      coordenadas = { latitude: pos.coords.latitude.toFixed(6), longitude: pos.coords.longitude.toFixed(6) };
      estado.textContent = `Localização anexada (precisão de cerca de ${Math.round(pos.coords.accuracy)} m). Continue preenchendo o endereço ou a referência.`;
    },
    () => { estado.textContent = "Não foi possível obter a localização. Digite o endereço acima."; },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
  );
});

// Passo 1: envio
$("form-relato").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  erro("erro-relato", "");
  const foto = $("foto").files[0];
  const local = $("local").value.trim();
  if (!foto) return erro("erro-relato", "Escolha ou tire uma foto do dano."), $("foto").focus();
  if (foto.size > 5 * 1024 * 1024) return erro("erro-relato", "A foto é maior que 5 MB. Tire outra ou reduza o tamanho.");
  if (local.length < 3) return erro("erro-relato", "Informe onde fica o problema."), $("local").focus();

  const dados = new FormData();
  dados.append("photo", foto);
  dados.append("location", local);
  dados.append("description", $("descricao").value.trim());
  if ($("categoria").value) dados.append("category", $("categoria").value);
  if (coordenadas) {
    dados.append("latitude", coordenadas.latitude);
    dados.append("longitude", coordenadas.longitude);
  }

  const botao = $("enviar");
  botao.disabled = true;
  botao.textContent = "Enviando e analisando a foto…";
  try {
    relatoAtual = await api("/api/reports", { method: "POST", body: dados });
    prepararConfirmacao(relatoAtual);
    mostrar("confirmar");
  } catch (e) {
    erro("erro-relato", e.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Enviar relato";
  }
});

function prepararConfirmacao(r) {
  $("sugestao").textContent = textoSugestao(r);
  const grupo = $("opcoes-categoria");
  grupo.querySelectorAll("label").forEach((l) => l.remove());
  for (const [valor, rotulo] of Object.entries(CATEGORIAS)) {
    grupo.append(el("label", {},
      el("input", { type: "radio", name: "categoria-final", value: valor, checked: valor === r.category, required: true }),
      el("span", {}, rotulo, valor === "dano_na_pista" && r.cv_label === "dano_na_pista" ? " (sugestão do sistema)" : ""),
    ));
  }
}

// Passo 2: confirmação
$("form-confirmar").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  erro("erro-confirmar", "");
  const escolhida = document.querySelector('input[name="categoria-final"]:checked');
  if (!escolhida) return erro("erro-confirmar", "Escolha uma categoria.");
  try {
    const r = await api(`/api/reports/${relatoAtual.id}/confirmation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category: escolhida.value, confirm_token: relatoAtual.confirm_token }),
    });
    relatoAtual = null; // o token não é mais necessário
    $("numero-protocolo").textContent = r.id;
    $("resumo-protocolo").textContent = `${CATEGORIAS[r.category]} em ${r.location}. Status: ${STATUS[r.status]}.`;
    $("protocolo").value = r.id;
    mostrar("protocolo");
  } catch (e) {
    erro("erro-confirmar", e.status === 409 ? "Este relato já foi confirmado." : e.message);
  }
});

$("novo-relato").addEventListener("click", () => {
  $("form-relato").reset();
  $("previa").classList.add("escondido");
  $("gps-estado").textContent = "";
  coordenadas = null;
  mostrar("relato");
});

// Acompanhar
$("form-acompanhar").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const saida = $("resultado-acompanhar");
  const numero = $("protocolo").value.trim();
  if (!numero) return;
  saida.replaceChildren(el("p", {}, "Consultando…"));
  try {
    const r = await api(`/api/reports/${encodeURIComponent(numero)}`);
    saida.replaceChildren(
      el("p", {}, el("span", { class: `selo ${r.status}` }, STATUS[r.status]), " ", EXPLICA_STATUS[r.status]),
      el("p", {}, `${CATEGORIAS[r.category] ?? r.category} em ${r.location}, enviado em ${dataHora(r.created_at)}.`),
      r.service_order ? el("p", {}, `Ordem de serviço: ${r.service_order}`) : null,
    );
  } catch (e) {
    saida.replaceChildren(el("p", { class: "cartao falha", role: "alert" }, e.message));
  }
});
