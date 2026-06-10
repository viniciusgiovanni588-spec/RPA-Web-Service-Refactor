from settings.settings import EMAIL_DEPARTAMENTO, EMAILS_GESTORES, MODO

from templates.email_template import template_email
from utils.email_utils import valid_emails

from utils.log import ExecutionLogger
from uuid import uuid4

"""
Serviço responsável pela geração e envio de notificações de cobrança através do Microsoft Outlook.

Fluxo:

1. Recebe informações consolidadas da cobrança
2. Valida destinatários
3. Gera conteúdo HTML
4. Monta mensagem Outlook
5. Salva ou envia o e-mail.

Integrações:

- Microsoft Outlook (COM)
- Template HTML de cobrança
- Sistema de logs
"""

execution_id = str(uuid4())

logger = ExecutionLogger(
    automation_name="EmailService",
    execution_id=execution_id
)

class EmailService:
    """
    Serviço responsável pelo envio de e-mails de cobrança.

    Atua como gateway entre a aplicação e o Microsoft Outlook,
    encapsulando toda a lógica de criação, validação e envio
    de mensagens.

    Responsabilidades
    - Criar mensagens Outlook
    - Validar destinatários
    - Aplicar templates HTML
    - Executar envio real ou modo teste
    - Registrar eventos de auditoria
    """
    
    def __init__(self, modo_teste: bool = MODO):
        self.modo_teste = modo_teste
        self._outlook = None


    @property
    def outlook(self):
        """
        Retorna uma instância singleton do Outlook
        
        A conexão é criada apenas na primeira utilização,
        evitando mútiplas inicializações do COM.
        
        Returns
        win32com.client.Dispatch
            Instância ativa do Microsoft Outlook.
        """
        if self._outlook is None:
            import win32com.client as win32

            self._outlook = win32.Dispatch("outlook.application")
        return self._outlook
    
    def enviar_email(self, usuario_origem: str, destinatarios: str, df_grupo, pior_atraso: str, setor: str, fluxo: str) -> bool:
        email = self.outlook.CreateItem(0)
        email.To = str(destinatarios).replace(",", ";")
        email.CC = ";".join(valid_emails([usuario_origem, EMAIL_DEPARTAMENTO, *EMAILS_GESTORES]))

        if not email.Recipients.ResolveAll():
            logger.error(f"Destinatário inválido: {email.To}")
            return False
        
        email.Subject = f"🚨 Ação Requerida: ILPNs Pendentes ({pior_atraso}) | Setores: {setor}"
        email.HTMLBody = template_email(usuario_origem, len(df_grupo), pior_atraso, fluxo, df_grupo)

        logger.info(f"\n\
                    \nTO: {email.To} \
                    \nCC: {email.cc} \
                    \nASSUNTO: {email.Subject} \
                    \n")
        
        if self.modo_teste:
            email.Save()
        else:
            email.Send()
        return True