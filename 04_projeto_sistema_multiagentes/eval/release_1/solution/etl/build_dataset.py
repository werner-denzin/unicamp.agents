#!/usr/bin/env python3
"""ETL do Entregável 1 — INF0093 (Semana 0, executado UMA vez, fora do grafo).

Constrói o artefato leve que o sistema consulta em tempo de execução:
uma linha por município da escola do candidato, com as médias do ENEM 2023
e dois indicadores municipais do IBGE (população estimada e PIB de 2021).

Fontes:
  - INEP, Microdados do ENEM 2023 (zip ~550 MB, CSV ~1,8 GB)
    https://download.inep.gov.br/microdados/microdados_enem_2023.zip
  - IBGE, API de Agregados v3 — agregado 6579 (população residente estimada, 2021)
  - IBGE, API de Agregados v3 — agregado 5938 (PIB a preços correntes, 2021)
  - IBGE, API de Localidades v1 — municípios (nome, UF, região)

Uso:
    python build_dataset.py --trabalho /tmp/enem --saida ../dados

O download do INEP costuma cair no meio; o script retoma (-C -) e repete.
O certificado de download.inep.gov.br não valida na cadeia padrão de vários
sistemas, por isso a verificação TLS é desligada apenas para esse host.
"""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL_ENEM = "https://download.inep.gov.br/microdados/microdados_enem_2023.zip"
URL_POP = ("https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021"
           "/variaveis/9324?localidades=N6[all]")
URL_PIB = ("https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021"
           "/variaveis/37?localidades=N6[all]")
URL_MUN = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

SUFIXO_CSV = "DADOS/MICRODADOS_ENEM_2023.csv"

COLUNAS_ENEM = [
    "CO_MUNICIPIO_ESC", "NO_MUNICIPIO_ESC", "SG_UF_ESC", "TP_ESCOLA",
    "TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT",
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
]
AREAS = ["CN", "CH", "LC", "MT"]


# --------------------------------------------------------------------------- #
# download
# --------------------------------------------------------------------------- #
def baixar(url: str, destino: Path, verificar_tls: bool = True) -> Path:
    if destino.exists() and destino.stat().st_size > 0:
        print(f"[cache] {destino.name} ({destino.stat().st_size/1e6:.1f} MB)")
        return destino
    contexto = None if verificar_tls else ssl._create_unverified_context()
    print(f"[get  ] {url}")
    with urllib.request.urlopen(url, context=contexto) as r, destino.open("wb") as f:
        while bloco := r.read(1 << 20):
            f.write(bloco)
    print(f"[ok   ] {destino.name} ({destino.stat().st_size/1e6:.1f} MB)")
    return destino


# --------------------------------------------------------------------------- #
# IBGE
# --------------------------------------------------------------------------- #
def ler_agregado(caminho: Path, coluna: str) -> pd.DataFrame:
    """Achata a resposta da API de Agregados v3 em (co_municipio, <coluna>)."""
    linhas = []
    for variavel in json.loads(caminho.read_text(encoding="utf-8")):
        for resultado in variavel["resultados"]:
            for serie in resultado["series"]:
                (_, valor), = serie["serie"].items()
                linhas.append({
                    "co_municipio": int(serie["localidade"]["id"]),
                    coluna: pd.to_numeric(valor, errors="coerce"),
                })
    return pd.DataFrame(linhas)


def ler_municipios(caminho: Path) -> pd.DataFrame:
    """Nome, UF e região de cada município.

    Municípios criados recentemente vêm com `microrregiao` nula; nesses casos a
    UF só aparece em `regiao-imediata`. Ignorar isso derruba o ETL.
    """
    def uf_de(m: dict) -> dict:
        micro = m.get("microrregiao")
        if micro:
            return micro["mesorregiao"]["UF"]
        return m["regiao-imediata"]["regiao-intermediaria"]["UF"]

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return pd.DataFrame([{
        "co_municipio": m["id"],
        "municipio": m["nome"],
        "uf": uf_de(m)["sigla"],
        "regiao": uf_de(m)["regiao"]["nome"],
    } for m in dados])


# --------------------------------------------------------------------------- #
# ENEM
# --------------------------------------------------------------------------- #
def agregar_enem(zip_path: Path, tamanho_bloco: int = 400_000) -> pd.DataFrame:
    """Percorre o CSV de 1,8 GB em blocos e soma notas por município da escola.

    Participante = presente nos dois dias (TP_PRESENCA_* == 1 nas quatro áreas)
    e com as cinco notas preenchidas. Só entram candidatos com escola declarada,
    porque é a escola que dá o vínculo municipal usado no cruzamento com o IBGE.
    """
    parciais = []
    notas = [f"NU_NOTA_{a}" for a in AREAS] + ["NU_NOTA_REDACAO"]

    with zipfile.ZipFile(zip_path) as z:
        interno = next(n for n in z.namelist() if n.endswith(SUFIXO_CSV))
        with z.open(interno) as fluxo:
            leitor = pd.read_csv(
                fluxo, sep=";", encoding="latin-1", usecols=COLUNAS_ENEM,
                chunksize=tamanho_bloco, low_memory=False,
            )
            for i, bloco in enumerate(leitor, 1):
                presente = (bloco[[f"TP_PRESENCA_{a}" for a in AREAS]] == 1).all(axis=1)
                bloco = bloco[bloco["CO_MUNICIPIO_ESC"].notna()
                              & presente
                              & bloco[notas].notna().all(axis=1)]
                if bloco.empty:
                    continue

                bloco = bloco.assign(
                    co_municipio=bloco["CO_MUNICIPIO_ESC"].astype("int64"),
                    media_geral=bloco[notas].mean(axis=1),
                    publica=(bloco["TP_ESCOLA"] == 2).astype("int64"),
                )
                parciais.append(bloco.groupby("co_municipio").agg(
                    n_participantes=("media_geral", "size"),
                    soma_cn=("NU_NOTA_CN", "sum"),
                    soma_ch=("NU_NOTA_CH", "sum"),
                    soma_lc=("NU_NOTA_LC", "sum"),
                    soma_mt=("NU_NOTA_MT", "sum"),
                    soma_red=("NU_NOTA_REDACAO", "sum"),
                    soma_geral=("media_geral", "sum"),
                    n_publica=("publica", "sum"),
                ))
                print(f"[bloco] {i:>3} lido", flush=True)

    total = pd.concat(parciais).groupby(level=0).sum()
    saida = pd.DataFrame({
        "n_participantes": total["n_participantes"],
        "media_cn": total["soma_cn"] / total["n_participantes"],
        "media_ch": total["soma_ch"] / total["n_participantes"],
        "media_lc": total["soma_lc"] / total["n_participantes"],
        "media_mt": total["soma_mt"] / total["n_participantes"],
        "media_redacao": total["soma_red"] / total["n_participantes"],
        "media_geral": total["soma_geral"] / total["n_participantes"],
        "pct_escola_publica": 100 * total["n_publica"] / total["n_participantes"],
    }).reset_index()
    return saida


# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trabalho", type=Path, required=True, help="diretório de downloads")
    p.add_argument("--saida", type=Path, required=True, help="onde gravar o CSV final")
    args = p.parse_args()
    args.trabalho.mkdir(parents=True, exist_ok=True)
    args.saida.mkdir(parents=True, exist_ok=True)

    zip_enem = baixar(URL_ENEM, args.trabalho / "enem2023.zip", verificar_tls=False)
    f_pop = baixar(URL_POP, args.trabalho / "ibge_pop_2021.json")
    f_pib = baixar(URL_PIB, args.trabalho / "ibge_pib_2021.json")
    f_mun = baixar(URL_MUN, args.trabalho / "ibge_municipios.json")

    cache_enem = args.trabalho / "enem2023_agregado_municipio.csv"
    if cache_enem.exists():
        enem = pd.read_csv(cache_enem)
        print(f"[cache] {cache_enem.name}")
    else:
        enem = agregar_enem(zip_enem)
        enem.to_csv(cache_enem, index=False)
    print(f"[enem ] {len(enem)} municípios, "
          f"{int(enem['n_participantes'].sum())} participantes")

    df = (ler_municipios(f_mun)
          .merge(ler_agregado(f_pop, "populacao_2021"), on="co_municipio", how="left")
          .merge(ler_agregado(f_pib, "pib_2021_mil_reais"), on="co_municipio", how="left")
          .merge(enem, on="co_municipio", how="inner"))

    # PIB per capita: o IBGE publica PIB em mil reais; população é do mesmo ano.
    df["pib_per_capita_2021"] = (df["pib_2021_mil_reais"] * 1_000
                                 / df["populacao_2021"]).round(2)

    numericas = [c for c in df.columns if c.startswith(("media_", "pct_"))]
    df[numericas] = df[numericas].round(2)
    df = df.sort_values(["uf", "municipio"]).reset_index(drop=True)

    destino = args.saida / "enem2023_ibge_municipios.csv"
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"[fim  ] {destino} — {len(df)} linhas, "
          f"{destino.stat().st_size/1e6:.2f} MB")
    print(df.head())


if __name__ == "__main__":
    main()
