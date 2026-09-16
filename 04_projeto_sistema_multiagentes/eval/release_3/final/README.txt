ENTREGÁVEL 3 — INF0093 (2S/2026)
Sistema multiagente para perguntas em linguagem natural sobre dados educacionais
Grupo: Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin


ARQUIVOS
--------

E3_DallaCosta_Murer_Denzin.ipynb
    O entregável. Notebook executado, com as saídas salvas. Contém a estrutura
    herdada do E1 e a v2 em forma executável (seção A), a limitação observada e a
    hipótese (B), os agentes (C), o padrão de organização (D), o contrato entre
    agentes (E), skills e planejamento (F), a observabilidade e a atribuição de
    custo por etapa (G), a comparação v2 x v3 (H), os novos modos de falha (I) e
    a análise arquitetural com a pergunta obrigatória (J).

enem2023_ibge_municipios.csv
    Dataset do projeto: 5.481 municípios x 15 colunas, 721.429 participantes do
    ENEM 2023 agregados pelo município da escola, cruzados com população e PIB do
    IBGE de 2021. Produzido pelo ETL do E1, fora do sistema. O notebook o baixa do
    repositório; esta cópia local é a que o servidor MCP lê.

servidor_dados_enem.py
    Servidor MCP local (FastMCP), executado como subprocesso e por stdio. Expõe a
    ferramenta buscar_municipio(nome, uf) e um recurso com o esquema do dataset.
    Idêntico ao do E2. Na v3 ele passa a ter dois clientes: o Resolvedor e o
    Validador.

servidor_mcp.log
    stderr do servidor MCP: registro de cada chamada recebida, com argumentos.

v3_resultados.json
    Resultados da execução, salvos pelo notebook: RUN_INFO da v1, da v2 e da v3,
    origem dos dados, impressão digital do conjunto congelado, papel de cada
    agente, comparações (conjunto completo e casos congelados), custo por agente,
    registros por caso, traces do grafo e as fichas entregues ao Sintetizador.


O QUE MUDA DA v2 PARA A v3
--------------------------

A v2 era um grafo único, com servidor MCP e memória por thread_id. A v3 divide o
sistema em três agentes — Resolvedor (herdado), Validador (novo) e Sintetizador
(novo) —, organizados como pipeline com um laço de validação limitado a uma
refação. Planejador, executor e abstenção continuam sendo etapas de fluxo, e a
seção C explica por quê.

O conjunto de casos congelado, as funções de verificação, os critérios de sucesso
e o formato de saída são os do E1, sem alteração. O modelo e a temperatura são os
mesmos das entregas anteriores, e a v2 é reexecutada na mesma sessão da v3.


COMO EXECUTAR
-------------

O notebook procura a chave da API em GROQ_API_KEY, no arquivo .secret dos
diretórios acima (eval/.secret), no userdata do Colab e, por último, no teclado.
Nenhuma chave está escrita no notebook.

A rodada da seção H respeita o limite de 8.000 tokens por minuto do provedor
(classe Vazao), então ela leva dezenas de minutos. O enunciado permite executar
uma célula de cada vez, sem "run all".
