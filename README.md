# UNICAMP — Agentes Inteligentes com LLMs

Materiais, notebooks e atividades do curso da UNICAMP sobre IA Generativa, LLMs e
Sistemas Multiagentes. <br>
O conteúdo é didático — slides, notebooks de aula e as atividades
entregues. 

## Estrutura

```
01_fundamentos_IA_generativa_NLP/   NLP, Transformers, tokenização, fine-tuning (QLoRA)
02_LLM_sistemas_software/           LLMs via API, LangChain, RAG, avaliação
03_agentes_inteligentes_LLM/        Agentes com LangGraph e DeepAgents (módulo principal)
04_projeto_sistema_multiagentes/    Projeto final — ainda vazio
docs/                               Documentos administrativos do curso
extra/                              Nivelamento em Python (5 notebooks + links)
```

Convenções:<br> 
* `wN/` = semana do módulo<br>
* `eval/` = atividade avaliativa entregue
* `extra/` = material de apoio
* `*.cleaned.pdf` = versão enxuta do slide
* `Aula - Assíncrona/Síncrona *` = aulas gravadas / ao vivo

## Módulos

**1 — Fundamentos de IA Generativa e NLP.** 
* Quatro semanas indo de análise de dados
(`pandas`/`scikit-learn`) a tokenizers e Transformers (`transformers`/`torch`), fine-tuning
com QLoRA sobre Gemma 3 1B (`peft`/`trl`) e análise do dataset SmolTalk2. A entrega em
`eval/` é um pipeline completo de fine-tuning e avaliação.

**2 — LLMs em Sistemas de Software.** 
* Cinco notebooks: acesso a LLMs via API (Groq, OpenAI,
Google), prompt engineering, LangChain, RAG com embeddings HuggingFace e avaliação por ROUGE
e similaridade semântica. A entrega é um RAG completo com avaliação quantitativa.

**3 — Agentes Inteligentes com LLMs.** 
* O módulo mais extenso: 15 notebooks numerados sobre
**LangGraph** e **DeepAgents**, cobrindo, por semana — fundamentos e especificação de agentes
(w1) · grafos de estado (w2) · ferramentas, MCP e skills (w3) · reasoning, planning, ReWOO e
ToT (w4) · memória e memória reflexiva (w5) · sistemas multiagentes, protocolo A2A e avaliação
(w6). Aulas em PDF numeradas de `A1` a `A17`.