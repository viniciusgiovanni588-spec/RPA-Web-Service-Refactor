import re
import pandas as pd

from typing import Any

from utils.log import ExecutionLogger
from uuid import uuid4

execution_id = str(uuid4())

logger = ExecutionLogger(
        automation_name="3.11 - Status Wave + oLPN",
        execution_id=execution_id
)


def read_csv_inteligente(caminho: str) -> pd.DataFrame:
    for encoding in ["utf-16", "iso-8859", "utf-8-sig", "cp1252"]:
        try:
            return pd.read_csv(caminho, sep=None, engine="python", encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    raise logger.erro(f"Erro ao ler {caminho}")

def normalizar_emal(email: Any) -> str:
    if pd.isna(email):
        return ""
    return str(email).strip().lower().replace("@casasbahia.com.br", "@viavarejo.com.br")

def limpar_texto(texto: Any) -> str:
    if pd.isna(texto):
        return ''
    return re.sub(r"\s+", " ", str(texto).strip().upper())

def limpar_nan(valor: Any) -> str:
    if pd.isna(valor) or str(valor).strip().lower() in ['nan', 'nat', 'none', ""]:
        return "-"
    return str(valor)
