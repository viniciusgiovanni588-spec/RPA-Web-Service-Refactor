from collections.abc import Callable

from typing import Dict

estilo_tabela = """
    <style>
        table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; font-size: 12px; }
        th { background-color: #004b87; color: white; text-align: left; padding: 8px; border: 1px solid #ddd; }
        td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .atraso-critico { color: red; font-weight: bold; }
    </style>
    """

def template_body_email(qtd_pendencias: int, pior_atraso: str, usuario_origem: str)-> Dict[str, str]:
    
    template_texto_din_1 = (
        f"Foram identificadas <b>{qtd_pendencias}</b> ILPN(s) com <b>{pior_atraso}</b> "
        "que requerem a vossa ação imediata."
    )

    template_texto_din_2 = (
        f"Foram identificadas <b>{qtd_pendencias}</b> ILPN(s) geradas pelo(a) colaborador(a) "
        f"<b>{usuario_origem}</b> com <b>{pior_atraso}</b> que requerem a vossa ação imediata."
    )

    template_corpo_html_1 = (
        '<p style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">'
        f"Olá,<br><br>{template_texto_din_1}<br>"
        "Abaixo encontra-se a lista detalhada para análise e regularização sistémica:</p><br>"
    )

    template_corpo_html_2 = (
        '<p style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">'
        f"Olá,<br><br>{template_texto_din_2}<br>"
        "Abaixo encontra-se a lista detalhada para análise e regularização sistémica:</p><br>"
    )

    template_assinatura = (
        '<br><br><p style="font-family: Arial, sans-serif; font-size: 12px; color: #777;">'
        "<i>Este é um e-mail automático gerado pela automação do Controle de Estoque CD 1200.</i><br>"
        "Por favor, não responda diretamente a esta mensagem sem manter os envolvidos em cópia.</p>"
    )

    return {
        "corpo_html_1": template_corpo_html_1,
        "corpo_html_2": template_corpo_html_2, 
        "assinatura": template_assinatura
        }

def template_atraso(atraso):

    atraso = f"<span class='atraso-critico'>{atraso}</span>"
    return atraso

def template_linhas_html(row, atraso, limpar_nan: str | Callable):
    linhas_html += (
            f"<tr><td>{row['LPN']}</td><td>{row['Setor']}</td><td>{row['Atributo item']}</td>"
            f"<td>{row['Data ilpn´s']}</td><td>{atraso}</td><td>{limpar_nan(row.get('Referencia 1'))}</td>"
            f"<td>{limpar_nan(row.get('Referencia 2'))}</td></tr>"
        )
    
    return linhas_html

def template_return(estilo_tabela, linhas_html):
    retorno = (
        f"{estilo_tabela}<table><thead><tr><th>LPN</th><th>Setor</th><th>Atributo Item</th>"
        f"<th>Data Atividade</th><th>Tempo de Atraso</th><th>Referência 1</th><th>Referência 2</th>"
        f"</tr></thead><tbody>{linhas_html}</tbody></table>"
    )
    return retorno