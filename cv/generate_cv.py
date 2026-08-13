#!/usr/bin/env python3
"""Generate Ahmad Kadri's ATS-friendly German CV.

The PDF deliberately uses a single-column layout, embedded fonts, selectable text,
and visible, clickable links so that it works for both recruiters and ATS parsers.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as ReportLabImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "Ahmad_kadri_Lebenslauf.pdf"

NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#0F7C86")
TEAL_LIGHT = colors.HexColor("#E8F5F6")
TEXT = colors.HexColor("#243B53")
MUTED = colors.HexColor("#526D82")
RULE = colors.HexColor("#C7D9E2")
WHITE = colors.white


def register_fonts() -> None:
    font_dir = Path("/usr/share/fonts/truetype/dejavu")
    pdfmetrics.registerFont(TTFont("DejaVu", str(font_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(font_dir / "DejaVuSans-Bold.ttf")))


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=base["Title"],
            fontName="DejaVu-Bold",
            fontSize=24,
            leading=27,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "role": ParagraphStyle(
            "Role",
            parent=base["Normal"],
            fontName="DejaVu-Bold",
            fontSize=11,
            leading=14,
            textColor=TEAL,
            spaceAfter=5,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=8.2,
            leading=11,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="DejaVu-Bold",
            fontSize=10.4,
            leading=12.5,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=4,
            borderColor=TEAL,
            borderWidth=0,
            borderPadding=0,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=8.6,
            leading=11.8,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "project_title": ParagraphStyle(
            "ProjectTitle",
            parent=base["Heading3"],
            fontName="DejaVu-Bold",
            fontSize=9.3,
            leading=12,
            textColor=TEAL,
            spaceBefore=3,
            spaceAfter=2,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=7.8,
            leading=10.2,
            textColor=MUTED,
            spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=8.25,
            leading=11.2,
            textColor=TEXT,
            leftIndent=10,
            firstLineIndent=-7,
            bulletIndent=2,
            spaceAfter=1.4,
        ),
        "skill_label": ParagraphStyle(
            "SkillLabel",
            parent=base["BodyText"],
            fontName="DejaVu-Bold",
            fontSize=8.35,
            leading=11.2,
            textColor=NAVY,
        ),
        "skill_text": ParagraphStyle(
            "SkillText",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=8.25,
            leading=11.2,
            textColor=TEXT,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=7.2,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def link(url: str, label: str | None = None) -> str:
    visible = label or url
    return f'<link href="{url}" color="#0F7C86"><u>{visible}</u></link>'


def section_heading(text: str, styles: dict[str, ParagraphStyle]) -> list:
    rule = Table([[""]], colWidths=[174 * mm], rowHeights=[0.35 * mm])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL)]))
    return [Paragraph(text.upper(), styles["section"]), rule, Spacer(1, 2.2 * mm)]


def bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"•&nbsp;&nbsp;{text}", styles["bullet"])


def project(
    title: str,
    meta: str,
    bullets: list[str],
    styles: dict[str, ParagraphStyle],
    links: str | None = None,
) -> KeepTogether:
    flowables = [
        Paragraph(title, styles["project_title"]),
        Paragraph(meta, styles["meta"]),
    ]
    flowables.extend(bullet(item, styles) for item in bullets)
    if links:
        flowables.append(Paragraph(links, styles["meta"]))
    flowables.append(Spacer(1, 2.1 * mm))
    return KeepTogether(flowables)


def skill_table(rows: list[tuple[str, str]], styles: dict[str, ParagraphStyle]) -> Table:
    content = [
        [Paragraph(label, styles["skill_label"]), Paragraph(value, styles["skill_text"])]
        for label, value in rows
    ]
    table = Table(content, colWidths=[41 * mm, 133 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2.7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.7),
                ("LINEBELOW", (0, 0), (-1, -2), 0.35, RULE),
            ]
        )
    )
    return table


def page_decoration(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(TEAL)
    canvas.rect(0, height - 4 * mm, width, 4 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 12.5 * mm, width - 18 * mm, 12.5 * mm)
    canvas.setFont("DejaVu", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.2 * mm, "Ahmad Kadri | Junior Software Engineer")
    canvas.drawRightString(width - 18 * mm, 8.2 * mm, f"Seite {doc.page}")
    canvas.restoreState()


def build_story(styles: dict[str, ParagraphStyle]) -> list:
    contact_one = (
        "Braunschweig, Deutschland&nbsp;&nbsp;|&nbsp;&nbsp;+49 177 5022755&nbsp;&nbsp;|&nbsp;&nbsp;"
        + link("mailto:ahmadkadri@web.de", "ahmadkadri@web.de")
    )
    contact_two = link(
        "https://ahmadkadri978.github.io/portfolio",
        "ahmadkadri978.github.io/portfolio",
    )
    contact_three = (
        link("https://github.com/ahmadkadri978", "github.com/ahmadkadri978")
        + "&nbsp;&nbsp;|&nbsp;&nbsp;"
        + link("https://linkedin.com/in/kadri-ahmad", "linkedin.com/in/kadri-ahmad")
    )

    profile_photo = ReportLabImage(
        str(REPO_ROOT / "cv" / "ahmad-cv.jpg"),
        width=31 * mm,
        height=31 * mm,
    )
    header = Table(
        [
            [
                [
                    Paragraph("AHMAD KADRI", styles["name"]),
                    Paragraph("Junior Software Engineer | Java & Spring Boot", styles["role"]),
                    Paragraph(contact_one, styles["contact"]),
                    Paragraph(contact_two, styles["contact"]),
                    Paragraph(contact_three, styles["contact"]),
                ],
                profile_photo,
            ]
        ],
        colWidths=[139 * mm, 35 * mm],
        hAlign="LEFT",
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )

    story = [Spacer(1, 1.5 * mm), header, Spacer(1, 2.5 * mm)]

    story.extend(section_heading("Kurzprofil", styles))
    story.append(
        Paragraph(
            "Junior Software Engineer mit Schwerpunkt Java 21 und Spring Boot. Entwicklung sicherer, "
            "testbarer REST-APIs und datenbankgestützter Backend-Systeme mit klaren Modulgrenzen. "
            "Praktische Projekterfahrung mit PostgreSQL, OIDC/JWT, Docker, GitHub Actions sowie "
            "Observability und Incident-/Support-Workflows. Ich suche den Einstieg in ein deutsches "
            "Entwicklungsteam; Application Support und Operations ergänzen mein Backend-Profil.",
            styles["body"],
        )
    )

    story.extend(section_heading("Ausgewählte Praxisprojekte (Eigenprojekte)", styles))
    story.append(
        project(
            "RheinOps Platform - Service Operations & Incident Management",
            "2026 | Primäre Backend-Fallstudie | Java 21 / Spring Boot / PostgreSQL / Docker",
            [
                "Entwicklung einer modularen Service-Operations-Plattform mit Servicekatalog, Incident Management und SLA-gesteuerten Supportfällen; Modulgrenzen werden durch Spring-Modulith-Architekturtests geprüft.",
                "Absicherung der REST-API mit Keycloak, OIDC/JWT, Audience-Prüfung, vier Betriebsrollen und deny-by-default Autorisierung; Rollenmatrix wird per Integrationstest verifiziert.",
                "Umsetzung nebenläufigkeitssicherer Zustandswechsel mit Optimistic Locking, Flyway-Migrationen und unveränderbarer, akteursbezogener Audit-Historie in PostgreSQL.",
                "Aufbau einer reproduzierbaren Reliability-Umgebung mit Testcontainers, Prometheus, Grafana, Tempo, k6, Toxiproxy, Runbooks sowie vier GitHub-Actions-CI-Jobs.",
            ],
            styles,
            links=(
                link(
                    "https://github.com/ahmadkadri978/rheinops-platform",
                    "github.com/ahmadkadri978/rheinops-platform",
                )
                + " &nbsp;|&nbsp; "
                + link("https://rheinops-portfolio-demo.kadriahmad59.chatgpt.site", "Read-only Live-Demo")
                + " &nbsp;|&nbsp; "
                + link(
                    "https://github.com/ahmadkadri978/rheinops-platform/blob/main/docs/portfolio/cv-case-study.md",
                    "Architektur & Trade-offs",
                )
            ),
        )
    )

    story.append(
        project(
            "Restaurant Operating System - QR Ordering Platform",
            "2026 | Spring Boot / JavaScript / Docker Compose / Nginx / Redis / FCM",
            [
                "Entwicklung digitaler QR-Bestellungen, Tisch-Sessions, Statusverfolgung, Echtzeit-Benachrichtigungen sowie Staff-, Owner- und Super-Admin-Dashboards.",
                "Containerisierte Umgebung mit Docker Compose und Nginx; zustandslose Backend-Ausrichtung mit externer Zustandsverwaltung über Datenbank und Redis.",
                "Lokaler 30-Minuten-k6-Soak-Test: 11.987 Requests, p95-Latenz 51 ms und Fehlerrate 0,09 %; Testkontext und Evidenz sind im Portfolio dokumentiert.",
            ],
            styles,
            links=link(
                "https://ahmadkadri978.github.io/portfolio/#projects",
                "ahmadkadri978.github.io/portfolio/#projects",
            ),
        )
    )

    story.append(
        project(
            "Rizq Platform - Local Services Marketplace",
            "2025 | Spring Boot / Spring Security / JWT / PostgreSQL / Thymeleaf / Docker",
            [
                "Entwicklung eines lokalen Dienstleistungsmarktplatzes mit Registrierungsfreigabe, Rollenmodell, User-/Admin-Dashboards und Listing-Verwaltung.",
                "Umsetzung geschützter Workflows mit JWT-Cookies, DTO-basierten API-Grenzen sowie Stadt- und Servicetyp-Filtern.",
            ],
            styles,
            links=link(
                "https://github.com/ahmadkadri978/rizq-platform",
                "github.com/ahmadkadri978/rizq-platform",
            ),
        )
    )

    story.append(PageBreak())
    story.extend(section_heading("Weitere Praxisprojekte", styles))
    story.append(
        project(
            "Digital Library Management System",
            "2025 | Spring Boot / Spring Security / MySQL / Redis / Thymeleaf / Docker",
            [
                "Umsetzung von Buchverwaltung, Reservierungen, Duplikatschutz und rollenbasierten Admin-Workflows mit GitHub-OAuth2-Anmeldung.",
                "Qualitätssicherung mit JUnit, Mockito und MockMvc; Redis-Caching, Docker, GitHub Actions sowie praktische Deployment-Erfahrung mit AWS und Railway.",
            ],
            styles,
            links=link(
                "https://github.com/ahmadkadri978/Digital-Library-Management-System",
                "github.com/ahmadkadri978/Digital-Library-Management-System",
            ),
        )
    )

    story.extend(section_heading("Technische Kenntnisse", styles))
    story.append(
        skill_table(
            [
                ("Programmierung", "Java 21, SQL, JavaScript, HTML, CSS"),
                ("Backend & APIs", "Spring Boot, Spring MVC, Spring Data JPA/Hibernate, Spring Modulith, REST, DTOs, Bean Validation, OpenAPI/Swagger"),
                ("Security", "Spring Security, OIDC/OAuth2, JWT, Keycloak, Auth0, RBAC"),
                ("Daten & Integrität", "PostgreSQL, MySQL, Flyway, Redis, Full-Text Search, Optimistic Locking"),
                ("Testing", "JUnit 5, Mockito, MockMvc, Testcontainers, Architekturtests, k6, JMeter, Postman"),
                ("DevOps & Delivery", "Git, GitHub, Maven, Docker, Docker Compose, Nginx, GitHub Actions, CI/CD, AWS, Railway, Render"),
                ("Observability", "Prometheus, Grafana, Tempo, strukturierte Logs, Correlation IDs, Health Checks, SLOs"),
            ],
            styles,
        )
    )

    story.extend(section_heading("Arbeitsweise & Support-Kompetenz", styles))
    for item in [
        "Strukturierte Fehleranalyse über Reproduktion, Logs, Metriken, Traces und Datenbankzustand; Ergebnisse und nächste Schritte werden nachvollziehbar dokumentiert.",
        "Sicherheits- und Datenintegritätsregeln werden als testbare Systemgrenzen behandelt, nicht nur als Controller-Logik.",
        "Dokumentation durch OpenAPI, Architekturentscheidungen (ADRs), Runbooks, Walkthroughs und bekannte Einschränkungen.",
    ]:
        story.append(bullet(item, styles))

    story.extend(section_heading("Studium", styles))
    education = Table(
        [
            [
                Paragraph("11/2015 - 12/2020", styles["skill_label"]),
                Paragraph(
                    "<b>Bachelor in Informatik</b><br/>Universität Aleppo | Fakultät für Informatikingenieurwesen",
                    styles["skill_text"],
                ),
            ]
        ],
        colWidths=[41 * mm, 133 * mm],
        hAlign="LEFT",
    )
    education.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(education)

    story.extend(section_heading("Sprachen", styles))
    story.append(
        skill_table(
            [
                ("Arabisch", "Muttersprache"),
                ("Deutsch", "A2 - aktiv im Ausbau Richtung B1/B2"),
                ("Englisch", "B2"),
            ],
            styles,
        )
    )

    story.extend(section_heading("Zielpositionen", styles))
    story.append(
        Paragraph(
            "Junior Software Engineer | Java/Spring Boot Backend Developer | Application Support Engineer",
            styles["body"],
        )
    )
    return story


def main() -> None:
    register_fonts()
    styles = make_styles()
    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=17 * mm,
        title="Lebenslauf Ahmad Kadri",
        author="Ahmad Kadri",
        subject="Junior Software Engineer | Java & Spring Boot",
    )
    document.build(
        build_story(styles),
        onFirstPage=page_decoration,
        onLaterPages=page_decoration,
    )
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
