import requests

from settings.settings import WEBHOOK_TEAMS
from templates.teams_template import montar_card_teams
from utils.log import ExecutionLogger
from uuid import uuid4

"""
Serviço responsável pelo envio de notificações para o Microsoft Teams
através de Webhooks.

Fluxo:

1. Recebe os dados da cobrança.
2. Gera o payload do card.
3. Realiza requisição HTTP ao Teams.
4. Registra o resultado da operação.

Integrações:

- Microsoft Teams Webhook
- Teams Template
- Sistema de Logs
"""


execution_id = str(uuid4())

logger = ExecutionLogger(
        automation_name="Teams Service",
        execution_id=execution_id
)

class TeamsService:

    """
    Serviço responsável pela publicação de mensagens
    no Microsoft Teams.

    Atua como adaptador entre a aplicação e o endpoint
    de Webhook configurado para o canal.

    Responsabilidades:
    - Gerar payloads de mensagens.
    - Enviar cards para Teams.
    - Registrar eventos de sucesso e falha.
    """

    def __init__(self, webhook: str = WEBHOOK_TEAMS):
        self.webhook = webhook
    
    def enviar_card_separado(self, coordenador: str, gestor: str, setor: str, detalhes_lpns: str) -> None:
        """
        Envia um card de cobrança para o Teams. loveu teu cu

        """
        
        if not self.webhook:
            return
        try:
            response = requests.post(self.webhook, json=montar_card_teams(coordenador, gestor, setor, detalhes_lpns), timeout=30)

            if not response.ok:
                logger.error(f"Erro ao enviar cartão para o teams: {response.status_code}")
            logger.info(f"Card enviado para Teams referente ao setor {setor}")
        except requests.RequestException as e:
            logger.error(f"Falha de conexão com o Teams: {e}")

            