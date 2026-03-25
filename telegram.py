from datetime import datetime

import telebot
import json
import os
import time

bot = telebot.TeleBot("8673078264:AAEnnENW1bAP8QqmaeIAm8xzu6iVjFvT2hc")

# Define caminhos absolutos para evitar erros de arquivo não encontrado
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_OFERTAS = os.path.join(DIRETORIO_ATUAL, 'ofertas.json')
CAMINHO_ID = os.path.join(DIRETORIO_ATUAL, 'chat_id.json')

@bot.message_handler(commands=['start', 'help', 'stop'])
def start(message):
    chat_id = message.chat.id
    
    # Salva o ID em um arquivo para usar depois no scraper
    with open(CAMINHO_ID, 'w') as f:
        json.dump({'chat_id': chat_id}, f)

    texto = f"Bot configurado! Seu Chat ID ({chat_id}) foi salvo.\nAgora você receberá as ofertas automaticamente aqui."
    bot.reply_to(message, texto)
    print(f"ID salvo: {chat_id}")


def enviar_ofertas():
    # Tenta carregar o CHAT_ID do arquivo salvo
    if os.path.exists(CAMINHO_ID):
        with open(CAMINHO_ID, 'r') as f:
            dados = json.load(f)
            chat_id_destino = dados.get('chat_id')
    else:
        print("ERRO: Nenhum Chat ID salvo. Execute o telegram.py e envie /start para configurar.")
        return

    if not os.path.exists(CAMINHO_OFERTAS):
        print(f"Arquivo ofertas.json não encontrado em: {CAMINHO_OFERTAS}")
        return

    with open(CAMINHO_OFERTAS, 'r', encoding='utf-8') as f:
        ofertas = json.load(f)

    if not ofertas:
        print("Nenhuma oferta para enviar.")
        return

    print(f"Enviando {len(ofertas)} oferta(s)...")
    for oferta in ofertas:
        msg = f"🔥 <b>OFERTA ENCONTRADA!</b> 🔥\n\n" \
              f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n" \
              f"📦 <b>{oferta['nome']}</b>\n" \
              f"💰 Preço: R$ {oferta['preco']}\n" \
              f"🔗 <a href='{oferta['link']}'>COMPRAR AGORA</a>"
        
        bot.send_message(chat_id_destino, msg, parse_mode='HTML')
        time.sleep(1) # Evita spam rápido demais

if __name__ == "__main__":
    enviar_ofertas() # Tenta enviar as ofertas assim que o script roda
    bot.infinity_polling() # Inicia o bot e mantém ele rodando para receber mensagens.
