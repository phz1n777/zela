#!/usr/bin/env bash
# Pré-voo da gravação do pitch: confere se o MVP no ar está pronto para a demo.
# Só faz leituras (GET). Não precisa de token nem de senha.
# Uso: bash docs/pitch_preflight.sh [URL]
URL="${1:-https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io}"
falhas=0

confere() { # descrição, comando que deve devolver 0
  if eval "$2" >/dev/null 2>&1; then printf '  ok     %s\n' "$1"; else printf '  FALHOU %s\n' "$1"; falhas=$((falhas+1)); fi
}
codigo() { curl -s -o /dev/null -m 20 -w '%{http_code}' "$URL$1"; }

echo "Pré-voo em $URL"
confere "/health responde ok"                 "curl -fsS -m 20 $URL/health | grep -q '\"ok\"'"
confere "app do cidadão abre (200)"           "[ \"\$(codigo /)\" = 200 ]"
confere "painel abre (200)"                   "[ \"\$(codigo /painel.html)\" = 200 ]"
confere "portal de demonstração pede login"   "[ \"\$(codigo /portal-demo/)\" = 200 ]"
confere "API lista relatos (200)"             "[ \"\$(codigo /api/reports)\" = 200 ]"
confere "relato inexistente dá 404, não 500"  "[ \"\$(codigo /api/reports/999999999999)\" = 404 ]"
confere "/metrics responde"                   "[ \"\$(codigo /metrics)\" = 200 ]"

n=$(curl -s -m 20 "$URL/api/reports?limit=500" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d), sum(1 for r in d if r.get("source")=="demo"))' 2>/dev/null)
set -- $n
echo "  relatos no banco: ${1:-?} (demonstração: ${2:-?})"
if [ "${1:-0}" -eq 0 ] 2>/dev/null; then echo "  AVISO  banco vazio: carregue os dados de demonstração antes de gravar"; fi

echo; echo "Sugestão automática (modelo de visão):"
if curl -s -m 20 "$URL/api/reports?limit=500" | python3 -c 'import sys,json;d=json.load(sys.stdin);sys.exit(0 if any(r.get("cv_model") for r in d) else 1)' 2>/dev/null; then
  echo "  há relatos com sugestão de modelo (caminho A da decisão D1)"
else
  echo "  nenhum relato com sugestão de modelo (caminho B da decisão D1: o modelo ainda não está no ar)"
fi

echo; [ "$falhas" -eq 0 ] && echo "Tudo certo para gravar." || echo "$falhas verificação(ões) falharam. Resolva antes de gravar."
exit "$falhas"
