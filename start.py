"""
E2seq - Easy to Chat with Sequencing
Easy to Chat with Sequencing - 快速启动脚本
"""

import os
import sys
import subprocess
import platform
import socket
import json
import re
import shutil
import argparse
from pathlib import Path

# 强制使用 UTF-8 输出，避免 Windows GBK 编码错误
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Hugging Face endpoint is opt-in so the launcher works outside one network.
# Hugging Face 端点仅在用户显式设置时覆盖，避免更换网络环境后失效。
if not os.environ.get("HF_ENDPOINT") and os.environ.get("E2SEQ_HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = os.environ["E2SEQ_HF_ENDPOINT"]
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_CONFIG_PATH = PROJECT_ROOT / ".e2seq" / "runtime_config.json"

# Import names used by the server are mapped to their PyPI distribution names.
# The launcher probes the real import graph first, so this list is only used
# when a selected Python environment is missing a package.
IMPORT_TO_PACKAGE = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "multipart": "python-multipart",
    "scanpy": "scanpy",
    "anndata": "anndata",
    "gseapy": "gseapy",
    "plotly": "plotly",
    "chromadb": "chromadb",
    "langchain_core": "langchain-core",
    "langchain_openai": "langchain-openai",
    "langchain_anthropic": "langchain-anthropic",
    "langchain_community": "langchain-community",
    "langgraph": "langgraph",
    "rank_bm25": "rank-bm25",
    "sentence_transformers": "sentence-transformers",
    "huggingface_hub": "huggingface-hub",
    "dotenv": "python-dotenv",
    "yaml": "pyyaml",
    "pydantic_settings": "pydantic-settings",
    "sklearn": "scikit-learn",
    "PIL": "pillow",
    "aiohttp": "aiohttp",
    "requests": "requests",
    "cryptography": "cryptography",
    "pyreadr": "pyreadr",
    "Bio": "biopython",
    "networkx": "networkx",
    "igraph": "igraph",
    "pyvis": "pyvis",
    "seaborn": "seaborn",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "statsmodels": "statsmodels",
    "numpy": "numpy",
    "pandas": "pandas",
    "typer": "typer",
    "rich": "rich",
    "redis": "redis",
    "sqlalchemy": "sqlalchemy",
}


def bilingual(english: str, chinese: str) -> str:
    """Return a concise bilingual terminal message for both user groups."""
    return f"{english} / {chinese}"


class Colors:
    """终端颜色"""
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def disable():
        """在Windows上禁用颜色"""
        if platform.system() == 'Windows':
            Colors.PURPLE = ''
            Colors.CYAN = ''
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.RED = ''
            Colors.BLUE = ''
            Colors.NC = ''


def print_banner():
    """打印启动横幅"""
    print()
    print(f"{Colors.PURPLE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.PURPLE}║                                                            ║{Colors.NC}")
    print(f"{Colors.PURPLE}║{Colors.NC}           {Colors.CYAN}E2seq - Easy to Chat with Sequencing{Colors.NC}         {Colors.PURPLE}║{Colors.NC}")
    print(f"{Colors.PURPLE}║{Colors.NC}                    {Colors.GREEN}一键启动脚本{Colors.NC}                          {Colors.PURPLE}║{Colors.NC}")
    print(f"{Colors.PURPLE}║                                                            ║{Colors.NC}")
    print(f"{Colors.PURPLE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()


def check_directory():
    """检查是否在正确的目录"""
    if not (PROJECT_ROOT / "e2seq").exists():
        print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('e2seq directory not found; run this script from the project root', '未找到 e2seq 目录，请在项目根目录运行此脚本')}")
        sys.exit(1)


def _load_runtime_config():
    """Load the launcher choices without failing on a damaged optional file."""
    try:
        if RUNTIME_CONFIG_PATH.exists():
            with RUNTIME_CONFIG_PATH.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"{Colors.YELLOW}[WARN / 警告]{Colors.NC} "
              f"{bilingual(f'Cannot read saved runtime settings: {exc}', f'无法读取已保存的运行环境设置：{exc}')}" )
    return {}


def _save_runtime_config(
    python_executable: Path,
    library_path: str,
    r_executable: Path | None = None,
) -> None:
    """Persist non-secret launcher choices for the next startup."""
    RUNTIME_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "python_executable": str(python_executable.resolve()),
        "library_path": library_path,
    }
    if r_executable:
        payload["r_executable"] = str(r_executable.resolve())
    with RUNTIME_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _python_candidate_from_path(value: str):
    """Return a valid Python executable path, accepting a Python directory."""
    if not value:
        return None
    candidate = Path(value.strip().strip('"')).expanduser()
    if candidate.is_dir():
        names = ["python.exe", "python"] if platform.system() == "Windows" else ["python", "python3"]
        search_dirs = [candidate, candidate / "bin", candidate / "bin" / "x64"]
        for folder in search_dirs:
            for name in names:
                possible = folder / name
                if possible.is_file():
                    return possible
        return None
    return candidate if candidate.is_file() else None


def _default_python_executable(saved):
    """Choose a useful default while still allowing any user-selected Python."""
    candidates = [
        saved,
        str(Path("venv") / "Scripts" / "python.exe") if platform.system() == "Windows" else str(Path("venv") / "bin" / "python"),
        sys.executable,
        shutil.which("python"),
        shutil.which("python3"),
    ]
    for value in candidates:
        found = _python_candidate_from_path(value or "")
        if found:
            return found
    return None


def _r_candidate_from_path(value: str):
    """Return a valid R executable, accepting either a file or an R folder."""
    if not value:
        return None
    candidate = Path(value.strip().strip('"')).expanduser()
    if candidate.is_dir():
        names = (
            ["Rterm.exe", "R.exe", "Rscript.exe"]
            if platform.system() == "Windows"
            else ["R", "Rscript"]
        )
        for name in names:
            possible = candidate / name
            if possible.is_file():
                return possible
        return None
    return candidate if candidate.is_file() else None


def _default_r_executable(saved):
    """Choose R from saved settings, environment variables, or PATH."""
    candidates = [
        saved,
        os.environ.get("E2SEQ_R_EXE"),
        os.environ.get("E2SEQ_R_PATH"),
        os.environ.get("R_HOME"),
        shutil.which("Rterm.exe"),
        shutil.which("R.exe"),
        shutil.which("Rscript.exe"),
        shutil.which("R"),
        shutil.which("Rscript"),
    ]
    for value in candidates:
        found = _r_candidate_from_path(value or "")
        if found:
            return found
    return None


def _infer_library_path(python_executable: Path) -> str:
    """Ask the selected interpreter where its site-packages directories are."""
    probe = (
        "import os, site; "
        "paths = list(dict.fromkeys((site.getsitepackages() if hasattr(site, 'getsitepackages') else []) "
        "+ [site.getusersitepackages()])); "
        "preferred = [p for p in paths if p and ('site-packages' in p or 'dist-packages' in p) and os.path.isdir(p)]; "
        "print(os.pathsep.join(preferred or [p for p in paths if p and os.path.isdir(p)]))"
    )
    try:
        result = subprocess.run(
            [str(python_executable), "-c", probe],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip().splitlines()[-1].strip()
    except Exception:
        return ""


def _runtime_environment(
    python_executable: Path,
    library_path: str,
    r_executable: Path | None = None,
):
    """Build the child environment, adding user-selected library directories."""
    env = os.environ.copy()
    project_path = str(PROJECT_ROOT)
    paths = [p.strip().strip('"') for p in library_path.split(os.pathsep) if p.strip()]
    python_path = [project_path] + paths
    existing = env.get("PYTHONPATH", "")
    if existing:
        python_path.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(python_path)
    env["E2SEQ_RUNTIME_PYTHON"] = str(python_executable.resolve())
    env["E2SEQ_LIBRARY_PATH"] = library_path
    if r_executable:
        env["E2SEQ_R_EXE"] = str(r_executable.resolve())
    return env


def configure_runtime(
    python_override: str | None = None,
    library_override: str | None = None,
    r_override: str | None = None,
    non_interactive: bool = False,
):
    """Let the user select Python and library paths before the server starts."""
    saved = _load_runtime_config()
    default_python = _default_python_executable(
        python_override or os.environ.get("E2SEQ_PYTHON") or saved.get("python_executable")
    )
    if default_python is None:
        print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
              f"{bilingual('No Python executable was found. Install Python or enter its path.', '未找到 Python 解释器，请先安装 Python 或输入解释器路径。')}" )
        sys.exit(1)

    if non_interactive or python_override or os.environ.get("E2SEQ_PYTHON"):
        selected = default_python
    else:
        while True:
            entered = input(
                f"{Colors.CYAN}[CONFIG / 配置]{Colors.NC} "
                f"{bilingual(f'Python executable (Enter for {default_python})', f'Python 解释器路径（回车使用 {default_python}）')}: "
            ).strip()
            selected = _python_candidate_from_path(entered) if entered else default_python
            if selected:
                break
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual('Python executable not found; enter a valid file or directory.', '未找到 Python 解释器，请输入有效的文件或目录。')}" )

    saved_library = str(saved.get("library_path") or "").strip()
    saved_library_items = [
        Path(item.strip().strip('"')).expanduser()
        for item in saved_library.split(os.pathsep)
        if item.strip()
    ]
    # A copied project may contain a runtime_config.json from another machine.
    # Ignore stale absolute library paths and infer them from the selected Python.
    default_library = (
        saved_library
        if saved_library_items and all(path.exists() for path in saved_library_items)
        else _infer_library_path(selected)
    )
    if library_override is not None or os.environ.get("E2SEQ_LIBRARY_PATH"):
        library_path = library_override or os.environ.get("E2SEQ_LIBRARY_PATH") or ""
    elif non_interactive:
        library_path = default_library or ""
    else:
        while True:
            library_path = input(
                f"{Colors.CYAN}[CONFIG / 配置]{Colors.NC} "
                f"{bilingual(f'Python library path(s), separated by {os.pathsep} (Enter for {default_library or "default"})', f'Python 库路径（多个路径用 {os.pathsep} 分隔；回车使用 {default_library or "默认路径"}）')}: "
            ).strip()
            library_path = library_path or default_library or ""
            library_items = [Path(item.strip().strip('"')).expanduser() for item in library_path.split(os.pathsep) if item.strip()]
            missing = [path for path in library_items if not path.exists()]
            if not missing:
                break
            missing_text = ", ".join(str(path) for path in missing)
            create = input(
                f"{Colors.YELLOW}[WARN / 警告]{Colors.NC} "
                f"{bilingual(f'Library path(s) do not exist: {missing_text}. Create them? [Y/n]', f'以下库路径不存在：{missing_text}。是否创建？[Y/n]')}: "
            ).strip().lower()
            if create in {"", "y", "yes"}:
                for path in missing:
                    path.mkdir(parents=True, exist_ok=True)
                break

    default_r = _default_r_executable(saved.get("r_executable"))
    configured_r = r_override or os.environ.get("E2SEQ_R_EXE") or os.environ.get("E2SEQ_R_PATH")
    if configured_r:
        r_executable = _r_candidate_from_path(configured_r)
    elif non_interactive:
        r_executable = default_r
    else:
        while True:
            entered_r = input(
                f"{Colors.CYAN}[CONFIG / 配置]{Colors.NC} "
                f"{bilingual(f'R executable (Enter to skip; default {default_r or "not found"})', f'R 解释器路径（回车跳过；默认 {default_r or "未找到"}）')}: "
            ).strip()
            r_executable = _r_candidate_from_path(entered_r) if entered_r else default_r
            if not entered_r or r_executable:
                break
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual('R executable not found; enter a valid file or directory, or press Enter to skip.', '未找到 R 解释器，请输入有效路径，或直接回车跳过。')}" )

    _save_runtime_config(selected, library_path, r_executable)
    env = _runtime_environment(selected, library_path, r_executable)
    r_display_en = str(r_executable) if r_executable else "not configured (Python fallback remains available)"
    r_display_zh = str(r_executable) if r_executable else "未配置（仍可使用 Python 兼容后端）"
    print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} "
          f"{bilingual(f'Using R: {r_display_en}', f'使用 R：{r_display_zh}')}")
    print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} "
          f"{bilingual(f'Using Python: {selected}', f'使用 Python：{selected}')}" )
    print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} "
          f"{bilingual(f'Using library path(s): {library_path or "default"}', f'使用库路径：{library_path or "默认路径"}')}" )
    print()
    return selected, env


def check_venv():
    """Return the project venv when present, otherwise the running Python."""
    saved = _load_runtime_config().get("python_executable")
    selected = _default_python_executable(saved)
    if selected is None:
        print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
              f"{bilingual('No Python executable found.', '未找到 Python 解释器。')}" )
        sys.exit(1)
    return selected


def _probe_server_import(python_exe, env):
    """Import the actual server and return its process result."""
    return subprocess.run(
        [str(python_exe), "-c", "import e2seq.api.server"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def _missing_import_name(output):
    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", output or "")
    if not match:
        return ""
    return match.group(1).split(".")[0]


def check_dependencies(python_exe, env=None, allow_install=True):
    """Check the real server import graph and install only missing packages."""
    print(f"{Colors.CYAN}[2/4]{Colors.NC} {bilingual('Checking only the packages required by the server...', '仅检查服务端实际需要的依赖包...')}")
    env = env or _runtime_environment(Path(python_exe), "")
    install_approved = False
    attempted = set()

    while True:
        try:
            result = _probe_server_import(python_exe, env)
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual(f'Python import check failed: {exc}', f'Python 导入检查失败：{exc}')}" )
            sys.exit(1)

        if result.returncode == 0:
            print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} "
                  f"{bilingual('Required server imports are available', '服务端实际依赖检查完成')}" )
            print()
            return True

        output = (result.stderr or "") + "\n" + (result.stdout or "")
        module_name = _missing_import_name(output)
        package_name = IMPORT_TO_PACKAGE.get(module_name)
        if not package_name:
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual('The selected environment failed during server import:', '所选环境在导入服务端时失败：')}\n{output[-1800:]}")
            sys.exit(1)
        if not allow_install:
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual(f'Missing package: {package_name}. Install dependencies, then run again.', f'缺少依赖：{package_name}。请安装依赖后重新运行。')}")
            sys.exit(1)
        if package_name in attempted:
            print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} "
                  f"{bilingual(f'Package {package_name} is still unavailable after installation.', f'安装后仍无法找到 {package_name}。')}" )
            sys.exit(1)

        if not install_approved:
            answer = input(
                f"{Colors.YELLOW}[INSTALL / 安装]{Colors.NC} "
                f"{bilingual(f'Missing package detected: {package_name}. Install only missing packages now? [Y/n]', f'检测到缺少依赖：{package_name}。现在只安装缺少的依赖吗？[Y/n]')}: "
            ).strip().lower()
            if answer not in {"", "y", "yes"}:
                print(f"{Colors.YELLOW}[INFO / 提示]{Colors.NC} "
                      f"{bilingual('Startup cancelled until dependencies are installed.', '依赖未安装，启动已取消。')}" )
                sys.exit(1)
            install_approved = True

        attempted.add(package_name)
        print(f"{Colors.CYAN}[INSTALL / 安装]{Colors.NC} "
              f"{bilingual(f'Installing missing package: {package_name}', f'正在安装缺少的依赖：{package_name}')}" )
        pip_check = subprocess.run(
            [str(python_exe), "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            env=env,
        )
        if pip_check.returncode != 0:
            print(f"{Colors.YELLOW}[INFO / 提示]{Colors.NC} "
                  f"{bilingual('pip is missing; bootstrapping it with ensurepip.', '未找到 pip，先使用 ensurepip 初始化。')}" )
            subprocess.run([str(python_exe), "-m", "ensurepip", "--upgrade"], check=True, env=env)
        install_command = [str(python_exe), "-m", "pip", "install", package_name]
        install_targets = [
            Path(item.strip().strip('"')).expanduser()
            for item in env.get("E2SEQ_LIBRARY_PATH", "").split(os.pathsep)
            if item.strip()
        ]
        if install_targets:
            install_command.extend(["--target", str(install_targets[0])])
        subprocess.run(
            install_command,
            check=True,
            env=env,
        )

    print()


def check_config():
    """检查配置"""
    print(f"{Colors.CYAN}[3/4]{Colors.NC} {bilingual('Checking configuration...', '检查配置...')}")

    config_dir = PROJECT_ROOT / ".e2seq"
    if not config_dir.exists():
        print(f"{Colors.YELLOW}[INFO / 提示]{Colors.NC} {bilingual('First run: creating the configuration directory', '首次运行，将创建配置目录')}")
        config_dir.mkdir(exist_ok=True)

    print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} {bilingual('Configuration check complete', '配置检查完成')}")
    print()


def is_port_available(port: int) -> bool:
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 如果 connect_ex 返回 0，说明连接成功 → 端口已被占用
        return s.connect_ex(('127.0.0.1', port)) != 0


def find_available_port(start: int = 8000, end: int = 9010) -> int | None:
    """查找范围内第一个可用端口"""
    for port in range(start, end + 1):
        if is_port_available(port):
            return port
    return None


def ask_port(port_override: int | None = None, non_interactive: bool = False) -> int:
    """询问用户想要的端口，并确保端口可用"""
    default_port = port_override or int(os.environ.get("E2SEQ_PORT", "8521"))

    if non_interactive or port_override is not None or os.environ.get("E2SEQ_PORT"):
        if is_port_available(default_port):
            return default_port
        next_free = find_available_port(default_port + 1)
        if next_free:
            print(f"{Colors.YELLOW}[BUSY / 占用]{Colors.NC} "
                  f"{bilingual(f'Port {default_port} is busy; using {next_free}', f'端口 {default_port} 已占用，改用 {next_free}')}")
            return next_free
        raise RuntimeError(bilingual("No free service port was found.", "没有找到可用服务端口。"))

    while True:
        user_input = input(
            f"{Colors.CYAN}[CONFIG / 配置]{Colors.NC} "
            f"{bilingual(f'Enter the service port (press Enter for {default_port})', f'请输入服务端口号（直接回车使用默认 {default_port}）')}: "
        ).strip()

        if user_input == "":
            chosen_port = default_port
        else:
            try:
                chosen_port = int(user_input)
                if not (1 <= chosen_port <= 65535):
                    print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('Port must be between 1 and 65535', '端口号必须在 1~65535 之间')}")
                    continue
            except ValueError:
                print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('Enter a valid number', '请输入有效数字')}")
                continue

        # 检查端口是否被占用
        if not is_port_available(chosen_port):
            print(f"{Colors.YELLOW}[BUSY / 占用]{Colors.NC} {bilingual(f'Port {chosen_port} is already in use', f'端口 {chosen_port} 已被其他进程占用')}")

            # 自动找下一个可用端口供用户参考
            next_free = find_available_port(chosen_port + 1)
            suggestion = str(next_free) if next_free else bilingual("no free port found automatically", "无法自动找到可用端口")

            retry = input(
                f"  {bilingual(f'Enter Y to use the next free port ({suggestion}), a number to choose another port, or Q to quit', f'输入 Y 使用下一个可用端口（{suggestion}），输入数字指定其他端口，或 Q 退出')}: "
            ).strip().lower()

            if retry == "y" or retry == "Y":
                if next_free:
                    print(f"{Colors.CYAN}[INFO / 信息]{Colors.NC} {bilingual(f'Switching to port {next_free}', f'切换到端口 {next_free}')}")
                    return next_free
                else:
                    print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('No free port was found automatically; choose another port', '无法自动找到可用端口，请手动指定其他端口')}")
                    continue
            elif retry == "q" or retry == "Q":
                print(f"{Colors.CYAN}[EXIT / 退出]{Colors.NC} {bilingual('Startup cancelled', '已取消启动')}")
                sys.exit(0)
            else:
                # 当作数字重新输入
                try:
                    chosen_port = int(retry)
                    if not (1 <= chosen_port <= 65535):
                        print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('Invalid port number', '端口号无效')}")
                        continue
                    # 再次检查新端口
                    if not is_port_available(chosen_port):
                        print(f"{Colors.RED}[BUSY / 占用]{Colors.NC} {bilingual(f'Port {chosen_port} is also in use', f'端口 {chosen_port} 也被占用')}")
                        continue
                    return chosen_port
                except ValueError:
                    print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual('Invalid input', '无效输入')}")
                    continue
        else:
            return chosen_port


def print_server_info(port: int, host: str = "127.0.0.1"):
    """打印服务器信息"""
    print()
    print(f"{Colors.BLUE}┌────────────────────────────────────────────────────────────┐{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  {bilingual('Server information', '服务器信息')}:                                      {Colors.BLUE}│{Colors.NC}")
    base_url = f"http://{host}:{port}"
    print(f"{Colors.BLUE}│{Colors.NC}  - {bilingual('Web app', '网页界面')}: {Colors.GREEN}{base_url}{Colors.NC}                     {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - {bilingual('API docs', 'API 文档')}: {Colors.GREEN}{base_url}/docs{Colors.NC}                 {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - {bilingual('Health check', '健康检查')}: {Colors.GREEN}{base_url}/api/health{Colors.NC}          {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}└────────────────────────────────────────────────────────────┘{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}[INFO / 提示]{Colors.NC} {bilingual('Press Ctrl+C to stop the server', '按 Ctrl+C 停止服务器')}")
    print()
    print(f"{Colors.PURPLE}════════════════════════════════════════════════════════════{Colors.NC}")
    print()


def start_server(python_exe, port: int, env=None, host: str = "127.0.0.1"):
    """启动服务器"""
    try:
        subprocess.run(
                    [
                        str(python_exe), "-m", "uvicorn",
                        "e2seq.api.server:app",
                        "--host", host,
                        "--port", str(port),
                    ],
            check=True,
            env=env,
        )
    except KeyboardInterrupt:
        print()
        print(f"{Colors.PURPLE}════════════════════════════════════════════════════════════{Colors.NC}")
        print()
        print(f"{Colors.CYAN}[INFO / 信息]{Colors.NC} {bilingual('Server stopped', '服务器已停止')}")
        print()
    except subprocess.CalledProcessError as e:
        print()
        print(f"{Colors.RED}[ERROR / 错误]{Colors.NC} {bilingual(f'Server failed to start: {e}', f'服务器启动失败：{e}')}")
        sys.exit(1)


def parse_args(argv=None):
    """Parse portable launcher options; all values also support E2SEQ_* env vars."""
    parser = argparse.ArgumentParser(
        description="E2seq portable launcher / E2seq 可迁移启动器"
    )
    parser.add_argument("--python", dest="python_path", help="Python executable or folder / Python 解释器或目录")
    parser.add_argument("--library-path", dest="library_path", help="Python library path(s) / Python 库路径")
    parser.add_argument("--r", dest="r_path", help="Rterm/R executable or folder / R 解释器或目录")
    parser.add_argument("--host", default=os.environ.get("E2SEQ_HOST", "127.0.0.1"), help="Bind host / 监听地址")
    parser.add_argument("--port", type=int, help="Service port / 服务端口")
    parser.add_argument("--no-install", action="store_true", help="Do not install missing packages / 不自动安装缺少的依赖")
    parser.add_argument("--non-interactive", action="store_true", help="Use defaults without prompts / 使用默认配置，不询问路径")
    parser.add_argument("--check-only", action="store_true", help="Check environment and exit / 仅检查环境后退出")
    return parser.parse_args(argv)


def main(argv=None):
    """主函数"""
    # 在Windows上禁用颜色（可选）
    if platform.system() == 'Windows':
        # 尝试启用Windows终端颜色支持
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            Colors.disable()

    args = parse_args(argv)
    os.chdir(PROJECT_ROOT)

    # 打印横幅
    print_banner()

    # 检查目录
    check_directory()

    # 选择 Python 和库目录
    print(f"{Colors.CYAN}[1/4]{Colors.NC} {bilingual('Configure the Python runtime...', '配置 Python 运行环境...')}")
    python_exe, runtime_env = configure_runtime(
        python_override=args.python_path,
        library_override=args.library_path,
        r_override=args.r_path,
        non_interactive=args.non_interactive,
    )

    # 检查依赖
    check_dependencies(python_exe, runtime_env, allow_install=not args.no_install)

    # 检查配置
    check_config()

    if args.check_only:
        print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} "
              f"{bilingual('Environment check finished; server was not started.', '环境检查完成；未启动服务器。')}")
        return

    # 询问端口
    print(f"{Colors.CYAN}[4/4]{Colors.NC} {bilingual('Configure the service port...', '配置服务端口...')}")
    chosen_port = ask_port(args.port, args.non_interactive)
    print(f"{Colors.GREEN}[OK / 完成]{Colors.NC} {bilingual(f'Using port {chosen_port}', f'使用端口 {chosen_port}')}")
    print()

    # 打印服务器信息
    print_server_info(chosen_port, args.host)

    # 启动服务器
    start_server(python_exe, chosen_port, runtime_env, args.host)


if __name__ == "__main__":
    main()
