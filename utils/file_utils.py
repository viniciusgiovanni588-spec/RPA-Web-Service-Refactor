from pathlib import Path

def existe(caminho: str | Path) -> bool:
    return Path(caminho).exists()

def criar_diretorio(caminho: str | Path) -> None:
    Path(caminho).mkdir(parents=True, exist_ok=True)