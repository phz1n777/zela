# Roteiro do pitch: 6 blocos em 5 minutos (formato oficial)

> Segue o roteiro do enunciado de BI & Startup Development (prof. Henio Scheidt). Equipe: **Pedro** e **Joseh**. **Os dois precisam aparecer e falar.** A demo tem que ser na **URL pública**, sem telas falsas. Tempo máximo: **5:00**.

URL do MVP: https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io

## Rubrica que este roteiro cobre

| Critério | Pontos | Onde aparece |
| --- | --- | --- |
| Lean Canvas: 9 blocos, o que foi validado desde o CP1 e o que mudou | 2,0 | Bloco 4 |
| Modelo de negócio: valor, receita e preço, canais, métricas, "a conta fecha" | 2,5 | Bloco 4 |
| Narrativa: problema, cidadão, solução e impacto, com todos | 2,5 | Blocos 1, 2, 5 e 6 |
| Demo ponta a ponta na URL pública | 3,5 | Bloco 3 |
| Valor entregue com evidência (uso real, teste documentado ou antes/depois) | 3,5 | Blocos 3 e 5 |

## Decisões que precisam ser tomadas antes de gravar

Estas três coisas mudam o que se pode mostrar. O roteiro abaixo já traz o caminho **honesto** para cada uma.

| # | Decisão | Situação hoje | Caminho recomendado |
| --- | --- | --- | --- |
| D1 | **A IA sugere "dano na pista"?** | O MVP no ar roda **sem o modelo** (o `best.pt` ainda não foi treinado). A opção "Deixar o sistema sugerir" não devolve sugestão. | **A:** se o Joseh treinar a tempo, eu refaço a imagem com o YOLO e a demo mostra a sugestão com a confiança. **B:** sem o modelo, escolher a categoria na lista e dizer que a sugestão automática está em treino e aparece no vídeo de Visão. **Não** mostrar sugestão que não existe. |
| D2 | **O robô UiPath faz parte da demo?** | O robô do Joseh opera o portal local dele, não o MVP no Azure. O MVP não muda de status sozinho. | Mostrar o fluxo do MVP **até "Em triagem"** e, em seguida, o corte do vídeo do robô **dizendo claramente** que ele opera o portal de demonstração. Só mostrar "Encaminhado" no painel se o robô realmente o gravar pela API. |
| D3 | **Território piloto** | **Decidido:** o bairro Jardim das Belezas, onde mora um dos integrantes. | Usar "bairro Jardim das Belezas" no vídeo, no PDF e na ficha. Nas fotos, nada de fachada ou número de casa à vista. |

## Os 6 blocos, com o texto sugerido

Os textos são rascunhos: ajustem às suas palavras e **só afirmem o que está documentado**. Cerca de 140 palavras por minuto.

### 1. Problema e cidadão · 0:00–0:45 · Pedro

**Mostrar:** uma foto real de um buraco no território piloto (sem rosto e sem placa).

> "Quem anda pelo meu bairro a pé, de bicicleta, de carro ou de cadeira de rodas já passou por um buraco assim. O que acontece depois? O aviso vai para o WhatsApp ou para um e-mail, sem foto, sem o local exato. A administração recebe o mesmo aviso três vezes, manda a equipe ao lugar errado, e quem avisou nunca sabe se alguém viu."

Se citarem dados das conversas, digam que as entrevistas foram **simuladas** (autorizadas pelo professor). Não apresentem como pesquisa real.

### 2. Solução e proposta de valor · 0:45–1:30 · Pedro

**Mostrar:** a tela inicial do app no celular.

> "O Zela transforma uma foto e um local em uma ocorrência que dá para acompanhar. Você fotografa o dano, confirma e recebe um número de protocolo. Não pedimos nome, telefone nem e-mail. O sistema sugere a categoria, mas quem confirma é a pessoa, porque a classificação apoia a triagem e não decide sozinha."

Se for o caminho B da decisão D1, troquem "o sistema sugere" por "o cidadão escolhe a categoria, e a sugestão automática por foto está em treinamento".

### 3. Demo do MVP · 1:30–3:00 · Pedro (app e painel) e Joseh (IA e dados)

Passo a passo na URL pública, com os rótulos reais das telas:

| Passo | Quem | O que fazer | O que dizer |
| --- | --- | --- | --- |
| 1 | Pedro | No celular, abrir a URL. Ver **"Relatar um dano na via"**. | "Pela rede móvel, sem instalar nada." |
| 2 | Pedro | Anexar a **foto**, preencher **Onde fica**. Opcional: **Usar minha localização**. | "Uma foto e um endereço aproximado." |
| 3 | Pedro | **Tipo de problema**: deixar o sistema sugerir (caminho A) ou escolher "Buraco ou dano na pista" (caminho B). Clicar **Enviar relato**. | "A sugestão aparece com a confiança, e eu confirmo." (só no caminho A) |
| 4 | Pedro | Mostrar o **protocolo** e o status **Recebido**. Em **Acompanhar um relato**, digitar o número e **Consultar**. | "Esse número acompanha o relato do começo ao fim." |
| 5 | Pedro | Abrir o **painel** (`/painel.html`). Colar o token **antes de gravar** e clicar **Usar token**. Mudar o status do relato para **Em triagem**. | "A equipe vê foto, local e status e libera o relato para o próximo passo." |
| 6 | Joseh | Corte de 10 a 20 s do robô UiPath. | "O robô registra a ordem de serviço. Aqui ele opera o portal de demonstração; a integração com um portal real depende de autorização." (decisão D2) |
| 7 | Pedro | Voltar ao app e **Consultar** o protocolo: mostrar o novo status. | "O cidadão vê o que aconteceu com o relato." |

Mantenham um relógio visível: mede o tempo do relato até a triagem. **Não digam** "a prefeitura recebe na hora".

### 4. Modelo de negócio · 3:00–4:00 · Pedro

**Mostrar:** o Lean Canvas de 9 blocos e a conta (do PDF de BI).

> "O cidadão usa de graça. Quem paga é a administração do território, com uma assinatura mensal: R$ 400 para campus e parque empresarial, R$ 200 para condomínio. A nuvem custa entre 30 e 60 dólares por mês, cerca de R$ 250. Com R$ 400, um território já cobre esse custo e a implantação se paga em cerca de dois meses e meio. É uma hipótese, que ajustamos em entrevistas simuladas. No caminho, mudamos duas coisas: reduzimos a IA a uma única categoria, sempre com confirmação humana, e passamos a cobrar por segmento."

Números iguais aos do PDF de BI e dos slides: nuvem US$ 30–60/mês (≈ R$ 250, pior caso R$ 330), preço R$ 400 (campus e parque) e R$ 200 (condomínio), implantação R$ 660 paga em ~2,4 meses. A estimativa de nuvem vem de `docs/custos_e_lgpd.md`.

### 5. Impacto e ODS · 4:00–4:30 · Joseh

> "Medimos relatos que chegam ao painel, a porcentagem de sugestões confirmadas e o tempo do relato até a triagem. Contribuímos para os ODS 11, cidades sustentáveis, e 9, infraestrutura, e abrimos caminho para o ODS 13, com o mapeamento futuro de pontos de alagamento. Para outro território, é a mesma plataforma com novas placas."

**Não** digam que reduziram buracos. Sem dados de reparo, não dá para afirmar.

### 6. Time e próximos passos · 4:30–5:00 · os dois, uma frase cada

> Pedro: "Eu fiz o aplicativo, a nuvem e a segurança." Joseh: "Eu fiz os dados, a visão e a automação." Juntos: "Falta validar com um comprador real, treinar o modelo com fotos locais e integrar a um portal oficial. Pedimos um território para um piloto de quatro semanas."

Encerrem com a URL na tela. Ajustem as frases ao que cada um fez.

## Antes de gravar (pré-voo)

**O ambiente do Azure foi pausado para não gerar cobrança.** Antes de gravar ou ensaiar, retomem: a seção "Pausar e retomar" do [infra/README.md](../infra/README.md) traz os 3 comandos (ligar o Postgres, voltar o app a 1 réplica e reativar o alerta). O Postgres leva alguns minutos para subir.

Depois, rodem `docs/pitch_preflight.sh` (confere URL, página, painel, portal de demonstração e a lista de relatos) e depois a lista abaixo.

- [ ] **Banco com dados.** O banco do MVP está vazio. Carreguem dados de demonstração (`python -m app.demo --quantidade 40`, rodado dentro do contêiner) para o painel não aparecer vazio. Eles vêm marcados como **demonstração**. Peçam isso a mim, pois mexe no banco de produção.
- [ ] **Um relato real feito no dia**, sem rosto nem placa na foto.
- [ ] URL testada **no celular pela rede móvel**, e o ambiente no ar até o fim da correção (cerca de 26/11).
- [ ] **Tokens e senhas fora da tela.** Colem o token de operador no painel **antes** de gravar e corte esse trecho, ou usem a aba já autenticada. O painel guarda o token só na aba.
- [ ] Corte de 10 a 20 s do robô UiPath, com a fala da decisão D2.
- [ ] Números do bloco 4 **iguais aos do PDF** (nuvem ≈ R$ 250, preço R$ 400/R$ 200, 2,4 meses). Já estão alinhados no PDF e nos slides.
- [ ] Vídeo em **link público** (YouTube não listado, ou Drive com acesso a qualquer pessoa com o link), com os dois integrantes aparecendo e falando.
- [ ] Cronômetro: no máximo **5:00**. Ensaiem uma vez cronometrando.
- [ ] Depois de gravar, coloquem o link do vídeo em `docs/entrega_bi/links.json` e rodem `python3 gerar_pdf.py` na pasta `docs/entrega_bi`.

## Frases a evitar

- "A IA detecta qualquer problema da rua." Ela só sugere dano na pista, com confirmação (e só quando o modelo estiver treinado).
- "A prefeitura recebe na hora." O encaminhamento vai para uma fila de demonstração.
- "Já temos clientes" ou "custa R$ X". Só digam se estiver documentado nas conversas.
- "Reduzimos os buracos." Sem dado de reparo, não dá para afirmar.
- "As entrevistas mostraram…" sem dizer que foram **simuladas**.
