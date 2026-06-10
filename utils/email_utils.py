from typing import Iterable

import pandas as pd

def somente_emails_validos(valores: Iterable[object]) -> list[str]:
    return [str(email).strip() for email in valores if pd.notna(email) and "@" in str(email)]


def lista_outlook(valores: Iterable[object]) -> str:
    return ";".join(somente_emails_validos(valores))