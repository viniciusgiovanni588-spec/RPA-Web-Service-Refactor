import re
from typing import Any
from settings.regras_pix import REGRAS_PIX_BASE
from models.model_cobranca_ilpn import RotaCobranca
from utils.dataframe_utils import limpar_texto, normalizar_email


"""
Serviço responsável pela aplicação das regras PIX utilizadas
na definição automática dos responsáveis pelas cobranças.

As regras são baseadas na combinação entre:

- Usuário responsável pela atividade.
- Referência PIX associada à ILPN.
- Palavras-chave configuradas.

Resultado:

- Determinação do gestor responsável.
- Definição dos destinatários.
- Definição do fluxo de cobrança.
"""

class PixRuleService:

    """
    Serviço responsável pela resolução das rotas de cobrança.

    Analisa as regras configuradas para cada usuário e identifica
    se existe alguma regra especial aplicável ao registro analisado.

    Responsabilidades:
    - Aplicar regras PIX.
    - Identificar gestores especiais.
    - Definir destinatários.
    - Determinar fluxo da cobrança.
    """

    def __init__(self, regras_pix: dict[str, dict[str, list[str]]] | None = None):
        self.regras_pix = regras_pix if regras_pix is not None else REGRAS_PIX_BASE
    
    @staticmethod
    def verificar_correspondencia_area(palavra_chave: str, ref_pix: str) -> bool:
        if palavra_chave in ref_pix:
            return True
        return " " not in palavra_chave and bool(re.search(rf"\b{re.escape(palavra_chave)}\b", ref_pix))
    
    def determinar_desiantario_linha(self, row: Any) -> RotaCobranca:
        """
        Determina a rota de cobrança para uma ILPN.

        Processo:
        1. Normaliza os dados da linha.
        2. Procura regras especiais PIX.
        3. Define gestor responsável.
        4. Monta lista de destinatários.
        5. Retorna a rota final.
        """
        usuario_norm = normalizar_email(row["Activity Tracking User ID"])
        ref2_limpa = limpar_texto(row["Referencia 2"])
        gestor_padrao = str(row["GESTOR"])
        coord_padrao = str(row["COORDENADOR"])

        gestor_alvo = None
        for gestor_nome, lista_palavras in self.regras_pix.get(usuario_norm, {}).items():
            if any(self.verificar_correspondencia_area(palavra, ref2_limpa) for palavra in lista_palavras):
                gestor_alvo = gestor_nome
                break
        if gestor_alvo:
            destinatarios = [gestor_alvo, coord_padrao, "controledeestoquecd1200@casasbahia.com.br"]
            return RotaCobranca(chave_gestor=gestor_alvo, destinatarios= destinatarios, fluxo="Especial (PIX)")
            
        destinatarios = [row["Activity Tracking User ID"], gestor_padrao, coord_padrao]
        return RotaCobranca(chave_gestor=gestor_padrao, destinatarios=destinatarios, fluxo="Normal")