ENTREGÁVEL 2 — INF0093 (2S/2026)
Sistema multiagente para perguntas em linguagem natural sobre dados educacionais
Grupo: Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin


ARQUIVOS
--------

E2_DallaCosta_Murer_Denzin.ipynb
    O entregável. Notebook executado, com as saídas salvas. Contém a estrutura
    herdada do E1 (seção A), a hipótese arquitetural (B), a arquitetura da v2 em
    LangGraph (C), memória por thread_id (D), integração via MCP (E), a
    comparação v1 x v2 (F), os novos modos de falha (G) e a análise (H).

enem2023_ibge_municipios.csv
    Dataset do projeto: 5.481 municípios x 15 colunas, 721.429 participantes do
    ENEM 2023 agregados pelo município da escola, cruzados com população e PIB
    do IBGE de 2021. Produzido pelo ETL do E1, fora do sistema. O notebook o
    baixa do repositório; esta cópia local é a que o servidor MCP lê.

servidor_dados_enem.py
    Servidor MCP local (FastMCP), executado como subprocesso e por stdio.
    Expõe uma ferramenta, buscar_municipio(nome, uf), que devolve a grafia exata
    do dataset, a UF e o número de participantes — revelando homônimos —, e um
    recurso com o esquema do dataset. Somente leitura do CSV passado por linha
    de comando; não acessa rede e não escreve nada.

servidor_mcp.log
    stderr do servidor MCP: registro de cada chamada recebida, com argumentos.
    É a contraparte, do lado do servidor, do log por transição do grafo.

v2_resultados.json
    Resultados da execução, salvos pelo notebook: RUN_INFO da v1 e da v2,
    origem dos dados, impressão digital do conjunto de casos, contrato da
    integração, comparações (conjunto completo e casos congelados), medições de
    memória, registros por caso e logs do grafo.