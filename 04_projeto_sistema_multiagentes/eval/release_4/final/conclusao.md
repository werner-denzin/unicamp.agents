# Conclusão do projeto — as quatro versões

**INF0093 — 2S/2026** · Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin
Sistema multiagente para perguntas em linguagem natural sobre dados educacionais brasileiros.

Todos os números vêm dos **13 casos congelados do E1** — a única régua que as quatro versões
enfrentaram. Detalhes e evidência: `E4_DallaCosta_Murer_Denzin.ipynb`.

---

## 1. O quadro em uma tabela

| | **v1** (E1) | **v2** (E2) | **v3** (E3) | **v4** (E4) |
|---|---|---|---|---|
| **O que é** | 1 chamada ao LLM + execução determinística | grafo único + servidor MCP + memória | 3 agentes em pipeline com validação | v3 + contenção + verificação ativa |
| **Acertos (11 automáticos)** | 11/11 | 10/11 | 11/11 | **11/11** |
| **Faixa entre execuções** | não medida | não medida | não medida | **11–11 (variação zero)** |
| **Agentes** | 0 | 1 (Resolvedor) | 3 | 3 + nó de conferência |
| **Chamadas ao LLM** | 13 | 26 | 67 | **57,7** |
| **Chamadas a ferramenta** | 0 | 6 | 8 | 10,7 |
| **Tokens por pergunta** | 1.854 | 2.682 | 5.977 | **5.892** |
| **Latência mediana** | 5,16 s | 11,47 s | 4,83 s | 5,03 s |
| **Latência máxima** | 15,84 s | 17,28 s | 35,39 s | **25,53 s** |
| **Custo por pergunta** | US$ 0,0004 | US$ 0,0006 | US$ 0,0015 | US$ 0,0015 |
| **Memória** | nenhuma | checkpointer por `thread_id`, janela de 5 turnos | herdada da v2 | herdada da v2 |

> **A taxa de acerto não evoluiu — e não tinha como.** A régua congelada foi construída no E1 contra
> um sistema de uma chamada só e **saturou a partir da v2**. Toda a análise útil mora fora dela.

---

## 2. O que cada versão agregou

### v1 → v2: acesso a dados vivos

* **Agregou:** servidor MCP com `buscar_municipio`, que resolve a grafia do IBGE e revela homônimos;
  memória por conversa.
* **Custo:** 2× as chamadas ao LLM.
* **Resultado medido:** **nenhum ganho de acerto** (11/11 → 10/11). O valor foi *expor problemas que
  a v1 não sabia que tinha* — os casos T14 (grafia `Sant'Ana do Livramento`) e T15 (cinco municípios
  chamados Bom Jesus) nasceram daí.

### v2 → v3: divisão em agentes

* **Agregou:** Validador (julga o resultado antes de entregar) e Sintetizador (escreve o texto
  **depois** de o número existir).
* **Custo:** **+158% de chamadas** (26 → 67) e +160% em dólar.
* **Resultado medido:** empate no acerto; recuperou 3 de 3 falhas de geração de código; rubrica de
  ambiguidade subiu de 1 para 5 pontos. **Introduziu duas regressões** (T15 e T18).

### v3 → v4: robustez e verificação

* **Agregou:** retentativa com espera crescente, tempo limite por operação, degradação que se
  declara, refazer determinístico sem LLM, síntese de reserva, e **três verificações que convertem
  falha silenciosa em detectável**.
* **Custo:** praticamente zero — na verdade, **negativo**.
* **Resultado medido:** empate no acerto, **menos chamadas** (67 → 57,7) e a única faixa medida do
  projeto.

---

## 3. v4 comparada com cada versão

### v4 × v1 — o baseline ainda é imbatível em custo

| | v4 ganha | v1 ganha |
|---|---|---|
| | resolve grafia e homônimos; se abstém com fundamento; declara limitações; sobrevive a falha do provedor; auditável caso a caso | **4× mais barata**, 4,4× menos chamadas, 3,2× menos tokens |

**Acerto: empate (11/11).** A v1 é a escolha certa se o critério for custo puro e as perguntas forem
simples. Ela não resolve nada do que motivou as três versões seguintes.

### v4 × v2 — o mesmo dinheiro não compra o mesmo

A v2 é 2,7× mais barata, mas **não julga o próprio resultado**: código recusado pela guarda chegava
ao usuário como mensagem de erro, sem segunda tentativa. A v4 recupera esses casos — em uma das
rodadas, sem gastar nenhuma chamada ao modelo.

### v4 × v3 — a comparação que importa

| Dimensão | v3 | v4 |
|---|---|---|
| Acerto | 11/11 | 11/11 |
| Chamadas ao LLM | 67 | **57,7** |
| Latência concentrada no Validador | **53,2%** | **36,1%** |
| Latência máxima | 35,4 s | **25,5 s** |
| Recupera falha do provedor no último nó | não (perdia o T18) | **sim, nas 3 rodadas** |
| Detecta falha silenciosa | não | **7 detecções em 57 execuções** |
| Rubrica de ambiguidade (T12, T15) | 1 e 0 | **0 e 0 — piorou** |

**A v4 domina a v3 em operação e perde em redação.** É a conclusão incômoda e é a que os dados
sustentam.

---

## 4. Limitações por versão — e quem consertou

| Limitação | Nasceu na | Corrigida em | Como |
|---|---|---|---|
| Não sabe a grafia do IBGE nem vê homônimos | v1 | **v2** | ferramenta MCP `buscar_municipio` |
| Ninguém julga o resultado antes de entregar | v1, v2 | **v3** | agente Validador, com laço de refação |
| Texto escrito **antes** de o número existir | v1, v2 | **v3** | agente Sintetizador, que redige depois |
| Código recusado vira erro para o usuário | v1, v2 | **v3 / v4** | v3 manda refazer; v4 refaz **sem LLM** quando o padrão é conhecido |
| Achado do Validador se perde na ficha (T15) | v3 | **não corrigida** | a v4 **detecta** (3 de 3 rodadas) e **não corrige** |
| Queda do provedor no último nó apaga a resposta (T18) | v3 | **v4** | síntese determinística de reserva |
| Sem retentativa, tempo limite ou degradação | v1–v3 | **v4** | seção B do E4 |
| Nenhuma verificação de falha silenciosa | v1–v3 | **v4** | 3 conferências após a síntese |
| Execução sem tempo limite nem limite de memória | v1 | **aberta** | exigiria outro processo; risco avaliado como baixo |
| Sem canal de volta ao usuário para desambiguar | v1–v4 | **aberta** | mudança arquitetural, proposta para uma v5 |

---

## 5. Onde o custo da v4 está

| Etapa | % da latência | % dos tokens | Papel |
|---|---|---|---|
| Validador | 36,1% | 31,0% | agente |
| Sintetizador | 35,9% | 23,4% | agente |
| Planejador | 17,6% | **34,3%** | etapa |
| Resolvedor | 10,5% | 11,4% | agente |
| Executor / conferência / abstenção | 0% | 0% | determinísticos |

Latência e consumo **não se concentram no mesmo nó**: o Planejador gasta um terço dos tokens com 18%
do relógio, porque carrega o esquema inteiro em todo prompt. Enxugá-lo é a próxima otimização óbvia —
foi deixada de fora de propósito, para não contaminar a comparação entre versões.

---

## 6. O que levar para produção

**A v4 — otimizando previsibilidade e auditabilidade, não qualidade.**

**Por quê:** é a única versão que sobrevive a uma falha do provedor sem perder a resposta, a única
que diz quando errou, e a única com variação medida (zero, nos casos congelados). E ficou **mais
barata** que a v3.

**O que os dados NÃO permitem afirmar:**

1. Que a v4 acerte mais que qualquer outra versão. **As faixas plausíveis das quatro se sobrepõem,
   seis pares em seis.**
2. Que a diferença entre versões signifique algo. A **mesma versão** varia um caso entre sessões
   (a v1 deu 11/11 no E1 e 10/11 no E2) — o tamanho de qualquer diferença que observamos.
3. Que a v4 responda melhor. Ela responde **pior** que a v3 em dois casos de ambiguidade.
4. Que o sistema seja neutro entre perfis. O par mínimo não achou tratamento desigual por registro
   linguístico, mas com 5 execuções por atributo **não teria poder para achar**.

**Antes de produção, duas correções baratas:** tratar `400 — Failed to generate JSON` como falha
transitória (foi o único erro da v4 em 57 execuções) e tirar o texto do erro do provedor da mensagem
entregue ao usuário.

---

## 7. As três lições do projeto

1. **Conjunto pequeno não sustenta comparação agregada.** Com 11 casos, um acerto vale 9 pontos
   percentuais e tudo se sobrepõe. A evidência forte é sempre *o caso específico que mudou, com o
   trace explicando por quê*.
2. **Medir a mesma versão duas vezes é mais informativo que medir duas versões uma vez.** A variação
   entre sessões só apareceu porque comparamos a v1 do E1 com a v1 do E2 — e ela é do tamanho de
   tudo o que estávamos tentando provar.
3. **Detectar não é corrigir.** A v4 sabe que errou no T15 e avisa, e mesmo assim entrega a resposta
   ruim. Foi o que a arquitetura prometeu, e é tudo o que ela entrega.
