# 📖 Fábrica de Apostilas — Escola Bíblica Epignósis (EBE)

**Sistema automático de geração das 1.029 apostilas do currículo completo da EBE**, usando GitHub Actions + API Gemini.

---

## 📊 Progresso

| Indicador | Valor |
|---|---|
| **Total de apostilas** | 1.029 |
| **Geradas** ✅ | 0 |
| **Pendentes** ⏳ | 1.029 |
| **Falhadas** ❌ | 0 |
| **Progresso** | 0.0% |
| **Ritmo diário** | 10 apostilas/dia (configurável) |
| **Previsão de conclusão** | ~103 dias |

> O manifesto em `progress/manifesto.json` é a **única fonte de verdade**.
> A exclusão de um .docx pelo utilizador **NÃO** implica regeneração — o sistema apenas consulta o manifesto.

---

## 🏛️ Arquitectura do Sistema

### Estrutura de Pastas

```
mssmministries/
├── .github/workflows/
│   └── gerar_apostilas.yml    # Workflow GitHub Actions (cron + manual)
├── _assets/                    # Logos institucionais
├── _estilos.py                 # Módulo de estilos DOCX (Garamond, cores, etc.)
├── curriculo.py                # Dados completos das 1.029 apostilas
├── gerador_apostila.py         # Gerador principal (Gemini → DOCX)
├── manifesto.py                # Gestão do manifesto de progresso
├── progress/
│   ├── manifesto.json          # Fonte de verdade do progresso
│   └── RELATORIO.md            # Relatório de progresso actualizado
├── apostilas/                  # Pasta de saída (gerada automaticamente)
│   └── Instituto/Escola/Curso/Módulo/EBE-APO-XXX_Titulo.docx
├── EBE-MODELO_APOSTILA_em_branco.docx  # Template de referência
├── EBE-APO-001_Apostila_Piloto_*.docx  # Apostila piloto (referência editorial)
└── [documentos institucionais, scripts auxiliares, logos...]
```

### Hierarquia Curricular

```
Nível Formativo (4) → Instituto (10) → Escola (54) → Curso (142) → Módulo (327) → Apostila (1.029)
```

| Nível | Nome | Institutos | Escolas | Cursos | Módulos | Apostilas |
|---|---|---|---|---|---|---|
| 1 | Discípulo (Conhecer) | 2 | 15 | 46 | 115 | 345 |
| 2 | Crescimento (Ser) | 2 | 13 | 36 | 87 | 261 |
| 3 | Servir (Ministério) | 3 | 14 | 40 | 88 | 264 |
| 4 | Multiplicação (Reino) | 3 | 12 | 24 | 53 | 159 |
| **TOTAL** | | **10** | **54** | **142** | **327** | **1.029** |

---

## ⚙️ Configuração

### 1. Configurar o Secret `GEMINI_API_KEY`

1. Obtenha uma chave de API gratuita em [Google AI Studio](https://aistudio.google.com/apikey)
2. No repositório GitHub, vá a **Settings → Secrets and variables → Actions**
3. Clique **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: a sua chave de API (formato: `AIza...`)
6. Clique **Add secret**

> ⚠️ **Nunca** coloque a chave de API no código, logs ou commits.

### 2. Execução Manual (sob demanda)

No GitHub, vá a **Actions → Gerar Apostilas EBE → Run workflow**:
- Deixe a quantidade padrão (10) ou defina quantas apostilas gerar.

### 3. Execução Automática (cron diário)

O workflow executa automaticamente todos os dias às 06:00 UTC, gerando até 10 apostilas por execução.

---

## 🔄 Como Funciona

1. **O workflow lê o manifesto** (`progress/manifesto.json`) para determinar as próximas apostilas pendentes.
2. **Para cada apostila pendente**, constrói um prompt dinâmico específico ao seu tema, incluindo:
   - Título exacto, posição na hierarquia curricular
   - Tema específico do módulo/curso
   - Lista de apostilas já geradas da mesma escola (para evitar repetição)
   - Instruções explícitas de originalidade e profundidade teológica
3. **Chama a API do Gemini** (modelo `gemini-2.0-flash`, camada gratuita) para gerar o conteúdo.
4. **Valida automaticamente** o conteúdo gerado:
   - Campos obrigatórios presentes e preenchidos
   - Nenhum placeholder vazio
   - Contagem de palavras (mínimo 2.000)
5. **Gera o ficheiro .docx** usando os estilos institucionais (Garamond, cores EBE, ARC).
6. **Salva o .docx** na subpasta correcta seguindo a hierarquia.
7. **Actualiza o manifesto** — marca como "gerado" ou "falhou" com o motivo.
8. **Faz commit e push** automático (arquivos gerados + manifesto actualizado).

### Resiliência a Falhas

- Se uma apostila falhar (erro de API, timeout, resposta vazia), é marcada como "falhou" no manifesto com o motivo.
- O lote **não é interrompido** — as apostilas seguintes continuam.
- Apostilas falhadas são retentadas na próxima execução.
- O manifesto é guardado após cada apostila (não apenas no fim do lote).

### Protecção contra Regeneração

- **A exclusão de um .docx pelo utilizador é tratada como "arquivo entregue"**.
- O sistema **nunca** verifica a presença do ficheiro — apenas consulta o manifesto.
- Uma apostila marcada como "gerado" **nunca** será regenerada.

---

## 📐 Padrões de Formatação

| Elemento | Padrão |
|---|---|
| Tipografia | Garamond (títulos e corpo) |
| Tamanho de página | A4 (21.0 × 29.7 cm) |
| Margens | Superior 2.5 cm, Inferior 2.5 cm, Esquerda 3.0 cm, Direita 2.5 cm |
| Cor primária (azul-marinho) | `#1B3A5C` |
| Cor secundária (verde) | `#2E7D4F` |
| Cor terciária (dourado) | `#C9A14B` |
| Versão bíblica | Almeida Revista e Corrigida (ARC) |
| Língua | Português europeu/Angola (pt-PT) |
| Cabeçalho | Escola Bíblica Epignósis · Título do documento |
| Rodapé | Código institucional · Número de página |

---

## 📝 Estrutura Padrão de cada Apostila

1. **Capa** — Logo + trilha hierárquica + número + título + quadro de identificação
2. **Marco Filosófico** — Citação institucional + Efésios 4.13
3. **Ficha Técnica** — Dados editoriais + citação 2 Timóteo 3.16-17
4. **Sumário**
5. **Apresentação da Apostila**
6. **Objectivos de Aprendizagem** — Conhecer · Crer · Viver · Servir
7. **Versículo-Chave**
8. **Texto-Base para Leitura**
9. **1. Introdução**
10. **2. Desenvolvimento do Conceito Central**
    - 2.1 Fundamentos bíblicos
    - 2.2 Desenvolvimento doutrinário
    - 2.3 Possíveis dúvidas e equívocos comuns
    - 2.4 Quadro de Destaque
11. **3. Aplicação Prática** — Vida pessoal · Família · Igreja · Trabalho · Ministério
12. **4. Síntese e Conclusão**
13. **Exercícios de Revisão** — Compreensão · Reflexão · Ministério
14. **Estudo Bíblico Complementar**
15. **Para a Próxima Apostila**
16. **Glossário** (tabela)
17. **Bibliografia Recomendada**
18. **Anotações Pessoais** (linhas para escrever)
19. **Selo Final** — Soli Deo Gloria

---

## 🔧 Scripts Disponíveis

### Geração manual (local)

```bash
# Gerar 5 apostilas (requer chave de API)
python3 gerador_apostila.py --api-key SUA_CHAVE --quantidade 5
```

### Gestão do manifesto

```python
from manifesto import *
from curriculo import APOSTILAS

# Inicializar manifesto
manifesto = inicializar_manifesto(APOSTILAS)

# Ver estatísticas
stats = estatisticas(manifesto)
print(stats)

# Ver próximas pendentes
pendentes = obter_pendentes(manifesto, limite=5)
```

---

## 📋 Documentos Institucionais

| Código | Documento |
|---|---|
| EBE-DOC-001 | Identidade Institucional — Missão, Visão, Valores e Filosofia de Ensino |
| EBE-DOC-002 | Declaração de Fé Institucional (16 artigos) |
| EBE-DOC-003 | Projecto Pedagógico Oficial (PPO) |
| EBE-DOC-004 | Regimento Acadêmico |
| EBE-DOC-005 | Arquitectura Oficial (estrutura de 7 níveis) |
| EBE-DOC-006 | Mapa Oficial de Cursos |
| EBE-DOC-007 | Duração Oficial dos Cursos |
| EBE-DOC-008 | Sistema de Pré-Requisitos |

---

> *"Acreditamos que o verdadeiro conhecimento de Deus transforma a mente pela verdade das Escrituras, o coração pela acção do Espírito Santo e a vida pelo compromisso de viver e anunciar o Evangelho de Jesus Cristo."*
>
> — Marco Filosófico, Escola Bíblica Epignósis

*Soli Deo Gloria.*
