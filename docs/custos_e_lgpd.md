# Custos e proteção de dados pessoais

Documento da disciplina de Secure DevOps & Cloud. Descreve o que o Zela custa para rodar e que dados pessoais trata. Vale para o piloto (MVP), não para produção.

## 1. Custos

### Recursos no Azure (Azure for Students, região `spaincentral`)

| Recurso | Configuração | Observação |
| --- | --- | --- |
| Container App | 0,5 vCPU, 1 GiB, 1 a 2 réplicas, HTTPS público | Maior parcela variável: paga por uso, com réplica mínima ligada |
| PostgreSQL Flexible Server | Burstable B1ms, 32 GB, backup de 7 dias | Custo fixo enquanto o servidor existir |
| Container Registry | Basic | Custo fixo pequeno |
| Log Analytics | PerGB2018, retenção de 30 dias | Custo pelo volume de logs; baixo no piloto |
| Alerta e grupo de ação (Azure Monitor) | 1 alerta de métrica, e-mail | Praticamente sem custo |
| Identidade gerenciada, grupo de recursos | n/a | Sem custo |

### Estimativa

**Entre US$ 30 e US$ 60 por mês** com o piloto ligado o tempo todo. É uma estimativa feita a partir dos preços públicos de cada recurso, **não** um valor medido: a consulta de consumo pelo CLI não retornou dados e o saldo real deve ser conferido em *Cost Management + Billing* no portal. (Uma primeira estimativa, de US$ 25 a 30, foi otimista porque desconsiderava a réplica sempre ligada e o armazenamento do banco.)

O crédito do Azure for Students (cerca de US$ 100) cobre as semanas até a entrega. Depois dela, o ambiente é **destruído**:

```bash
cd infra/terraform && terraform destroy
```

### Como reduzir

- Parar o Container App ou usar `min_replicas = 0`, aceitando a latência da primeira requisição.
- Desligar o servidor Postgres quando não houver demonstração.
- Manter a retenção de logs em 30 dias ou menos.
- Em produção: reservar capacidade e usar o plano Basic do ACR só se necessário.

O GitHub Actions é gratuito para repositório público, e o OpenRouter usa modelo gratuito (`:free`), sem custo no piloto.

## 2. Dados pessoais (LGPD, Lei 13.709/2018)

### Que dados o Zela trata

| Dado | Origem | Onde fica | Pessoal? |
| --- | --- | --- | --- |
| Foto da via | Cidadão, no relato | Disco do contêiner (`/app/uploads`) | Pode ser: pode conter pessoas, placas de veículos ou fachadas |
| Localização (texto e latitude/longitude) | Cidadão | Postgres, tabela `reports` | Pode ser: associada a quem relata, é dado de localização |
| Descrição livre | Cidadão | Postgres | Pode ser: o texto é livre e pode conter nome ou telefone |
| Categoria, status, ordem de serviço | Sistema e triagem | Postgres | Não |
| Token de confirmação | Sistema | Postgres | Não; identifica o relato, não a pessoa |

**O que não coletamos:** nome, CPF, telefone, e-mail ou login do cidadão. O relato é anônimo por desenho (ver `api/app/db.py`). Isso reduz bastante o risco, mas **não elimina** o tratamento de dados pessoais, porque foto, localização e texto livre podem identificar alguém indiretamente.

### Princípios aplicados

- **Finalidade e necessidade:** os dados servem só para registrar e encaminhar o dano na via. Nada é usado para outro fim, e nenhum dado é vendido.
- **Minimização:** sem cadastro, sem rastreamento de usuário. A foto é limitada a JPEG, PNG ou WebP de até 5 MB, tem os metadados (EXIF e GPS) removidos no upload e recebe um nome gerado pelo servidor, nunca o nome enviado.
- **Segurança:** HTTPS na borda; segredos (tokens e senha do banco) em *secrets* do Container App e fora do git; usuário não-root no contêiner; ações de triagem e do robô protegidas por token; Gitleaks, Semgrep e Trivy rodados sobre o código e a imagem.
- **Humano no controle:** a IA só sugere a categoria, e o cidadão confirma ou corrige antes da triagem.
- **Dados de demonstração:** os registros simulados são marcados com `source = demo` e removíveis com `python -m app.demo --apagar`.

### Operadores e transferência internacional

| Terceiro | Papel | Dados enviados |
| --- | --- | --- |
| Microsoft Azure (Espanha) | Hospedagem e banco | Todos os dados do relato. Região da União Europeia, então há transferência internacional (art. 33 da LGPD) |
| OpenRouter | LLM do FonteBot | Apenas as **dúvidas de uso** do cidadão. Fotos e relatos não são enviados |

### Direitos do titular

Como o relato é anônimo, o sistema não consegue localizar os dados de uma pessoa pelo nome. Para o piloto, quem quiser a exclusão informa o **protocolo** (o id do relato). Ainda não existe rota de exclusão: ver "Pendências".

## 3. Riscos conhecidos e o que ainda não foi tratado

Estas lacunas existem hoje no MVP e devem ser consideradas antes de qualquer uso real:

1. **Leitura pública.** `GET /api/reports`, `GET /api/reports/{id}` e a foto não exigem login, porque o painel da demo os consome. Qualquer pessoa com a URL pode listar relatos, localizações e fotos. Mitigação futura: exigir o token do operador na listagem e na foto, e expor publicamente só o protocolo de cada relato.
2. ~~Metadados da foto (EXIF)~~ **Tratado.** A API remove EXIF (GPS e modelo do aparelho), XMP, comentários e perfil de cor antes de gravar a foto, aplicando a orientação nos pixels (`api/app/services/imagem.py`, com testes). Arquivos que não são imagens de verdade são recusados com erro 400. Fotos enviadas antes desta mudança não foram reprocessadas.
3. **Texto livre.** O campo de descrição pode receber nome ou telefone. Mitigação futura: aviso no formulário para não incluir dados pessoais e revisão pela triagem.
4. **Sem exclusão nem retenção definida.** Não há rota para apagar um relato nem prazo de retenção. Proposta: apagar fotos e relatos encerrados após 12 meses e criar a rota de exclusão para o operador.
5. **Fotos em disco efêmero.** As fotos somem a cada novo deploy do contêiner, o que é uma falha de disponibilidade e, por acaso, limita a retenção. Mitigação futura: Azure Files com política de retenção.
6. **`/metrics` público.** Expõe só contadores agregados, sem dado pessoal, mas deve ser restringido em produção.
7. **Banco com acesso público restrito.** O Postgres aceita apenas conexões originadas em serviços do Azure, com senha e TLS. Para produção, usar rede privada.
8. **Estado do Terraform local.** O *state* guarda a senha do banco em texto. Fica fora do git, em `terraform.tfstate`, e deve ir para um backend remoto criptografado em produção.

## 4. Responsabilidades

- **Controlador (piloto):** a equipe do projeto, até que um território parceiro assuma o papel.
- **Encarregado (DPO):** não designado. Em produção, o parceiro precisa nomear um e publicar o canal de contato.
- **Base legal prevista:** execução de políticas públicas e legítimo interesse (arts. 7º, III e IX), a validar com o parceiro. Para o piloto, o consentimento é dado pelo próprio ato de enviar o relato, após o aviso na tela.
