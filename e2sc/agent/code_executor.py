"""Secure code execution sandbox for E2sc AI agent.

Provides a restricted Python execution environment where the AI can
run data analysis code with access to:
- Uploaded h5ad (AnnData) datasets
- Local SQLite databases (STRING, HMDB, TRRUST, GUTMGENE)
- Custom uploaded databases
- Scientific libraries (numpy, pandas, scanpy, matplotlib, plotly)
"""

import io
import sqlite3
import sys
import textwrap
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional

from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)

# Allowed top-level imports inside AI-generated code
_ALLOWED_IMPORTS = {
    "numpy", "np", "pandas", "pd", "scanpy", "sc",
    "matplotlib", "plt", "seaborn", "sns",
    "plotly", "scipy", "sklearn", "statsmodels",
    "math", "statistics", "itertools", "collections",
    "json", "re", "datetime", "typing",
    "anndata", "networkx",
}

# Blocked builtins that could be dangerous
_BLOCKED_BUILTINS = {
    "__import__", "eval", "exec", "compile",
    "open",  # override with safe version
    "input",
}


class ExecutionResult:
    """Result of a code execution."""

    def __init__(
        self,
        success: bool,
        stdout: str = "",
        result: Any = None,
        error: str = "",
        plots: Optional[List[Any]] = None,
        dataframes: Optional[List[Dict]] = None,
    ):
        self.success = success
        self.stdout = stdout
        self.result = result
        self.error = error
        self.plots = plots or []
        self.dataframes = dataframes or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "plot_count": len(self.plots),
            "dataframe_count": len(self.dataframes),
        }

    def as_context_text(self) -> str:
        """Format result as LLM context text."""
        parts = []
        if self.stdout.strip():
            parts.append(f"[Code Output]\n{self.stdout.strip()}")
        if self.result is not None and str(self.result).strip():
            parts.append(f"[Return Value]\n{str(self.result)[:2000]}")
        if self.dataframes:
            for i, df_info in enumerate(self.dataframes):
                parts.append(
                    f"[DataFrame {i+1}]\nShape: {df_info.get('shape')}\n"
                    f"Columns: {df_info.get('columns')}\n"
                    f"Preview:\n{df_info.get('head', '')}"
                )
        if self.error:
            parts.append(f"[Error]\n{self.error}")
        return "\n\n".join(parts) if parts else "(no output)"


class CodeExecutor:
    """Secure Python code executor with pre-injected scientific context."""

    def __init__(
        self,
        adata=None,
        custom_dbs: Optional[Dict[str, Path]] = None,
    ):
        """
        Args:
            adata: AnnData object (user-uploaded h5ad), may be None
            custom_dbs: dict of {name: path} for user-uploaded SQLite/CSV databases
        """
        self.adata = adata
        self.custom_dbs = custom_dbs or {}
        self._db_dir = Path(get_config().database.db_path).expanduser()

    def _build_namespace(self) -> Dict[str, Any]:
        """Build the execution namespace with pre-injected variables."""
        import numpy as np
        import pandas as pd

        ns: Dict[str, Any] = {
            # Scientific stack
            "np": np,
            "numpy": np,
            "pd": pd,
            "pandas": pd,
        }

        # Optional heavy imports — only if available
        try:
            import scanpy as sc
            ns["sc"] = sc
            ns["scanpy"] = sc
        except ImportError:
            pass

        try:
            import matplotlib
            matplotlib.use("Agg")  # non-interactive
            import matplotlib.pyplot as plt
            ns["plt"] = plt
            ns["matplotlib"] = matplotlib
        except ImportError:
            pass

        try:
            import plotly.express as px
            import plotly.graph_objects as go
            ns["px"] = px
            ns["go"] = go
        except ImportError:
            pass

        try:
            import seaborn as sns
            ns["sns"] = sns
        except ImportError:
            pass

        # Inject AnnData if available
        if self.adata is not None:
            ns["adata"] = self.adata

        # Inject local DB helpers
        ns["query_db"] = self._query_db
        ns["list_dbs"] = self._list_dbs

        # Custom databases
        for name, path in self.custom_dbs.items():
            ns[f"db_{name}"] = str(path)

        # Safe print that captures output
        ns["__builtins__"] = {
            k: v for k, v in __builtins__.items()
            if k not in _BLOCKED_BUILTINS
        } if isinstance(__builtins__, dict) else {
            k: getattr(__builtins__, k)
            for k in dir(__builtins__)
            if k not in _BLOCKED_BUILTINS and not k.startswith("_")
        }

        return ns

        def _query_db(
        self, db_name: str, sql: str, params: tuple = ()
    ) -> "pd.DataFrame":
        """Execute SQL against a local database and return a DataFrame.

        Args:
            db_name: One of 'string', 'hmdb', 'trrust', 'gutmgene',
                     or a custom DB name.
            sql: SQL query string.
            params: Optional query parameters.

        Returns:
            pandas DataFrame with results.
        """
        import pandas as pd

        # SQL injection prevention: whitelist allowed SQL patterns
        allowed_patterns = ("SELECT", "PRAGMA", "WITH")
        sql_stripped = sql.strip().upper()
        if not any(sql_stripped.startswith(p) for p in allowed_patterns):
            raise ValueError(
                "Only SELECT/PRAGMA/WITH queries are allowed for security reasons. "
                f"Received: {sql[:50]}..."
            )

        # Check custom databases first
        if db_name in self.custom_dbs:
            db_path = self.custom_dbs[db_name]
        else:
            db_path = self._db_dir / f"{db_name}.db"

        if not Path(db_path).exists():
            raise FileNotFoundError(
                f"Database '{db_name}' not found at {db_path}. "
                f"Available: {self._list_dbs()}"
            )

        conn = sqlite3.connect(str(db_path))
        try:
            df = pd.read_sql_query(sql, conn, params=params)
            return df
        finally:
            conn.close()

    def _list_dbs(self) -> List[str]:
        """List available databases."""
        builtin = [p.stem for p in self._db_dir.glob("*.db")]
        custom = list(self.custom_dbs.keys())
        return builtin + custom

    def execute(
        self,
        code: str,
        timeout: int = 30,
    ) -> ExecutionResult:
        """Execute Python code in the secure sandbox.

        Args:
            code: Python code string to execute.
            timeout: Maximum execution time in seconds.

        Returns:
            ExecutionResult with stdout, return value, plots, errors.
        """
        import signal

        code = textwrap.dedent(code)
        ns = self._build_namespace()
        captured_stdout = io.StringIO()
        plots = []
        dataframes = []

        def _timeout_handler(signum, frame):
            raise TimeoutError(f"Code execution timed out after {timeout}s")

        # Wrap last expression to capture return value
        try:
            tree_lines = code.strip().split("\n")
            exec_code = code
            result_var = None

            with redirect_stdout(captured_stdout):
                # Set timeout on Unix; skip on Windows
                use_signal = hasattr(signal, "SIGALRM")
                if use_signal:
                    signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.alarm(timeout)
                try:
                    exec(compile(exec_code, "<ai_code>", "exec"), ns)  # noqa: S102
                    result_var = ns.get("result", ns.get("_result", None))
                finally:
                    if use_signal:
                        signal.alarm(0)

            # Collect matplotlib figures
            try:
                import matplotlib.pyplot as plt
                figs = [plt.figure(i) for i in plt.get_fignums()]
                plots.extend(figs)
                plt.close("all")
            except Exception:
                pass

            # Collect DataFrames from namespace
            try:
                import pandas as pd
                for k, v in ns.items():
                    if isinstance(v, pd.DataFrame) and not k.startswith("_"):
                        dataframes.append({
                            "name": k,
                            "shape": list(v.shape),
                            "columns": list(v.columns),
                            "head": v.head(10).to_string(),
                        })
            except Exception:
                pass

            stdout_val = captured_stdout.getvalue()
            logger.info(
                f"Code executed successfully. "
                f"stdout={len(stdout_val)} chars, plots={len(plots)}, dfs={len(dataframes)}"
            )
            return ExecutionResult(
                success=True,
                stdout=stdout_val,
                result=result_var,
                plots=plots,
                dataframes=dataframes,
            )

        except Exception as exc:
            error_msg = traceback.format_exc()
            logger.warning(f"Code execution error: {exc}")
            return ExecutionResult(
                success=False,
                stdout=captured_stdout.getvalue(),
                error=error_msg,
            )


# Module-level singleton per session
_executors: Dict[str, CodeExecutor] = {}


def get_executor(session_id: str, adata=None, custom_dbs=None) -> CodeExecutor:
    """Get or create a CodeExecutor for a session."""
    if session_id not in _executors or adata is not None:
        _executors[session_id] = CodeExecutor(adata=adata, custom_dbs=custom_dbs or {})
    return _executors[session_id]
