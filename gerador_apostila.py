"""
GERADOR DE APOSTILAS — Escola Bíblica Epignósis

Gera apostilas completas usando a API do Gemini, preenchendo
o template institucional com conteúdo teologicamente específico.

Cada apostila tem entre 15 e 20 páginas de conteúdo real,
seguindo fielmente a profundidade, estilo teológico, estrutura
pedagógica e formatação (Garamond, cores institucionais, ARC).

PROIBIDO conteúdo genérico ou reciclado entre apostilas.
"""

import json
import os
import sys
import re
import time
from datetime import datetime, timezone

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from _estilos import *
from _estilos import _shade_cell, _add_horizontal_line
from curriculo import APOSTILAS, NIVEIS, NIVEL_SHORT
from manifesto import (
    carregar_manifesto, guardar_manifesto, inicializar_manifesto,
    obter_pendentes, marcar_gerado, marcar_falha, estatisticas,
    MANIFESTO_PATH,
)

# --- Gemini API (SDK novo: google-genai) ---
try:
    from google import genai
except ImportError:
    genai = None


def configurar_gemini(api_key):
    """Configura a API do Gemini com a chave fornecida (SDK google-genai)."""
    if genai is None:
        raise RuntimeError(
            "Biblioteca google-genai não instalada. "
            "Instale com: pip install google-genai"
        )
    client = genai.Client(api_key=api_key)
    return client


def construir_prompt(apostila_info, apostilas_anteriores_mesma_escola=None):
    """
    Constrói o prompt dinâmico para o Gemini, específico para cada apostila.
    Inclui instruções rigorosas de originalidade e não-repetição.
    """
    numero = apostila_info["numero"]
    titulo = apostila_info["titulo"]
    nivel = NIVEIS.get(apostila_info["nivel"], "")
    instituto = apostila_info["instituto_nome"]
    escola = apostila_info["escola"]
    curso = apostila_info["curso"]
    modulo_nome = apostila_info["modulo_nome"]

    # Texto sobre apostilas anteriores da mesma escola (para evitar repetição)
    repeticao_instrucao = ""
    if apostilas_anteriores_mesma_escola:
        titulos_anteriores = [a["titulo"] for a in apostilas_anteriores_mesma_escola[:10]]
        repeticao_instrucao = f"""
ATENÇÃO — NÃO REPETIR CONTEÚDO:
As seguintes apostilas JÁ FORAM produzidas para esta mesma Escola de {escola}:
{chr(10).join(f'  - {t}' for t in titulos_anteriores)}
É TERMINANTEMENTE PROIBIDO reciclar ou parafrasear conteúdo dessas apostilas.
Cada apostila deve abordar o seu tema específico com profundidade e originalidade,
incluindo exegese bíblica, estudo de termos em grego/hebraico quando pertinente,
exemplos históricos distintos e aplicações práticas únicas.
"""

    prompt = f"""És um teólogo cristão evangélico sénior, professor da Escola Bíblica Epignósis (EBE),
com expertise em exegese bíblica, teologia sistemática e pedagogia cristã.
Escreves em português europeu/Angola (pt-PT), com rigor académico mas linguagem acessível.
Usas a versão bíblica Almeida Revista e Corrigida (ARC) para todas as citações.

TAREFA: Produzir o conteúdo COMPLETO para a seguinte apostila:

IDENTIFICAÇÃO:
- Número: {numero} de 1.029
- Título: {titulo}
- Nível formativo: Nível {apostila_info["nivel"]} — {nivel}
- Instituto: {instituto}
- Escola: {escola}
- Curso: {curso}
- Módulo: {apostila_info["modulo"]} — {modulo_nome}

{repeticao_instrucao}

ESTRUTURA OBRIGATÓRIA — responde em formato JSON com os seguintes campos:

{{
  "subtitulo": "subtítulo descritivo da apostila (1 frase)",
  "carga_horaria": "X horas de estudo",
  "apresentacao": "2 a 4 parágrafos apresentando o conceito central, a relevância para a vida cristã e o lugar dentro do módulo e do curso. Destaque por que vale a pena estudar este tema agora.",
  "objectivos": [
    "CONHECER — [verbo no infinitivo: identificar, descrever, distinguir…]",
    "CRER — [interiorizar uma convicção bíblica específica]",
    "VIVER — [aplicar a verdade aprendida em uma situação concreta]",
    "SERVIR — [exercer um dom ou uma prática ministerial decorrente]"
  ],
  "versiculo_chave_texto": "texto bíblico completo em ARC",
  "versiculo_chave_ref": "Referência bíblica (ex: Romanos 8.28)",
  "texto_base_ref": "Livro Cap.versículo-versículo (passagem mais relevante para o tema)",
  "introducao": "2 a 3 parágrafos contextualizando o tema histórica, teológica e pastoralmente. Que problema, pergunta ou necessidade espiritual esta apostila responde? Faça a ponte com o conhecimento anterior.",
  "fundamentos_biblicos": "4 a 6 parágrafos desenvolvendo as bases bíblicas do tema, com citações de 3 a 5 textos fundamentais. Cada citação bíblica deve ter: texto_em_arc e referencia.",
  "citacoes_biblicas_fund": [
    {{"texto": "texto bíblico em ARC", "referencia": "Referência"}}
  ],
  "desenvolvimento_doutrinario": "4 a 6 parágrafos desenvolvendo o conteúdo doutrinário. Linguagem clara e didáctica. Defina termos-chave logo na primeira ocorrência. Inclua, quando pertinente, estudo de termos em grego ou hebraico.",
  "definicao_conceito": "Definição precisa do conceito central da apostila (1 parágrafo denso).",
  "aspectos_principais": [
    "Aspecto 1 — explicação detalhada (2-3 frases)",
    "Aspecto 2 — explicação detalhada",
    "Aspecto 3 — explicação detalhada"
  ],
  "duvidas_equivocos": "2 a 3 parágrafos apresentando dúvidas frequentes ou interpretações erradas sobre o tema, respondendo com base nas Escrituras.",
  "para_reter": "Síntese em 1-2 frases — o aluno deve sair com isto na memória.",
  "aplicacoes": [
    "Na vida pessoal e devocional — aplicação concreta",
    "Na família — aplicação concreta",
    "Na igreja local — aplicação concreta",
    "No trabalho e na sociedade — aplicação concreta",
    "No exercício ministerial — aplicação concreta"
  ],
  "sintese": "1 parágrafo recapitulando o que foi estudado, terminando com um apelo pastoral.",
  "versiculo_encerramento_texto": "texto bíblico em ARC",
  "versiculo_encerramento_ref": "Referência bíblica",
  "exercicios_compreensao": [
    "Pergunta 1 de compreensão",
    "Pergunta 2 de compreensão",
    "Pergunta 3 de compreensão"
  ],
  "exercicios_reflexao": [
    "Pergunta 1 de reflexão pessoal",
    "Pergunta 2 de reflexão pessoal",
    "Pergunta 3 de reflexão pessoal"
  ],
  "exercicios_ministerio": [
    "Pergunta 1 sobre ministério e serviço",
    "Pergunta 2 sobre ministério e serviço"
  ],
  "estudo_biblico_ref": "Livro Cap.versículos (passagem para estudo complementar)",
  "estudo_biblico_perguntas": [
    "Pergunta 1 sobre a passagem complementar",
    "Pergunta 2",
    "Pergunta 3",
    "Pergunta 4",
    "Pergunta 5"
  ],
  "proxima_apostila_tema": "Tema da próxima apostila no módulo",
  "proxima_apostila_leitura": "Referência bíblica para leitura prévia",
  "proxima_apostila_perguntas": [
    "Pergunta orientadora 1",
    "Pergunta orientadora 2"
  ],
  "glossario": [
    {{"termo": "Termo 1", "definicao": "Definição clara e breve"}},
    {{"termo": "Termo 2", "definicao": "Definição"}},
    {{"termo": "Termo 3", "definicao": "Definição"}},
    {{"termo": "Termo 4", "definicao": "Definição"}},
    {{"termo": "Termo 5", "definicao": "Definição"}}
  ],
  "bibliografia": [
    "Sobrenome, Nome. Título da obra. Cidade: Editora, ano.",
    "Sobrenome, Nome. Título da obra. Cidade: Editora, ano.",
    "Sobrenome, Nome. Título da obra. Cidade: Editora, ano."
  ]
}}

REGRAS DE CONTEÚDO:
1. Cada apostila deve ter conteúdo TEOLÓGICAMENTE ESPECÍFICO ao seu tema.
2. PROIBIDO gerar um texto-molde e apenas trocar o título.
3. Incluir exegese bíblica apropriada ao tema (não genérica).
4. Quando pertinente, incluir estudo de termos em grego/hebraico com transliteração.
5. Citar exemplos históricos e bíblicos DISTINTOS dos de qualquer outra apostila.
6. Aplicações práticas devem ser concretas e específicas ao tema, não genéricas.
7. Todas as citações bíblicas devem ser da versão Almeida Revista e Corrigida (ARC).
8. O conteúdo deve gerar entre 15 e 20 páginas de texto real no formato DOCX.
9. Linguagem: português europeu/Angola (pt-PT). Evitar brasileirismos.
10. Estilo: académico formal mas acessível. Garamond, alinhamento justificado.

Responda APENAS com o JSON válido, sem explicações adicionais.
"""

    return prompt


def gerar_conteudo_gemini(client, apostila_info, apostilas_anteriores=None):
    """
    Chama a API do Gemini para gerar o conteúdo de uma apostila.
    Retorna o dicionário com os dados ou None em caso de falha.
    """
    prompt = construir_prompt(apostila_info, apostilas_anteriores)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.85,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
            ),
        )

        texto = response.text.strip()

        # Extrair JSON da resposta (pode vir com marcação de código)
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()

        conteudo = json.loads(texto)
        return conteudo

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Resposta do Gemini não é JSON válido: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro na chamada ao Gemini: {e}")


def validar_conteudo(conteudo):
    """
    Valida o conteúdo gerado pelo Gemini.
    Retorna (True, "") se válido, ou (False, "motivo") se inválido.
    """
    campos_obrigatorios = [
        "subtitulo", "apresentacao", "objectivos", "versiculo_chave_texto",
        "versiculo_chave_ref", "texto_base_ref", "introducao",
        "fundamentos_biblicos", "desenvolvimento_doutrinario",
        "definicao_conceito", "aspectos_principais", "duvidas_equivocos",
        "para_reter", "aplicacoes", "sintese", "glossario",
    ]

    for campo in campos_obrigatorios:
        if campo not in conteudo or not conteudo[campo]:
            return False, f"Campo obrigatório ausente ou vazio: {campo}"

    # Verificar objectivos
    if len(conteudo.get("objectivos", [])) < 4:
        return False, "Objectivos insuficientes (mínimo 4)"

    # Verificar aplicações
    if len(conteudo.get("aplicacoes", [])) < 3:
        return False, "Aplicações insuficientes (mínimo 3)"

    # Verificar glossário
    if len(conteudo.get("glossario", [])) < 3:
        return False, "Termos de glossário insuficientes (mínimo 3)"

    # Verificar se há placeholders não preenchidos
    texto_completo = json.dumps(conteudo, ensure_ascii=False)
    if "«[" in texto_completo or "[TÍTULO" in texto_completo.upper():
        return False, "Contém placeholders não preenchidos"

    # Contagem aproximada de palavras
    palavras = len(texto_completo.split())
    if palavras < 2000:
        return False, f"Conteúdo demasiado curto ({palavras} palavras, mínimo 2000)"

    return True, ""


def calcular_caminho_ficheiro(apostila_info):
    """
    Calcula o caminho do ficheiro .docx seguindo a hierarquia:
    Instituto/Escola/Curso/Módulo/Apostila.docx
    """
    # Limpar nomes para uso em caminhos de ficheiro
    def limpar(nome):
        return re.sub(r'[<>:"/\\|?*]', '', nome).strip()

    inst = limpar(apostila_info["instituto_nome"])
    escola = limpar(apostila_info["escola"])
    curso = limpar(apostila_info["curso"])
    mod = f"Módulo {apostila_info['modulo']} — {limpar(apostila_info['modulo_nome'])}"

    # Nome do ficheiro: EBE-APO-XXX_Titulo.docx
    num_str = str(apostila_info["numero"]).zfill(3)
    titulo_limpo = limpar(apostila_info["titulo"])
    # Limitar comprimento do título no nome do ficheiro
    if len(titulo_limpo) > 60:
        titulo_limpo = titulo_limpo[:57] + "..."
    filename = f"EBE-APO-{num_str}_{titulo_limpo.replace(' ', '_')}.docx"

    caminho = os.path.join("apostilas", inst, escola, curso, mod, filename)
    return caminho


def gerar_docx(apostila_info, conteudo):
    """
    Gera o ficheiro .docx completo usando os estilos institucionais da EBE.
    """
    doc = novo_documento(
        f"Apostila — {apostila_info['titulo']}",
        f"EBE-APO-{str(apostila_info['numero']).zfill(3)}"
    )

    numero = apostila_info["numero"]
    titulo = apostila_info["titulo"]
    subtitulo = conteudo.get("subtitulo", "")
    nivel_str = NIVEL_SHORT.get(apostila_info["nivel"], "")

    # ====== CAPA ======
    doc.add_paragraph()
    inserir_logo(doc, LOGO_PATH, largura_cm=5.5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Conhecer a Deus. Viver a Palavra. Manifestar o Reino.")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    _add_horizontal_line(p, color=HEX_SECUNDARIA, size=6)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    r = p.add_run(f"INSTITUTO {apostila_info['instituto_nome'].replace('Instituto de ', '').replace('Instituto ', '').upper()}")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{apostila_info['escola']}  ·  Curso «{apostila_info['curso']}»  ·  Módulo {apostila_info['modulo']} — {apostila_info['modulo_nome']}")
    r.font.name = FONTE_CORPO
    r.font.size = Pt(10)
    r.font.color.rgb = COR_CITACAO

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"APOSTILA N.º  {str(numero).zfill(2)}")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(titulo)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA

    if subtitulo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(subtitulo)
        r.font.name = FONTE_TITULO
        r.font.size = Pt(13)
        r.font.italic = True
        r.font.color.rgb = COR_TEXTO

    doc.add_paragraph()
    doc.add_paragraph()

    # Quadro de identificação
    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    dados_capa = [
        ("Autor / Docente", "Direcção Pedagógica · Escola Bíblica Epignósis"),
        ("Carga horária estimada", conteudo.get("carga_horaria", "2 horas de estudo")),
        ("Nível formativo", f"Nível {apostila_info['nivel']} — {nivel_str}"),
        ("Edição / Ano", "1.ª edição — 2026"),
    ]
    for i, (k, v) in enumerate(dados_capa):
        row = tbl.rows[i].cells
        row[0].text = k
        row[1].text = v
        _shade_cell(row[0], "E8F1EC")
        for p in row[0].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.name = FONTE_TITULO
                r.font.size = Pt(10)
                r.font.color.rgb = COR_PRIMARIA
        for p in row[1].paragraphs:
            for r in p.runs:
                r.font.name = FONTE_CORPO
                r.font.size = Pt(10)

    doc.add_paragraph()
    p = doc.add_paragraph()
    _add_horizontal_line(p, color=HEX_SECUNDARIA, size=4)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    codigo = f"EBE-APO-{str(numero).zfill(3)}"
    r = p.add_run(f"Material didáctico oficial · Código {codigo} · 2026")
    r.font.name = FONTE_CORPO
    r.font.size = Pt(9)
    r.font.color.rgb = COR_CITACAO

    page_break(doc)

    # ====== MARCO FILOSÓFICO ======
    add_marco_filosofico(doc)

    # ====== FICHA TÉCNICA ======
    h1(doc, "Ficha Técnica")
    paragrafo(doc,
              "Este material didáctico é propriedade intelectual da Escola Bíblica "
              "Epignósis (EBE), produzido para uso exclusivo no âmbito dos seus "
              "programas de formação. A sua reprodução, no todo ou em parte, "
              "depende de autorização institucional escrita.")
    lista(doc, [
        f"Título da apostila: {titulo}.",
        f"Curso: {apostila_info['curso']}.",
        f"Módulo: {apostila_info['modulo']} — {apostila_info['modulo_nome']}.",
        "Autor / Docente: Direcção Pedagógica da Escola Bíblica Epignósis.",
        "Revisão pedagógica: Coordenação Acadêmica.",
        "Revisão doutrinária: Conselho Doutrinário.",
        "Versão bíblica de referência: Almeida Revista e Corrigida (ARC).",
        "Edição: 1.ª — 2026.",
        f"Código institucional: {codigo}.",
    ])
    citacao(doc,
            "Toda a Escritura é divinamente inspirada e proveitosa para ensinar, "
            "para redarguir, para corrigir, para instruir em justiça; para que o "
            "homem de Deus seja perfeito e perfeitamente instruído para toda a boa obra.",
            "2 Timóteo 3.16-17")

    page_break(doc)

    # ====== SUMÁRIO ======
    h1(doc, "Sumário")
    lista(doc, [
        "Apresentação da apostila",
        "Objectivos de aprendizagem",
        "Versículo-chave",
        "Texto-base para leitura",
        "1. Introdução",
        "2. Desenvolvimento do conceito central",
        "   2.1 Fundamentos bíblicos",
        "   2.2 Desenvolvimento doutrinário",
        "   2.3 Possíveis dúvidas e equívocos comuns",
        "   2.4 Quadro de destaque",
        "3. Aplicação prática",
        "4. Síntese e conclusão",
        "Exercícios de revisão",
        "Estudo bíblico complementar",
        "Para a próxima apostila",
        "Glossário",
        "Bibliografia recomendada",
        "Anotações pessoais",
    ])

    page_break(doc)

    # ====== APRESENTAÇÃO ======
    h1(doc, "Apresentação da Apostila")
    for parag in conteudo.get("apresentacao", "").split("\n\n"):
        if parag.strip():
            paragrafo(doc, parag.strip())

    # ====== OBJECTIVOS ======
    h1(doc, "Objectivos de Aprendizagem")
    paragrafo(doc, "Ao concluir o estudo desta apostila, o(a) aluno(a) será capaz de:")
    lista(doc, conteudo.get("objectivos", []), ordenada=True)

    # ====== VERSÍCULO-CHAVE ======
    h1(doc, "Versículo-Chave")
    citacao(doc,
            conteudo.get("versiculo_chave_texto", ""),
            conteudo.get("versiculo_chave_ref", ""))

    # ====== TEXTO-BASE ======
    h1(doc, "Texto-Base para Leitura")
    paragrafo(doc,
              "Antes de iniciar o estudo, o(a) aluno(a) é convidado(a) a ler atentamente, "
              "em sua Bíblia (Almeida Revista e Corrigida), a seguinte passagem:")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(conteudo.get("texto_base_ref", ""))
    r.font.name = FONTE_TITULO
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    page_break(doc)

    # ====== 1. INTRODUÇÃO ======
    h1(doc, "Introdução", numero=1)
    for parag in conteudo.get("introducao", "").split("\n\n"):
        if parag.strip():
            paragrafo(doc, parag.strip())

    # ====== 2. DESENVOLVIMENTO ======
    h1(doc, "Desenvolvimento do Conceito Central", numero=2)

    # 2.1 Fundamentos bíblicos
    h2(doc, "Fundamentos bíblicos", numero="2.1")
    for parag in conteudo.get("fundamentos_biblicos", "").split("\n\n"):
        if parag.strip():
            paragrafo(doc, parag.strip())

    # Citações bíblicas dos fundamentos
    for cit in conteudo.get("citacoes_biblicas_fund", []):
        citacao(doc, cit.get("texto", ""), cit.get("referencia", ""))

    # 2.2 Desenvolvimento doutrinário
    h2(doc, "Desenvolvimento doutrinário", numero="2.2")
    for parag in conteudo.get("desenvolvimento_doutrinario", "").split("\n\n"):
        if parag.strip():
            paragrafo(doc, parag.strip())

    h3(doc, "Definição")
    paragrafo(doc, conteudo.get("definicao_conceito", ""))

    h3(doc, "Aspectos principais")
    lista(doc, conteudo.get("aspectos_principais", []), ordenada=True)

    # 2.3 Dúvidas e equívocos
    h2(doc, "Possíveis dúvidas e equívocos comuns", numero="2.3")
    for parag in conteudo.get("duvidas_equivocos", "").split("\n\n"):
        if parag.strip():
            paragrafo(doc, parag.strip())

    # 2.4 Quadro de destaque
    h2(doc, "Quadro de Destaque", numero="2.4")
    tbl = doc.add_table(rows=1, cols=1)
    cell = tbl.rows[0].cells[0]
    cell.text = ""
    _shade_cell(cell, "E8F1EC")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run("✦ Para reter:  ")
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11)
    r2 = p.add_run(conteudo.get("para_reter", ""))
    r2.font.name = FONTE_CORPO
    r2.font.size = Pt(11)
    r2.font.italic = True

    page_break(doc)

    # ====== 3. APLICAÇÃO ======
    h1(doc, "Aplicação Prática", numero=3)
    lista(doc, conteudo.get("aplicacoes", []), ordenada=True)

    # ====== 4. SÍNTESE ======
    h1(doc, "Síntese e Conclusão", numero=4)
    paragrafo(doc, conteudo.get("sintese", ""))
    citacao(doc,
            conteudo.get("versiculo_encerramento_texto", ""),
            conteudo.get("versiculo_encerramento_ref", ""))

    page_break(doc)

    # ====== EXERCÍCIOS ======
    h1(doc, "Exercícios de Revisão")
    paragrafo(doc,
              "Responda às questões a seguir com base no conteúdo desta apostila "
              "e na sua leitura bíblica.")

    h3(doc, "I — Verifique a sua compreensão")
    lista(doc, conteudo.get("exercicios_compreensao", []), ordenada=True)

    h3(doc, "II — Reflexão pessoal")
    lista(doc, conteudo.get("exercicios_reflexao", []), ordenada=True)

    h3(doc, "III — Ministério e serviço")
    lista(doc, conteudo.get("exercicios_ministerio", []), ordenada=True)

    # ====== ESTUDO BÍBLICO ======
    h1(doc, "Estudo Bíblico Complementar")
    ref_estudo = conteudo.get("estudo_biblico_ref", "")
    paragrafo(doc, f"Leia atentamente {ref_estudo} e responda:")
    lista(doc, conteudo.get("estudo_biblico_perguntas", []), ordenada=True)

    # ====== PRÓXIMA APOSTILA ======
    h1(doc, "Para a Próxima Apostila")
    prox_tema = conteudo.get("proxima_apostila_tema", "")
    prox_leitura = conteudo.get("proxima_apostila_leitura", "")
    paragrafo(doc,
              f"Na próxima apostila estudaremos {prox_tema}. "
              f"Para se preparar, leia previamente {prox_leitura} e "
              f"reflicta sobre as perguntas a seguir:")
    lista(doc, conteudo.get("proxima_apostila_perguntas", []))

    page_break(doc)

    # ====== GLOSSÁRIO ======
    h1(doc, "Glossário")
    paragrafo(doc, "Definições breves dos termos-chave utilizados nesta apostila.")
    tbl = doc.add_table(rows=1, cols=2)
    hdr = tbl.rows[0].cells
    for i, t in enumerate(["Termo", "Definição"]):
        hdr[i].text = ""
        _shade_cell(hdr[i], HEX_PRIMARIA)
        p = hdr[i].paragraphs[0]
        r = p.add_run(t)
        r.font.bold = True
        r.font.name = FONTE_TITULO
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for item in conteudo.get("glossario", []):
        row = tbl.add_row().cells
        row[0].text = item.get("termo", "")
        row[1].text = item.get("definicao", "")
        for c in row:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = FONTE_CORPO
                    r.font.size = Pt(10)
        for p in row[0].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = COR_PRIMARIA

    # ====== BIBLIOGRAFIA ======
    h1(doc, "Bibliografia Recomendada")
    bibliografia = ["Bíblia Sagrada. Tradução de João Ferreira de Almeida, Revista e Corrigida."]
    bibliografia.extend(conteudo.get("bibliografia", []))
    lista(doc, bibliografia)

    # ====== ANOTAÇÕES ======
    h1(doc, "Anotações Pessoais")
    for _ in range(12):
        p = doc.add_paragraph()
        _add_horizontal_line(p, color="C8C8C8", size=4)

    selo_final(doc)

    return doc


def processar_apostila(client, apostila_info, manifesto, todas_apostilas):
    """
    Processa uma apostila completa: gera conteúdo via Gemini,
    valida, gera DOCX, salva e actualiza o manifesto.

    Retorna (True, caminho) se sucesso, (False, erro_msg) se falha.
    """
    # Obter apostilas anteriores da mesma escola (para evitar repetição)
    mesma_escola = [
        a for a in todas_apostilas
        if a["escola"] == apostila_info["escola"]
        and a["numero"] < apostila_info["numero"]
    ]

    # 1. Gerar conteúdo via Gemini
    conteudo = gerar_conteudo_gemini(client, apostila_info, mesma_escola)

    # 2. Validar
    valido, motivo = validar_conteudo(conteudo)
    if not valido:
        return False, f"Validação falhou: {motivo}"

    # 3. Gerar DOCX
    doc = gerar_docx(apostila_info, conteudo)

    # 4. Calcular caminho e salvar
    caminho = calcular_caminho_ficheiro(apostila_info)
    caminho_abs = os.path.join(BASE_DIR, caminho)
    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)
    doc.save(caminho_abs)

    return True, caminho


def executar_lote(api_key, quantidade=10):
    """
    Função principal: executa um lote de geração de apostilas.

    Args:
        api_key: chave da API do Gemini
        quantidade: número de apostilas a gerar neste lote

    Returns:
        dict com estatísticas do lote
    """
    # Configurar Gemini
    client = configurar_gemini(api_key)

    # Carregar currículo e manifesto
    manifesto = carregar_manifesto()
    manifesto = inicializar_manifesto(APOSTILAS)  # Garantir que está completo
    stats_inicial = estatisticas(manifesto)

    # Obter pendentes
    pendentes = obter_pendentes(manifesto, limite=quantidade)

    if not pendentes:
        print("✅ Todas as 1.029 apostilas já foram geradas!")
        return {"geradas": 0, "falhadas": 0, "total_pendentes": 0}

    print(f"📊 Progresso: {stats_inicial['gerados']}/{stats_inicial['total']} "
          f"({stats_inicial['percentagem']}%) — "
          f"{stats_inicial['pendentes']} pendentes, {stats_inicial['falhados']} falhados")
    print(f"🔄 Gerando lote de {len(pendentes)} apostila(s)...")

    geradas = 0
    falhadas = 0

    for i, apostila_entry in enumerate(pendentes):
        # Encontrar dados completos da apostila
        apostila_info = next(
            (a for a in APOSTILAS if a["numero"] == apostila_entry["id"]),
            None
        )
        if apostila_info is None:
            print(f"  ⚠️  Apostila #{apostila_entry['id']} não encontrada no currículo")
            marcar_falha(manifesto, apostila_entry["id"], "Não encontrada no currículo")
            falhadas += 1
            continue

        num = apostila_info["numero"]
        titulo = apostila_info["titulo"]
        print(f"  [{i+1}/{len(pendentes)}] #{num:03d} — {titulo}... ", end="", flush=True)

        try:
            sucesso, resultado = processar_apostila(client, apostila_info, manifesto, APOSTILAS)

            if sucesso:
                marcar_gerado(manifesto, num, resultado)
                geradas += 1
                print(f"✅ → {resultado}")
            else:
                marcar_falha(manifesto, num, resultado)
                falhadas += 1
                print(f"❌ {resultado}")

        except Exception as e:
            marcar_falha(manifesto, num, str(e))
            falhadas += 1
            print(f"❌ Erro: {e}")

        # Guardar manifesto após cada apostila (para não perder progresso)
        guardar_manifesto(manifesto)

        # Pausa entre chamadas API (para respeitar rate limits)
        if i < len(pendentes) - 1:
            time.sleep(2)

    # Estatísticas finais
    stats_final = estatisticas(manifesto)
    print(f"\n📊 Lote concluído: {geradas} geradas, {falhadas} falhadas")
    print(f"📊 Progresso total: {stats_final['gerados']}/{stats_final['total']} "
          f"({stats_final['percentagem']}%)")

    return {
        "geradas": geradas,
        "falhadas": falhadas,
        "progresso_gerados": stats_final["gerados"],
        "progresso_total": stats_final["total"],
        "progresso_pct": stats_final["percentagem"],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerador de Apostilas EBE")
    parser.add_argument("--api-key", required=True, help="Chave da API do Gemini")
    parser.add_argument("--quantidade", type=int, default=10,
                        help="Número de apostilas a gerar (padrão: 10)")
    args = parser.parse_args()

    resultado = executar_lote(args.api_key, args.quantidade)
    print(f"\nResultado: {json.dumps(resultado, ensure_ascii=False, indent=2)}")
