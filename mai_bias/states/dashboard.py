from PySide6.QtWidgets import (
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QScrollArea,
    QMessageBox,
    QLineEdit,
)
from PySide6.QtCore import Qt
from datetime import datetime

from mammoth_commons.externals import prepare
from .step import save_all_runs
from .style import Styled
import re
from PySide6.QtGui import QPixmap
from functools import partial


def now():
    return datetime.now().strftime("%y-%m-%d %H:%M")


ENGLISH_MONTHS = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def convert_to_readable(date_str):
    dt = datetime.strptime(date_str, "%y-%m-%d %H:%M")
    return f"{dt.day} {ENGLISH_MONTHS[dt.month]} {dt.year} - {dt.strftime('%H:%M')}"


class Dashboard(Styled):
    def __init__(self, stacked_widget, runs, tag_descriptions):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.runs = runs

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        top_row_layout = QHBoxLayout()
        top_row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_button = QPushButton(self)
        logo_pixmap = QPixmap(
            prepare(
                "https://raw.githubusercontent.com/mammoth-eu/mammoth-commons/dev/mai_bias/logo.png"
            )
        )
        logo_pixmap = logo_pixmap.scaled(
            270,
            135,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        logo_button.setIcon(logo_pixmap)
        logo_button.setIconSize(logo_pixmap.size())
        logo_button.setFixedSize(
            logo_pixmap.width() + 15, logo_pixmap.height() + 15
        )  # accommodate padding
        logo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logo_button.setToolTip("New analysis")
        logo_button.clicked.connect(self.create_new_item)

        logo_button.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
                padding: 10px;
                margin-left: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                border: 2px solid black;
            }
        """
        )

        top_row_layout.addWidget(logo_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Spacer to push buttons to the right
        top_row_layout.addStretch()

        # Buttons on the right
        search_field = QLineEdit(self)
        search_field.setPlaceholderText("Search for title or module...")
        search_field.setFixedSize(200, 30)
        search_field.textChanged.connect(self.filter_runs)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        button_layout.addWidget(search_field)

        # Wrap buttons in a widget so layout behaves properly
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        top_row_layout.addWidget(button_widget, alignment=Qt.AlignmentFlag.AlignTop)

        # Add everything to the main layout
        self.main_layout.addLayout(top_row_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea QWidget {
                background: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                border: none;
                background: transparent;
            }
        """
        )

        # Content Widget
        self.content_widget = QWidget()
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(0)
        self.scroll_area.setWidget(self.content_widget)

        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)
        self.tag_descriptions = tag_descriptions

        self.invisible_runs = set()
        self.refresh_dashboard()

    def filter_runs(self, text):
        prev = self.invisible_runs
        self.invisible_runs = set()
        for index, run in enumerate(self.runs):
            if text.lower() in run["description"].lower():
                continue
            if text.lower() in run.get("dataset", dict()).get("module", "").lower():
                continue
            if text.lower() in run.get("model", dict()).get("module", "").lower():
                continue
            if text.lower() in run.get("analysis", dict()).get("module", "").lower():
                continue
            if text.lower() in get_special_title(run).lower():
                continue
            self.invisible_runs.add(index)
        # refresh but only if something changed
        if (
            len(prev - self.invisible_runs) == 0
            and len(self.invisible_runs - prev) == 0
        ):
            return
        self.refresh_dashboard()

    def view_result(self, index):
        run = self.runs.pop(index)
        self.runs.append(run)
        self.refresh_dashboard()
        self.stacked_widget.slideToWidget(4)

    def edit_item(self, index):
        if self.runs[index].get("status", "") != "completed":
            reply = QMessageBox.StandardButton.Yes
        else:
            reply = QMessageBox.question(
                self,
                "Edit?",
                f"You can change modules and modify parameters. "
                "However, this will also remove its results. Consider creating a variation if you want to preserve current results.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.runs[index]["timestamp"] = now()
        run = self.runs.pop(index)
        self.runs.append(run)
        self.refresh_dashboard()
        self.stacked_widget.slideToWidget(1)

    def create_variation(self, index):
        new_run = self.runs[index].copy()
        new_run["status"] = "new"
        new_run["timestamp"] = now()
        self.runs.append(new_run)
        self.stacked_widget.slideToWidget(1)

    def create_new_item(self):
        self.runs.append(
            {"description": "", "timestamp": now(), "status": "in_progress"}
        )
        self.stacked_widget.slideToWidget(1)
        self.refresh_dashboard()

    def delete_item(self, index):
        reply = QMessageBox.question(
            self,
            "Delete?",
            f"The analysis will be permanently deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.runs.pop(index)
        self.refresh_dashboard()
        save_all_runs("history.json", self.runs)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())

    def showEvent(self, event):
        self.refresh_dashboard()

    def refresh_dashboard(self):
        self.clear_layout(self.layout)

        visual_pos = -1
        sorted_items = sorted(
            (
                (i, run)
                for i, run in enumerate(self.runs)
                if i not in self.invisible_runs
            ),
            key=lambda x: x[1]["description"]
            + x[1].get("dataset", {}).get("module", "")
            + x[1].get("model", {}).get("module", "")
            + x[1].get("analysis", {}).get("module", "")
            + x[1]["status"]
            + x[1]["timestamp"],
        )

        current_group_key = None
        group_layout = None
        button_rows = []
        tags_to_show = []

        for index, run in sorted_items:
            visual_pos += 1
            group_key = (
                run["description"],
                run.get("dataset", {}).get("module", ""),
                run.get("model", {}).get("module", ""),
                run.get("analysis", {}).get("module", ""),
            )

            if group_key != current_group_key:
                if group_layout:
                    for row in button_rows:
                        group_layout.addLayout(row)

                    if last_run["description"] or tags_to_show:
                        title_and_tags_layout = QHBoxLayout()
                        title_and_tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                        if last_run["status"] == "completed":
                            current_row.addWidget(
                                self.create_icon_button(
                                    "➕",
                                    "#007bff",
                                    "New variation",
                                    partial(
                                        lambda i=last_index: self.create_variation(i)
                                    ),
                                )
                            )

                        current_row.addWidget(
                            self.create_icon_button(
                                "🗑",
                                "#dc3545",
                                "Delete",
                                partial(lambda i=last_index: self.delete_item(i)),
                            )
                        )

                        for tag in tags_to_show:
                            tag_btn = self.create_tag_button(
                                f" {tag} ",
                                "Module info",
                                partial(lambda t=tag: self.show_tag_description(t)),
                            )
                            title_and_tags_layout.addWidget(tag_btn)

                        if last_run["description"]:
                            title_label = QLabel(" " + last_run["description"], self)
                            title_label.setStyleSheet(
                                "font-size: 15px; font-weight: bold;"
                            )
                            title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                            title_and_tags_layout.addWidget(title_label)

                        group_layout.addLayout(title_and_tags_layout)
                        group_layout.addSpacing(5)

                    self.layout.addLayout(group_layout)

                current_group_key = group_key
                group_layout = QVBoxLayout()
                group_layout.addSpacing(5)
                button_rows = []
                tags_to_show = []

            # Create run button
            button_color = (
                "#ffbbbb"
                if "fail" in get_special_title(run).lower()
                or "bias" in get_special_title(run).lower()
                else (
                    "#aaccff"
                    if any(
                        word in get_special_title(run).lower()
                        for word in [
                            "report",
                            "audit",
                            "scan",
                            "analysis",
                            "explanation",
                        ]
                    )
                    else "#bbffbb"
                )
            )
            if run["status"] != "completed":
                button_color = "#ffffbb"

            run_button = QPushButton(self)
            special = get_special_title(run)
            label = QLabel(
                (
                    "<b>" + special + "</b><br>" + convert_to_readable(run["timestamp"])
                    if run["status"] == "completed"
                    else "<b>Creating</b><br>" + convert_to_readable(run["timestamp"])
                ),
                run_button,
            )
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            label.setToolTip("Show results")
            label.setWordWrap(True)
            button_layout = QVBoxLayout(run_button)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            button_layout.addWidget(label)
            button_layout.setContentsMargins(5, 5, 5, 5)
            run_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: white;
                    color: black;
                    border-radius: 5px;
                    font-size: 16px;
                    border: 1px solid {self.darker_color(self.darker_color(button_color))};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid black;
                    background-color: {self.highlight_color(button_color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.highlight_color(self.highlight_color(button_color))};
                }}
            """
            )
            run_button.clicked.connect(
                partial(
                    lambda i=index, r=run: (
                        self.view_result(i)
                        if r["status"] == "completed"
                        else self.edit_item(i)
                    )
                )
            )
            run_button.setFixedSize(160, 42)

            widget_width = self.scroll_area.viewport().width() or 600
            margin = 5
            current_row = button_rows[-1] if button_rows else QHBoxLayout()
            current_row_width = sum(
                child.widget().width() + margin
                for i in range(current_row.count())
                if (child := current_row.itemAt(i)) and child.widget()
            )

            if current_row_width + 160 + margin > widget_width:
                current_row = QHBoxLayout()
                current_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
                button_rows.append(current_row)

            if not button_rows:
                current_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
                button_rows.append(current_row)

            current_row.addWidget(run_button)

            for key in ["dataset", "model", "analysis"]:
                mod = run.get(key, {}).get("module", "")
                if mod and mod not in tags_to_show:
                    tags_to_show.append(mod)

            last_run = run
            last_index = index

        # Final group
        if group_layout:
            for row in button_rows:
                group_layout.addLayout(row)

            if last_run["description"] or tags_to_show:
                title_and_tags_layout = QHBoxLayout()
                title_and_tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                if last_run["status"] == "completed":
                    current_row.addWidget(
                        self.create_icon_button(
                            "➕",
                            "#007bff",
                            "New variation",
                            partial(lambda i=last_index: self.create_variation(i)),
                        )
                    )

                current_row.addWidget(
                    self.create_icon_button(
                        "🗑",
                        "#dc3545",
                        "Delete",
                        partial(lambda i=last_index: self.delete_item(i)),
                    )
                )

                for tag in tags_to_show:
                    tag_btn = self.create_tag_button(
                        f" {tag} ",
                        "Module info",
                        partial(lambda t=tag: self.show_tag_description(t)),
                    )
                    title_and_tags_layout.addWidget(tag_btn)

                if last_run["description"]:
                    title_label = QLabel(" " + last_run["description"], self)
                    title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
                    title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    title_and_tags_layout.addWidget(title_label)

                group_layout.addLayout(title_and_tags_layout)
                group_layout.addSpacing(5)

            self.layout.addLayout(group_layout)

        self.content_widget.adjustSize()

    def show_tag_description(self, tag):
        """Show description of a tag."""
        msg = QMessageBox()
        msg.setWindowTitle("Module info")
        msg.setText(self.tag_descriptions.get(tag, "No description available."))
        msg.exec()


def get_special_title(run):
    try:
        match = re.search(
            r"<h1\b[^>]*>.*?</h1>",
            run.get("analysis", dict()).get("return", ""),
            re.DOTALL,
        )
        if match:
            return match.group().replace("h1", "span")
    except Exception:
        pass
    return ""
