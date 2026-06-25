"""
E2seq - Easy to Chat with Sequencing
Easy to Chat with Sequencing - 快速启动脚本
"""

import os
import sys
import subprocess
import socket
from pathlib import Path

# Avoid `import platform` — on some Windows/PowerShell combos it spawns a
# subprocess (`cmd /c ver`) that hangs. Use OS env var instead (zero-cost).
IS_WINDOWS = os.environ.get("OS", "").startswith("Windows") or sys.platform == "win32"
IS_POSIX = not IS_WINDOWS


def _is_windows() -> bool:
    return IS_WINDOWS


# 强制使用 UTF-8 输出，避免 Windows GBK 编码错误
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# HuggingFace 镜像配置（加速模型下载）
if not os.environ.get("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# 虚拟环境配置
VENV_DIR = Path("venv")
VENV_NAME = "e2seq"  # 虚拟环境名称


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
        if _is_windows():
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
    print(f"{Colors.PURPLE}║{Colors.NC}           {Colors.CYAN}E2seq - Easy to Chat with Sequencing{Colors.NC}             {Colors.PURPLE}║{Colors.NC}")
    print(f"{Colors.PURPLE}║{Colors.NC}                    {Colors.GREEN}一键启动脚本{Colors.NC}                            {Colors.PURPLE}║{Colors.NC}")
    print(f"{Colors.PURPLE}║                                                            ║{Colors.NC}")
    print(f"{Colors.PURPLE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()


def check_directory():
    """检查是否在正确的目录"""
    if not Path("e2sc").exists():
        print(f"{Colors.RED}[错误]{Colors.NC} 未找到 e2sc 目录，请确保在项目根目录运行此脚本")
        sys.exit(1)


def get_venv_info():
    """获取虚拟环境信息，返回 (python_exe, activate_cmd, is_venv_active)"""
    if _is_windows():
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        activate_cmd = str(VENV_DIR / "Scripts" / "activate.bat")
    else:
        python_exe = VENV_DIR / "bin" / "python"
        activate_cmd = f"source {VENV_DIR / 'bin' / 'activate'}"

    # 检查是否已经在虚拟环境中
    is_active = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )

    # 检查venv目录是否存在
    venv_exists = python_exe.exists()

    return python_exe, activate_cmd, is_active, venv_exists


def check_venv():
    """检查并准备虚拟环境，返回python解释器路径"""
    print(f"{Colors.CYAN}[1/5]{Colors.NC} 检查虚拟环境...")

    python_exe, activate_cmd, is_active, venv_exists = get_venv_info()

    # 如果已经在正确的虚拟环境中
    if is_active:
        current_venv = os.environ.get('VIRTUAL_ENV', '')
        if VENV_DIR.resolve().samefile(current_venv) or current_venv.endswith(VENV_NAME):
            print(f"{Colors.GREEN}[✓]{Colors.NC} 当前已在虚拟环境中: {current_venv}")
            return sys.executable

    # 如果虚拟环境不存在，尝试创建
    if not venv_exists:
        print(f"{Colors.YELLOW}[提示]{Colors.NC} 未找到虚拟环境，正在创建...")
        try:
            create_venv(python_exe.parent if python_exe.exists() else Path.cwd())
            print(f"{Colors.GREEN}[✓]{Colors.NC} 虚拟环境创建成功")
        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 创建虚拟环境失败: {e}")
            print(f"{Colors.YELLOW}[提示]{Colors.NC} 请手动创建: python -m venv {VENV_DIR}")
            sys.exit(1)

    # 验证虚拟环境的Python
    try:
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"{Colors.GREEN}[✓]{Colors.NC} 找到虚拟环境: {VENV_NAME}")
        print(f"{Colors.GREEN}[✓]{Colors.NC} Python版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"{Colors.RED}[错误]{Colors.NC} 无法执行虚拟环境Python: {e}")
        sys.exit(1)

    return str(python_exe)


def create_venv(base_path: Path):
    """创建虚拟环境"""
    if _is_windows():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def activate_venv_and_run(python_exe: str, func, *args, **kwargs):
    """激活虚拟环境后执行函数"""
    # 设置环境变量
    venv_path = Path(python_exe).parent.parent
    os.environ['VIRTUAL_ENV'] = str(venv_path.resolve())

    # 添加虚拟环境的Scripts/Lib到PATH
    if _is_windows():
        os.environ['PATH'] = f"{venv_path / 'Scripts'};{os.environ.get('PATH', '')}"
    else:
        os.environ['PATH'] = f"{venv_path / 'bin'}:{os.environ.get('PATH', '')}"

    return func(*args, **kwargs)


def _check_one_package(python_exe: str, import_name: str, timeout: int = 15) -> tuple[bool, str]:
    """Check if a package is installed WITHOUT actually importing it.

    Uses importlib.util.find_spec in a subprocess so we don't pay the cost of
    torch/transformers initialization (which can take 10-20s on first import).
    find_spec only inspects sys.path metadata, so it returns instantly.
    """
    code = (
        "import importlib.util as u, sys; "
        "spec = u.find_spec(sys.argv[1]); "
        "sys.exit(0 if spec is not None else 1)"
    )
    try:
        result = subprocess.run(
            [python_exe, "-c", code, import_name],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return (True, "")
        return (False, (result.stderr or "not found").strip()[:200])
    except subprocess.TimeoutExpired:
        return (False, "timeout")
    except Exception as e:
        return (False, str(e)[:200])


def _pip_check(python_exe: str, timeout: int = 60) -> tuple[bool, str]:
    """Run `pip check` to verify all installed deps have consistent versions.

    Returns (ok, detail). pip check exits 0 when everything is consistent.
    This is advisory only — a slow/failed pip check will NOT block startup,
    since on a large venv (torch, transformers, etc.) it can be slow.
    """
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (result.returncode == 0, (result.stdout or result.stderr or "").strip()[:500])
    except subprocess.TimeoutExpired:
        # Treat as advisory: don't fail startup on slow pip check
        return (True, "pip check timed out (skipped)")
    except Exception as e:
        return (True, f"pip check unavailable: {e}")


def check_dependencies(python_exe):
    """检查依赖包 — 仅在确实缺失时安装"""
    print(f"{Colors.CYAN}[2/5]{Colors.NC} 检查依赖包...")

    required_packages = [
        "fastapi", "uvicorn", "python-multipart",
        "scanpy", "anndata", "pandas", "numpy",
        "plotly", "networkx", "gseapy",
        "sentence-transformers", "chromadb",
        "rich", "typer", "pydantic"
    ]

    # sentence-transformers depends on torch/transformers; we check the
    # top-level spec without actually importing torch (which is slow).
    # If sentence-transformers is installed, its deps must be too.
    package_to_import = {
        "python-multipart": "multipart",
    }

    print(f"  -> 检查 {len(required_packages)} 个依赖是否已安装...")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results: dict[str, tuple[bool, str]] = {}
    with ThreadPoolExecutor(max_workers=min(8, len(required_packages))) as pool:
        futures = {}
        for pkg in required_packages:
            import_name = package_to_import.get(pkg, pkg.replace("-", "_"))
            futures[pool.submit(_check_one_package, python_exe, import_name, 15)] = pkg
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            pkg = futures[fut]
            ok, err = fut.result()
            results[pkg] = (ok, err)
            done += 1
            mark = f"{Colors.GREEN}OK  {Colors.NC}" if ok else f"{Colors.RED}MISS{Colors.NC}"
            sys.stdout.write(f"\r  -> [{done}/{total}] {mark} {pkg}    ")
            sys.stdout.flush()
        print()

    missing = [p for p, (ok, _) in results.items() if not ok]
    installed = [p for p, (ok, _) in results.items() if ok]

    # Also verify dependency graph is internally consistent
    print(f"  -> 验证依赖图完整性 (pip check)...")
    consistent, detail = _pip_check(python_exe, timeout=30)
    if consistent:
        print(f"  {Colors.GREEN}[OK]{Colors.NC} 依赖图完整")
    else:
        print(f"  {Colors.YELLOW}[WARN]{Colors.NC} pip check 报告: {detail}")

    if not missing and consistent:
        print(f"  {Colors.GREEN}[OK]{Colors.NC} 所有依赖包已安装且完整 ({len(installed)} 个)")
        print()
        return

    # Missing OR inconsistent — install only what's missing
    to_install = missing[:]
    if missing:
        print(f"  {Colors.YELLOW}[WARN]{Colors.NC} 缺少依赖包: {', '.join(missing)}")
    if missing:
        try:
            print(f"  -> 正在安装缺失的依赖 (这可能需要 1-5 分钟)...")
            subprocess.run(
                [python_exe, "-m", "pip", "install", "--quiet"] + missing,
                check=True,
                timeout=600,
            )
            print(f"  {Colors.GREEN}[OK]{Colors.NC} 依赖安装完成")
        except subprocess.TimeoutExpired:
            print(f"  {Colors.RED}[ERR]{Colors.NC} 安装超时 (>10 分钟)")
            print(f"  {Colors.YELLOW}[HINT]{Colors.NC} 请手动安装: {python_exe} -m pip install {' '.join(missing)}")
            sys.exit(1)
        except Exception as e:
            print(f"  {Colors.RED}[ERR]{Colors.NC} 安装失败: {e}")
            print(f"  {Colors.YELLOW}[HINT]{Colors.NC} 请手动安装: {python_exe} -m pip install {' '.join(missing)}")
            sys.exit(1)
    elif not consistent:
        # Everything installed but inconsistent — show a warning, do not reinstall.
        print(f"  {Colors.YELLOW}[WARN]{Colors.NC} 依赖完整但 pip check 报告不一致。请运行:")
        print(f"           {python_exe} -m pip install --upgrade {' '.join(required_packages)}")

    print()


def check_config():
    """检查配置"""
    print(f"{Colors.CYAN}[3/5]{Colors.NC} 检查配置...")

    config_dir = Path(".e2sc")
    if not config_dir.exists():
        print(f"{Colors.YELLOW}[提示]{Colors.NC} 首次运行，将创建配置目录")
        config_dir.mkdir(exist_ok=True)

    # 检查配置文件
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        print(f"{Colors.YELLOW}[提示]{Colors.NC} 未找到配置文件，将使用默认配置")

    print(f"{Colors.GREEN}[✓]{Colors.NC} 配置检查完成")
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


def ask_port() -> int:
    """询问用户想要的端口，并确保端口可用"""
    default_port = 8000

    while True:
        user_input = input(
            f"{Colors.CYAN}[配置]{Colors.NC} 请输入服务端口号"
            f"（直接回车使用默认 {Colors.GREEN}{default_port}{Colors.NC}）: "
        ).strip()

        if user_input == "":
            chosen_port = default_port
        else:
            try:
                chosen_port = int(user_input)
                if not (1 <= chosen_port <= 65535):
                    print(f"{Colors.RED}[错误]{Colors.NC} 端口号必须在 1~65535 之间，请重新输入")
                    continue
            except ValueError:
                print(f"{Colors.RED}[错误]{Colors.NC} 请输入有效的数字，请重新输入")
                continue

        # 检查端口是否被占用
        if not is_port_available(chosen_port):
            print(f"{Colors.YELLOW}[占用]{Colors.NC} 端口 {Colors.RED}{chosen_port}{Colors.NC} 已被其他进程占用")

            # 自动找下一个可用端口供用户参考
            next_free = find_available_port(chosen_port + 1)
            suggestion = f"{Colors.GREEN}{next_free}{Colors.NC}" if next_free else "无法自动找到可用端口"

            retry = input(
                f"  → 输入 {Colors.GREEN}Y{Colors.NC} 换用下一个可用端口"
                f"，输入数字指定其他端口，"
                f"或 {Colors.RED}Q{Colors.NC} 退出: "
            ).strip().lower()

            if retry == "y" or retry == "Y":
                if next_free:
                    print(f"{Colors.CYAN}[信息]{Colors.NC} 切换到端口 {Colors.GREEN}{next_free}{Colors.NC}")
                    return next_free
                else:
                    print(f"{Colors.RED}[错误]{Colors.NC} 无法自动找到可用端口，请手动指定其他端口")
                    continue
            elif retry == "q" or retry == "Q":
                print(f"{Colors.CYAN}[退出]{Colors.NC} 已取消启动")
                sys.exit(0)
            else:
                # 当作数字重新输入
                try:
                    chosen_port = int(retry)
                    if not (1 <= chosen_port <= 65535):
                        print(f"{Colors.RED}[错误]{Colors.NC} 端口号无效，请重新输入")
                        continue
                    # 再次检查新端口
                    if not is_port_available(chosen_port):
                        print(f"{Colors.RED}[占用]{Colors.NC} 端口 {chosen_port} 也被占用了，请重新选择")
                        continue
                    return chosen_port
                except ValueError:
                    print(f"{Colors.RED}[错误]{Colors.NC} 无效输入，请重新输入")
                    continue
        else:
            return chosen_port


def print_server_info(port: int, python_exe: str):
    """打印服务器信息"""
    print()
    print(f"{Colors.BLUE}┌────────────────────────────────────────────────────────────┐{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  服务器信息:                                               {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - 虚拟环境: {Colors.GREEN}{VENV_NAME}{Colors.NC}                                      {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - Python: {Colors.GREEN}{Path(python_exe).parent.parent.name}{Colors.NC}                                  {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - 后端地址: {Colors.GREEN}http://localhost:{port}{Colors.NC}                     {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - 前端界面: {Colors.GREEN}http://localhost:{port}{Colors.NC}                     {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - API文档: {Colors.GREEN}http://localhost:{port}/docs{Colors.NC}                 {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}│{Colors.NC}  - 健康检查: {Colors.GREEN}http://localhost:{port}/api/health{Colors.NC}          {Colors.BLUE}│{Colors.NC}")
    print(f"{Colors.BLUE}└────────────────────────────────────────────────────────────┘{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}[提示]{Colors.NC} 按 Ctrl+C 停止服务器")
    print()
    print(f"{Colors.PURPLE}════════════════════════════════════════════════════════════{Colors.NC}")
    print()


def start_server(python_exe: str, port: int):
    """启动服务器"""
    # 确保使用正确的Python解释器
    python_path = Path(python_exe)
    if not python_path.exists():
        print(f"{Colors.RED}[错误]{Colors.NC} Python解释器不存在: {python_exe}")
        sys.exit(1)

    # 设置环境变量
    venv_path = python_path.parent.parent
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(venv_path.resolve())
    env['PATH'] = f"{python_path.parent};{env.get('PATH', '')}"

    print(f"{Colors.CYAN}[5/5]{Colors.NC} 启动服务器...")

    # Quick post-start probe so user sees the server come up immediately
    # (uvicorn imports / model loads can take 20-60s; without this the user
    # would see no output between [5/5] and the first INFO line).
    import threading
    import time
    import urllib.request
    import urllib.error

    ready_event = threading.Event()

    def _probe_ready():
        for i in range(120):  # up to 120s
            if not ready_event.is_set():
                time.sleep(1.0)
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/api/health", timeout=1
                ) as r:
                    if r.status == 200:
                        ready_event.set()
                        return
            except (urllib.error.URLError, ConnectionRefusedError, OSError):
                continue
            except Exception:
                continue

    t = threading.Thread(target=_probe_ready, daemon=True)
    t.start()

    # Launch uvicorn via Popen so we can stream output AND monitor readiness.
    proc = subprocess.Popen(
        [
            str(python_path), "-m", "uvicorn",
            "e2sc.api.server:app",
            "--host", "127.0.0.1",
            "--port", str(port),
            "--no-access-log",
            "--log-level", "warning",
        ],
        env=env,
        cwd=str(Path.cwd()),
    )

    # Print "Server ready" as soon as /api/health responds
    try:
        t.join(timeout=120)
        if ready_event.is_set():
            print(f"  {Colors.GREEN}[READY]{Colors.NC} Server responding on http://127.0.0.1:{port}")
        else:
            print(f"  {Colors.YELLOW}[WARN]{Colors.NC} Server not ready in 120s, check logs above")
    except KeyboardInterrupt:
        pass

    # Now just wait for the uvicorn process (Ctrl+C interrupts this)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print()
        print(f"{Colors.PURPLE}════════════════════════════════════════════════════════════{Colors.NC}")
        print()
        print(f"{Colors.CYAN}[信息]{Colors.NC} 服务器已停止")
        print()
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    except subprocess.CalledProcessError as e:
        print()
        print(f"{Colors.RED}[错误]{Colors.NC} 服务器启动失败: {e}")
        print()
        print(f"{Colors.YELLOW}[手动启动]{Colors.NC} 如果自动启动失败，可以手动执行:")
        print(f"  {python_path} -m uvicorn e2sc.api.server:app --host 127.0.0.1 --port {port}")
        sys.exit(1)


def check_database():
    """检查数据库文件"""
    print(f"{Colors.CYAN}[4/5]{Colors.NC} 检查数据库...")

    db_dir = Path("database")
    if not db_dir.exists():
        print(f"{Colors.YELLOW}[提示]{Colors.NC} 未找到 database 目录，知识库功能可能不可用")
    else:
        # 支持 .db 文件和源 CSV 文件的检查
        db_files = list(db_dir.glob("*.db"))
        csv_files = list(db_dir.glob("*.csv"))
        
        if db_files:
            print(f"{Colors.GREEN}[✓]{Colors.NC} 找到 {len(db_files)} 个数据库文件 (.db)")
            for db in db_files[:5]:
                print(f"{Colors.GREEN}[ ]{Colors.NC} {db.name}")
            if len(db_files) > 5:
                print(f"{Colors.YELLOW}[...]{Colors.NC} 还有 {len(db_files) - 5} 个数据库文件")
        elif csv_files:
            # CSV源文件存在，服务器启动时会自动转换为.db文件
            print(f"{Colors.GREEN}[✓]{Colors.NC} 找到 {len(csv_files)} 个源数据文件 (.csv)")
            for csv in csv_files[:5]:
                print(f"{Colors.GREEN}[ ]{Colors.NC} {csv.name}")
            if len(csv_files) > 5:
                print(f"{Colors.YELLOW}[...]{Colors.NC} 还有 {len(csv_files) - 5} 个源数据文件")
            print(f"{Colors.CYAN}[提示]{Colors.NC} 服务器启动时将自动初始化数据库")
        else:
            print(f"{Colors.YELLOW}[提示]{Colors.NC} database 目录为空，知识库功能可能不可用")

    print()


def main():
    """主函数"""
    # 在Windows上禁用颜色（可选）
    if _is_windows():
        # 尝试启用Windows终端颜色支持
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            Colors.disable()

    # 打印横幅
    print_banner()

    # 检查目录
    check_directory()

    # 检查虚拟环境
    python_exe = check_venv()
    print()

    # 检查依赖
    check_dependencies(python_exe)

    # 检查配置
    check_config()

    # 检查数据库
    check_database()

    # 询问端口
    chosen_port = ask_port()
    print(f"{Colors.GREEN}[✓]{Colors.NC} 使用端口 {chosen_port}")
    print()

    # 打印服务器信息
    print_server_info(chosen_port, python_exe)

    # 启动服务器
    start_server(python_exe, chosen_port)


if __name__ == "__main__":
    main()
