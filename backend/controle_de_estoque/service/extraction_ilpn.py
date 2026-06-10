from datetime import datetime

import pandas as pd
from uuid import uuid4

from settings.paths import PATH_COLABORADORES, PATH_ILPNS, PATH_ILPNS_PENDENTES, PATH_LOG_EXECUCAO, PATH_PIX, ensure_output_dirs
from repositories.excel_repository import DataFrameRepository
from service.pix_rules_ilpn import PixRuleService
from utils.date_utils import set_label_delay
from models.model_cobranca_ilpn import COLUNAS_PENDENTES
from utils.log import ExecutionLogger

"""
Serviço responsável pela preparação dos dados utilizados no processo
de cobrança de ILPN's 

Fluxo de processamento:
1. Carrega arquivos fonte
2. Realiza saneamento dos dados
3. Identifica ILPNs em atraso
4. Enriquece informações com dados de RH
5. Aplica regras de destinatários
6. Consolida indicadores
7. Gera dataset final para cobrança

Entradas:
    - ILPNs exportadas do sistema
    - Base PIX
    - Base de colaboradores
"""
execution_id = str(uuid4())

logger = ExecutionLogger(
    automation_name='OrchestratorService',
    execution_id=execution_id
)

class OrchestratorService:

    """
    Serviço responsável pela consolidação e preparação
    dos dados para cobrança.

    Atua como orquestrador do pipeline de transformação,
    aplicando regras de negócio e produzindo o dataset
    utilizado pelas etapas posteriores.

    Responsabilidades
    -----------------
    - Carregar arquivos fonte.
    - Validar e tratar dados.
    - Identificar pendências.
    - Aplicar regras PIX.
    - Consolidar métricas.
    - Gerar relatório final.
    """

    def __init__ (self, repository: DataFrameRepository | None = None, pix_rule_service: PixRuleService | None = None):
        self.repository = repository or DataFrameRepository()
        self.pix_rule_service = pix_rule_service or PixRuleService()

    async def process_automation(self) -> None:

        """
        Executa o pipeline completo de preparação dos dados.

        Etapas:
        1. Carregamento das bases.
        2. Remoção de duplicidades.
        3. Identificação de atrasos.
        4. Cruzamento com RH.
        5. Aplicação das regras PIX.
        6. Agrupamentos.
        7. Construção do dataset final.
        8. Persistência do resultado.

        """

        logger.info("Iniciando tratamento de dados referente a ILPNs atrasadas")
        ensure_output_dirs()

        try:
            df_ilpns = await self.repository.read_csv(PATH_ILPNS)
            df_pix = await self.repository.read_csv(PATH_PIX)
            df_colab = await self.repository.read_excel(PATH_COLABORADORES)
            logger.info("Dataframes criados")

            df_pix = df_pix.drop_duplicates(subset=["LPN ID"], keep="last")
            df_ilpns['Data_Convertida'] = pd.to_datetime(df_ilpns['Data_Convertida'].dt.normalize()).dt.days_in_month

            df_validos = df_ilpns[df_ilpns["Activity Tracking User ID"].notna()].copy()
            contagem_total_por_usuario = df_validos["Activity Tracking User ID"].value_counts().to_dict()
            df_atrasados = (df_validos[df_validos["Dias_Aberto"] >= 2]).copy()

            if df_atrasados.empty:
                logger.info("Nenhuma pendência igual ou superior a 2 dias encontrada")
                self.repository.save_excel(pd.DataFrame(columns=COLUNAS_PENDENTES), PATH_ILPNS_PENDENTES)
                logger.info(f"DataFrame vazio salvo em: {PATH_ILPNS_PENDENTES}")
                return
            
            df_atrasados = df_atrasados.merge(
                df_colab, left_on="Activity Tracking User ID", right_on="EMAIL | MATRICULA", how='left'
            )
            df_atrasados = df_atrasados.merge(
                df_pix[["LPN ID", "Referencia 2", "Referencia 1"]], left_on="LPN ID", how="left", right_on="LPN ID"
            )
            df_atrasados["Setor"] = df_atrasados['Setor'].fillna("SEM SETOR")
            df_atrasados['Atributo Item'] = df_atrasados['Atributo Item'].fillna("-")
            df_atrasados['Data_Formatada'] = df_atrasados['Data_Convertida'].dt.strftime("%d/%m/%Y")

            logger.info('Aplicando regras e definindo destinatários')

            rotas = []
            for idx, row in df_atrasados.iterrows():
                rota = self.pix_rule_service.determinar_destinatario_linha(row)
                emails_limpos = [str(dest).strip() for dest in rota.destinatarios if str(dest).lower() not in ["nan", "none", ""]]

                rotas.append(
                    {
                        "Index": idx,
                        "Chave_Gestor": rota.chave_gestor,
                        "Destinatarios_Final": ", ".join(dict.fromkeys(emails_limpos)),
                        "Fluxo_Final": rota.fluxo,
                        "Etiqueta_Final": set_label_delay(row["Dias_Aberto"]),
                    }
                )

            df_rotas = pd.DataFrame(rotas)
            df_atrasados = df_atrasados.merge(df_rotas, left_index=True, right_on="Index")
            group_cols = ["Activity Tracking User ID", "Chave_Gestor", "Setor"]
            df_contagem_grpo = df_atrasados.groupby(group_cols).size().reset_index(name="Contagem_Grupo")
            df_atrasados = df_atrasados.merge(df_contagem_grpo, on=group_cols, how="left")

            logger.info('Gerando arquivo final')

            analise_final = []

            for _, row in df_atrasados.iterrows():
                usuario = row["Activity Tracking User ID"]
                analise_final.append({
                    "Data ilpn´s": row["Data_Formatada"],
                        "Usuário": usuario,
                        "Quantidade ILPNs": contagem_total_por_usuario.get(usuario, 0),
                        "Ilpn´s em atraso": row["Contagem_Grupo"],
                        "Tempo de atraso": row["Etiqueta_Final"],
                        "Fluxo aplicado": row["Fluxo_Final"],
                        "Referencia 1": str(row["Referencia 1"]) if pd.notna(row["Referencia 1"]) else "",
                        "Referencia 2": str(row["Referencia 2"]) if pd.notna(row["Referencia 2"]) else "",
                        "Destinatários": row["Destinatarios_Final"],
                        "LPN": str(row["LPN"]),
                        "Setor": str(row["Setor"]),
                        "Atributo item": str(row["Atributo Item"]),
                        "Inventory type": str(row["Inventory Type ID"]) if pd.notna(row["Inventory Type ID"]) else "",
                })

            df_final = pd.DataFrame(analise_final)[COLUNAS_PENDENTES]
            df_final = df_final.sort_values(by=["Usuário", "Setor", "Tempo de atraso"], ascending=[True,True, False])
            self.repository.save_excel(df_final, PATH_ILPNS_PENDENTES)

            logger.info('Relatório de envio para todos os responsáveis gerado')

        except Exception as erro:
            logger.info(f'Erro: {erro}')    

async def processar_automacao() -> None:
   await OrchestratorService().process_automation()
