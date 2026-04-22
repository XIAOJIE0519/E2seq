"""
E2seq - Easy to Chat with Sequencing
Easy to Chat with Sequencing - 快速启动脚本
"""

import os
import sys
import subprocess
import platform
import socket
from pathlib import Path

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
# Windows PowerShell: 设置控制台代码页为 UTF-8 (65001)
try:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)
    kernel32.SetConsoleOutputCP(65001)
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
    if platform.system() == 'Windows':
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
    if platform.system() == 'Windows':
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def activate_venv_and_run(python_exe: str, func, *args, **kwargs):
    """激活虚拟环境后执行函数"""
    # 设置环境变量
    venv_path = Path(python_exe).parent.parent
    os.environ['VIRTUAL_ENV'] = str(venv_path.resolve())

    # 添加虚拟环境的Scripts/Lib到PATH
    if platform.system() == 'Windows':
        os.environ['PATH'] = f"{venv_path / 'Scripts'};{os.environ.get('PATH', '')}"
    else:
        os.environ['PATH'] = f"{venv_path / 'bin'}:{os.environ.get('PATH', '')}"

    return func(*args, **kwargs)


def check_dependencies(python_exe):
    """检查依赖包"""
    print(f"{Colors.CYAN}[2/5]{Colors.NC} 检查依赖包...")

    # 核心依赖列表
    required_packages = [
        "fastapi", "uvicorn", "python-multipart",
        "scanpy", "anndata", "pandas", "numpy",
        "plotly", "networkx", "gseapy",
        "sentence-transformers", "chromadb",
        "rich", "typer", "pydantic"
    ]

    # sentence-transformers 依赖 torch + transformers，首次 import 较慢（~20s）。
    # 用其子依赖做检查：torch 和 transformers 加载快（1-3s），无需长 timeout。
    # 如果 torch/transformers 能导入，说明 sentence-transformers 所需的底层环境完整。
    _st_imports = ["torch", "transformers"]

    missing_packages = []
    installed_packages = []

    for package in required_packages:
        import_name = package.replace("-", "_")
        # 对于 sentence-transformers，改为检查其快速加载的核心子依赖
        check_imports = _st_imports if package == "sentence-transformers" else [import_name]
        all_ok = True
        for check_name in check_imports:
            try:
                result = subprocess.run(
                    [python_exe, "-c", f"import {check_name}"],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode != 0:
                    all_ok = False
                    break
            except Exception:
                all_ok = False
                break
        if all_ok:
            installed_packages.append(package)
        else:
            missing_packages.append(package)

    if missing_packages:
        print(f"{Colors.YELLOW}[警告]{Colors.NC} 缺少以下依赖包，正在安装: {', '.join(missing_packages)}")
        try:
            subprocess.run(
                [python_exe, "-m", "pip", "install"] + missing_packages,
                check=True,
                timeout=300
            )
            print(f"{Colors.GREEN}[✓]{Colors.NC} 依赖包安装完成")
        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 安装依赖失败: {e}")
            print(f"{Colors.YELLOW}[提示]{Colors.NC} 请手动安装: pip install {' '.join(missing_packages)}")
            sys.exit(1)
    else:
        print(f"{Colors.GREEN}[✓]{Colors.NC} 所有依赖包已安装 ({len(installed_packages)} 个)")

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

    try:
        subprocess.run(
            [
                str(python_path), "-m", "uvicorn",
                "e2sc.api.server:app",
                "--host", "127.0.0.1",
                "--port", str(port),
            ],
            check=True,
            env=env,
            cwd=str(Path.cwd())
        )
    except KeyboardInterrupt:
        print()
        print(f"{Colors.PURPLE}════════════════════════════════════════════════════════════{Colors.NC}")
        print()
        print(f"{Colors.CYAN}[信息]{Colors.NC} 服务器已停止")
        print()
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
    if platform.system() == 'Windows':
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
