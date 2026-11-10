# install.py
import json
import shutil
import sys
from pathlib import Path


def install_kernel():
    """Устанавливает kernelspec для Jupyter."""
    here = Path(__file__).parent.resolve()
    source = here / "kernelspec" / "kernel.json"
    if not source.exists():
        print(f"❌ Не найден {source}")
        sys.exit(1)

    # куда Jupyter смотрит kernelspec
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming" / "jupyter" / "kernels"
    else:
        base = Path.home() / ".local" / "share" / "jupyter" / "kernels"

    target_dir = base / "algrus"
    target_dir.mkdir(parents=True, exist_ok=True)

    # копируем kernel.json
    shutil.copy(source, target_dir / "kernel.json")

    # заменяем "python" на полный путь к venv-python (надёжнее)
    spec_path = target_dir / "kernel.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["argv"][0] = sys.executable  # путь к python из venv
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    print(f"✅ Ядро установлено в {target_dir}")
    print(f"   Python: {sys.executable}")
    print("   Перезапустите Jupyter и выберите ядро 'АлгРус'")


if __name__ == "__main__":
    install_kernel()
