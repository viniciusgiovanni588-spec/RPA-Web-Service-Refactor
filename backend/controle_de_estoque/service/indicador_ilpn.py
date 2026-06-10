from datetime import datetimes

import pandas as pd
from uuid import uuid4

from settings.paths import PATH_COLABORADORES, PATH_HISTORICO_PBI, PATH_ILPNS_PENDENTES, PATH_PRONTO_ENVIO
from models.model_cobranca_ilpn import HistoricoResumo
from repositories.colaborador_repository import ColaboradorRepository
from repositories.excel_repository import DataFrameRepository
from repositories.historico_repository import HistoricoRepository
from service.rh_service import RHService
from utils.log import ExecutionLogger

execution_id = str(uuid4())

logger = ExecutionLogger(
        automation_name="3.11 - Status Wave + oLPN",
        execution_id=execution_id
)

class IndicadorService:

    def __init__(self, repository: DataFrameRepository | None = None):
        self.repository = repository or DataFrameRepository
        self.rh_service = RHService(ColaboradorRepository(PATH_COLABORADORES))
        self.historico_repository = HistoricoRepository(PATH_HISTORICO_PBI)

    def processar_indicadores(self) -> HistoricoRepository | None:
        logger.info("Iniciando IndicatorService")

        df_hoje = self.repository.read_excel(PATH_ILPNS_PENDENTES)
        
        if df_hoje.empty:
            logger.info("Dataframe vazio. Processando pendências anteriores")
        else:
            df_hoje['LPN'] = df_hoje['LPN'].astype(str).str.strip()
        
        logger.info("Consultando a base de colaboradores")
        dict_email, dict_nome = self.rh_service.load_base()
        if not df_hoje.empty:
            coordenadores, gestores, setores_rh = [], [], []

            for _, row in df_hoje.iterrow():
                fluxo = str(row.get("Fluxo aplicado", ""))
                destinatarios = str(row.get("Destinatários", ""))
                usuario = str(row.get("Usuário", ""))
                setor_original = str(row.get("Setor", ""))
                alvo = destinatarios.split(",")[0].strip() if "Especial" in fluxo else usuario.strip()
                dados_rh = self.rh_service.buscar_dados_rh(alvo, dict_email, dict_nome)
                coordenadores.append(dados_rh.get("COORDENADOR", "Não Localizado"))
                gestores.append(dados_rh.get("GESTOR", "Não Localizado"))
                setores_rh.append(dados_rh.get("SETOR", setor_original))

            df_hoje["COORDENADOR"] = coordenadores
            df_hoje['GESTOR'] = gestores
            df_hoje['SETOR_RH'] = setores_rh

        self.repository.save_excel(df_hoje, PATH_PRONTO_ENVIO)
        logger.info("Arquivo ILPNs_pendentes_pronta_entrega.xlsx criado")

        logger.info("atualizando o histórico de ilpn atrasada")
        resumo = self._atualizar_historico(df_hoje)
        logger.info("Histórico atualizado")
        logger.info(f"ILPNs resolvidas D-1: {resumo.resolvidas}")
        logger.info(f"ILPNs mapeadas: {resumo.novas}")
        logger.info(f"ILPNs pendentes: {resumo.atualizadas}")
        return resumo
    
    def _atualizar_historico(self, df_hoje: pd.DataFrame) -> HistoricoResumo:
        data_hoje_str = datetimes.now().strftime("%d/%m/%Y")
        hora_agora_str = datetimes.now().strftime("%d/%m/%Y %H:%M")
        df_historico = self.historico_repository.carregar()
        if not df_historico.empty():
            df_historico["ILPN"] = df_historico['ILPN'].astype(str).str.strip()

        lista_lpns_hoje = df_hoje['LPN'].tolist() if not df_hoje.empty else []
        resolvidas = 0
        if not df_historico.empty:
            for index, row in df_historico.iterrows():
                if row['STATUS_SISTEMA'] == "Pendente" and row['ILPN'] not in lista_lpns_hoje:
                    df_historico.at[index, "STATUS_SISTEMA"] = "Resolvido"
                    df_historico.at[index, "DATA_HORA_RESOLUCAO"] = hora_agora_str
                    resolvido += 1

        novas_linhas = []
        novas = 0
        atualizadas = 0
        if not df_hoje.empty:
            for _, row in df_hoje.iterrows():
                ilpn_atual = row['LPN']
                mascara_existente = df_historico['ILPN'] == ilpn_atual
                if not df_historico.empty and mascara_existente.any():
                    idx_hist = df_historico.index[mascara_existente][0]
                    df_historico.at[idx_hist, "FAIXA_DE_ATRASO"] = row.get("Tempo de atraso", "")
                    df_historico.at[idx_hist, "STATUS_SISTEMA"] = 'Pendente'
                    atualizadas += 1
                else:
                    novas_linhas.append(
                        {
                            "DATA_FOTO": data_hoje_str,
                            "ILPN": ilpn_atual,
                            "STATUS_SISTEMA": "Pendente",
                            "DATA_CRIACAO_ILPN": row.get("Data ilpn´s", ""),
                            "DATA_HORA_RESOLUCAO": "",
                            "FAIXA_DE_ATRASO": row.get("Tempo de atraso", ""),
                            "USUARIO_CRIADOR": row.get("Usuário", ""),
                            "REFERENCIA_1": row.get("Referencia 1", ""),
                            "REFERENCIA_2": row.get("Referencia 2", ""),
                            "PALAVRA_CHAVE": str(row.get("Destinatários", "")).split(",")[0],
                            "SETOR_RESPONSAVEL": row.get("SETOR_RH", ""),
                            "GESTOR": row.get("GESTOR", ""),
                            "COORDENADOR": row.get("COORDENADOR", ""),
                        }
                    )
                    novas += 1

        if novas_linhas:
            df_historico = pd.concat([df_historico, pd.DataFrame(novas_linhas)], ignore_index=True)
        self.historico_repository.salvar(df_historico)
        return HistoricoRepository(resolvidas=resolvidas, novas=novas, atualizadas=atualizadas)
    
    def processar_indicadores() -> HistoricoResumo | None:
        return IndicadorService().processar_indicadores()
                