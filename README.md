# GitHub Releases to PDF

GitHub üzerindeki herhangi bir reponun **release (sürüm) notlarını** çekip, düzenli ve Türkçe karakter destekli bir **PDF raporuna** dönüştüren PyQt5 tabanlı masaüstü uygulaması.

Repo URL'sini yapıştırın, sürümleri tabloda görüntüleyin ve tek tıkla PDF çıktısı alın.

## Özellikler

- 🔗 **Repo URL'si ile çalışır** — `https://github.com/owner/repo` adresini yapıştırmanız yeterli
- 📄 **Tüm sürümleri çeker** — GitHub API üzerinden sayfalandırmalı (pagination) olarak, 100'den fazla release olsa bile tamamını alır
- 🖥️ **Tablo önizlemesi** — sürüm etiketi, yayın tarihi ve açıklamayı PDF oluşturmadan önce arayüzde gösterir
- 📝 **Markdown desteği** — release notlarındaki `**kalın**`, `_italik_` ve `### başlık` biçimleri PDF'e yansıtılır; `:emoji:` kodları otomatik temizlenir
- 🇹🇷 **Türkçe karakter desteği** — gömülü DejaVu fontları sayesinde ç, ğ, ı, ö, ş, ü sorunsuz görüntülenir
- 🕐 **Yerel saat dönüşümü** — UTC yayın tarihleri bilgisayarın saat dilimine çevrilir
- 📑 **Sayfa düzeni seçeneği** — her sürümü ayrı sayfaya yazma veya tek akış halinde listeleme
- 🔑 **GitHub token desteği** — `GITHUB_TOKEN` ortam değişkeni tanımlıysa API istek limiti artar
- 📦 **Tek dosya .exe** — PyInstaller ile bağımsız Windows çalıştırılabilir dosyası üretilebilir

## Ekran Görüntüsü

Uygulama akışı:

1. GitHub repo URL'sini girin ve **Getir** butonuna basın
2. Release'ler tabloya yüklenir
3. Çıktı klasörünü seçin (boş bırakılırsa mevcut dizin kullanılır)
4. İsteğe bağlı olarak "her sürüm ayrı sayfada" seçeneğini işaretleyin
5. **PDF Oluştur** butonuna basın → `releases_<owner>_<repo>.pdf` dosyası oluşur

## Kurulum

```bash
git clone https://github.com/r1b1t/python-github-releases-to-pdf.git
cd python-github-releases-to-pdf
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py
```

### GitHub Token (opsiyonel)

GitHub API, anonim istekleri saatte 60 ile sınırlar. Daha yüksek limit için bir [Personal Access Token](https://github.com/settings/tokens) oluşturup ortam değişkeni olarak tanımlayın:

```bash
# Linux / macOS
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Windows (PowerShell)
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

### Windows için .exe oluşturma

```bash
pip install pyinstaller
pyinstaller main.spec
```

Çıktı `dist/main.exe` olarak üretilir. Fontlar exe içine gömüldüğü için tek dosya halinde dağıtılabilir.

## Proje Yapısı

```
├── main.py                  # Uygulama girişi ve PyQt5 ana pencere mantığı
├── main.spec                # PyInstaller yapılandırması (font gömme dahil)
├── requirements.txt
├── include/
│   └── main_window_ui.py    # Qt Designer'dan üretilen arayüz kodu
├── qtdesigner/
│   └── untitled.ui          # Qt Designer arayüz tasarım dosyası
└── src/
    ├── pdfconv.py           # GitHub API istekleri ve PDF üretimi
    └── fonts/               # DejaVu fontları (Türkçe karakter desteği)
```

## Kullanılan Teknolojiler

| Teknoloji | Amaç |
|---|---|
| [PyQt5](https://pypi.org/project/PyQt5/) | Masaüstü arayüzü |
| [requests](https://pypi.org/project/requests/) | GitHub REST API istekleri |
| [fpdf](https://pypi.org/project/fpdf/) | PDF üretimi (Unicode font desteğiyle) |
| [PyInstaller](https://pyinstaller.org/) | Bağımsız .exe paketleme |
