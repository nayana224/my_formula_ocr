APP_STYLESHEET = """
QWidget#root {
    background: #f4f7fb;
}
QMainWindow, QStatusBar {
    background: #f4f7fb;
    color: #172033;
}
QFrame#card {
    background: #ffffff;
    border: 1px solid #dce3ee;
    border-radius: 12px;
}
QLabel#sectionLabel {
    color: #27364f;
    font-size: 13px;
    font-weight: 700;
}
QLabel#preview {
    background: #fbfcfe;
    border: 1px solid #e2e7f0;
    border-radius: 9px;
    color: #667085;
}
QPlainTextEdit, QLineEdit, QListWidget, QComboBox {
    background: #fbfcfe;
    color: #172033;
    border: 1px solid #d8e0eb;
    border-radius: 8px;
    selection-background-color: #bfdbfe;
    selection-color: #172033;
}
QPlainTextEdit {
    padding: 10px;
    font-family: monospace;
    font-size: 13px;
}
QLineEdit, QComboBox {
    min-height: 32px;
    padding: 0 10px;
}
QListWidget {
    padding: 4px;
}
QListWidget::item {
    min-height: 30px;
    padding: 4px 8px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background: #dbeafe;
    color: #172033;
}
QPushButton {
    min-height: 34px;
    padding: 0 14px;
    background: #ffffff;
    color: #27364f;
    border: 1px solid #cfd8e6;
    border-radius: 8px;
    font-weight: 600;
}
QPushButton:hover {
    background: #f8fafc;
    border-color: #aebbd0;
}
QPushButton:pressed {
    background: #eef2f7;
}
QPushButton:disabled {
    color: #98a2b3;
    background: #f2f4f7;
    border-color: #e4e7ec;
}
QPushButton#primaryButton {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
    padding: 0 18px;
}
QPushButton#primaryButton:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
}
QCheckBox {
    spacing: 7px;
    color: #344054;
    font-weight: 600;
}
QCheckBox::indicator {
    width: 17px;
    height: 17px;
}
QSplitter::handle {
    background: transparent;
    width: 8px;
}
QStatusBar {
    border-top: 1px solid #e3e8ef;
}
"""
