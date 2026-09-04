# Diário do projeto — INF0093 (2S/2026)

Registro cronológico das sessões de trabalho. Entrada mais recente primeiro.

---

## 04/09/2026, 11:00 (BRT) — Reorganização de pastas e `.secret` compartilhado

**Quem:** Werner (reorganização) + sessão com Claude Code (ajustes)

### Novo layout

```
eval/
├── .secret              ← chave da Groq, UMA para todos os entregáveis (ignorada pelo git)
├── .secret.example      ← modelo versionado
├── project/             ← proposta (PDD v1/v2) e planejamento_execucao.md
└── release_N/
    ├── requirements/    ← enunciado + template do entregável
    ├── solution/        ← notebook, dados/, etl/, resultados
    └── diary.md         ← este arquivo
```

### O que mudou no notebook por causa disso

- **Loader da chave** (seção 11): procura `.secret` no diretório atual **e em até quatro
  níveis acima** — de `release_N/solution/` acha `eval/.secret`. Vale para qualquer release
  futura sem copiar a chave. Ordem completa: env var → `.secret` → Colab `userdata` → teclado.
- **URL de fallback do dataset** (seção 12): a reorganização quebrou o caminho do GitHub raw
  (`release_1/dados/` → `release_1/solution/dados/`). Corrigido. Continua dependendo do push.
- Só essas duas células de código mudaram; as saídas salvas continuam verdadeiras (a
  mensagem impressa é a mesma). Nenhuma reexecução foi necessária.

### Incidente: `baseline_v1_resultados.json` sobrescrito e restaurado

Rodar o dublê (`etl/test_nb.py`) a partir de `solution/` executou a célula que grava o JSON
e **sobrescreveu o artefato da execução real** com dados do STUB. Restaurado a partir das
saídas salvas do notebook (todos os campos de todos os casos estão lá) e conferido contra o
`RESUMO` impresso: tokens, acertos, abstenções e latências batem. O arquivo carrega um campo
`nota` explicando isso. **Correção definitiva:** o dublê agora grava em
`baseline_v1_resultados.STUB.json` e apaga no fim — não consegue mais tocar no arquivo real.

### Para quem for começar o Entregável 2

Crie `release_2/solution/`, copie a célula de chave da seção 11 do E1 e pronto — a chave já
está em `eval/.secret`. `etl/test_nb.py` (dublê de LLM) continua funcionando a partir de
`solution/`.

---

## 03/09/2026, 21:35 (BRT) — Execução real do baseline (Groq)

**Quem:** Werner (sessão de trabalho com Claude Code)
**Arquivos:** `E1_DallaCosta_Murer_Denzin.ipynb` (agora **com saídas**), `baseline_v1_resultados.json`

### Setup da chave

Chave gratuita da Groq em `release_1/.secret` (formato `GROQ_API_KEY=gsk_…`), **ignorada pelo
git** (`.gitignore` tem `.secret` e `.env`). Modelo em `.secret.example`. A célula da seção 11
procura: env var → `.secret` → Colab `userdata["INF0093-2026-2S"]` → teclado.

### A primeira execução abortou — e isso virou conteúdo

HTTP 400 da Groq: *"attempted to call tool 'json' which was not in request.tools"*. Com o
prompt completo, o `gpt-oss-20b` inventou o nome da ferramenta no modo *tool calling*
(o teste curto passou; o dublê de LLM não pega isso). **Correção:**
`with_structured_output(..., method="json_schema")` — saída estruturada nativa da Groq — e
`baseline()` passou a registrar erro de API como caso falho em vez de derrubar o notebook.

### Resultados (`openai/gpt-oss-20b`, temp 0, prompt v1, 21:28)

| Métrica | Valor | Meta |
|---|---|---|
| Aprovação automática | **11 / 11** | ≥ 8 |
| Abstenções corretas | 3 / 3 | 3 / 3 |
| Erros de execução / parsing | 0 / 0 | ≤ 1 |
| Chamadas ao LLM | 13 (1 por caso) | ≤ 1 por caso |
| Tokens entrada / saída | 17.295 / 7.597 | — |
| Custo estimado | US$ 0,0055 | < 0,05 |
| **Latência mediana** | **11,51 s** (máx. 21,17) | **< 10 s — não atendido** |
| Rubrica manual T12 / T13 | **0 / 0** | — |

### Três achados para o time

1. **T12 é o erro silencioso previsto.** "Melhor município para estudar" → **Uru (SP), média
   741, 1 participante.** Código certo, resposta inútil, confiança total. Os 5 maiores
   `media_geral` sem filtro têm 1, 2, 3, 1 e 1 participantes. É **o** caso para o Validador
   do E2 e para a categoria "filtro implícito" do conjunto ampliado do E4.
2. **Efeito de teto.** Com 11/11, o conjunto automático atual **não consegue mostrar
   melhoria** — só piora. A hipótese da seção 20 foi ajustada: a vantagem da arquitetura
   final terá de aparecer em erro silencioso, ambiguidade e casos mais difíceis. Ao ampliar
   para 25–30 casos, priorizar tipo T12, não tipo T01.
3. **Latência bimodal, sem relação com tokens.** 4 chamadas em 0,5–5 s, 9 em 11–21 s (T02:
   235 tokens/0,51 s; T05: 229 tokens/14,6 s). É fila do plano gratuito, não o modelo — mas
   é o que o usuário sente, e a medição atual não separa os dois. A partir do E2: registrar
   horário e repetir 3× por caso.

Bônus: `gpt-oss-20b` é modelo com raciocínio — ~60% dos tokens de saída são `reasoning`.
Os 7.597 tokens de saída não são texto visível.

### O que **não** falhou (e a gente esperava que falhasse)

T03 aplicou o filtro explícito; T07 encadeou as duas operações; T11 recusou 2019 sem vazar
memória paramétrica; 13/13 templates bem formados.

### Estado da entrega

- [x] Notebook executado do início ao fim, salvo com saídas, 0 erros
- [x] 8 marcadores `[da execução]` preenchidos; rubrica T12/T13 aplicada; checklist completo
- [ ] `git add` + commit + push (inclusive `dados/` — o fallback de download da seção 12
      depende disso) e submissão no Classroom até **07/09**

---

## 03/09/2026, 20:50 (BRT) — Revisão do Entregável 1

**Quem:** Werner (sessão de trabalho com Claude Code)

Revisão do notebook contra o enunciado, o template e a proposta do projeto.

### Bug encontrado e corrigido

`numeros_de` interpretava `0.2868` como milhar pt-BR (`0.286` → 286). Efeito: uma resposta
**correta** ao T06 (correlação) seria reprovada como `texto_fiel=nao`. Entrou quando floats
abaixo de 1 passaram a ter quatro casas decimais, e o veredito do T06 não foi reconferido.
Corrigido: um ponto só é separador de milhar com dois ou mais grupos (`1.234.567`) ou com
vírgula decimal depois (`1.234,56`). Parser testado em 10 casos de borda.

> Lição para o time: **toda mudança na formatação ou na verificação exige rodar os 13 casos
> de novo**, mesmo que pareça cosmética. O dublê de LLM (`test_nb.py`) faz isso em segundos.

### Ajustes de alinhamento

- Seção 1 ganhou um `## Objetivo do sistema` explícito (item 3.4 do enunciado — estava
  implícito no texto).
- Seção 16 passou a nomear `registros` como semente do **log estruturado** previsto na
  proposta (§4, "observabilidade desde a primeira entrega").

### Conferido e OK

- Os 12 itens de especificação do enunciado (3.1–3.12) têm seção correspondente.
- Registro de execução completo: modelo, temperatura, versão do prompt, data, latência
  por caso, chamadas e tokens. Nenhuma chave no notebook.
- 13 casos executam com o dublê; 11 automáticos aprovados com planos corretos.

### Atenção — divergência entre planejamento interno e enunciado

`planejamento_execucao.md` previa para o E1 "grafo LangGraph Planejador → Supervisor →
Loader". O enunciado diz o oposto: o baseline **não deve ser multiagente**. O notebook
segue o **enunciado**; o grafo entra no E2. Vale atualizar o planejamento.

### Pendências (inalteradas)

- Rodar com chave da Groq e salvar com saídas; preencher os 8 marcadores.
- **Commitar e dar push em `dados/`**: o fallback de download da seção 12 aponta para o
  GitHub raw do repositório — sem push, quem abrir no Colab precisa subir o CSV à mão.

---

## 03/09/2026, 20:36 (BRT) — Entregável 1: ETL, dataset e notebook

**Quem:** Werner (sessão de trabalho com Claude Code)
**Onde:** `04_projeto_sistema_multiagentes/eval/release_1/`

### O que foi produzido

| Arquivo | O que é |
|---|---|
| `E1_DallaCosta_Murer_Denzin.ipynb` | Notebook do Entregável 1 — 51 células, 21 seções do template preenchidas |
| `etl/build_dataset.py` | ETL da "Semana 0": ENEM 2023 + 3 APIs do IBGE → artefato leve |
| `dados/enem2023_ibge_municipios.csv` | Artefato pré-processado, 0,59 MB |
| `dados/DICIONARIO.md` | Dicionário de dados + limitações conhecidas |

O `Template_Entregavel_1.ipynb` original **não** foi alterado; o entregável é um arquivo
novo, nomeado conforme a sugestão do enunciado (`E1_sobrenomes.ipynb`).

### Dataset — decisões tomadas

- **Escopo fechado:** ENEM 2023 (uma edição) × IBGE 2021 (população e PIB municipais).
  Ficaram de fora outros anos, outras bases e microdados por candidato.
- **Chave de agregação:** **município da escola** (`CO_MUNICIPIO_ESC`), não o de residência
  nem o de prova. É o vínculo com sentido educacional para cruzar com o IBGE.
- **Critério de participante:** escola declarada **e** presente nos dois dias **e** com as
  cinco notas.
- **Resultado:** 5.481 municípios, **721.429 participantes** (de ~3,9 milhões de inscritos),
  15 colunas, **zero nulos**, 0,59 MB.
- **Memória do sistema:** *stateless*, uma pergunta por vez (conforme o planejamento).

### Duas descobertas que mudam premissas da proposta

1. **O risco do código de município não se materializou.** A proposta apontava que
   `CO_MUNICIPIO_ESC` do INEP poderia não casar 1:1 com o código do IBGE. **Casou:
   5.481 de 5.481.** O risco real está em outro lugar: *quem conta como participante*
   (721k de 3,9M) muda qualquer resposta muito mais do que o código de município.
2. **O artefato não tem valores faltantes.** A proposta previa tratamento de dados
   ausentes como parte do problema; a agregação por município eliminou isso no nível dos
   dados. O tema reapareceu **deslocado**: como *pergunta sem coluna correspondente*.
   Por isso o RF-05 do notebook mede **abstenção**, não imputação.

### Baseline implementado

Uma **única chamada ao LLM** que devolve um plano estruturado (`viavel` /
`codigo_pandas` / `template_resposta`), seguida de execução e formatação
**determinísticas**. Classificado como **parcial**.

Deliberadamente **sem** validador, **sem** retry, **sem** gráfico e com nota de limitação
**fixa** — é o que mantém mensurável o ganho dos Entregáveis 2, 3 e 4.

Guarda de segurança: `ast.parse(mode="eval")` + passeio na árvore recusando nomes fora de
`{df, pd, np}` e atributos privados. **Não é sandbox** — e o notebook demonstra o furo
explicitamente: `df.to_csv("arquivo.csv")` **passa** na guarda. Fechar isso exige
subprocesso com timeout (tarefa do Entregável 2).

### Conjunto de avaliação — CONGELADO

**13 casos** (11 automáticos + 2 de rubrica manual). Respostas de referência calculadas
com pandas escrito à mão, **antes** de qualquer chamada ao LLM.

- T01–T05: valor único, contagem, ranking com filtro, agregação por grupo
- T06–T08: cruzamento ENEM × IBGE e composição de operações
- T09–T11: armadilhas de abstenção (coluna inexistente, indicador inexistente, **ano
  inexistente** — o mais perigoso, porque o modelo tem 2019 na memória paramétrica)
- T12–T13: ambíguos, rubrica manual de 0 a 2

> **Não alterar esses casos sem reexecutar o baseline.** Comparação entre arquiteturas
> exige a mesma régua. A ampliação para 25–30 casos está prevista para o Entregável 4.

### Estado da entrega — o que falta

- [x] Especificação completa (seções 1–10)
- [x] Baseline implementado e validado
- [x] Conjunto de avaliação congelado + verificações
- [ ] **Executar o notebook do início ao fim com chave da Groq e salvar com as saídas**
- [ ] Preencher os 8 pontos marcados `**[da execução]**` / `**[preencher…]**`
      (seções 17, 18 e 21) com os números reais
- [ ] Notas da rubrica manual de T12 e T13 (seção 17)

**Validação já feita:** as 21 células de código foram executadas com um dublê no lugar do
LLM — carga de dados, esquema, guarda, executor, formatação, as cinco funções de
verificação, laço de experimentos e agregação de resultados passam. Falta apenas a
execução real contra a Groq.

### Notas operacionais (para quem for reproduzir)

- O download do INEP **cai no meio** com frequência (`Connection reset by peer`) e o
  certificado de `download.inep.gov.br` **não valida** na cadeia padrão. O ETL já trata os
  dois casos (retomada + TLS desligado só para esse host). Levou ~10 tentativas.
- Alguns municípios do IBGE vêm com `microrregiao: null` (criados recentemente); a UF só
  aparece em `regiao-imediata`. Ignorar isso derruba o ETL.
- O ETL guarda um cache do agregado do ENEM em `--trabalho`, para não reprocessar 1,8 GB
  a cada execução.
- Reprodução: `python etl/build_dataset.py --trabalho /tmp/enem --saida dados`

### Próximo passo (Entregável 2 — 13/09)

Grafo LangGraph + **Validador com retry** + sandbox real por subprocesso. O Validador é o
incremento com maior ganho esperado por unidade de custo: ataca a limitação arquitetural
mais cara do baseline — erro que passa direto para o usuário — cobrando chamadas extras
**só** nos casos que falham. A partir daí, **três execuções por caso** e mediana como valor
reportado, porque `temperature=0` não garante saída idêntica.

---
