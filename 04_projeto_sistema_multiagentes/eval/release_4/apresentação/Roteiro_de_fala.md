# Roteiro de fala — Apresentação final (E4)

INF0093 · Rodolfo Dalla Costa, Thais Caroline Murer, Werner Conrado Jacob Denzin

Tempo-alvo: ~8:15 (limite do enunciado: 5 a 10 minutos). Se o ensaio passar de 9:30, cortar nos slides 4 e 6.

| # | Slide | Quem | Tempo |
|---|---|---|---|
| 1 | Capa | Werner | ~0:10 |
| 2 | Problema e usuário | Thais | ~0:45 |
| 3 | Baseline (v1) | Thais | ~0:50 |
| 4 | Da v1 à v4 | Thais | ~0:25 |
| 5 | Arquitetura final | Werner | ~1:00 |
| 6 | Decisões e motivos | Werner | ~0:50 |
| 7 | Demonstração (T17) | Rodolfo | ~1:30 |
| 8 | Resultados | Rodolfo | ~0:50 |
| 9 | Leitura honesta | Rodolfo | ~0:40 |
| 10 | Recomendação | Werner | ~0:40 |
| 11 | Ressalvas | Thais | ~0:35 |
| 12 | Obrigado | Thais | ~0:05 |

---

## 1. Capa — Werner (~0:10)

Olá, somos Rodolfo, Thais e Werner. Este é o nosso projeto de INF0093: um sistema multiagente que responde perguntas em linguagem natural sobre o ENEM 2023. Vamos mostrar o problema, como o sistema evoluiu em quatro versões, uma demonstração e qual versão levaríamos para uso real.

## 2. Problema e usuário — Thais (~0:45)

O problema: os dados do ENEM e do IBGE são públicos, mas responder uma pergunta simples exige conhecer o esquema da base. Nosso usuário é quem sabe o que quer perguntar, como um jornalista, um gestor ou um estudante, mas não conhece as colunas nem as armadilhas dos dados.

E as armadilhas são concretas: o IBGE grafa Sant'Ana do Livramento com apóstrofo; existem cinco municípios chamados Bom Jesus; e o município com a maior média do país, Uru, tem um único participante.

Uma busca manual tropeça nisso. O nosso sistema traduz a pergunta em uma consulta pandas, executa, confere o resultado e devolve o número junto com o código que o produziu, para que qualquer pessoa possa auditar.

## 3. Baseline (v1) — Thais (~0:50)

A primeira versão, do E1, era simples: uma única chamada ao LLM, que gerava o código pandas e também o texto da resposta, e um executor determinístico com uma guarda sintática.

Ela acertava os casos automáticos, 11 de 11. Mas tinha limitações concretas. Primeiro, o texto era escrito antes de o número existir, na mesma chamada que gerava o código. Segundo, ninguém julgava o resultado: no caso T12 ela respondeu que o melhor município para estudar é Uru, com média baseada em um único participante. Terceiro, resolvia ambiguidades em silêncio: perguntada sobre a média de São Paulo, deu a da cidade sem avisar que existia a leitura do estado.

Esses erros não apareciam na taxa automática, só na rubrica manual, onde ela tirou zero. Essa é a origem de tudo o que veio depois.

## 4. Da v1 à v4 — Thais (~0:25)

Daí em diante, cada versão respondeu a uma limitação da anterior. A v2 trouxe um servidor MCP que confirma a grafia do IBGE e revela homônimos. A v3 dividiu o trabalho em agentes: um Validador que julga o resultado e um Sintetizador que só escreve depois que o número existe. A v4, deste último entregável, acrescentou contenção de falhas e uma conferência final, porque a v3 perdeu o caso T18 com um erro 429 do provedor e perdeu em silêncio um achado do validador no T15.

Um detalhe importante: o prompt do planejador é o mesmo desde a v1, para que as diferenças entre versões possam ser atribuídas à arquitetura. Agora o Werner mostra como o sistema ficou.

## 5. Arquitetura final — Werner (~1:00)

Esta é a arquitetura final, a v4. A pergunta passa por seis nós.

O Resolvedor é um agente que identifica os municípios citados e consulta o servidor MCP, que devolve a grafia oficial do IBGE e os homônimos. O Planejador é o LLM que escreve a consulta pandas, com o mesmo prompt da v1. O Executor é determinístico: passa o código por uma guarda sintática e executa. O Validador é um agente com três skills, carregadas sob demanda, que julga se o resultado responde de fato à pergunta; se reprova, a consulta volta ao Planejador, no máximo duas vezes. O Sintetizador redige a resposta a partir de uma ficha fechada, depois que o número existe. E a Conferência, nova na v4, roda três verificações determinísticas de falha silenciosa no texto final.

O que está em laranja é o que a v4 acrescentou: retentativa, tempo limite e degradação declarada na ferramenta; o refazer sem LLM, quando o erro de execução tem padrão conhecido; e a resposta de reserva, montada da ficha quando o Sintetizador falha.

## 6. Decisões e motivos — Werner (~0:50)

Cada decisão tem um motivo. O LLM nunca escreve o número: escreve a consulta, e o número vem da execução, o que deixa o código como evidência auditável. A identidade do município vem do servidor MCP, porque grafia e homônimos não cabem no prompt. O Validador carrega só a instrução da skill que precisa, uma de três, a partir de um índice onze vezes menor.

O Sintetizador só vê a ficha: isso impede que ele invente números, mas tem um custo, porque ele não recupera um achado que ficou fora da ficha, foi o que aconteceu no T15 da v3.

Na v4, o veredito do Validador virou uma ferramenta do laço, o que reduziu as chamadas de 67 para 57,7; erros mecânicos conhecidos são refeitos sem chamar o modelo; e a conferência transforma falha silenciosa em aviso. Por fim, mantivemos o prompt do planejador idêntico ao da v1 de propósito, para poder comparar as versões.

## 7. Demonstração (T17) — Rodolfo (~1:30)

*Trocar este slide pela gravação de tela do notebook.*

Agora a demonstração. Escolhemos o T17, um caso composto e difícil: a pergunta pede dois valores sobre um município cuja grafia oficial tem apóstrofo, Sant'Ana do Livramento. Vamos mostrar uma execução salva, a da rodada 2 da seção D, gravada em v4_rodada_2.jsonl. (Se a execução for ao vivo, dizer: "esta é uma execução ao vivo".)

Repare no trace. O Resolvedor consulta o servidor MCP com o nome como o usuário escreveu e recebe a grafia do IBGE. O Planejador escreve uma única expressão pandas com os dois valores. A guarda sintática recusa essa primeira versão. O executor reconhece um erro de padrão conhecido e devolve ao Planejador com uma instrução de correção, sem chamar o modelo. A segunda versão executa, o Validador aprova, o Sintetizador redige e a conferência não encontra problema.

Resultado: média de 530,26 e 275 participantes, os dois corretos.

(Se perguntarem: o erro da guarda nessa rodada foi "unexpected indent", porque o código começava com um espaço e também aninhava aspas simples; a instrução aplicada foi a genérica de expressão única.) Este mesmo caso falhou na rodada 1: o provedor devolveu um erro 400 ao planejador e a resposta saiu como abstenção marcada como degradada. Voltamos a isso nas ressalvas.

## 8. Resultados — Rodolfo (~0:50)

Os resultados. A régua comum são os 13 casos congelados do E1, os únicos que as quatro versões enfrentaram; 11 deles têm verificação automática.

Em acerto, as quatro empatam: 11, 10, 11 e 11. A v4 foi a única medida três vezes na mesma sessão, e deu 11 nas três. As faixas plausíveis de Wilson são largas, de 74 a 100 por cento, porque 11 casos é pouco.

Em custo, a v1 é a mais barata, cerca de um quarto da v4. Entre v3 e v4, a v4 faz menos chamadas, 57,7 contra 67, mas o custo em dólares é praticamente o mesmo.

Na última linha, a qualidade ponderada pela gravidade do erro, incluindo os casos de rubrica manual: aqui a v3 fica à frente da v4.

## 9. Leitura honesta — Rodolfo (~0:40)

Como ler esses números com honestidade? Primeiro: os seis pares de versões têm faixas plausíveis sobrepostas, então nenhuma versão é superior em acerto agregado. Segundo: a mesma versão, sem nenhuma mudança de código, variou um caso entre sessões. A v1 deu 11 no E1 e 10 no E2; a v2 deu 10 e depois 11. Ou seja, uma diferença de um caso é do tamanho do ruído.

Terceiro: das quatro mudanças de resultado entre versões consecutivas, só uma tem mecanismo identificável no trace, o T18 entre v3 e v4. T03 e T14 mudaram sem que nenhum componente novo atuasse.

Por isso, a nossa evidência é sempre o caso específico, com o trace explicando a mudança. Com isso, o Werner apresenta a recomendação.

## 10. Recomendação — Werner (~0:40)

A nossa recomendação: levaríamos a v4 para uso real, otimizando previsibilidade e auditabilidade, e não qualidade nem custo.

A evidência: primeiro, o T18. A v3 perdia uma abstenção correta quando o provedor falhava no último nó; a v4 a recupera nas três rodadas, por um mecanismo determinístico que não depende do provedor. Segundo, a v4 detecta falhas que a v3 entregava em silêncio: sete detecções em 57 execuções, os homônimos do T15 em todas as rodadas e uma subtração que o redator inventou no T08 em duas de três. Terceiro, é a única versão medida três vezes na mesma sessão, e deu 11 de 11 nas três. E faz tudo isso com menos chamadas que a v3, sem custo extra em dólares.

Ou seja: a v4 não acerta mais. Ela se comporta melhor quando algo dá errado. A Thais fecha com as ressalvas.

## 11. Ressalvas — Thais (~0:35)

E as ressalvas, porque elas fazem parte da recomendação. A v4 não acerta mais que as outras versões. Ela detecta problemas, mas não os corrige: no T15 o usuário recebe "169" seguido do aviso de que há cinco Bom Jesus, o que é melhor que "169" sozinho, mas não é uma boa resposta. A verificação também não pegou a amostra frágil do T12 em duas de três rodadas. Na rubrica manual, a v3 fica à frente. E quem quer apenas custo deve usar a v1.

Antes de uso real, três correções baratas: tratar o erro 400 de geração de JSON como transitório, que foi o único erro da v4 em 57 execuções; tirar o texto do erro do provedor da resposta; e estender a verificação de confiança ao T12. E, para uma v5, um canal para perguntar ao usuário quando a pergunta é ambígua.

## 12. Obrigado — Thais (~0:05)

Obrigado pela atenção!
