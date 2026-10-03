# Guia: demonstração ao vivo do T17 na v4

Slide 7 da apresentação, ~1:30, apresentado pelo Rodolfo. O enunciado (seção 3.1) exige dizer se a execução é ao vivo ou salva, e permite manter no vídeo uma falha ao vivo, desde que comentada.

O caso é o **T17**, uma pergunta composta sobre um município de grafia irregular:

> Qual é a média em matemática de Santana do Livramento, e quantos participantes ela teve?

Resultado correto: **530,26** de média em matemática e **275** participantes.

---

## 1. Na véspera: preparar uma cópia do entregável

Não rode a demonstração na pasta `20261003_v_entregavel/`. O "Executar tudo" regrava `servidor_mcp.log` e `e4_resultados.json`, que são parte da entrega.

```bash
cd 04_projeto_sistema_multiagentes/eval/release_4
cp -r 20261003_v_entregavel demo_ao_vivo        # não fazer commit desta pasta
```

Mantenha a cópia dentro de `eval/`. O notebook procura a chave em `eval/.secret` (até 4 pastas acima). Fora dali, defina a variável `GROQ_API_KEY` antes de abrir o Jupyter.

**Verifique:**

- [ ] O ambiente Python tem `langgraph`, `mcp`, `langchain-mcp-adapters`, `langchain-groq`, `pandas` e `pydantic`. A célula 2 instala o que faltar.
- [ ] Há internet: a célula A baixa o CSV do GitHub, e o modelo roda na Groq.
- [ ] A chave carrega. A célula 4 deve imprimir `Chave carregada via: arquivo eval/.secret` ou `variável de ambiente`.

## 2. Cota da Groq

A chave tem 200.000 tokens por dia e **8.000 tokens por minuto**. Nas três rodadas, o T17 gastou entre 2 mil e 10 mil tokens por execução, levando de 5 a 28 s.

- Um ensaio mais a gravação cabem com folga na cota diária.
- **Espere pelo menos 90 s entre duas execuções.** Uma execução sozinha pode encostar no limite por minuto, e duas seguidas provocam erro 429.
- Não rode nenhuma outra célula que chame o modelo logo antes de gravar.

## 3. Antes de gravar

1. Abra `demo_ao_vivo/E4_DallaCosta_Murer_Denzin.ipynb` (VS Code ou Jupyter) e execute **todas as células**.
   - Nenhuma célula das seções D a K chama o provedor: todas leem os checkpoints `v4_rodada_N.jsonl`. O "Executar tudo" leva poucos minutos e não gasta cota.
   - Confira que nenhuma célula terminou em erro, principalmente a A.3, que sobe o servidor MCP, e a C.3, que compila o grafo.
2. No fim do notebook, crie as duas células da seção 4 abaixo. Não as execute ainda.
3. Ajuste a tela para o vídeo:
   - fonte do editor em 16 a 18;
   - painel lateral fechado;
   - célula da demonstração no topo da tela;
   - saída da célula sem limite de altura, para não precisar rolar.

## 4. As células da demonstração

### Célula 1: execução ao vivo

```python
# DEMONSTRAÇÃO AO VIVO — T17 na v4 (uma execução, sem retentativa externa)
caso = next(c for c in TODOS_OS_CASOS if c["id"] == "T17")
print("PERGUNTA:", caso["pergunta"], "\n")

resposta, metricas, estado = await responder_v4(caso["pergunta"])

print("ROTA:", " > ".join(metricas["rota"]), "\n")
for t in estado.get("trace") or []:
    print(f'[{t["etapa"]:<12}] {str(t.get("decisao"))[:38]:<38} | {str(t.get("motivo"))[:80]}')
    if t.get("tool_calls"):
        print(" " * 15, "ferramenta:", t["tool_calls"])
    if t.get("codigo"):
        print(" " * 15, "código    :", t["codigo"][:110])
    if t.get("erro") and t["erro"] != "None":
        print(" " * 15, "erro      :", str(t["erro"])[:110])

print("\nRESPOSTA ENTREGUE:\n ", resposta.texto.split("Recorte:")[0].strip())
print("\nCÓDIGO EXECUTADO:", resposta.codigo)
print("RESULTADO       :", formatar_valor(resposta.resultado))
print(f'\n{metricas["chamadas_llm"]} chamadas ao LLM · {metricas["latencia_s"]} s · '
      f'degradada: {metricas["degradado"]} · conferência: '
      f'{metricas["problemas_verificacao"] or "sem problemas"}')
print("Régua do E1:", avaliar(caso, resposta))
```

### Célula 2: plano B, a execução salva

Use esta célula se a cota acabar ou se a rede cair. Ela não chama o modelo.

```python
reconstruir("T17", 2)    # rodada 2: mostra o refazer sem LLM
```

## 5. Durante a gravação

| Momento | O que fazer | O que dizer |
|---|---|---|
| Início | Mostrar a célula 1 ainda sem executar | "Esta é uma **execução ao vivo** da v4, no caso T17: uma pergunta composta sobre Santana do Livramento, que no IBGE se escreve com apóstrofo." |
| Executar | `Shift+Enter` | "A execução leva de 5 a 30 segundos, porque passa por três agentes e pelo servidor MCP." |
| Espera | Apontar a célula enquanto roda | "Primeiro o Resolvedor consulta o servidor MCP para confirmar a grafia. Depois o Planejador escreve uma única consulta pandas com os dois valores, o Executor roda o código, o Validador julga o resultado e o Sintetizador redige." |
| Saída: rota e trace | Rolar devagar pelo trace | Ler a rota. Mostrar `buscar_municipio` e o código com `Sant'Ana do Livramento`. Se aparecer `refazer sem LLM`: "aqui a guarda recusou o código e o sistema devolveu ao planejador sem chamar o modelo". |
| Saída: resposta | Destacar a resposta e o resultado | "530,26 e 275 participantes, os dois corretos. O número vem da execução do código, que está aqui embaixo, e não do texto do modelo." |
| Fechamento | Mostrar a última linha | "A régua do E1 aprova, e a conferência final não encontrou problemas. Foram N chamadas ao modelo." |

O total fica em ~1:30. Se a execução demorar mais de 40 s, continue narrando o fluxo, sem silêncio.

## 6. Se algo der errado ao vivo

| O que aparece | Leitura | O que fazer |
|---|---|---|
| Resposta começa com `[resposta em modo degradado] … 400 … Failed to generate JSON` | A mesma falha da rodada 1. O provedor não gerou o plano, e a v4 se absteve e se declarou degradada. | **Manter no vídeo** e comentar: "a contenção funcionou: em vez de uma resposta errada, o sistema avisa que não conseguiu responder. É a correção nº 1 da nossa lista: tratar esse erro como transitório." Depois, opcionalmente, rodar a célula 2. |
| Trace mostra `refazer sem LLM` | Erro de geração corrigido sem chamar o modelo, como na rodada 2. | Ótimo para o vídeo: destacar. |
| Rota sem `refazer`, acerto de primeira | Como na rodada 3. | Normal: dizer que o refazer "só entra quando o código falha". |
| `RateLimitError` / `429` | Limite de tokens por minuto. | Esperar 90 s e executar de novo. Se for gravação contínua, comentar e ir para a célula 2. |
| Erro de cota diária (`tokens per day`) | Cota de 200k esgotada. | Usar a célula 2 e dizer: "esta é a **execução salva** da rodada 2". |
| `NameError` em `responder_v4`, `TODOS_OS_CASOS` etc. | O notebook não foi executado até o fim. | Executar tudo antes de gravar (seção 3). |
| Erro ao subir o servidor MCP (célula A.3) | Caminho do CSV ou do `servidor_dados_enem.py`. | Executar o Jupyter a partir da pasta `demo_ao_vivo/`, onde os dois arquivos estão. |

## 7. Ajuste no slide 7

O slide 7 e as notas assumem a execução salva ("Execução salva: rodada 2 da seção D"). Se a demonstração for ao vivo, troque essa linha por "Execução ao vivo" no PowerPoint. Se cair no plano B, mantenha o texto original.

## 8. Ensaio rápido (5 minutos, na véspera)

- [ ] Executar tudo na cópia, sem erros.
- [ ] Rodar a célula 1 uma vez e cronometrar a narração com a execução.
- [ ] Rodar a célula 2 e confirmar que o plano B funciona.
- [ ] Testar o áudio do OBS ou do Meet com a tela do notebook em 1280×720 ou mais.
- [ ] Esperar 90 s antes de gravar a tomada definitiva.
