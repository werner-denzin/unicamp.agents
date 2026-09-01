# Planejamento de Execução — Projeto Multiagente (ENEM + IBGE)
### INF0093 – Projeto Prático com Sistemas Multiagentes

Planejamento para 5 semanas e 4 entregas, considerando os riscos mapeados: escopo de dados enxuto desde o início, sandbox e observabilidade como trabalho de primeira classe, e memória/estado decididos explicitamente antes de codar.

---

## Semana 0 (antes do Entregável 1) — Decisões de arquitetura

Antes de escrever qualquer agente, fechar por escrito (README ou ADR curto) três decisões que evitam retrabalho depois:

1. **Escopo de dados fixado.** Ex.: ENEM de um único ano (o mais recente disponível), filtrado para um conjunto pequeno de estados ou municípios. Indicadores do IBGE limitados às variáveis que efetivamente serão cruzadas (renda, população, IDH municipal — não puxar a base toda). Documentar isso como limitação conhecida do sistema, não esconder.
2. **Pré-processamento fora do grafo.** Rodar uma vez, manualmente, um script de ETL que baixa os microdados, filtra, faz o join com o código de município do IBGE (aqui há um risco: nem todo `CO_MUNICIPIO_ESC` do INEP bate 1:1 com o código do IBGE — validar isso cedo) e salva um parquet/csv já tratado e leve (idealmente < 200MB). O agente "loader" carrega esse artefato pronto, não os microdados brutos.
3. **Modelo de memória do sistema.** Decidir explicitamente: cada pergunta é uma sessão nova (stateless), ou o sistema mantém um histórico curto por sessão para perguntas de follow-up? Recomenda-se começar **stateless** (mais simples, mais fácil de avaliar) e, se sobrar tempo, adicionar memória de sessão como extensão no Entregável 4.

Também criar, desde o início, um **log estruturado simples** (um JSON por execução, com timestamp, agente, input, output, decisão) — não precisa ser LangSmith, pode ser uma lista de dicts salva em arquivo. Isso é a base da observabilidade e é muito mais barato de instrumentar desde o dia 1 do que retroativamente.

---

## Entregável 1 — 7 de setembro
**Objetivo: esqueleto do grafo funcionando com dado real, mesmo que a resposta ainda seja simples.**

- Grafo LangGraph com **Planejador → Supervisor → loader** funcionando ponta a ponta.
- Loader lê o dataset pré-tratado (da Semana 0) e consegue responder uma pergunta trivial hardcoded (ex.: "quantos candidatos há no dataset?") só para provar que o pipeline de dados → agente → resposta funciona.
- Logging estruturado já plugado nesse fluxo mínimo.
- Documento curto descrevendo: arquitetura do grafo (diagrama dos nós/arestas), decisão de escopo de dados, decisão de memória.

O que **não** fazer ainda: não tentar plugar análise, validação e visualização juntas nessa entrega. O risco aqui é gastar a primeira semana brigando com o ETL do ENEM/IBGE — por isso o pré-processamento é tarefa da Semana 0, antes da entrega valer.

---

## Entregável 2 — 13 de setembro
**Objetivo: loop de análise + validação funcionando para perguntas simples.**

- Agente de **análise**: recebe a pergunta (ou um plano do Planejador) e gera/executa código pandas em sandbox.
  - Sandbox mínimo viável: subprocess isolado com timeout, sem acesso a rede/filesystem fora do diretório de dados, captura de stdout/stderr e de exceptions. Não superengenheirar isso — o objetivo é "não trava o sistema e não executa nada perigoso", não uma solução de segurança de produção.
- Agente **validador**: checa consistência do resultado (ex.: tipo de retorno esperado, valores dentro de faixas plausíveis, ausência de erro de execução) e decide aprovar ou mandar de volta para o agente de análise com feedback do que falhou. Testar esse loop de retry deliberadamente com pelo menos um caso que force uma reprovação, para provar que o ciclo funciona.
- Ampliar o log estruturado para capturar também as tentativas reprovadas pelo validador (isso vira dado interessante para discutir confiabilidade no vídeo final).
- Começar a esboçar o **conjunto de avaliação**: um arquivo com ~10 perguntas simples e suas respostas corretas conhecidas (calculadas manualmente ou com uma query de referência). Não precisa estar completo, mas o formato (pergunta, resposta esperada, tolerância de erro se numérica) deve existir agora, porque será usado continuamente nas próximas entregas.

---

## Entregável 3 — 20 de setembro
**Objetivo: sistema ponta a ponta com saída completa (texto + gráfico) e primeira medição de confiabilidade.**

- Agente de **visualização**: gera gráfico (matplotlib/plotly) a partir do resultado validado.
- Agente **sintetizador**: monta a resposta final combinando texto, gráfico e as limitações relevantes dos dados (ex.: "esse indicador é de 2022, mais recente que o ENEM usado, então a comparação é aproximada").
- Rodar o conjunto de avaliação (as ~10 perguntas) contra o sistema completo e registrar: taxa de acerto, quantas precisaram de retry do validador, tempo médio de execução. Esse é o primeiro número real de confiabilidade que poderá ser mostrado evoluindo até a próxima entrega.
- Revisar a instrumentação de observabilidade: nesse ponto o log já deveria permitir reconstruir, para qualquer pergunta, o caminho completo pelos 5 agentes.

---

## Entregável 4 — 4 de outubro
**Objetivo: consolidação, robustez e apresentação.**

- Expandir o conjunto de avaliação (de ~10 para ~25-30 perguntas), cobrindo casos fáceis, casos que exigem cruzamento ENEM+IBGE, e casos "armadilha" com dado ausente ou ambíguo, já que testar o tratamento de valores ausentes é parte da proposta original.
- Métricas de confiabilidade consolidadas: acurácia no conjunto de teste, taxa de reprovação pelo validador, análise de onde o sistema mais falha (ótimo conteúdo para o vídeo).
- Se sobrar tempo: memória de sessão (se deixada para depois na Semana 0) ou expansão do escopo de dados (mais um ano do ENEM, mais municípios) — mas só depois de tudo acima estar estável. Não expandir escopo de dados às custas de deixar a avaliação malfeita.
- Vídeo (5-10 min): mostrar o grafo, uma execução com retry do validador (é visualmente interessante e mostra o diferencial do projeto), e os números de confiabilidade — conecta diretamente com o que a disciplina pede em "avaliação, confiabilidade e arquitetura".

---

## Resumo da lógica do faseamento

A ideia central é inverter a ordem natural de tentação: ao invés de gastar a Semana 1 brigando com terabytes de microdados brutos e só chegar num sistema multiagente de verdade na Semana 3, o dado pequeno e tratado é fixado logo na Semana 0, e cada entrega adiciona exatamente **um** agente novo ao pipeline, sempre testável ponta a ponta. Avaliação e observabilidade entram cedo (Entregável 2) e crescem ao longo do projeto, ao invés de serem "anexadas" no fim — o que também gera números reais para citar na entrega final em vez de alegações genéricas de que o sistema "funciona bem".
