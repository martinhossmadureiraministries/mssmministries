"""Gera o relatorio de progresso em progress/RELATORIO.md"""
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifesto import carregar_manifesto, estatisticas

manifesto = carregar_manifesto()
stats = estatisticas(manifesto)
ritmo_diario = 10
pendentes = stats["pendentes"] + stats["falhados"]
dias_restantes = (pendentes + ritmo_diario - 1) // ritmo_diario if pendentes > 0 else 0
agora = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

linhas = [
    "# Progresso da Geracao de Apostilas EBE",
    "",
    "| Indicador | Valor |",
    "|---|---|",
    "| Total de apostilas | " + str(stats["total"]) + " |",
    "| Geradas | " + str(stats["gerados"]) + " |",
    "| Pendentes | " + str(stats["pendentes"]) + " |",
    "| Falhadas | " + str(stats["falhados"]) + " |",
    "| Progresso | " + str(stats["percentagem"]) + "% |",
    "| Ritmo diario | " + str(ritmo_diario) + " apostilas/dia |",
    "| Previsao de conclusao | ~" + str(dias_restantes) + " dias |",
    "",
    "> Ultima actualizacao: " + agora,
    "",
    "O manifesto em progress/manifesto.json e a unica fonte de verdade.",
]

with open("progress/RELATORIO.md", "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))
print("Relatorio gerado: " + str(stats["gerados"]) + "/" + str(stats["total"]))
