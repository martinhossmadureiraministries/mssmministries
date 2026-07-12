"""
MÓDULO DE GESTÃO DO MANIFESTO — Escola Bíblica Epignósis

O manifesto é a ÚNICA fonte de verdade sobre o progresso de geração
das apostilas. Nunca se decide com base na presença/ausência do
ficheiro .docx — apenas o manifesto determina o que já foi gerado.

Formato: JSON com uma lista de entradas, cada uma contendo:
  - id: identificador único (número da apostila, 1–1029)
  - status: "pendente" | "gerado" | "falhou"
  - data_geracao: ISO timestamp ou null
  - caminho: caminho relativo do .docx no repositório
  - erro: mensagem de erro (se status="falhou"), ou null
  - tentativas: número de tentativas de geração
"""

import json
import os
from datetime import datetime, timezone

MANIFESTO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "progress", "manifesto.json")


def carregar_manifesto(caminho=None):
    """Carrega o manifesto do disco. Se não existe, cria vazio."""
    caminho = caminho or MANIFESTO_PATH
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    return {"apostilas": [], "metadata": {
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "ultima_actualizacao": None,
    }}


def guardar_manifesto(manifesto, caminho=None):
    """Guarda o manifesto no disco."""
    caminho = caminho or MANIFESTO_PATH
    manifesto["metadata"]["ultima_actualizacao"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)


def inicializar_manifesto(apostilas_data, caminho=None):
    """
    Cria o manifesto inicial com todas as apostilas do currículo.
    Se o manifesto já existe, preserva os status já registados.

    Args:
        apostilas_data: lista de dicionários com dados do currículo
                        (do módulo curriculo.py)
        caminho: caminho alternativo para o manifesto
    """
    manifesto = carregar_manifesto(caminho)

    # Indexar apostilas já registadas por id
    existentes = {}
    for entry in manifesto["apostilas"]:
        existentes[entry["id"]] = entry

    # Construir lista completa, preservando status existentes
    novas_apostilas = []
    for a in apostilas_data:
        aid = a["numero"]
        if aid in existentes:
            # Preservar o registo existente (pode ter status="gerado")
            novas_apostilas.append(existentes[aid])
        else:
            # Nova entrada pendente
            novas_apostilas.append({
                "id": aid,
                "titulo": a["titulo"],
                "nivel": a["nivel"],
                "instituto": a["instituto"],
                "instituto_nome": a["instituto_nome"],
                "escola": a["escola"],
                "curso": a["curso"],
                "modulo": a["modulo"],
                "modulo_nome": a["modulo_nome"],
                "status": "pendente",
                "data_geracao": None,
                "caminho": None,
                "erro": None,
                "tentativas": 0,
            })

    manifesto["apostilas"] = novas_apostilas
    manifesto["metadata"]["total_apostilas"] = len(novas_apostilas)
    guardar_manifesto(manifesto, caminho)
    return manifesto


def obter_pendentes(manifesto, limite=10):
    """
    Retorna as próximas N apostilas pendentes, na ordem do currículo.
    Prioriza apostilas que falharam (para retentativa) antes das
    nunca tentadas, mas respeita a ordem numérica.
    """
    pendentes = [a for a in manifesto["apostilas"]
                 if a["status"] in ("pendente", "falhou")]
    # Ordenar por número (ordem do currículo)
    pendentes.sort(key=lambda x: x["id"])
    return pendentes[:limite]


def marcar_gerado(manifesto, apostila_id, caminho_ficheiro):
    """Marca uma apostila como gerada com sucesso."""
    for a in manifesto["apostilas"]:
        if a["id"] == apostila_id:
            a["status"] = "gerado"
            a["data_geracao"] = datetime.now(timezone.utc).isoformat()
            a["caminho"] = caminho_ficheiro
            a["erro"] = None
            a["tentativas"] += 1
            return True
    return False


def marcar_falha(manifesto, apostila_id, erro_msg):
    """Marca uma apostila como falhada, com mensagem de erro."""
    for a in manifesto["apostilas"]:
        if a["id"] == apostila_id:
            a["status"] = "falhou"
            a["erro"] = erro_msg
            a["tentativas"] += 1
            return True
    return False


def estatisticas(manifesto):
    """Retorna estatísticas agregadas do manifesto."""
    total = len(manifesto["apostilas"])
    gerados = sum(1 for a in manifesto["apostilas"] if a["status"] == "gerado")
    pendentes = sum(1 for a in manifesto["apostilas"] if a["status"] == "pendente")
    falhados = sum(1 for a in manifesto["apostilas"] if a["status"] == "falhou")
    pct = (gerados / total * 100) if total > 0 else 0

    return {
        "total": total,
        "gerados": gerados,
        "pendentes": pendentes,
        "falhados": falhados,
        "percentagem": round(pct, 1),
    }


if __name__ == "__main__":
    # Teste: inicializar o manifesto com o currículo completo
    from curriculo import APOSTILAS
    manifesto = inicializar_manifesto(APOSTILAS)
    stats = estatisticas(manifesto)
    print(f"Manifesto inicializado: {stats}")
