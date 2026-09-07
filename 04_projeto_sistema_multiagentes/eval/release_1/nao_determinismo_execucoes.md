# Por que o T03 falhou em uma execução e passou na outra

Nota técnica do Entregável 1 — 07/09/2026.
Resumo da investigação que originou o item 7.3 da seção 18 do notebook.

## O fato

O mesmo conjunto de 13 casos foi executado três vezes, com o **mesmo modelo**
(`openai/gpt-oss-20b`), o **mesmo prompt** (v1) e `temperature=0`:

| Execução | Aprovados | Erros de execução | Latência mediana | Tokens de saída | Custo |
|---|---|---|---|---|---|
| 03/09, 21:28 | 11 de 11 | 0 | 11,51 s | 7.597 | US$ 0,005528 |
| 07/09, 05:16 | 11 de 11 | 0 | 11,10 s | 7.257 | US$ 0,005358 |
| 07/09, 05:48 | **10 de 11** | **1 (T03)** | 10,32 s | 7.153 | US$ 0,005306 |

Na terceira, o T03 ("cinco municípios de SP com maior média de matemática, entre os que
têm pelo menos 100 participantes") gerou:

```python
df[df.uf=="SP" & df.n_participantes>=100].nlargest(5,'media_mt')[['municipio','media_mt']].
```

Dois defeitos: o ponto solto no final (erro de sintaxe, que foi o que a guarda reportou) e a
falta de parênteses em volta dos operandos do `&`. Em pandas, `&` tem precedência **maior**
que `==` e `>=`, então `df.uf=="SP" & df.n_participantes>=100` seria avaliado como
`df.uf == ("SP" & df.n_participantes) >= 100` e levantaria exceção mesmo sem o ponto.

## O que não foi a causa

Não houve alteração de prompt entre as execuções. A prova está nos próprios registros:
`tokens_entrada` deu **17.295 nas três execuções**, valor idêntico ao dígito. Qualquer
mudança de um caractere no prompt alteraria essa contagem. A única célula de código editada
entre a segunda e a terceira execução foi a do carregamento da chave, que não participa da
construção do prompt.

## A causa

`temperature=0` elimina a **amostragem** — o modelo passa a escolher sempre o token de maior
probabilidade —, mas não elimina a variação numérica do cálculo que produz essas
probabilidades. Três fontes, todas do lado do provedor:

1. **Agrupamento em lote (*batching*).** A Groq atende várias requisições no mesmo lote, e a
   composição do lote muda a cada instante. Soma em ponto flutuante não é associativa
   (`(a+b)+c ≠ a+(b+c)` no último bit), então o mesmo prompt em lotes diferentes produz
   *logits* minimamente diferentes.
2. **Mistura de especialistas (MoE).** O `gpt-oss-20b` roteia cada token para um subconjunto
   de especialistas, e esse roteamento depende do lote. É a fonte de variação mais forte
   nessa família de modelos.
3. **Hardware e kernels.** Requisições podem cair em nós diferentes, com tamanhos de lote e
   caminhos de execução distintos na GPU.

Quando dois tokens candidatos têm probabilidade quase empatada, uma diferença no último bit
inverte qual é o maior — e basta **um** token diferente para toda a geração seguinte divergir.

## Por que justamente o T03

O T03 é o único caso do conjunto cuja tradução para pandas exige uma **decisão sintática
ambígua logo no início da expressão**: emitir `(` antes de `df.uf`, produzindo
`(df.uf=="SP") & (df.n_participantes>=100)`, ou emitir `df` direto. As duas continuações são
plausíveis para o modelo, e o empate é apertado. Em duas execuções ele abriu o parêntese; na
terceira, não. O ponto solto no final é o mesmo fenômeno em outro ponto da geração.

Os outros 12 casos têm um caminho de tradução dominante, sem empate — por isso não oscilam.
A conclusão prática é que **condições compostas (`&`, `|`) são o ponto frágil do baseline**,
mais do que a escolha de coluna ou a agregação.

## Consequências para o projeto

- **Uma execução por caso não sustenta conclusão.** A diferença entre duas execuções do mesmo
  sistema (um caso, 9 pontos percentuais) é do tamanho do efeito que se pretende atribuir à
  arquitetura no Entregável 4. Daí o protocolo de **três execuções por caso e mediana
  reportada** a partir do Entregável 2 (seção 20 do notebook).
- **O RNF-02 não é julgável com a medição atual.** A mediana variou 11,51 → 11,10 → 10,32 s,
  atravessando quase a meta de 10 s. Qual lado da meta o sistema cai depende da execução.
- **A guarda sintática se pagou.** Foi escrita para conter código malicioso; o que apareceu
  foi código quebrado. Barrou o erro antes do `eval`, sem gastar chamada nem risco.
- **É o caso mais barato para o Validador do Entregável 2 resolver:** devolver a mensagem de
  erro ao modelo e pedir nova tentativa converte esta falha em acerto, com custo só no caso
  que falhou.

O enunciado do Entregável 1 já advertia sobre isso na seção 3.2 ("temperature=0 reduz a
variação, mas não garante saídas idênticas em serviços de inferência distribuída"). O que
esta nota acrescenta é a medição própria.
