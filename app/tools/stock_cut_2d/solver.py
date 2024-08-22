"""
    Stock Cutting Solver | Two dimensional problem
"""

import uuid
from pathlib import Path
from typing import List

from const import TEMP
from opcut.calculate import calculate
from opcut.common import OutputFormat
from opcut.common import OutputSettings
from opcut.generate import generate
from pypdf import PdfWriter
from tools.stock_cut_2d.models import JobModel
from tools.stock_cut_2d.models import ResultModel


class Solver:
    """
    2D Stock cutting solver class.
    Utilizes opcut module.
    """

    SETTINGS = OutputSettings(
        pagesize=(210, 297),
        margin_top=20,
        margin_bottom=20,
        margin_left=20,
        margin_right=20,
    )

    def __init__(self) -> None:
        pass

    def calculate(self, job: JobModel) -> ResultModel:
        """Calculates the perfect fit for the given model.

        Args:
            job (JobModel): The job from which to draw the result.

        Returns:
            ResultModel: The result of the given job.
        """
        self._ensure_unique_ids(job=job)
        result = calculate(
            method=job.method,
            params=job.params,  # type: ignore
        )
        return result  # type: ignore

    def generate(self, result: ResultModel, output_format: OutputFormat) -> Path:
        """Generates a file output from the given result.

        Args:
            result (ResultModel): The result from which to generate the pdf.
            output_format (Literal[OutputFormat.PDF, OutputFormat.SVG]): The output format.

        Returns:
            Path: The path to the generated pdf file.
        """
        paths = self._generate_output(result=result, output_format=output_format)
        match output_format:
            case OutputFormat.PDF:
                return self._merge_pdf(paths=paths)
            case OutputFormat.SVG:
                return self._merge_svg(paths=paths)
            case _:
                raise NotImplementedError(f"The given output format is not supported: {output_format}.")

    def _generate_output(self, result: ResultModel, output_format: OutputFormat) -> List[Path]:
        """Generates the output from the given result. Utilizes opcut.generate.

        Args:
            result (ResultModel): The result from which to generate the output.
            output_format (Literal[OutputFormat.PDF, OutputFormat.SVG]): The output format.

        Returns:
            List[Path]: The output file list with all paths to all generated files.
        """
        paths: List[Path] = []
        for panel in result.params.panels:
            pdf_bytes = generate(
                result=result,  # type: ignore
                output_format=output_format,
                panel_id=panel.id,
                settings=Solver.SETTINGS,
            )
            file_path = Path(TEMP, f"{uuid.uuid4()}.{output_format.value}")
            paths.append(file_path)
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)

        return paths

    def _merge_pdf(self, paths: List[Path]) -> Path:
        """Merges the given list of pdf files.

        Args:
            paths (List[Path]): The list of files to merge.

        Returns:
            Path: The merged pdf file path.
        """
        path = Path(TEMP, f"{uuid.uuid4()}.pdf")
        with PdfWriter() as merger:
            for pdf in paths:
                merger.append(pdf)
            merger.write(path)
        return path

    def _merge_svg(self, paths: List[Path]) -> Path:
        """Not implemented."""
        # FIXME
        raise NotImplementedError("SVG export ist not supported yet.")

    def _ensure_unique_ids(self, job: JobModel) -> None:
        """Ensures that all ids (panels and items) of the given job are unique.

        Args:
            job (JobModel): The job to validate.

        Raises:
            ValueError: Raised if panel IDs are not unique.
            ValueError: Raised if item IDs are not unique.
        """
        panel_ids: List[str] = []
        item_ids: List[str] = []

        for panel in job.params.panels:
            if panel.id in panel_ids:
                raise ValueError("Panel IDs are not unique.")
            panel_ids.append(panel.id)

        for item in job.params.items:
            if item.id in item_ids:
                raise ValueError("Item IDs are not unique.")
            item_ids.append(item.id)
