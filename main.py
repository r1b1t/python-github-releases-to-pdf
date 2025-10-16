import sys
import os
from PyQt5 import QtWidgets
from include.main_window_ui import Ui_MainWindow
from src.pdfconv import get_releases, make_pdf
from datetime import datetime, timezone


class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("GitHub Release PDF Oluşturucu")

        # Butonlar
        self.pushButton.clicked.connect(self.fetch_data)            # Getir
        self.pushButton_3.clicked.connect(self.create_pdf)          # PDF OLUŞTUR
        self.pushButton_2.clicked.connect(self.select_output_dir)   # Gözat (klasör)

        # Tabloyu düzenlenemez yap
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Dahili veri
        self.releases = []
        self.owner = ""
        self.repo = ""

    def select_output_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "PDF'nin Kaydedileceği Klasörü Seç")
        if dir_path:
            self.lineEdit_2.setText(dir_path)

    def _utc_to_local_str(self, utc_iso: str) -> str:
        try:
            dt_utc = datetime.strptime(utc_iso, "%Y-%m-%dT%H:%M:%SZ")
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            local_tz = datetime.now().astimezone().tzinfo
            dt_local = dt_utc.astimezone(local_tz)
            return dt_local.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return utc_iso

    def fetch_data(self):
        url = self.lineEdit.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Lütfen bir GitHub repo URL girin.")
            return

        try:
            parts = url.replace("https://github.com/", "").split("/")
            if len(parts) < 2 or not parts[0] or not parts[1]:
                QtWidgets.QMessageBox.warning(self, "Uyarı", "Geçerli bir GitHub repo URL'si girin (ör. https://github.com/owner/repo).")
                return

            self.owner, self.repo = parts[0], parts[1]

            self.releases = get_releases(self.owner, self.repo)

            self.tableWidget.setRowCount(0)
            for rel in self.releases:
                tag = rel.get("tag_name", "-")
                published_raw = rel.get("published_at", "-")
                name_or_body = rel.get("name", "") or rel.get("body", "")

                published = "-"
                if published_raw and published_raw != "-":
                    published = self._utc_to_local_str(published_raw)

                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(tag))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(published))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(name_or_body))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Veri alınamadı:\n{e}")

    def create_pdf(self):
        if not self.releases:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Henüz veri yok!")
            return

        out_dir = self.lineEdit_2.text().strip() or os.getcwd()
        base_name = f"releases_{self.owner}_{self.repo}.pdf" if (self.owner and self.repo) else "releases.pdf"
        output_path = os.path.join(out_dir, base_name)

        try:
            project_title = f"{self.owner}/{self.repo}" if (self.owner and self.repo) else "Release Notes"

           # <<< YENİ: checkbox değerini al >>>
            separate_pages = self.checkBox.isChecked()

            make_pdf(
                self.releases,
                output_path,
                project_title=project_title,
                separate_pages=separate_pages  # <<< YENİ PARAMETRE >>>
            )
            QtWidgets.QMessageBox.information(self, "Başarılı", f"PDF oluşturuldu:\n{output_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı:\n{e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
