# Conclusão do projeto: as quatro versões

**INF0093 — 2S/2026** · Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin
Sistema multiagente para perguntas em linguagem natural sobre dados educacionais brasileiros.

Os números vêm dos 13 casos congelados do E1, os únicos que as quatro versões enfrentaram. Detalhes e evidência: `E4_DallaCosta_Murer_Denzin.ipynb`.

---

## 1. Quadro comparativo

| | v1 (E1) | v2 (E2) | v3 (E3) | v4 (E4) |
|---|---|---|---|---|
| Descrição | 1 chamada ao LLM + execução determinística | grafo único + servidor MCP + memória | 3 agentes em pipeline com validação | v3 + contenção + verificação ativa |
| Acertos (11 automáticos) | 11/11 | 10/11 | 11/11 | 11/11 |
| Faixa entre execuções | 10–11 (2 sessões: E1, E2) | 10–11 (2 sessões: E2, E3) | não medida (1 execução) | 11–11 (3 rodadas, mesma sessão) |
| Agentes | 0 | 1 (Resolvedor) | 3 | 3 + nó de conferência |
| Chamadas ao LLM | 13 | 26 | 67 | 57,7 |
| Chamadas a ferramenta | 0 | 6 | 8 | 10,7 |
| Tokens por pergunta | 1.854 | 2.682 | 5.977 | 5.892 |
| Latência mediana | 5,16 s | 11,47 s | 4,83 s | 5,03 s |
| Latência máxima | 15,84 s | 17,28 s | 35,39 s | 25,53 s |
| Custo por pergunta | US$ 0,0004 | US$ 0,0006 | US$ 0,0015 | US$ 0,0015 |
| Memória | nenhuma | checkpointer por `thread_id`, janela de 5 turnos | herdada da v2 | herdada da v2 |

A taxa de acerto não variou entre versões além do que a própria v1 e a v2 variam entre sessões. A régua congelada foi construída no E1 para um sistema de uma chamada e está saturada desde a v2. A latência não é comparável entre sessões: a v2 teve mediana de 11,47 s no E2 e de 1,86 s no E3.

---

## 2. O que cada versão acrescentou

### v1 → v2: acesso a dados

* Servidor MCP com `buscar_municipio`, que resolve a grafia do IBGE e revela homônimos; memória por conversa.
* Custo: o dobro de chamadas ao LLM.
* Acerto: sem ganho (11/11 → 10/11). A v2 expôs problemas que a v1 não detectava: os casos T14 (grafia `Sant'Ana do Livramento`) e T15 (cinco municípios chamados Bom Jesus) vieram daí.

### v2 → v3: divisão em agentes

* Validador (julga o resultado antes de entregar) e Sintetizador (escreve o texto depois de o número existir).
* Custo: +158% de chamadas (26 → 67) e +160% em dólar.
* Acerto: empate. Recuperou 3 de 3 falhas de geração de código e a rubrica de ambiguidade subiu de 1 para 5 pontos. Introduziu duas regressões (T15 e T18).

### v3 → v4: robustez e verificação

* Retentativa com espera crescente, tempo limite por operação, degradação declarada, refazer determinístico sem LLM, síntese de reserva e três verificações de falha silenciosa.
* Custo: menos chamadas ao modelo (67 → 57,7), com custo em dólares equivalente (US$ 0,00146 contra 0,00145 por pergunta).
* Acerto: empate. Primeira versão com três rodadas na mesma sessão.

---

## 3. v4 comparada com cada versão

### v4 × v1

| v4 | v1 |
|---|---|
| resolve grafia e homônimos, se abstém com fundamento, declara limitações, sobrevive a falha do provedor, é auditável caso a caso | custa cerca de um quarto por pergunta, com 4,4 vezes menos chamadas e 3,2 vezes menos tokens |

O acerto empata (11/11). A v1 é a escolha adequada se o critério for custo e as perguntas forem simples.

### v4 × v2

A v2 custa cerca de 2,7 vezes menos, mas não julga o próprio resultado: código recusado pela guarda chegava ao usuário como mensagem de erro, sem segunda tentativa. A v4 recupera esses casos e, em uma das rodadas, sem chamada ao modelo.

### v4 × v3

| Dimensão | v3 | v4 |
|---|---|---|
| Acerto | 11/11 | 11/11 |
| Chamadas ao LLM | 67 | 57,7 |
| Custo por pergunta | US$ 0,00145 | US$ 0,00146 |
| Latência do Validador (parte do total) | 53,2% | 36,1% |
| Latência máxima | 35,4 s | 25,5 s |
| Recupera falha do provedor no último nó | não (perdia o T18) | sim, nas 3 rodadas |
| Detecta falha silenciosa | não | 7 detecções em 57 execuções |
| Rubrica de ambiguidade | T12: 1; T15: 0 | T12: 0/1/0; T15: 0 |
| Qualidade ponderada com rubrica (congelados / completo) | 0,957 / 0,870 | 0,901 / 0,869 |

A v4 supera a v3 em operação (chamadas, recuperação de falha, detecção) e fica abaixo ou igual nos casos de rubrica manual.

---

## 4. Limitações por versão

| Limitação | Nasceu na | Corrigida em | Como |
|---|---|---|---|
| Não sabe a grafia do IBGE nem vê homônimos | v1 | v2 | ferramenta MCP `buscar_municipio` |
| Ninguém julga o resultado antes de entregar | v1, v2 | v3 | agente Validador, com laço de refação |
| Texto escrito antes de o número existir | v1, v2 | v3 | agente Sintetizador, que redige depois |
| Código recusado vira erro para o usuário | v1, v2 | v3 / v4 | v3 manda refazer; v4 refaz sem LLM quando o padrão é conhecido |
| Achado do Validador se perde na ficha (T15) | v3 | não corrigida | a v4 detecta (3 de 3 rodadas) e não corrige |
| Queda do provedor no último nó apaga a resposta (T18) | v3 | v4 | síntese determinística de reserva |
| Sem retentativa, tempo limite ou degradação | v1–v3 | v4 | seção B do E4 |
| Nenhuma verificação de falha silenciosa | v1–v3 | v4 | 3 conferências após a síntese |
| Execução sem tempo limite nem limite de memória | v1 | aberta | exigiria outro processo; risco avaliado como baixo |
| Sem canal de volta ao usuário para desambiguar | v1–v4 | aberta | mudança arquitetural, proposta para uma v5 |

---

## 5. Custo da v4 por etapa

| Etapa | % da latência | % dos tokens | Papel |
|---|---|---|---|
| Validador | 36,1% | 31,0% | agente |
| Sintetizador | 35,9% | 23,4% | agente |
| Planejador | 17,6% | 34,3% | etapa |
| Resolvedor | 10,5% | 11,4% | agente |
| Executor / conferência / abstenção | 0% | 0% | determinísticos |

Latência e consumo de tokens não se concentram no mesmo nó: o Planejador usa um terço dos tokens com 18% da latência, porque carrega o esquema inteiro em todo prompt. Enxugá-lo é a próxima otimização e não foi aplicada para manter o prompt idêntico ao da v1 na comparação.

---

## 6. Versão recomendada

**v4, otimizando previsibilidade e auditabilidade.**

Evidência: é a única versão que mantém a resposta quando o provedor falha no último nó (T18, 3 de 3 rodadas), a única que sinaliza os próprios erros (T15 em 3 de 3 rodadas, T08 em 2 de 3) e a única com três rodadas na mesma sessão (11–11 nos congelados).

O que os dados não permitem afirmar:

1. Que a v4 acerte mais que outra versão. As faixas plausíveis se sobrepõem nos seis pares.
2. Que as diferenças entre versões sejam reais. v1 e v2 variaram um caso entre sessões (v1: 11/11 no E1 e 10/11 no E2; v2: 10/11 no E2 e 11/11 no E3).
3. Que a v4 responda melhor nos casos de rubrica manual. No T12 ficou abaixo da v3, e no T15 igualou a v3 e ficou abaixo da v2.
4. Que o custo seja menor que o da v3. Há menos chamadas, mas o custo em dólares é equivalente.
5. Que as verificações cubram os erros silenciosos. A amostra frágil do T12 (Uru, 1 participante) passou sem ressalva e sem detecção nas rodadas 1 e 3, porque a verificação 3 só lê o número de participantes de municípios devolvidos por `buscar_municipio`. A verificação `dentro_do_escopo` não detectou nada em dados reais.
6. Que o sistema seja neutro entre perfis. O par mínimo não achou tratamento desigual por registro linguístico, mas com 5 execuções por atributo não detectaria um efeito moderado.

Correções antes de uso real: tratar `400 — Failed to generate JSON` como falha transitória (único erro da v4 em 57 execuções), retirar o texto do erro do provedor da mensagem entregue ao usuário e ampliar a verificação 3 para ler `n_participantes` do resultado executado.

---

## 7. Lições do projeto

1. Com 11 casos automáticos, um acerto vale 9 pontos percentuais e as faixas se sobrepõem. A evidência utilizável é o caso específico que mudou, com explicação pelo trace. Nem todas as mudanças têm explicação: T03 e T14 mudaram entre v2 e v3 sem que o trace mostre algum mecanismo atuando.
2. Medir a mesma versão em sessões diferentes mostrou uma variação de um caso, do tamanho das diferenças entre versões.
3. A v4 detecta o erro do T15 e avisa, mas entrega a resposta sem corrigi-la.
