# Dicionário de dados — `enem2023_ibge_municipios.csv`

Artefato pré-processado do Entregável 1. Uma linha por **município da escola**
do candidato. Gerado pelo ETL descrito na seção 12 do notebook (execução única, fora do grafo).

| Coluna | Tipo | Descrição |
|---|---|---|
| `co_municipio` | int | Código IBGE do município (7 dígitos). |
| `municipio` | str | Nome do município. |
| `uf` | str | Sigla da unidade da federação (`SP`, `BA`, ...). |
| `regiao` | str | Norte, Nordeste, Centro-Oeste, Sudeste, Sul. |
| `populacao_2021` | float | População residente estimada em 2021 (IBGE, agregado 6579, variável 9324). |
| `pib_2021_mil_reais` | float | PIB municipal a preços correntes de 2021, em mil reais (IBGE, agregado 5938, variável 37). |
| `pib_per_capita_2021` | float | `pib_2021_mil_reais * 1000 / populacao_2021`, em reais por habitante. Calculado no ETL. |
| `n_participantes` | int | Candidatos do município considerados na média (ver critério abaixo). |
| `media_cn` | float | Média da nota de Ciências da Natureza. |
| `media_ch` | float | Média da nota de Ciências Humanas. |
| `media_lc` | float | Média da nota de Linguagens e Códigos. |
| `media_mt` | float | Média da nota de Matemática. |
| `media_redacao` | float | Média da nota de Redação. |
| `media_geral` | float | Média das cinco notas por candidato, agregada por município. |
| `pct_escola_publica` | float | Percentual dos participantes cuja escola é da rede pública (`TP_ESCOLA == 2`). |

## Critério de inclusão do candidato

Entram na agregação apenas candidatos que, simultaneamente:

1. declararam escola (`CO_MUNICIPIO_ESC` preenchido) — é o vínculo municipal usado
   no cruzamento com o IBGE;
2. estiveram **presentes nos dois dias** (`TP_PRESENCA_CN/CH/LC/MT == 1`);
3. têm as **cinco notas** preenchidas.

Resultado: **721.429 participantes** em **5.481 municípios**, de um total de ~3,9 milhões
de inscritos no ENEM 2023.

## Limitações conhecidas

- **Recorte de candidatos.** O subconjunto com escola declarada é majoritariamente de
  concluintes do ensino médio regular; treineiros e egressos ficam sub-representados.
  As médias **não** são a média do ENEM 2023 do município como um todo.
- **Município da escola ≠ município de residência ≠ município de prova.** A escolha
  é deliberada (é o vínculo com sentido educacional), mas muda o número.
- **Anos diferentes.** ENEM de 2023, indicadores do IBGE de 2021. Comparações
  socioeconômicas são aproximadas.
- **Municípios com poucos participantes.** O mínimo observado é 1 participante;
  médias de municípios pequenos são instáveis e rankings sem filtro de
  `n_participantes` são dominados por ruído.
- **PIB per capita não é renda das famílias.** É produto por habitante; municípios
  com uma grande planta industrial ou poço de petróleo aparecem no topo sem que
  isso reflita a renda local.
- **Cobertura do cruzamento.** Todos os 5.481 códigos de município do INEP casaram
  1:1 com o código do IBGE — o risco levantado na proposta não se materializou
  nesta edição.

## Fontes

- INEP/MEC, Microdados do ENEM 2023 — <https://download.inep.gov.br/microdados/microdados_enem_2023.zip>
- IBGE, API de Agregados v3, agregado 6579 (população estimada 2021)
- IBGE, API de Agregados v3, agregado 5938 (PIB municipal 2021)
- IBGE, API de Localidades v1 (nome, UF e região dos municípios)

Acessos verificados em 03/09/2026.
