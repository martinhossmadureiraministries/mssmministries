"""Mostra o resumo da execucao."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifesto import carregar_manifesto, estatisticas

if os.path.exists("progress/manifesto.json"):
    manifesto = carregar_manifesto()
    stats = estatisticas(manifesto)
    print("RESUMO: " + str(stats["gerados"]) + "/" + str(stats["total"]) + " apostilas geradas (" + str(stats["percentagem"]) + "%)")
    print("  Geradas: " + str(stats["gerados"]))
    print("  Pendentes: " + str(stats["pendentes"]))
    print("  Falhadas: " + str(stats["falhados"]))
else:
    print("Manifesto nao encontrado")
