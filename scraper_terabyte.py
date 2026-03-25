from playwright.sync_api import sync_playwright
import time
import json
import os
from telegram import enviar_ofertas


PAGEURL = 'https://www.terabyteshop.com.br/'
PRODUTO = 'ryzen 5 5500'
QUATIDADE = 10
PRECO_LIMITE = 1000.00

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PRODUTOS = os.path.join(DIRETORIO_ATUAL, 'produtos.json')
CAMINHO_OFERTAS = os.path.join(DIRETORIO_ATUAL, 'ofertas.json')

#  -----------------------------------------------------------------------------------------------------------------------

def navegar_para_pagina(page, url):
    page.goto(url, wait_until='domcontentloaded')
    page.fill('#isearch', PRODUTO)
    page.keyboard.press('Enter')
    


#  -----------------------------------------------------------------------------------------------------------------------

def esperar_resultados(page):
    """
    Espera a página de resultados da busca carregar, garantindo que o
    primeiro item de produto esteja visível antes de continuar.
    """
    print('Aguardando o carregamento dos resultados da busca...')
    # Espera pelo contêiner principal dos produtos
    page.wait_for_selector('.products-grid', timeout=20000)

    # Espera pelo NOME do primeiro produto. 
    # Isso garante que o conteúdo dentro do card (texto) foi realmente carregado.
    page.locator('.product-item__name').first.wait_for(state='visible', timeout=30000)
    print('Resultados carregados!')

# -----------------------------------------------------------------------------------------------------------------------

def raspar_pagina(page):

    produtos = []
    ofertas = []

    # devolve uma lista com os 10 primeiros itens que possuem um determinado seletor DOM
    itens = page.locator('.product-item__box').all()[:QUATIDADE]

    for item in itens:
        link = item.locator('.product-item__name')
        
        try:
            # Tenta pegar o nome com um timeout menor para não travar se for um item inválido
            nome = link.get_attribute('title') 
            l = link.get_attribute('href')
        except:
            print("Erro ao extrair nome ou link do item, pulando...")
            continue # se falhar (ex: é um banner ou esqueleto), pula para o próximo
        
        # pega o texto do preço e converte para float para permitir ordenação
        try:
            preco_text = item.locator('.product-item__new-price').inner_text()
            # remove R$, pontos de milhar e troca vírgula por ponto. Ex: "R$ 1.200,50" -> 1200.50
            preco = float(preco_text.replace('R$', '').replace('.', '').replace(',', '.').strip().split()[0])
        except Exception:
            preco = 0.0
            preco_text = "Indisponível"

        produto_atual = {
            'nome': nome,
            'link': l,
            'preco': preco,
        }

        if preco > 0 and preco < PRECO_LIMITE:
            print(f"OFERTA: {[produto_atual['nome'], produto_atual['preco']]}")
            ofertas.append(produto_atual)
        else:
            print("Nenhuma oferta encontrada abaixo do limite de preço.")

        produtos.append(produto_atual)
    return produtos, ofertas

#  -----------------------------------------------------------------------------------------------------------------------


def ordenar_produtos(produtos):
    # Ordena os produtos pelo preço (do menor para o maior)
    produtos_ordenados = sorted(produtos, key=lambda x: x['preco'])
    

    # Salva em JSON
    with open(CAMINHO_PRODUTOS, 'w', encoding='utf-8') as f: #
        json.dump(produtos_ordenados, f, ensure_ascii=False, indent=2) # Salva a lista de produtos ordenados em um arquivo JSON, com formatação legível e suporte a caracteres acentuados.
    
    print(f'Produtos salvos em {CAMINHO_PRODUTOS}')
    return produtos_ordenados




#  -----------------------------------------------------------------------------------------------------------------------

def main():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        content = browser.new_context()
        # content = browser.launch_persistent_context(user_data_dir='.temp', headless=False)
        page = content.new_page()
        

        navegar_para_pagina(page, PAGEURL)
        esperar_resultados(page)
        produtos, ofertas = raspar_pagina(page)
        produtos_ordenados = ordenar_produtos(produtos)

        # Salva as ofertas em um JSON separado
        if ofertas:
            with open(CAMINHO_OFERTAS, 'w', encoding='utf-8') as f:
                json.dump(ofertas, f, ensure_ascii=False, indent=2)
            print(f'{len(ofertas)} ofertas salvas em {CAMINHO_OFERTAS}')
        
        enviar_ofertas()



        content.close()
        browser.close()

#  -----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()