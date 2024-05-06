import json
import os
import sys

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (
    QScrollArea, QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QLineEdit,
    QTextEdit, QLabel, QGridLayout, QMessageBox, QRadioButton, QStyleFactory
)
from fpdf import FPDF


def clean_string(s):
    return s.encode('latin-1', 'ignore').decode('latin-1')


def get_json_file_path(filepath):
    if getattr(sys, 'frozen', False):
        # Executable path in PyInstaller environment
        bundle_dir = sys._MEIPASS
    else:
        # Running as a script
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    json_file_path = os.path.join(bundle_dir, filepath)
    return json_file_path


class UnicodePDF(FPDF):
    def __init__(self, sadhaka_name, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.sadhaka_name = sadhaka_name

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sadhaka Report for ' + self.sadhaka_name, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, align='L')
        self.ln(10)

    def chapter_body(self, content):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, content)
        self.ln()

    def chapter(self, title, content):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(content)


class AsanaRow(QWidget):
    def __init__(self, asanas, day_type=None, practice=None, parent=None):
        super().__init__(parent)

        self.asana_dropdown = QComboBox()
        self.asana_dropdown.addItems([asana['name'] for asana in asanas])

        self.duration_entry = QLineEdit()
        self.duration_entry.setMaxLength(10)  # Set maximum length to 10 characters
        self.duration_entry.setMaximumWidth(100)
        self.notes_entry = QTextEdit()
        self.notes_entry.setMaximumWidth(1000)

        self.delete_button = QPushButton("-")
        self.delete_button.setFixedWidth(40)
        self.delete_button.clicked.connect(self.delete)

        self.cardio_button = QRadioButton("Cardio")
        self.non_cardio_button = QRadioButton("Non-Cardio")
        if day_type == "cardio":
            self.cardio_button.setChecked(True)
        else:
            self.non_cardio_button.setChecked(True)

        layout = QGridLayout()
        layout.addWidget(self.asana_dropdown, 0, 0)
        layout.addWidget(self.duration_entry, 0, 1)
        layout.addWidget(self.cardio_button, 0, 2)
        layout.addWidget(self.non_cardio_button, 0, 3)
        layout.addWidget(self.notes_entry, 1, 0, 1, 4)
        layout.addWidget(self.delete_button, 1, 4)

        self.delete_button.setText('-')
        self.delete_button.setStyleSheet("QPushButton { color: red }")

        self.setLayout(layout)

        if practice:
            index = self.asana_dropdown.findText(practice['asana'])
            if index >= 0:
                self.asana_dropdown.setCurrentIndex(index)
            self.duration_entry.setText(practice['duration'])
            self.notes_entry.setText(practice['additionalNotes'])


    def delete(self):
        self.setParent(None)

    def get_values(self):
        return {
            'day_type': 'cardio' if self.cardio_button.isChecked() else 'nonCardio',
            'asana': self.asana_dropdown.currentText(),
            'duration': self.duration_entry.text(),
            'additionalNotes': self.notes_entry.toPlainText()
        }


class SadhakaApp(QWidget):
    def __init__(self):
        super().__init__()

        self.json_file_path = get_json_file_path('asanas.json')
        self.sadhakas_file_path = get_json_file_path('sadhakas.json')

        self.asanas = json.load(open(self.json_file_path))['asanas']
        self.sadhakas = json.load(open(self.sadhakas_file_path))['sadhakas']

        self.sadhaka_dropdown = QComboBox()
        self.sadhaka_dropdown.addItems([sadhaka['name'] for sadhaka in self.sadhakas])
        self.sadhaka_dropdown.currentTextChanged.connect(self.load_asanas)

        self.asana_rows = []

        self.add_asana_button = QPushButton("Add New Asana")
        self.add_asana_button.clicked.connect(self.add_asana_row)

        self.add_sadhaka_button = QPushButton("Add Sadhaka")
        self.add_sadhaka_button.clicked.connect(self.add_sadhaka)

        self.save_button = QPushButton("Save Sadhaka")
        self.save_button.clicked.connect(self.save_sadhaka)

        self.save_pdf_button = QPushButton("Save to PDF")
        self.save_pdf_button.clicked.connect(self.save_to_pdf)

        self.diet_and_notes_entry = QTextEdit()
        self.diet_and_notes_entry.setMaximumWidth(1000)

        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Sadhaka"))
        layout.addWidget(self.sadhaka_dropdown)
        layout.addWidget(self.scrollArea)
        layout.addWidget(self.add_asana_button)
        layout.addWidget(self.add_sadhaka_button)
        layout.addWidget(QLabel("Diet and Additional Notes"))
        layout.addWidget(self.diet_and_notes_entry)

        layout.addWidget(self.save_button)
        layout.addWidget(self.save_pdf_button)
        self.setLayout(layout)

        self.load_asanas()

    def load_asanas(self):
        for row in self.asana_rows:
            row.delete()
        self.asana_rows.clear()

        selected_sadhaka = self.sadhaka_dropdown.currentText()
        for sadhaka in self.sadhakas:
            if sadhaka['name'] == selected_sadhaka:
                for day_type, practices in sadhaka['practiceDays'].items():
                    for practice in practices:
                        self.add_asana_row(day_type, practice)
                if 'dietandadditionalnotes' in sadhaka:
                    self.diet_and_notes_entry.setText(sadhaka['dietandadditionalnotes'])

    def add_asana_row(self, day_type=None, practice=None):
        if day_type is None and practice is None:
            msgBox = QMessageBox()
            msgBox.setText("Is this Asana for a Cardio or Non-Cardio day?")
            msgBox.addButton(QPushButton('Cardio'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton('Non-Cardio'), QMessageBox.NoRole)
            ret = msgBox.exec_()
            day_type = 'cardio' if ret == 0 else 'nonCardio'

        row = AsanaRow(self.asanas, day_type, practice)
        self.asana_rows.append(row)
        self.scrollLayout.addWidget(row)

    def add_sadhaka(self):
        name, ok = QInputDialog.getText(self, 'Add Sadhaka', 'Enter Sadhaka Name:')
        if ok and name:
            self.sadhakas.append({'name': name, 'practiceDays': {}, 'dietandadditionalnotes': ''})
            self.sadhaka_dropdown.addItem(name)

    def save_sadhaka(self):
        selected_sadhaka = self.sadhaka_dropdown.currentText()
        for sadhaka in self.sadhakas:
            if sadhaka['name'] == selected_sadhaka:
                sadhaka['practiceDays']['cardio'] = [row.get_values() for row in self.asana_rows if
                                                     row.cardio_button.isChecked()]
                sadhaka['practiceDays']['nonCardio'] = [row.get_values() for row in self.asana_rows if
                                                        row.non_cardio_button.isChecked()]
                sadhaka['dietandadditionalnotes'] = self.diet_and_notes_entry.toPlainText()
            with open(self.sadhakas_file_path, 'w') as f:
                json.dump({"sadhakas": self.sadhakas}, f)

    def save_to_pdf(self):
        selected_sadhaka = self.sadhaka_dropdown.currentText()
        for sadhaka in self.sadhakas:
            if sadhaka['name'] == selected_sadhaka:
                pdf = UnicodePDF(sadhaka['name'])
                pdf.add_page()
                pdf.set_font("Helvetica", size=10)
                pdf.cell(0, 10, txt=clean_string(f"Sadhaka: {sadhaka['name']}"), ln=True)

                asanas = json.load(open(self.json_file_path))['asanas']
                for practice_day, practice_details in sadhaka['practiceDays'].items():
                    pdf.set_font("Helvetica", size=10, style='B')
                    pdf.cell(0, 10, txt=clean_string(practice_day.capitalize()), ln=True)
                    for practice in practice_details:
                        asana_name = practice['asana']
                        asana_description = ""
                        for asana in asanas:
                            if asana['name'] == asana_name:
                                asana_description = asana['description']
                                break
                        pdf.set_font("Helvetica", size=10)
                        pdf.cell(0, 10, txt=clean_string(asana_name), ln=True)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.cell(0, 10, txt=clean_string(f"Duration: {practice['duration']}"), ln=True)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.cell(0, 10, txt=clean_string(f"Special instructions: {practice['additionalNotes']}"), ln=True)

                        image_x = (pdf.w - 40) / 2
                        image_y = pdf.get_y() + 10
                        pdf.image(asana_name + ".png", x=image_x, y=image_y, w=40)
                        pdf.set_y(image_y + 40)

                        pdf.cell(0, 10, txt="Description:", ln=True)
                        pdf.set_font("Helvetica", size=8)
                        pdf.multi_cell(0, 10, txt=clean_string(asana_description), align='L')

                        pdf.set_y(pdf.h)

                pdf.set_font("Helvetica", size=10, style='B')
                pdf.cell(0, 10, txt="Diet and Additional Notes:", ln=True)
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(0, 10, txt=clean_string(self.diet_and_notes_entry.toPlainText()), align='L')

                pdf.output('sadhaka_report.pdf')
                QMessageBox.information(self, "Save to PDF", "Sadhaka details saved to PDF successfully!")
                break


def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('Fusion'))

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(242, 242, 242))
    palette.setColor(QPalette.WindowText, QColor(53, 53, 53))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(242, 242, 242))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, QColor(53, 53, 53))
    palette.setColor(QPalette.Button, QColor(242, 242, 242))
    palette.setColor(QPalette.ButtonText, QColor(53, 53, 53))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)

    sadhaka_app = SadhakaApp()
    sadhaka_app.showMaximized()

    app.exec_()


if __name__ == "__main__":
    main()
