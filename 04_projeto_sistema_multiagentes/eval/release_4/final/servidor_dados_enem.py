"""Servidor MCP local: acesso de leitura ao artefato ENEM 2023 x IBGE 2021.

Sobe como subprocesso e conversa por stdio. Nao acessa rede: le apenas o CSV
cujo caminho e passado como argumento de linha de comando.
"""

import json
import re
import sys
import unicodedata

import pandas as pd
from mcp.server.fastmcp import FastMCP

CAMINHO_CSV = sys.argv[1] if len(sys.argv) > 1 else "enem2023_ibge_municipios.csv"

df = pd.read_csv(CAMINHO_CSV)

DESCRICOES = {
    "co_municipio":        "código IBGE do município (7 dígitos)",
    "municipio":           "nome do município (ex.: 'Campinas', 'São Paulo')",
    "uf":                  "sigla da UF (ex.: 'SP', 'BA')",
    "regiao":              "Norte, Nordeste, Centro-Oeste, Sudeste ou Sul",
    "populacao_2021":      "população residente estimada em 2021 (IBGE)",
    "pib_2021_mil_reais":  "PIB municipal de 2021 em MIL reais (IBGE)",
    "n_participantes":     "candidatos do ENEM 2023 considerados na média do município",
    "media_cn":            "média da nota de Ciências da Natureza (0 a 1000)",
    "media_ch":            "média da nota de Ciências Humanas (0 a 1000)",
    "media_lc":            "média da nota de Linguagens e Códigos (0 a 1000)",
    "media_mt":            "média da nota de Matemática (0 a 1000)",
    "media_redacao":       "média da nota de Redação (0 a 1000)",
    "media_geral":         "média das cinco notas por candidato, agregada por município",
    "pct_escola_publica":  "percentual de participantes de escola pública (0 a 100)",
    "pib_per_capita_2021": "PIB por habitante em 2021, em reais",
}

mcp = FastMCP("dados-enem-ibge")


def _chave(texto: str) -> str:
    """Normaliza para comparação: sem acento, sem caixa, sem pontuação."""
    t = unicodedata.normalize("NFKD", str(texto).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t)


_CHAVES = df["municipio"].map(_chave)


@mcp.tool()
def buscar_municipio(nome: str, uf: str | None = None) -> str:
    """Confirma como um município é grafado no dataset e revela homônimos.

    Use SEMPRE antes de escrever um filtro por nome de município. A busca ignora
    acentos, caixa, hifens e apóstrofos, então 'sao jose', 'Sao José' e
    'São José' chegam ao mesmo registro. O nome armazenado segue a grafia do
    IBGE, que às vezes surpreende (por exemplo, o dataset tem
    "Sant'Ana do Livramento", não "Santana do Livramento").

    Argumentos:
        nome: nome do município como apareceu na pergunta do usuário.
        uf: sigla da UF (por exemplo "RS") para restringir a busca; opcional.

    Devolve JSON com 'encontrados' (quantos municípios casaram), 'candidatos'
    (grafia exata, uf, n_participantes e media_geral de cada um) e 'aviso'
    quando há homônimos em mais de uma UF. Use a grafia exata devolvida aqui
    dentro do codigo_pandas.
    """
    alvo = _chave(nome)
    exato = _CHAVES == alvo
    selecao = exato if bool(exato.any()) else _CHAVES.str.contains(alvo, regex=False)

    sub = df[selecao]
    if uf:
        sub = sub[sub["uf"] == uf.strip().upper()]

    candidatos = [
        {
            "municipio": r["municipio"],
            "uf": r["uf"],
            "n_participantes": int(r["n_participantes"]),
            "media_geral": float(r["media_geral"]),
        }
        for _, r in sub.sort_values("n_participantes", ascending=False).head(12).iterrows()
    ]

    resposta = {
        "consulta": {"nome": nome, "uf": uf},
        "encontrados": int(len(sub)),
        "candidatos": candidatos,
    }
    if len(sub) == 0:
        resposta["aviso"] = (
            "Nenhum município do dataset casou com esse nome. Verifique a grafia ou "
            "considere que o município pode não ter participantes no recorte."
        )
    elif sub["uf"].nunique() > 1:
        resposta["aviso"] = (
            f"Homônimos: {len(sub)} municípios com esse nome, em "
            f"{sorted(sub['uf'].unique())}. Filtre por uf ou responda sobre todos, "
            "deixando o recorte explícito."
        )

    print(f"[servidor] buscar_municipio(nome={nome!r}, uf={uf!r}) -> "
          f"{len(sub)} municipio(s)", file=sys.stderr, flush=True)
    return json.dumps(resposta, ensure_ascii=False)


@mcp.resource("dataset://enem2023/esquema")
def esquema() -> str:
    """Descrição das colunas do artefato ENEM 2023 x IBGE 2021."""
    print("[servidor] resource dataset://enem2023/esquema", file=sys.stderr, flush=True)
    return "\n".join(f"- {c} ({df[c].dtype}): {DESCRICOES[c]}" for c in df.columns)


if __name__ == "__main__":
    print(f"[servidor] pronto: {df.shape[0]} municipios x {df.shape[1]} colunas "
          f"de {CAMINHO_CSV}", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
