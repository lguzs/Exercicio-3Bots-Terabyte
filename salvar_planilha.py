import asyncio
import os
from datetime import datetime

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright
import scraper_terabyte


load_dotenv()

CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS', 'credentials.json')
SHEET_NAME       = os.getenv('SHEET_NAME', 'resultados-terabyte')

SELETOR_ITEM   = 'li.ui-search-layout__item'
SELETOR_TITULO = '.poly-component__title-wrapper a'
SELETOR_LINK   = '.poly-component__title-wrapper a'
SELETOR_PRECO  = '.andes-money-amount__fraction'

def conectar_sheets():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]

    creds  = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)

    planilha = client.open(SHEET_NAME)
    aba      = planilha.sheet1

    if not aba.row_values(1):
        aba.append_row(
            ['Data/Hora', 'Produto Buscado', 'Título', 'Preço (R$)', 'Link', 'Oferta?'],
            value_input_option='USER_ENTERED'
        )
        print('Cabeçalho criado na planilha.')

    return aba


def salvar_na_planilha(aba, resultados):
    agora  = datetime.now().strftime('%d/%m/%Y %H:%M')
    linhas = []

    for r in resultados:
        oferta = 'SIM' if r['preco'] and r['preco'] < PRECO_LIMITE else 'NAO'
        linhas.append([
            agora,
            PRODUTO,
            r['titulo'],
            float(r['preco']) if r['preco'] else 0,
            r['link'],
            oferta,
        ])

    aba.append_rows(linhas, value_input_option='USER_ENTERED')
    print(f'{len(linhas)} linhas adicionadas na planilha.')


async def main():
    # 1. Raspa o Mercado Livre
    resultados = await raspar_mercado_livre()

    # 2. Conecta ao Google Sheets e salva
    print('\nConectando ao Google Sheets...')
    aba = conectar_sheets()
    salvar_na_planilha(aba, resultados)

    # 3. Verifica ofertas e envia alerta no WhatsApp
    ofertas = [r for r in resultados if r['preco'] and r['preco'] < PRECO_LIMITE]

    if ofertas:
        print(f'\n{len(ofertas)} oferta(s) encontrada(s)! Enviando alerta...')
        mensagem = formatar_alerta_ml(PRODUTO, ofertas)
        enviar_whatsapp(mensagem)
    else:
        print('\nNenhuma oferta encontrada. Sem alerta.')

    print(f'\nConcluído! Planilha "{SHEET_NAME}" atualizada.')


if __name__ == '__main__':
    asyncio.run(main())