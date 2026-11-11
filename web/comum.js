// Rótulos e chamadas à API usados pelo app do cidadão e pelo painel.

export const CATEGORIAS = {
  dano_na_pista: "Buraco ou dano na pista",
  calcada: "Calçada danificada",
  bueiro: "Bueiro ou boca de lobo",
  lixo: "Lixo ou entulho",
  iluminacao: "Iluminação pública",
  outro: "Outro problema",
};

export const STATUS = {
  recebido: "Recebido",
  em_triagem: "Em triagem",
  encaminhado: "Encaminhado",
  descartado: "Descartado",
};

export const EXPLICA_STATUS = {
  recebido: "O relato foi salvo e recebeu protocolo.",
  em_triagem: "A equipe está revisando foto, local e categoria.",
  encaminhado: "O relato virou ordem de serviço na fila de manutenção de teste.",
  descartado: "O relato estava duplicado, fora do território ou sem informação suficiente.",
};

export function textoSugestao(r) {
  if (r.cv_label === "dano_na_pista") {
    return `O sistema identificou um possível dano na pista (confiança de ${Math.round(r.cv_confidence * 100)}%).`;
  }
  if (r.cv_label === "sem_deteccao") {
    return "O sistema não identificou dano na pista nesta foto.";
  }
  return "A análise automática da foto não está disponível agora.";
}

export function dataHora(iso) {
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export async function api(caminho, opcoes = {}) {
  let resposta;
  try {
    resposta = await fetch(caminho, opcoes);
  } catch {
    throw new Error("Sem conexão. Verifique a internet e tente de novo.");
  }
  if (!resposta.ok) {
    let detalhe = "";
    try {
      const corpo = await resposta.json();
      detalhe = typeof corpo.detail === "string" ? corpo.detail : "";
    } catch { /* corpo sem JSON */ }
    const erro = new Error(mensagemErro(resposta.status, detalhe));
    erro.status = resposta.status;
    throw erro;
  }
  return resposta.json();
}

function mensagemErro(status, detalhe) {
  if (status === 413) return "A foto é maior que 5 MB. Tire outra ou reduza o tamanho.";
  if (status === 415) return "Envie uma foto em JPEG, PNG ou WebP.";
  if (status === 404) return "Protocolo não encontrado.";
  if (status === 422) return "Confira os campos: algum valor está fora do formato esperado.";
  if (status === 401) return "Token inválido.";
  return detalhe ? `Não foi possível concluir: ${detalhe}.` : "Algo deu errado. Tente de novo em instantes.";
}

export function el(tag, atributos = {}, ...filhos) {
  const no = document.createElement(tag);
  for (const [k, v] of Object.entries(atributos)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") no.className = v;
    else if (k.startsWith("on")) no.addEventListener(k.slice(2), v);
    else no.setAttribute(k, v === true ? "" : v);
  }
  for (const f of filhos.flat()) {
    if (f !== null && f !== undefined && f !== false) no.append(f);
  }
  return no;
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => {}));
}
