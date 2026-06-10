from dataclasses import dataclass, field
from datetime import date

"""
Modelos de domínio utilizados no processo de cobrança automática de ILPNs pendentes.

Responsabilidades:
- Representar rotas de envio de cobrança.
- Estruturar dados de colaboradores e gestores.
- Padronizar registros utilizados durante o processamento.
- Definir contratos de dados entre as etapas da automação.

Todos os modelos são imutáveis (frozen=True) para garantir integridade dos dados durante a execução do fluxo.
"""

@dataclass(frozen=True)
class RotaCobranca:
    """
    Define uma rota de envio de notificações para cobrança.
    """
    chave_gestor: str # Identificador utilizado para localizar o gestor responsável.
    destinatarios: list[str] = field(default_factory=list) # Lista de e-mails que receberão a cobrança.
    fluxo: str = "Normal" # Tipo de fluxo utilizado na cobrança. Exemplo: "Normal", "Escalonado".

@dataclass(frozen=True)
class CobrancaGrupo:
    """
    Representa um agrupamento de pendências por colaborador.
    
    Utilizado para consolidar informações enviadas nos e-mails de cobrança.
    """

    usuario: str
    destinatarios: str
    quantidade_pendencias: int
    pior_atraso: str
    coordenador: str
    gestor: str
    setor: str

@dataclass(frozen=True)
class Colaborador:
    """
    Representa os dados cadastrais de um colaborador
    
    Pode ser identificado tanto por matrícula quanto por endereço de e-mail.
    """

    email_ou_matricula: str
    nome: str = ""
    gestor: str = ""
    coordenador: str = ""
    setor: str = ""

COLUNAS_HISTORICO = [
    "DATA_FOTO",
    "ILPN",
    "STATUS_SISTEMA",
    "DATA_CRIACAO_ILPN",
    "DATA_HORA_RESOLUCAO",
    "FAIXA_DE_ATRASO",
    "USUARIO_CRIADOR",
    "REFERENCIA_1",
    "REFERENCIA_2",
    "PALAVRA_CHAVE",
    "SETOR_RESPONSAVEL",
    "GESTOR",
    "COORDENADOR",
]
"""
Colunas obrigat´roias para DF histórico.
Utilizadas para:
- Presistência de snapshots diários.
- Comparação de estados.
- Construção de indicadores históricos.
"""

COLUNAS_PENDENTES = [
    "Data ilpn´s",
    "Usuário",
    "Quantidade ILPNs",
    "Ilpn´s em atraso",
    "Tempo de atraso",
    "Fluxo aplicado",
    "Referencia 1",
    "Referencia 2",
    "Destinatários",
    "LPN",
    "Setor",
    "Atributo item",
    "Inventory type",
]

@dataclass(frozen=True)
class HistoricoResumo:
    """
    Resumo das alterações identificadas entre snapshots consecutivos.
    """
    resolvidas: int # Quantidade de ILPNs resolvidas
    novas: int # Quantidade de novas ILPNs identificadas
    atualizadas: int # Quantidade de ILPNs que soferam alteração de status.

@dataclass(frozen=True)
class ILPnPendente:
    """
    Representa uma ILPN pendente de tratamento
    Este modelo é utilizado durante todo o pipeline de processamento,
    agrupamento e geração de cobranças
    """
    ilpn: str
    usuario: str
    data_atividade: date | str
    setor: str
    atributo_item: str
    inventory_type: str
    reference_1: str = ""
    reference_2: str = ""