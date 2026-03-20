from playwright.sync_api import sync_playwright
import time
import json


PAGEURL = 'https://www.terabyteshop.com.br/'
PESQUISA = 'Fonte 650W'
FILE = 'produtos.json'
QUATIDADE = 10

#  -----------------------------------------------------------------------------------------------------------------------

def navegar_para_pagina(page, url):
    page.goto(url, wait_until='domcontentloaded')
    page.fill('#isearch', PESQUISA)
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
            continue # Se falhar (ex: é um banner ou esqueleto), pula para o próximo
        
        # pega o texto do preço e converte para float para permitir ordenação
        try:
            preco_text = item.locator('.product-item__new-price').inner_text()
            # Remove R$, pontos de milhar e troca vírgula por ponto. Ex: "R$ 1.200,50" -> 1200.50
            preco = float(preco_text.replace('R$', '').replace('.', '').replace(',', '.').strip().split()[0])
        except Exception:
            preco = 0.0
            preco_text = "Indisponível"


        produtos.append({
            'nome': nome,
            'link': l,
            'preco': preco
        })
    return produtos

#  -----------------------------------------------------------------------------------------------------------------------


def ordenar_produtos(produtos):
    # Ordena os produtos pelo preço (do menor para o maior)
    produtos_ordenados = sorted(produtos, key=lambda x: x['preco'])
    
    # Salva em JSON
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(produtos_ordenados, f, ensure_ascii=False, indent=2)
    
    print(f'Produtos salvos em {FILE}')
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
        produtos = raspar_pagina(page)
        produtos_ordenados = ordenar_produtos(produtos)


        content.close()
        browser.close()

#  -----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()