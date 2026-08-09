from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    ListFlowable,
    ListItem,
)

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_MARKDOWN = BASE_DIR / "documentos" / "conhecimento"
PASTA_PDF = BASE_DIR / "documentos" / "pdf"
LOGO = BASE_DIR / "capturas" / "logo" / "marvin-logo.png"

PASTA_PDF.mkdir(parents=True, exist_ok=True)


def criar_estilos():
    estilos_base = getSampleStyleSheet()

    return {
        "titulo": ParagraphStyle(
            "Titulo",
            parent=estilos_base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0B2A52"),
            spaceAfter=16,
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo",
            parent=estilos_base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#F97316"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "corpo": ParagraphStyle(
            "Corpo",
            parent=estilos_base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
        ),
        "capa": ParagraphStyle(
            "Capa",
            parent=estilos_base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0B2A52"),
        ),
    }


def adicionar_capa(elementos, titulo, estilos):
    elementos.append(Spacer(1, 5 * cm))

    if LOGO.exists():
        logo = Image(str(LOGO), width=7 * cm, height=7 * cm)
        logo.hAlign = "CENTER"
        elementos.append(logo)

    elementos.append(Spacer(1, 1.2 * cm))
    elementos.append(Paragraph("MARVIN LOGISTICS", estilos["capa"]))
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(
        Paragraph(
            titulo,
            ParagraphStyle(
                "TituloDocumento",
                parent=estilos["corpo"],
                alignment=TA_CENTER,
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#555555"),
            ),
        )
    )

    elementos.append(PageBreak())


def converter_markdown(caminho_md, caminho_pdf):
    estilos = criar_estilos()

    linhas = caminho_md.read_text(encoding="utf-8").splitlines()

    titulo_documento = caminho_md.stem.replace("-", " ").title()

    for linha in linhas:
        if linha.startswith("# "):
            titulo_documento = linha[2:].strip()
            break

    documento = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=titulo_documento,
        author="Marvin Logistics",
    )

    elementos = []

    adicionar_capa(elementos, titulo_documento, estilos)

    itens_lista = []

    def finalizar_lista():
        nonlocal itens_lista

        if itens_lista:
            lista = ListFlowable(
                [
                    ListItem(
                        Paragraph(item, estilos["corpo"]),
                        leftIndent=12,
                    )
                    for item in itens_lista
                ],
                bulletType="bullet",
                leftIndent=20,
                bulletFontName="Helvetica",
                bulletFontSize=8,
            )

            elementos.append(lista)
            elementos.append(Spacer(1, 6))
            itens_lista = []

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            finalizar_lista()
            elementos.append(Spacer(1, 4))
            continue

        if linha.startswith("# "):
            finalizar_lista()
            elementos.append(
                Paragraph(linha[2:].strip(), estilos["titulo"])
            )

        elif linha.startswith("## "):
            finalizar_lista()
            elementos.append(
                Paragraph(linha[3:].strip(), estilos["subtitulo"])
            )

        elif linha.startswith("### "):
            finalizar_lista()
            elementos.append(
                Paragraph(
                    f"<b>{linha[4:].strip()}</b>",
                    estilos["corpo"],
                )
            )

        elif linha.startswith("- "):
            itens_lista.append(linha[2:].strip())

        elif linha[:2].isdigit() and linha[2:3] == ".":
            finalizar_lista()
            elementos.append(
                Paragraph(linha, estilos["corpo"])
            )

        else:
            finalizar_lista()
            elementos.append(
                Paragraph(linha, estilos["corpo"])
            )

    finalizar_lista()

    documento.build(elementos)


def main():
    arquivos_md = sorted(PASTA_MARKDOWN.glob("*.md"))

    if not arquivos_md:
        print("Nenhum arquivo Markdown encontrado.")
        return

    print("Gerando PDFs...\n")

    for arquivo_md in arquivos_md:
        arquivo_pdf = PASTA_PDF / f"{arquivo_md.stem}.pdf"

        converter_markdown(arquivo_md, arquivo_pdf)

        print(f"OK: {arquivo_pdf.name}")

    print(f"\nConcluído: {len(arquivos_md)} PDF(s) gerado(s).")


if __name__ == "__main__":
    main()