from settings.settings import MENSAGEM_TEAMS_CABECALHO

def montar_card_teams(coordenador: str, gestor: str, setor: str, detalhes_lpns: str) -> dict:
    texto_bloco_gestao = (
        "================================================\n\n"
        f"👔 **COORDENADOR:** {coordenador}\n\n"
        f"👤 **GESTOR:** {gestor}\n\n"
        f"🏢 **SETOR:** {setor}\n\n"
        "================================================"
    )
    return {
            "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {"type": "TextBlock", "text": MENSAGEM_TEAMS_CABECALHO, "wrap": True},
                        {"type": "TextBlock", "text": texto_bloco_gestao, "wrap": True, "weight": "Bolder", "color": "Accent"},
                        {"type": "TextBlock", "text": detalhes_lpns, "wrap": True},
                    ],
                },
            }
        ],
    }