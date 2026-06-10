from utils.dataframe_utils import limpar_nan
from backend.controle_de_estoque.templates.templates import estilo_tabela , template_atraso, template_linhas_html, template_return, template_body_email



def formatar_tabela_html(df_grupo) -> str:
    est_table = estilo_tabela
    linhas_html = ""

    for _, row in df_grupo.iterrows():
        l_atraso = row["Tempo de atraso"]

        if "6 a 10" in l_atraso or "+ de 10" in l_atraso:
            l_atraso = template_atraso(l_atraso)
        
        linhas_html += template_linhas_html(row=row, atraso=l_atraso, limpar_nan=limpar_nan)

    return template_return(estilo_tabela=est_table, linhas_html=linhas_html)

def montar_corpo_email(usuario_origem: str, qtd_pendencias: int, pior_atraso: str, fluxo: str, df_grupo) -> str:
    
    template_body = template_body_email(qtd_pendencias=qtd_pendencias, pior_atraso=pior_atraso, usuario_origem=usuario_origem)

    body = ""
    if "Especial" in fluxo:
        body = template_body['corpo_html_1']
    else:
        body = template_body['corpo_html_2']

    
    return body + formatar_tabela_html(df_grupo=df_grupo) + template_body['assinatura']