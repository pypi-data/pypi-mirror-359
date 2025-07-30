# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import json
from typing import Optional, Any

import pandas as pd


class InteractiveResponse:
    """
    Represents a rich response that may include text, a DataFrame, a Plotly chart, and code.

    Attributes:
        text (str): Main textual answer.
        table (Optional[pd.DataFrame]): DataFrame result.
        chart (Any): Plotly chart or visualization object.
        code (str): Python code used to generate the result.
        value (dict): JSON-serializable representation.
    """

    def __init__(
        self,
        text: str = "",
        value: Optional[Any] = None,
        code: str = "",
        table: Optional[pd.DataFrame] = None,
        chart: Optional[Any] = None,
    ) -> None:
        """
        Initializes the response container with optional components.

        Args:
            text (str): Main textual message.
            value (Optional[Any]): Precomputed value (not used directly; auto-generated).
            code (str): Generated Python code.
            table (Optional[pd.DataFrame]): Table result.
            chart (Optional[Any]): Chart object, typically a Plotly figure.
        """
        self.text = text or ""
        self.table = table
        self.chart = chart
        self.code = code
        self.value = self._build_value_json()

    def _build_value_json(self) -> dict:
        """
        Builds a JSON-serializable dictionary representing the response.

        Returns:
            dict: Dictionary with keys 'text', 'table', and 'chart'.
        """
        return {
            "text": self.text,
            "table": self._serialize_table(),
            "chart": self._serialize_chart(),
        }

    def _serialize_table(self) -> Any:
        """
        Serializes the table to a list of dictionaries.

        Returns:
            Any: Table in JSON-compatible format or empty string.
        """
        if isinstance(self.table, pd.DataFrame):
            return self.table.to_dict(orient="records")
        return ""

    def _serialize_chart(self) -> Any:
        """
        Serializes the chart to Plotly JSON format if applicable.

        Returns:
            Any: Plotly JSON or empty string.
        """
        if hasattr(self.chart, "to_plotly_json"):
            return self.chart.to_plotly_json()
        return ""

    def __str__(self) -> str:
        """
        Returns the textual part of the response.

        Returns:
            str: Text content or placeholder.
        """
        return self.text or "<No textual response>"

    def _repr_html_(self) -> str:
        """
        Custom Jupyter/IPython HTML rendering.

        Returns:
            str: Combined HTML for text, table, and chart.
        """
        from IPython.display import HTML

        html = ""

        # Text section
        if self.text:
            html += f"<p><strong>Response:</strong> {self.text}</p>"

        # Table section
        if hasattr(self.table, "_repr_html_"):
            html += self.table._repr_html_()
        elif hasattr(self.table, "to_html"):
            html += self.table.to_html()

        # Chart section
        if hasattr(self.chart, "_repr_html_"):
            html += self.chart._repr_html_()
        elif hasattr(self.chart, "show"):
            return self.chart.show()

        return html
