ENTREGÁVEL 4 — INF0093 (2S/2026)
Sistema multiagente para perguntas em linguagem natural sobre dados educacionais
Grupo: Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin


ARQUIVOS
--------

E4_DallaCosta_Murer_Denzin.ipynb
    O entregável. Notebook executado, com as saídas salvas. Contém a estrutura
    herdada do E3 e a origem declarada de cada número (A), as falhas plausíveis e
    os cinco mecanismos de contenção (B), as três verificações que convertem falha
    silenciosa em detectável e o grafo da v4 (C), as três rodadas do conjunto e a
    faixa (D), a consolidação das quatro versões (E), sinal e ruído (F), a
    avaliação ética — gravidade dos erros, distribuição e pares mínimos (G e H) —,
    a rastreabilidade (I), a matriz de consequências e os riscos da arquitetura
    (J) e a recomendação final (K).

enem2023_ibge_municipios.csv
    Dataset do projeto: 5.481 municípios x 15 colunas, 721.429 participantes do
    ENEM 2023 agregados pelo município da escola, cruzados com população e PIB do
    IBGE de 2021. Produzido pelo ETL do E1, fora do sistema. O notebook o baixa do
    repositório; esta cópia local é a que o servidor MCP lê.

servidor_dados_enem.py
    Servidor MCP local (FastMCP), executado como subprocesso e por stdio. Idêntico
    ao do E2 e do E3. Na v4 ele deixa de ser consumido diretamente: todos os
    agentes passam por `buscar_municipio`, um invólucro que acrescenta retentativa,
    tempo limite e degradação declarada.

servidor_mcp.log
    stderr do servidor MCP: registro de cada chamada recebida, com argumentos.

v4_rodada_1.jsonl, v4_rodada_2.jsonl, v4_rodada_3.jsonl
    As três rodadas do conjunto completo (19 casos) na v4. Uma linha por caso, com
    o trace integral, gravada assim que o caso termina. É o registro que sobrevive
    à sessão e o que a seção I usa para reconstruir uma execução.

v4_pares_minimos.jsonl
    As 10 execuções do experimento de pares mínimos (seção H.3): duas variantes de
    registro linguístico, com repetição e reformulação.

v4_demo_contencao.json
    A execução da seção C.4, com a fonte de identidade instável a 60%.

v4_piloto_rodada.jsonl, v4_piloto_rodada_2.jsonl
    As duas iterações piloto, preservadas e FORA de toda tabela. Cada uma encontrou
    um defeito e mudou o código, e por isso nenhuma entra em nenhuma faixa. A
    seção D explica o que cada uma achou.

e4_resultados.json
    O consolidado: RUN_INFO, origem de cada número, conjunto e impressão digital,
    mecanismos de contenção, confiabilidade, comparações, custo por etapa, pesos de
    gravidade, matriz de consequências, pares mínimos, registros e traces.


O QUE MUDA DA v3 PARA A v4
--------------------------

A v4 é a v3 com uma camada de robustez, mais as correções que o E3 deixou
pendentes:

  - contenção: retentativa com espera crescente, tempo limite por operação,
    degradação graciosa que se declara no texto, validação de saída e limite de
    passos;
  - verificação ativa: três conferências (evidência na fonte, escopo declarado,
    confiança compatível) num nó novo, depois do sintetizador;
  - refazer determinístico: erro de execução com padrão conhecido volta ao
    planejador SEM chamar o modelo;
  - veredito como ferramenta do laço do validador: 1 chamada quando o modelo
    coopera, 2 quando responde em texto — a v3 fazia 2 ou 3 sempre;
  - síntese determinística de reserva: a correção que o T18 exigia.

O conjunto congelado, as funções de verificação, os critérios de sucesso e o
formato de saída são os do E1, sem alteração. O prompt do planejador continua
byte a byte o da v1, DE PROPÓSITO: é o que mantém a comparação das quatro
versões atribuível. A otimização de enxugá-lo, proposta no E3, foi descartada
por esse motivo e o motivo está declarado no notebook.


O CASO NOVO
-----------

T19 — "Qual é a média geral do ENEM 2023 no município de São Gabriel da
Cachoeira, no Amazonas?" O perfil menos usual do domínio: município de maioria
indígena mais populoso do país, no Norte, 100% de escola pública, com amostra
robusta (102 participantes). A pergunta é a do T01 com o município trocado, para
que qualquer diferença de tratamento fique isolada.


RESULTADO, EM UMA LINHA
-----------------------

Nos 13 casos congelados as quatro versões empatam (11/11, exceto a v2 com 10/11)
e as faixas plausíveis se sobrepõem 6 a 6: nenhuma superioridade agregada se
sustenta. A v4 é recomendada por previsibilidade e auditabilidade, não por
qualidade — ela recupera o T18 por mecanismo determinístico, detecta falhas
silenciosas de forma reprodutível e custa menos chamadas que a v3. Ela também
RESPONDE PIOR que a v3 em dois casos de ambiguidade, e detecta sem corrigir.
A seção K sustenta a escolha e declara o que os dados não permitem afirmar.


COMO EXECUTAR
-------------

O notebook procura a chave da API em GROQ_API_KEY, no arquivo .secret dos
diretórios acima (eval/.secret), no userdata do Colab e, por último, no teclado.
Nenhuma chave está escrita no notebook.

Toda célula cara tem checkpoint em disco: as rodadas gravam caso a caso, os pares
gravam repetição a repetição, e a demonstração da seção C.4 grava o resultado.
Reexecutar o notebook do início ao fim NÃO repete nenhuma chamada ao provedor —
ele lê o que já está medido. Para refazer alguma medição, apague o arquivo
correspondente.

A chave usada tem 200.000 tokens por dia e 8.000 por minuto. Uma rodada completa
consome cerca de 115.000 tokens, então a medição desta entrega levou três dias de
cota, com as rodadas retomando de onde a cota do dia anterior as interrompeu.
