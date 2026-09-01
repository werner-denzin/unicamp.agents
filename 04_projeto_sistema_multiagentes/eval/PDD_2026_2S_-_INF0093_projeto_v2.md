# INF0093 – Projeto Prático com Sistemas Multiagentes

## 1. Integrantes

- Rodolfo Dalla Costa
- Thais Caroline Murer
- Werner Conrado Jacob Denzin

## 2. Tema / Problema

As bases de dados públicas brasileiras, como os microdados do ENEM (INEP/MEC) e os indicadores municipais do IBGE, são abertas, mas de difícil consulta para quem não tem conhecimento técnico: responder uma pergunta simples exige conhecer o schema dos dados, tratar valores ausentes e escrever código. Propomos um sistema multiagente, implementado em LangGraph, que responde perguntas em linguagem natural sobre esses dados, devolvendo texto, gráfico e as eventuais limitações dos dados utilizados na resposta.

## 3. Proposta de Solução / Arquitetura

Um Planejador interpreta a pergunta do usuário e define a estratégia de resolução, que é executada por um Supervisor responsável por orquestrar cinco agentes especializados:

1. **Loader** — carrega os dados já pré-processados;
2. **Analisador** — gera e executa código pandas em um ambiente isolado (sandbox);
3. **Validador** — verifica a consistência do resultado, encaminhando-a para o Supervisor: no caso de reprovação, retorna para o Analisador efetuar os ajustes necessários, caso contrário, Visualizador ou Sintetizador;  
4. **Visualizador** — gera o gráfico correspondente, se solicitado pelo usuário;
5. **Sintetizador** — compõe a resposta final unindo texto, gráfico e limitações dos dados.

## 4. Escopo e decisões de projeto

- Escopo de dados será revisto pela equipe, inicialmente, mais restrito (uma edição do ENEM, um recorte de municípios/estados, ...) de forma a não comprometer complexidade e prazo da disciplina;
- Observabilidade é tratada desde a primeira entrega, com registro estruturado (log) de cada decisão e transição entre agentes, incluindo as tentativas reprovadas pelo validador;
- A confiabilidade do sistema será medida sobre um conjunto de perguntas com resposta previamente conhecida, construído e ampliado ao longo do desenvolvimento, permitindo acompanhar a evolução da taxa de acerto entre as entregas.
- A solução evoluirá quanto à sua complexidade (adição de novas camadas e funcionalidades) de acordo com os requisitos definidos dentre cada uma das entregas do projeto; 

## 5. Datasets candidatos
> Obs: Serão explorados e definidos pela equipe na entrega 1

| Fonte | Link | Tamanho |
|---|---|---|
| ENEM 2023 — microdados | [microdados_enem_2023.zip](https://download.inep.gov.br/microdados/microdados_enem_2023.zip) | 550 MB zip → 1,78 GB CSV |
| IBGE — API de Agregados (v3) | [servicodados.ibge.gov.br/api/v3/agregados](https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6%5Ball%5D) | 690 KB JSON |
| IBGE — Localidades | [servicodados.ibge.gov.br/api/v1/localidades](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | 2,4 MB JSON |
| IBGE — API SIDRA | [apisidra.ibge.gov.br](https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2021) | 1,5 MB JSON |
| ENEM 2025 — microdados | [microdados_enem_2025.zip](https://download.inep.gov.br/microdados/microdados_enem_2025.zip) | 630 MB zip |
| ENEM 2024 — microdados | [microdados_enem_2024.zip](https://download.inep.gov.br/microdados/microdados_enem_2024.zip) | 526 MB zip |
| Sinopse Estatística ENEM 2025 | [sinopse_enem_2025.zip](https://download.inep.gov.br/informacoes_estatisticas/sinopses_estatisticas/sinopses_enem/2025/sinopse_enem_2025.zip) | 2 MB |
| ENEM — página oficial (1998 a 2025) | [gov.br/inep — microdados do Enem](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) | — |

Acessos verificados em 28/08/2026.