"""Componente de Inteligência (Generative AI for Engineering).

PROVISÓRIO: enquanto o prof. Reinaldo não define o que a disciplina exige
e não há chave de LLM configurada, o pedido formal sai de um modelo de
texto fixo. A troca pelo LLM real entra aqui, sem mudar quem chama.
"""

NOMES = {
    "buraco": "buraco na via",
    "rachadura": "rachadura no pavimento",
    "calcada_quebrada": "calçada danificada",
    "bueiro_entupido": "bueiro entupido",
    "lixo": "descarte irregular de lixo",
    "outro": "problema na via pública",
}


def redigir_pedido(categoria: str, gravidade: str, lat: float, lon: float, descricao: str) -> str:
    problema = NOMES.get(categoria, NOMES["outro"])
    texto = (
        f"Solicito vistoria e reparo de {problema}, gravidade {gravidade}, "
        f"nas coordenadas {lat:.6f}, {lon:.6f}."
    )
    if descricao.strip():
        texto += f" Observação do cidadão: {descricao.strip()}"
    return texto
