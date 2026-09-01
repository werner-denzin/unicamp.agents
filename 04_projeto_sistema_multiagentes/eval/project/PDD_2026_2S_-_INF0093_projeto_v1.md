# INF0093 — Projeto Prático com Sistemas Multiagentes

**Definição de grupo e tema — 2º semestre de 2026**

## 1. Integrantes

- Rodolfo Dalla Costa
- Thais Caroline Murer
- Werner Conrado Jacob Denzin

## 2. Projeto

Bases de dados públicas brasileiras são abertas, mas de consulta difícil para quem não tem conhecimento
técnico: responder uma pergunta simples exige conhecer o schema, tratar valores ausentes e escrever código.
Construiremos um sistema multiagente, em LangGraph, que responde perguntas em linguagem natural sobre os
microdados do ENEM (INEP/MEC), complementados por indicadores municipais do IBGE, devolvendo texto, gráfico
e as eventuais limitações dos dados. A arquitetura prevê um Planejador e um Supervisor que orquestra cinco
agentes: (1) loader de dados, (2) análise, que executa pandas em sandbox, (3) validador, que reprova
resultados inconsistentes e devolve para nova tentativa, (4) visualização e (5) sintetizador, que gera a
resposta final. A confiabilidade será medida sobre um conjunto de perguntas com resposta previamente
conhecida.

## 3. Datasets candidatos

| Fonte | Link | Tamanho | Escolhida |
|---|---|---|:---:|
| ENEM 2023 — microdados | [microdados_enem_2023.zip](https://download.inep.gov.br/microdados/microdados_enem_2023.zip) | 550 MB zip → 1,78 GB CSV | ✅ |
| IBGE — API de Agregados (v3) | [servicodados.ibge.gov.br/api/v3/agregados](https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6%5Ball%5D) | 690 KB JSON | ✅ |
| IBGE — Localidades | [servicodados.ibge.gov.br/api/v1/localidades](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | 2,4 MB JSON | ✅ |
| IBGE — API SIDRA | [apisidra.ibge.gov.br](https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2021) | 1,5 MB JSON | ✅ |
| ENEM 2025 — microdados | [microdados_enem_2025.zip](https://download.inep.gov.br/microdados/microdados_enem_2025.zip) | 630 MB zip | |
| ENEM 2024 — microdados | [microdados_enem_2024.zip](https://download.inep.gov.br/microdados/microdados_enem_2024.zip) | 526 MB zip | |
| Sinopse Estatística ENEM 2025 | [sinopse_enem_2025.zip](https://download.inep.gov.br/informacoes_estatisticas/sinopses_estatisticas/sinopses_enem/2025/sinopse_enem_2025.zip) | 2 MB | |
| ENEM — página oficial (1998 a 2025) | [gov.br/inep — microdados do Enem](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) | — | |

Acessos verificados em 28/08/2026.