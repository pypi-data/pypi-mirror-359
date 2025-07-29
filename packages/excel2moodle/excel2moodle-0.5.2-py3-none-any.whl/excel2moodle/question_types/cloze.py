"""Implementation of tde cloze question type.

This question type is like the NFM but supports multiple fields of answers.
All Answers are calculated off an equation using the same variables.
"""

import logging
import math
import re
from typing import Literal, overload

import lxml.etree as ET

from excel2moodle.core.exceptions import QNotParsedException
from excel2moodle.core.globals import (
    Tags,
    TextElements,
)
from excel2moodle.core.question import ParametricQuestion
from excel2moodle.core.settings import Tags
from excel2moodle.question_types.nfm import NFMQuestionParser

logger = logging.getLogger(__name__)


class ClozePart:
    def __init__(
        self,
        question: ParametricQuestion,
        text: list[str],
    ) -> None:
        self.question = question
        self.text: list[ET.Element] = self._setupText(text)
        if not self.text:
            msg = f"Answer part for cloze question {self.question.id} is invalid without partText"
            raise ValueError(msg)

    @property
    def points(self) -> float:
        if hasattr(self, "_points"):
            return self._points
        return 0.0
        self.question.logger.error("Invalid call to points of unparsed cloze part")
        return 0.0

    @points.setter
    def points(self, points: float) -> None:
        self._points = points if points > 0 else 0.0

    @property
    def typ(self) -> Literal["MC", "NFM"] | None:
        if hasattr(self, "_typ"):
            return self._typ
        return None

    @property
    def mcAnswerString(self) -> str:
        if hasattr(self, "_mcAnswer"):
            return self._mcAnswer
        msg = "No MC Answer was set"
        raise ValueError(msg)

    @mcAnswerString.setter
    def mcAnswerString(self, answerString: str) -> None:
        self._mcAnswer: str = answerString

    def _setupText(self, text: list[str]) -> ET.Element:
        textList: list[ET.Element] = []
        for t in text:
            textList.append(TextElements.PLEFT.create())
            textList[-1].text = t
        return textList

    def setAnswer(
        self,
        equation: str | None = None,
        trueAns: list[str] | None = None,
        falseAns: list[str] | None = None,
    ) -> bool:
        if falseAns is not None:
            self.falseAnswers: list[str] = falseAns
        if trueAns is not None:
            self.trueAnswers: list[str] = trueAns
        if equation is not None:
            self.equation: str = equation
        check = False
        t = hasattr(self, "trueAnswers")
        f = hasattr(self, "falseAnswers")
        eq = hasattr(self, "equation")
        if t and f and not eq:
            self._typ: Literal["MC", "NFM"] = "MC"
            return True
        if eq and not t and not f:
            self._typ: Literal["MC", "NFM"] = "NFM"
            self.nfResults: list[float] = []
            return True
        return False

    def __repr__(self) -> str:
        answers: str = (
            self.equation
            if self.typ == "NFM"
            else f"{self.trueAnswers}\n {self.falseAnswers}"
        )
        return f"Cloze Part {self.typ}\n Answers: '{answers}'"


class ClozeQuestion(ParametricQuestion):
    """Cloze Question Type."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.questionParts: dict[int, ClozePart] = {}
        self.questionTexts: list[ET.Element] = []

    @property
    def partsNum(self) -> int:
        return len(self.questionParts)

    @property
    def points(self) -> float:
        pts: float = 0
        if self.isParsed:
            for p in self.questionParts.values():
                pts = pts + p.points
        else:
            pts = self.rawData.get(Tags.POINTS)
        return pts

    def _assembleAnswer(self, variant: int = 1) -> None:
        for partNum, part in self.questionParts.items():
            if part.typ == "MC":
                ansStr = part.mcAnswerString
                self.logger.info("MC answer part: %s ", ansStr)
            elif part.typ == "NFM":
                result = part.nfResults[variant - 1]
                ansStr = ClozeQuestionParser.getNumericAnsStr(
                    result,
                    self.rawData.get(Tags.TOLERANCE),
                    wrongSignCount=self.rawData.get(Tags.WRONGSIGNPERCENT),
                    points=part.points,
                )
                self.logger.info("NF answer part: %s ", ansStr)
            else:
                msg = "Type of the answer part is invalid"
                raise QNotParsedException(msg, self.id)
            ul = TextElements.ULIST.create()
            item = TextElements.LISTITEM.create()
            item.text = ansStr
            ul.append(item)
            part.text.append(ul)
            self.logger.debug("Appended part %s %s to main text", partNum, part)
            part.text.append(ET.Element("hr"))
            self.questionTexts.extend(part.text)

    def _assembleText(self, variant=0) -> list[ET.Element]:
        textParts = super()._assembleText(variant=variant)
        self.logger.debug("Appending QuestionParts to main text")
        textParts.extend(self.questionTexts)
        return textParts


class ClozeQuestionParser(NFMQuestionParser):
    """Parser for the cloze question type."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.question: ClozeQuestion

    def setup(self, question: ClozeQuestion) -> None:
        self.question: ClozeQuestion = question
        super().setup(question)

    def _parseAnswers(self) -> None:
        self._setupParts()
        self._parseAnswerParts()

    def _setupParts(self) -> None:
        parts: dict[int, ClozePart] = {
            self.getPartNumber(key): ClozePart(self.question, self.rawInput[key])
            for key in self.rawInput
            if key.startswith(Tags.QUESTIONPART)
        }
        partsNum = len(parts)
        equations: dict[int, str] = self._getPartValues(Tags.RESULT)
        trueAnsws: dict[int, list[str]] = self._getPartValues(Tags.TRUE)
        falseAnsws: dict[int, list[str]] = self._getPartValues(Tags.FALSE)
        points: dict[int, float] = self._getPartValues(Tags.POINTS)
        for num, part in parts.items():
            eq = equations.get(num)
            true = trueAnsws.get(num)
            false = falseAnsws.get(num)
            part.setAnswer(equation=eq, trueAns=true, falseAns=false)
        if len(points) == 0:
            pts = round(self.rawInput.get(Tags.POINTS) / partsNum, 3)
            for part in parts.values():
                part.points = pts
        elif len(points) != partsNum:
            logger.warning(
                "Some Answer parts are missing the points, they will get the standard points"
            )
            for num, part in parts.items():
                p = points.get(num)
                part.points = p if p is not None else self.rawInput.get(Tags.POINTS)

        self.question.questionParts = parts

    @overload
    def _getPartValues(self, Tag: Literal[Tags.RESULT]) -> dict[int, str]: ...
    @overload
    def _getPartValues(self, Tag: Literal[Tags.POINTS]) -> dict[int, float]: ...
    @overload
    def _getPartValues(
        self, Tag: Literal[Tags.TRUE, Tags.FALSE]
    ) -> dict[int, list[str]]: ...
    def _getPartValues(self, Tag):
        tagValues: dict = {
            self.getPartNumber(key): self.rawInput[key]
            for key in self.rawInput
            if key.startswith(Tag)
        }
        self.logger.warning("Found part data %s:  %s", Tag, tagValues)
        return tagValues

    def _parseAnswerParts(self) -> None:
        """Parse the numeric or MC result items."""
        try:
            bps = str(self.rawInput[Tags.BPOINTS])
        except KeyError:
            bps = None
            number = 1
        else:
            varNames: list[str] = self._getVarsList(bps)
            self.question.variables, number = self._getVariablesDict(varNames)
        for variant in range(number):
            self.setupAstIntprt(self.question.variables, variant)
            for partNum, part in self.question.questionParts.items():
                if part.typ == "NFM":
                    result = self._calculateNFMPartResult(part, partNum, variant)
                    part.nfResults.append(result)
                    logger.debug("Appended NF part %s result: %s", partNum, result)
                elif part.typ == "MC":
                    ansStr = self.getMCAnsStr(
                        part.trueAnswers, part.falseAnswers, points=part.points
                    )
                    part.mcAnswerString = ansStr
                    logger.debug("Appended MC part %s: %s", partNum, ansStr)
        self._setVariants(number)

    def _calculateNFMPartResult(
        self, part: ClozePart, partNum: int, variant: int
    ) -> float:
        result = self.astEval(part.equation)
        if isinstance(result, float):
            try:
                firstResult = self.rawInput[f"{Tags.FIRSTRESULT}:{partNum}"]
            except KeyError:
                firstResult = 0.0
            if variant == 0 and not math.isclose(result, firstResult, rel_tol=0.002):
                self.logger.warning(
                    "The calculated result %s differs from given firstResult: %s",
                    result,
                    firstResult,
                )
            return result
        msg = f"The expression {part.equation} could not be evaluated."
        raise QNotParsedException(msg, self.question.id)

    def getPartNumber(self, indexKey: str) -> int:
        """Return the number of the question Part.

        The number should be given after the `@` sign.
        This is number is used, to reference the question Text
        and the expected answer fields together.
        """
        try:
            num = re.findall(r":(\d+)$", indexKey)[0]
        except IndexError:
            msg = f"No :i question Part value given for {indexKey}"
            raise QNotParsedException(msg, self.question.id)
        else:
            return int(num)

    @staticmethod
    def getNumericAnsStr(
        result: float,
        tolerance: float,
        points: float = 1,
        wrongSignCount: int = 50,
        wrongSignFeedback: str = "your result has the wrong sign (+-)",
    ) -> str:
        """Generate the answer string from `result`.

        Parameters.
        ----------
        wrongSignCount:
            If the wrong sign `+` or `-` is given, how much of the points should be given.
            Interpreted as percent.
        tolerance:
            The relative tolerance, as fraction

        """
        absTol = f":{round(result * tolerance, 3)}"
        answerParts: list[str | float] = [
            "{",
            points,
            ":NUMERICAL:=",
            round(result, 3),
            absTol,
            "~%",
            wrongSignCount,
            "%",
            round(result * (-1), 3),
            absTol,
            f"#{wrongSignFeedback}",
            "}",
        ]
        answerPStrings = [str(part) for part in answerParts]
        return "".join(answerPStrings)

    @staticmethod
    def getMCAnsStr(
        true: list[str],
        false: list[str],
        points: float = 1,
    ) -> str:
        """Generate the answer string for the MC answers."""
        truePercent: float = round(100 / len(true), 1)
        falsePercent: float = round(100 / len(false), 1)
        falseList: list[str] = [f"~%-{falsePercent}%{ans}" for ans in false]
        trueList: list[str] = [f"~%{truePercent}%{ans}" for ans in true]
        answerParts: list[str | float] = [
            "{",
            points,
            ":MULTIRESPONSE:",
        ]
        answerParts.extend(trueList)
        answerParts.extend(falseList)
        answerParts.append("}")

        answerPStrings = [str(part) for part in answerParts]
        return "".join(answerPStrings)
