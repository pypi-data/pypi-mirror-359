from PySide6.QtWidgets import QPushButton, QWidget, QSizePolicy


class Styled(QWidget):
    def create_icon_button(self, text, color, tooltip, callback, size=30):
        button = QPushButton(text, self)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                border-radius: 5px;
                font-size: {size*6//8 if text=='+' else size//2}px;
                border: 1px solid black;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 2px solid black;
                background-color: {self.highlight_color(color)};
            }}
        """
        )

        button.setFixedSize(size, size)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button

    def create_tag_button(self, text, tooltip, callback):
        button = QPushButton(text, self)

        button.setStyleSheet(
            """
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border-radius: 2px;
                font-size: 12px;
                border: 1px solid black;
            }
            QPushButton:hover {
                border: 2px solid black;
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #7A7A7A;
            }
        """
        )
        button.setFixedHeight(20)

        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        # button.setFixedSize(180, 30)

        return button

    def highlight_color(self, color):
        if color.startswith("#"):
            color = color[1:]
        r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(r + 22, 255)
        g = min(g + 22, 255)
        b = min(b + 22, 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def darker_color(self, color):
        if color.startswith("#"):
            color = color[1:]
        r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(r - 64, 0)
        g = max(g - 64, 0)
        b = max(b - 64, 0)
        return f"#{r:02x}{g:02x}{b:02x}"
