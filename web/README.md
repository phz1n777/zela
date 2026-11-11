# web: app do cidadão e painel (PWA)

HTML, CSS e JavaScript puros, sem etapa de build. A própria API serve estes arquivos em `/`, então o MVP inteiro sobe num container só e responde numa única URL.

| Página | Para quem | O que faz |
| --- | --- | --- |
| `/` ([`index.html`](index.html), [`app.js`](app.js)) | Cidadão | 1. Envia foto, local, descrição e, se quiser, a localização do GPS e a categoria. 2. Mostra a sugestão da visão e pede a confirmação ou correção. 3. Mostra o protocolo. Também consulta o status pelo número do protocolo |
| `/painel.html` ([`painel.js`](painel.js)) | Equipe de triagem e demo do pitch | Resumo por status, filtros por status, categoria e origem, cartões com foto, local, sugestão e confirmação. Com o token de operador, inicia a triagem ou descarta o relato |

Arquivos de apoio: [`comum.js`](comum.js) (rótulos e chamadas à API), [`estilo.css`](estilo.css), [`manifest.webmanifest`](manifest.webmanifest), [`sw.js`](sw.js) e [`icone.svg`](icone.svg).

## Decisões

- **Sem conta e sem dados pessoais.** O formulário pede só a foto, o local e a descrição. O GPS é opcional e só é lido quando a pessoa toca no botão.
- **Confirmação humana.** O `confirm_token` devolvido no envio fica só na memória da página e é descartado depois de confirmar.
- **Token de operador.** Fica no `sessionStorage` da aba e some ao fechá-la. Sem token, o painel fica só para leitura.
- **PWA.** O service worker guarda só a "casca" do app para abrir com internet fraca. Respostas da API nunca entram no cache.
- **Segurança.** A API envia Content-Security-Policy sem scripts nem estilos inline, `nosniff`, `no-referrer` e Permissions-Policy (câmera e localização só no próprio site).
- **Acessibilidade.** Rótulos e dicas ligados aos campos, mensagens de erro com `role="alert"`, link "Pular para o conteúdo", foco visível, botões com 48 px de altura, modo escuro automático e lista no lugar de mapa.

## Rodar localmente

```bash
cd api
OPERADOR_TOKEN=dev-operador ROBO_TOKEN=dev-robo .venv/bin/uvicorn app.main:app --reload
```

Abra http://localhost:8000 para o app do cidadão e http://localhost:8000/painel.html para o painel.

## Limitações conhecidas

- Não há mapa nem fila offline de envios: sem internet, o envio falha com uma mensagem clara.
- O ícone é só SVG. Alguns Android antigos pedem PNG de 192 e 512 px para instalar o app.
- A lista pública mostra as fotos. Por isso o formulário pede para evitar rostos e placas, e a triagem deve descartar fotos com esse problema.
