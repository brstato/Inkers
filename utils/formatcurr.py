def formatar_moeda_brasileira(valor):
    """
    Formata um valor numérico para o padrão monetário brasileiro (R$)
    Exemplo: 1234.56 -> 'R$ 1.234,56'
    """
    try:
        # Converte para float e formata com 2 casas decimais
        valor = float(valor)
        # Formata com separador de milhar e decimal conforme padrão BR
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00"
    


def _parse_currency(value_str: str) -> float:
    """Converte uma string de moeda para float, tratando valores vazios."""
    if not value_str:
        return 0.00
    try:
        return float(value_str.replace(',', '.'))
    except (ValueError, TypeError):
        return 0.00    