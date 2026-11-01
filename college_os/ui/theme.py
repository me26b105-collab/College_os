THEME_QSS = """
/* Global Window & Typography */
QWidget {
    background-color: #09090B;
    color: #FAFAFA;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
    outline: none;
}

/* Sidebar Navigation */
QWidget#Sidebar {
    background-color: #121215;
    border-right: 1px solid #27272A;
}

QPushButton.NavButton {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #A1A1AA;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #18181B;
    color: #FAFAFA;
    border-color: #27272A;
}

QPushButton.NavButton[active="true"] {
    background-color: #27272A;
    color: #FFFFFF;
    font-weight: 600;
}

/* Card Containers */
QFrame.Card {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 10px;
}

QFrame.Card:hover {
    border-color: #3F3F46;
}

/* Action Buttons */
QPushButton.PrimaryButton {
    background-color: #6366F1;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #4F46E5;
}

QPushButton.SecondaryButton {
    background-color: #27272A;
    color: #FAFAFA;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #3F3F46;
}

QPushButton.DangerButton {
    background-color: #7F1D1D;
    color: #FECACA;
    border: 1px solid #991B1B;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton.DangerButton:hover {
    background-color: #991B1B;
}

/* Text Inputs & Combo Boxes */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 6px;
    padding: 8px 12px;
    color: #FAFAFA;
    selection-background-color: #6366F1;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #6366F1;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #18181B;
    border: 1px solid #27272A;
    color: #FAFAFA;
    selection-background-color: #27272A;
}

/* Tables */
QTableWidget {
    background-color: #18181B;
    gridline-color: #27272A;
    border: 1px solid #27272A;
    border-radius: 8px;
    color: #E4E4E7;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #27272A;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #121215;
    color: #A1A1AA;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #27272A;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #09090B;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #27272A;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #3F3F46;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""