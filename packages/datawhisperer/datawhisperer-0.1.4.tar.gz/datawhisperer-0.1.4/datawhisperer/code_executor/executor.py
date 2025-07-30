# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import ast
import io
import re
import sys
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from datawhisperer.code_executor.fixer import CodeFixer


def sanitize_code(code: str) -> str:
    """
    Cleans LLM-generated code by removing Markdown formatting and disallowed function calls.

    Args:
        code (str): Raw code string from the LLM.

    Returns:
        str: Sanitized Python code.
    """
    code = code.strip()

    if code.startswith("```"):
        code = code.strip("`").strip()
        if code.startswith("python"):
            code = code[6:].strip()

    code = re.sub(r"^\s*(fig|plt)\.show\s*\(\s*\)\s*;?\s*$", "", code, flags=re.MULTILINE)
    code = code.replace("fig.show()", "")

    return code.strip()


def detect_last_of_type(context: Dict[str, Any], expected_type: type, exclude: str = "df") -> Any:
    """
    Finds the last object of a given type in the context, excluding a specific name.

    Args:
        context (Dict[str, Any]): Variable execution context.
        expected_type (type): Expected type to find.
        exclude (str): Name to exclude.

    Returns:
        Any: Last matching object or None.
    """
    for key in reversed(list(context.keys())):
        if key != exclude and isinstance(context[key], expected_type):
            return context[key]
    return None


def detect_last_dataframe(
    context: Dict[str, Any],
    dataframe_name: str,
    generated_names: Optional[list[str]] = None,
) -> Optional[pd.DataFrame]:
    """
    Detects the most recent DataFrame different from the original.

    Args:
        context (Dict[str, Any]): Execution context.
        dataframe_name (str): Original DataFrame name.
        generated_names (Optional[list[str]]): List of newly created variable names.

    Returns:
        Optional[pd.DataFrame]: Most recent new DataFrame or None.
    """
    original_df = context.get(dataframe_name)

    if generated_names:
        for name in reversed(generated_names):
            candidate = context.get(name)
            if isinstance(candidate, pd.DataFrame) and candidate is not original_df:
                return candidate

    for key in reversed(list(context.keys())):
        val = context[key]
        if isinstance(val, pd.DataFrame) and val is not original_df:
            return val

    return None


def detect_last_plotly_chart(context: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Detects the last Plotly figure-like object in the context.

    Args:
        context (Dict[str, Any]): Execution context.

    Returns:
        Optional[go.Figure]: Last chart-like object or None.
    """
    for key in reversed(list(context.keys())):
        val = context[key]
        if hasattr(val, "to_plotly_json"):
            return val
    return None


def run_user_code(
    code: str,
    context: Dict[str, object],
    dataframe_name: str,
) -> Tuple[str, Any, Any, str, bool]:
    """
    Executes user-generated Python code within a controlled context.

    Args:
        code (str): User code to execute.
        context (Dict[str, object]): Context in which to execute the code.
        dataframe_name (str): Reference name for the main DataFrame.

    Returns:
        Tuple[str, Any, Any, str, bool]: Output text, resulting DataFrame, chart, final code, success flag.
    """
    code = sanitize_code(code)
    stdout = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = stdout

    table_result = None
    chart_result = None
    output_text = ""

    try:
        parsed = ast.parse(code, mode="exec")
        last_expr = parsed.body[-1] if isinstance(parsed.body[-1], ast.Expr) else None
        if last_expr:
            parsed.body = parsed.body[:-1]

        local_context = context.copy()
        before_keys = set(local_context.keys())

        exec(compile(ast.Module(parsed.body, type_ignores=[]), "<exec>", "exec"), local_context)

        after_keys = set(local_context.keys())
        new_vars = list(after_keys - before_keys)
        generated_dataframes = [var for var in new_vars if isinstance(local_context[var], pd.DataFrame)]

        final_value = None
        if last_expr:
            final_value = eval(compile(ast.Expression(last_expr.value), "<eval>", "eval"), local_context)

        output_text = context.get("response") or stdout.getvalue().strip()
        table_result = detect_last_dataframe(local_context, dataframe_name, generated_dataframes)

        if table_result is None and isinstance(final_value, pd.DataFrame):
            table_result = final_value

        chart_result = detect_last_plotly_chart(context)
        if chart_result is None and hasattr(final_value, "to_plotly_json"):
            chart_result = final_value

        return output_text.strip(), table_result, chart_result, code, True

    except ModuleNotFoundError as e:
        missing_module = str(e).split("'")[1]
        message = f"To answer this question, you need to install the `{missing_module}` package."
        return message, None, None, code, False

    except Exception as e:
        return f"Execution error:\n{e}", None, None, code, False

    finally:
        sys.stdout = sys_stdout


def run_with_repair(
    code: str,
    question: str,
    context: Dict[str, object],
    schema: Dict[str, str],
    dataframe_name: str,
    api_key: str,
    model: str,
    max_retries: int = 3  
) -> Tuple[str, Any, Any, str, bool]:
    """
    Executes code generated by an LLM. Attempts automatic repair via LLM if execution fails.

    Returns:
        Tuple[str, Any, Any, str, bool]: Final response, DataFrame, chart, code, success flag.
    """
    fixer = CodeFixer(api_key, model)
    cleaned_code = sanitize_code(code)

    # First try
    text, table, chart, final_code, success = run_user_code(cleaned_code, context, dataframe_name)
    if success:
        return text, table, chart, final_code, True

    # Tries with auto repair
    current_code = cleaned_code
    current_error = text

    for _ in range(max_retries):
        repaired_code = fixer.fix_code(
            question=question,
            code=current_code,
            error=current_error,
            schema=schema,
            dataframe_name=dataframe_name,
        )

        repaired_text, repaired_table, repaired_chart, _, repaired_success = run_user_code(
            repaired_code, context, dataframe_name
        )

        if repaired_success:
            return repaired_text, repaired_table, repaired_chart, repaired_code, True

        current_code = repaired_code
        current_error = repaired_text  # new erro for LLM

    return repaired_text, repaired_table, repaired_chart, repaired_code, False
