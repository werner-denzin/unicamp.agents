"""Executa as células do notebook com o LLM substituído por um dublê.

Objetivo: validar tudo que não depende da Groq — carga de dados, esquema,
guarda de segurança, execução, formatação, verificações, laço de experimentos
e agregação de resultados.
"""
import json, sys, types
from pathlib import Path

# Uso (a partir de release_1/, onde está ./dados):
#     python etl/test_nb.py
RELEASE = Path(__file__).resolve().parent.parent
NB = RELEASE / "E1_DallaCosta_Murer_Denzin.ipynb"
import os; os.chdir(RELEASE)

# --- planos que o dublê devolve, um por pergunta (inclui erros de propósito) ---
PLANOS = {
    "Campinas": (True, 'df.loc[(df.municipio == "Campinas") & (df.uf == "SP"), "media_geral"].item()',
                 "A média geral do ENEM 2023 em Campinas (SP) é {resultado}."),
    "Acre": (True, 'int((df.uf == "AC").sum())',
             "Há {resultado} municípios do Acre na base."),
    "maior média em matemática, considerando": (
        True, 'df[(df.uf == "SP") & (df.n_participantes >= 100)].nlargest(5, "media_mt")[["municipio", "media_mt"]]',
        "Os cinco municípios são: {resultado}."),
    "região do país": (True, 'df.groupby("regiao")["media_redacao"].mean().idxmax()',
                       "A região com maior média de redação é {resultado}."),
    "acima de 550": (True, 'int((df.media_geral > 550).sum())',
                     "{resultado} municípios têm média geral acima de 550."),
    "correlação": (True, 'df[df.n_participantes >= 50]["pib_per_capita_2021"].corr(df[df.n_participantes >= 50]["media_geral"])',
                   "A correlação é de {resultado}."),
    "mais populosos": (True, 'df.nlargest(10, "populacao_2021").nlargest(1, "media_mt")[["municipio", "media_mt"]]',
                       "Entre os dez mais populosos, o de maior média em matemática é {resultado}."),
    "Compare": (True, 'df.groupby("regiao")["media_geral"].mean()[["Nordeste", "Sul"]]',
                "A comparação: {resultado}."),
    "inglês": (False, "", ""),
    "IDH": (False, "", ""),
    "2019": (False, "", ""),
    "melhor município": (True, 'df[df.n_participantes >= 100].nlargest(1, "media_geral")[["municipio", "uf", "media_geral"]]',
                         "O município com maior média geral é {resultado}."),
    "média de São Paulo": (True, 'df.loc[(df.municipio == "São Paulo") & (df.uf == "SP"), "media_geral"].item()',
                           "A média geral do município de São Paulo é {resultado}."),
    # perguntas da demonstração da seção 13
    "Ceará": (True, 'df[df.uf == "CE"]["media_redacao"].mean()',
              "A média de redação no Ceará é {resultado}."),
    "escolas particulares": (False, "", ""),
}

class _Raw:
    usage_metadata = {"input_tokens": 900, "output_tokens": 120}

class StubLLM:
    """Dublê de `llm.with_structured_output(PlanoConsulta, include_raw=True)`."""
    def __init__(self, modelo):
        self.modelo = modelo
    def invoke(self, prompt):
        pergunta = prompt.rsplit("PERGUNTA:\n", 1)[-1].strip()
        for chave, (viavel, codigo, template) in PLANOS.items():
            if chave.lower() in pergunta.lower():
                plano = self.modelo(
                    viavel=viavel,
                    motivo=("estratégia planejada" if viavel else
                            "O recorte não tem essa informação; as colunas cobrem notas do "
                            "ENEM 2023, população e PIB municipais de 2021."),
                    codigo_pandas=codigo, template_resposta=template,
                    colunas_usadas=["media_geral"] if viavel else [],
                )
                return {"parsed": plano, "raw": _Raw(), "parsing_error": None}
        raise AssertionError(f"pergunta sem plano no dublê: {pergunta!r}")

nb = json.loads(NB.read_text())
codigos = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]

ambiente = {"__name__": "__main__", "StubLLM": StubLLM, "display": print}
pulados = 0
for i, fonte in enumerate(codigos):
    if fonte.startswith("%pip") or "carregar_chave_groq" in fonte or "ChatGroq" in fonte:
        pulados += 1
        continue
    fonte = fonte.replace("llm.with_structured_output(PlanoConsulta, method=\"json_schema\", include_raw=True)",
                          "StubLLM(PlanoConsulta)")
    # NUNCA sobrescrever o artefato da execução real: o dublê grava em outro nome e apaga no fim.
    fonte = fonte.replace('"baseline_v1_resultados.json"', '"baseline_v1_resultados.STUB.json"')
    if "RUN_INFO" not in ambiente:
        ambiente["RUN_INFO"] = {"modelo": "STUB", "temperatura": 0,
                                "prompt_versao": "v1", "data": "teste", "python": "3.12"}
    print(f"\n{'='*70}\n### célula de código {i}\n{'='*70}")
    try:
        exec(compile(fonte, f"<cell {i}>", "exec"), ambiente)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n!!! FALHA NA CÉLULA {i}")
        sys.exit(1)

Path("baseline_v1_resultados.STUB.json").unlink(missing_ok=True)
print(f"\n\nTODAS AS CÉLULAS EXECUTARAM ({pulados} puladas por dependerem da Groq)")
