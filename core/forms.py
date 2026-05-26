import inspect
from fastapi import Form

"""
Utilitários para integração entre modelos Pydantic e formulários do FastAPI.
"""

def as_form(cls):
    """
    Adiciona um método ``as_form`` a um modelo Pydantic.

    Este decorator permite que o FastAPI converta automaticamente
    dados enviados via ``form-data`` em uma instância do modelo Pydantic

    O método ``as_form`` é criado dinamicamente com base nos campos
    definidos no modelo, permitindo que cada atributo seja tratado
    como um parâmetro ``Form`` do FastAPI.

    Args:
        cls:
            Classe do modelo Pydantic que receberá o método ``as_form``.
    Returns:
        A própia classe modificada com o método ``as_form`` adicionado.
    """

    new_params = []

    for field_name, model_field in cls.model_fields.items():
        new_params.append(
            inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Form(...)
                if model_field.is_required 
                else Form(model_field.default),
                annotation=model_field.annotation,
            )
        )

    async def _as_form(**data):
        """
        Cria uma instância do modelo Pydantic a partir dos dados do formulário.

        Args:
            **data:
                Dados recebidos via formulário HTTP.

        Returns:
            Uma instância do modelo Pydantic decorado.
        """

        return cls(**data)
    
    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)

    _as_form.__signature__ = sig

    cls.as_form = _as_form

    return cls