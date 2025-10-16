import sys
import requests
from fpdf import FPDF
from datetime import datetime, timezone
import os, re

def get_releases(owner, repo):
    """GitHub API'den TÜM release verilerini çeker (sayfalandırmalı)."""
    releases = [] # Tüm sürümleri toplayacağımız liste
    page = 1  # GitHub API sayfa numarası
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases?page={page}&per_page=100"
        response = requests.get(url) # API isteği gönder

        if response.status_code != 200: # Başarısızsa hata ver
            raise Exception("Veri çekilirken hata oluştu.")

        page_data = response.json()  # JSON verisini al
        if not page_data:
            break  # sayfa boşsa dur
        releases.extend(page_data)
        page += 1

    return releases


def _utc_to_local_str(utc_iso: str) -> str:
    """'2025-10-16T09:01:01Z' -> yerel saat '16.10.2025 12:01' gibi."""
    try:
        # UTC stringini datetime nesnesine çevir
        dt_utc = datetime.strptime(utc_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        # Bilgisayarın yerel saat dilimini al
        local_tz = datetime.now().astimezone().tzinfo
        # UTC zamanı yerel zamana dönüştür
        dt_local = dt_utc.astimezone(local_tz)
        # okunabilir formatta döndür
        return dt_local.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return utc_iso # Eğer dönüştürme başarısızsa orijinal metni döndür

#Her PDF sayfasının başına proje başlığı ve ayraç çizgisi ekler.
def _draw_header(pdf, title_text):
    pdf.set_font("DejaVu", "B", 18) # Büyük, kalın font
    pdf.cell(0, 12, txt=title_text, ln=True, align="C") # Başlık (ortalanmış)
    pdf.set_font("DejaVu", "", 13)
    pdf.cell(0, 8, txt="Release Notes", ln=True, align="C") # Alt başlık
    pdf.ln(2)
    pdf.set_draw_color(80, 80, 80) # Gri renkli çizgi
    pdf.set_line_width(0.6)
    x1, x2 = 10, 200
    y = pdf.get_y() + 2
    pdf.line(x1, y, x2, y)  # Yatay çizgi çiz
    pdf.ln(6)


def _write_markdown(pdf, text: str):
    """
    Basit Markdown desteği:
      **bold**, _italic_, ### heading
    """
    lines = text.splitlines()  # Satırlara böl
    for line in lines:
        line = line.strip() 
        if not line: # Boş satırsa sadece satır atla
            pdf.ln(4)
            continue

        # ### başlık
        if line.startswith("###"):
            content = line.lstrip("#").strip() # # öğelerini atar
            pdf.set_font("DejaVu", "B", 13) # Kalın yap
            pdf.multi_cell(0, 7, txt=content) # Alt satıra otomatik geçer
            pdf.ln(2)
            continue

        # Kalın ve italik metinleri yakala
        # **kalın**
        """
        Bu, iki yıldız (**) karakterini kelimenin tam anlamıyla arar
        Normalde regex’te * özel bir karakterdir (önceki karakteri tekrarlamak anlamına gelir).
        Ama biz burada gerçekten yıldız işaretini aramak istiyoruz,
        o yüzden önüne \ koyarak “kaçırıyoruz” → \*.
        
        (.*?) → “iki yıldız arasındaki metni, kısa yoldan al”
        """
        bold_matches = re.findall(r"\*\*(.*?)\*\*", line)
        # __italik__
        italic_matches = re.findall(r"_(.*?)_", line)

        # Eğer bold veya italic varsa, satırı parça parça yaz
        if bold_matches or italic_matches:
            # regex ile sıralı parçala (hem kalın hem italik desteği)
            tokens = re.split(r"(\*\*.*?\*\*|_.*?_)", line)
            for tok in tokens:
                if not tok:
                    continue
                if tok.startswith("**") and tok.endswith("**"):
                    pdf.set_font("DejaVu", "B", 12)
                    pdf.write(6, tok[2:-2])
                elif tok.startswith("_") and tok.endswith("_"):
                    pdf.set_font("DejaVu", "I", 12)
                    pdf.write(6, tok[1:-1]) 
                else:
                    pdf.set_font("DejaVu", "", 12)
                    pdf.write(6, tok) #yoksa  aynen devam
            pdf.ln(6) #imleci 6 pt aşağı kaydırır
        else:
            # normal satır
            pdf.set_font("DejaVu", "", 12)
            pdf.multi_cell(0, 6, txt=line)
    pdf.ln(4)


def make_pdf(data, output_path, project_title="", separate_pages=False):
    """Verilerden Türkçe karakter destekli, stilli bir PDF oluşturur (markdown destekli)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # === Fontlar ===
    # === FONTLAR ===
    # python main.py şeklinde çalıştırılıyorsa burası geçerli
    base_dir = os.path.dirname(__file__)
    fonts_dir = os.path.join(base_dir, "fonts")

    # Eğer exe olarak çalıştırılırsa bu blok devreye girer
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS, "src")
        fonts_dir = os.path.join(base_dir, "fonts")

    # Font dosyalarını yükle
    regular_ttf = os.path.join(fonts_dir, "DejaVuLGCSans.ttf")
    bold_ttf = os.path.join(fonts_dir, "DejaVuLGCSans-Bold.ttf")
    italic_ttf = os.path.join(fonts_dir, "DejaVuLGCSerif-Italic.ttf")

    pdf.add_font("DejaVu", "", regular_ttf, uni=True)
    pdf.add_font("DejaVu", "B", bold_ttf,    uni=True)
    pdf.add_font("DejaVu", "I", italic_ttf, uni=True) 

    # Başlık
    title = project_title or "Project"
    _draw_header(pdf, title)

    x1, x2 = 10, 200  # ayraç için

    # İçerik
    for idx, release in enumerate(data, start=1):
        if separate_pages and idx > 1:
            pdf.add_page()
            _draw_header(pdf, title)

        tag = release.get("tag_name", "-")
        desc = release.get("body", "") or release.get("name", "")
        pub  = release.get("published_at", "-")
        if pub and pub != "-":
            pub = _utc_to_local_str(pub)

        # Sürüm
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, txt="Sürüm:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 7, txt=str(tag))
        pdf.ln(1)

        # Açıklama (markdown destekli)
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, txt="Açıklama:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        if desc:
            _write_markdown(pdf, desc)
        else:
            pdf.multi_cell(0, 7, txt="(Açıklama yok)")
        pdf.ln(1)

        # Tarih
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, txt="Tarih:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 7, txt=pub)

        if not separate_pages:
            pdf.ln(2)
            pdf.set_draw_color(120, 120, 120)
            y = pdf.get_y()
            pdf.line(x1, y, x2, y)
            pdf.ln(6)

    pdf.output(output_path)
