"""This Module hosts the various Dialog Classes, that can be shown from main Window."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as ET
from PySide6 import QtGui, QtWidgets
from PySide6.QtSvgWidgets import QGraphicsSvgItem

from excel2moodle import e2mMetadata
from excel2moodle.core.globals import XMLTags
from excel2moodle.core.question import Question
from excel2moodle.ui.UI_exportSettingsDialog import Ui_ExportDialog
from excel2moodle.ui.UI_variantDialog import Ui_Dialog

if TYPE_CHECKING:
    from excel2moodle.ui.appUi import MainWindow

logger = logging.getLogger(__name__)


class QuestionVariantDialog(QtWidgets.QDialog):
    def __init__(self, parent, question: Question) -> None:
        super().__init__(parent)
        self.setWindowTitle("Question Variant Dialog")
        self.maxVal = question.variants
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.spinBox.setRange(1, self.maxVal)
        self.ui.catLabel.setText(f"{question.katName}")
        self.ui.qLabel.setText(f"{question.name}")
        self.ui.idLabel.setText(f"{question.id}")

    @property
    def variant(self):
        return self.ui.spinBox.value()

    @property
    def categoryWide(self):
        return self.ui.checkBox.isChecked()


class ExportDialog(QtWidgets.QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export question Selection")
        self.appUi: MainWindow = parent
        self.ui = Ui_ExportDialog()
        self.ui.setupUi(self)
        self.ui.btnExportFile.clicked.connect(self.getExportFile)

    @property
    def exportFile(self) -> Path:
        return self._exportFile

    @exportFile.setter
    def exportFile(self, value: Path) -> None:
        self._exportFile = value
        self.ui.btnExportFile.setText(
            f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
        )

    def getExportFile(self) -> None:
        path = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            dir=str(self.exportFile),
            filter="xml Files (*.xml)",
        )
        path = Path(path[0])
        if path.is_file():
            self.exportFile = path
            self.ui.btnExportFile.setText(
                f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
            )
        else:
            logger.warning("No Export File selected")


class QuestionPreview:
    def __init__(self, parent) -> None:
        self.ui = parent.ui
        self.parent = parent

    def setupQuestion(self, question: Question) -> None:
        self.question: Question = question
        self.ui.qNameLine.setText(f"{self.question.qtype} - {self.question.name}")
        self.picScene = QtWidgets.QGraphicsScene(self.parent)
        self.ui.graphicsView.setScene(self.picScene)
        self.setText()
        self.setAnswers()
        if hasattr(self, "picItem") and self.picItem.scene() == self.picScene:
            logger.debug("removing Previous picture")
            self.picScene.removeItem(self.picItem)
            del self.picItem
        self.setPicture()

    def setPicture(self) -> None:
        if hasattr(self.question, "picture") and self.question.picture.ready:
            path = self.question.picture.path
            if path.suffix == ".svg":
                self.picItem = QGraphicsSvgItem(str(path))
            else:
                pic = QtGui.QPixmap(str(path))
                self.picItem = QtWidgets.QGraphicsPixmapItem(pic)
                if pic.isNull():
                    logger.warning("Picture null")
            scale = self._getImgFittingScale()
            self.picItem.setScale(scale)
            self.picScene.addItem(self.picItem)

    def _getImgFittingScale(self) -> float:
        view_size = self.ui.graphicsView.viewport().size()
        view_width = view_size.width()
        view_height = view_size.height()
        if isinstance(self.picItem, QtWidgets.QGraphicsPixmapItem):
            original_size = self.picItem.pixmap().size()
        elif isinstance(self.picItem, QGraphicsSvgItem):
            original_size = self.picItem.renderer().defaultSize()
        else:
            return 1  # Unknown item type
        scale_x = view_width / original_size.width()
        scale_y = view_height / original_size.height()
        return min(scale_x, scale_y)

    def setText(self) -> None:
        t = []
        for text in self.question.qtextParagraphs:
            t.append(ET.tostring(text, encoding="unicode"))
        if self.question.bulletList is not None:
            t.append(ET.tostring(self.question.bulletList, encoding="unicode"))
        self.ui.questionText.setText("\n".join(t))

    def setAnswers(self) -> None:
        if self.question.qtype == "NFM":
            list = ET.Element("ol")
            for ans in self.question.answerVariants:
                textEle = ET.Element("li")
                textEle.text = f"Result: {ans.find('text').text}"
                list.append(textEle)
            self.ui.answersLabel.setText(ET.tostring(list, encoding="unicode"))
        elif self.question.qtype == "NF":
            ans = self.question.element.find(XMLTags.ANSWER)
            self.ui.answersLabel.setText(f" Result: {ans.find('text').text}")
        elif self.question.qtype == "MC":
            list = ET.Element("ol")
            for ans in self.question.element.findall(XMLTags.ANSWER):
                textEle = ET.Element("li")
                pEle = ans.find("text").text
                frac = ans.get("fraction")
                anstext = ET.fromstring(pEle).text
                text = f"Fraction {frac}: {anstext}"
                textEle.text = text
                list.append(textEle)
            self.ui.answersLabel.setText(ET.tostring(list, encoding="unicode"))


class AboutDialog(QtWidgets.QMessageBox):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {e2mMetadata['name']}")
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)

        self.aboutMessage: str = f"""
        <h1> About {e2mMetadata["name"]} v{e2mMetadata["version"]}</h1><br>
        <p style="text-align:center">

                <b><a href="{e2mMetadata["homepage"]}">{e2mMetadata["name"]}</a> - {e2mMetadata["description"]}</b>
        </p>
        <p style="text-align:center">
            If you need help you can find some <a href="https://gitlab.com/jbosse3/excel2moodle/-/example/"> examples.</a>
            </br>
            A Documentation can be viewed by clicking "F1",
            or onto the documentation button.
            </br>
        </p>
        <p style="text-align:center">
        To see whats new in version {e2mMetadata["version"]} see the <a href="https://gitlab.com/jbosse3/excel2moodle#changelogs"> changelogs.</a>
        </p>
        <p style="text-align:center">
        This project is maintained by {e2mMetadata["author"]}.
        <br>
        Development takes place at <a href="{e2mMetadata["homepage"]}"> GitLab: {e2mMetadata["homepage"]}</a>
        contributions are very welcome
        </br>
        If you encounter any issues please report them under the <a href="https://gitlab.com/jbosse3/excel2moodle/-/issues/"> repositories issues page </a>.
        </br>
        </p>
        <p style="text-align:center">
        <i>This project is published under {e2mMetadata["license"]}, you are welcome, to share, modify and reuse the code.</i>
        </p>
        """
        self.setText(self.aboutMessage)
