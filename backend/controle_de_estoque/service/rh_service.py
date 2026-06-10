from repositories.colaborador_repository import ColaboradorRepository
from utils.dataframe_utils import normalizar_email 
from models.model_cobranca_ilpn import Colaborador

from utils.log import ExecutionLogger
from uuid import uuid4

"""
Serviço responsável pela consulta e recuperação de informações
cadastrais dos colaboradores.

As consultas podem ser realizadas utilizando:

- E-mail corporativo
- Matrícula
- Nome do colaborador

Os dados são obtidos através dos índices construídos pelo
ColaboradorRepository.
"""

execution_id = str(uuid4())

logger = ExecutionLogger(
        automation_name="RH Service",
        execution_id=execution_id
)

class RHService:

    """
    Serviço responsável pelas consultas de dados de RH.

    Atua como camada intermediária entre os serviços da aplicação
    e os repositórios de colaboradores.

    Responsabilidades
    -----------------
    - Carregar índices de RH.
    - Realizar buscas por e-mail.
    - Realizar buscas por matrícula.
    - Realizar buscas por nome.
    """

    def __init__(self, colaborador_repository: ColaboradorRepository):
        self.colaborador_repository = colaborador_repository
    
    def carregar_bases_rh(self) -> tuple[dict[str, dict], dict[str, dict]]:

        """
        Carrega os índices de consulta dos colaboradores.
        """

        try:
            return self.colaborador_repository.carregar_indices_rh()
        except Exception as e:
            logger.error(f'Falha ao carregar a base de colaboradores. Erro: {e}')
            raise
    
    @staticmethod
    def buscar_dados_rh(alvo: object, dict_email: dict[str,dict], dict_nome: dict[str, dict]) -> Colaborador | None:
        
        """
        Localiza informações cadastrais de um colaborador.
        """
        
        alvo_str = str(alvo).strip()
        if "@" in alvo_str:
            return dict_email.get(normalizar_email(alvo_str), {})
        return dict_nome.get(alvo_str.upper(), {})
            
        