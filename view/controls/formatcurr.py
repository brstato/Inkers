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