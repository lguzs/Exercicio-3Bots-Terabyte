import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

# definir variaveis, como o corpo do email, titulo e destinatario
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PWD = os.getenv('GMAIL_PWD')

DEST = 'luizgustavosilvamarinho71@gmail.com'
ASSUNTO = 'teste de bot do gmail'

CORPO_TEXTO = """\
E ai malandro!!!

Teste de hacker aqui, perdeu

Att,

Hacker doidão
"""

ANEXO = None
# ANEXO = r'C:\Users\Anderson\Downloads\bot_gmail\noticias.json'

# funcoes necessarias do bot
# 1. criar a msg
# 2. carregar o anexo
# 3. enviar o email

def criar_msg():
    # opcional
    msg = MIMEMultipart('alternative')

    msg['Subject'] = ASSUNTO
    msg['From'] = GMAIL_USER
    msg['To'] = DEST

    msg.attach(MIMEText(CORPO_TEXTO, 'plain', 'utf-8'))

    return msg

def carregar_anexo(msg, path):
    # abrir o arquivo em formato binario
    with open(path, 'rb') as f:
        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(f.read()) # carregar (upload)

    # criptografar o arquivo
    encoders.encode_base64(parte)
    # definir o nome do arquivo
    nome_arquivo = os.path.basename(path)
    parte.add_header(
        'Content-Disposition',
        f"attachment; filename='{nome_arquivo}'"
    )
    # anexar o arquivo junto com a msg
    msg.attach(parte)
    print(f'anexo adicionado: {nome_arquivo}')

def enviar_email(msg):
    print('Tentando se conectar no GMAIL...')
    with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
        servidor.ehlo() # handshake entre cliente e servidor
        servidor.starttls() # criptografar a comunicação
        servidor.login(GMAIL_USER, GMAIL_PWD)
        print(f'Conectado como {GMAIL_USER}')
        servidor.sendmail(
            from_addr=GMAIL_USER,
            to_addrs=DEST,
            msg=msg.as_string()
        )
    print(f'Mensagem enviada com sucesso ao {DEST}')

def main():
    if not GMAIL_USER or not GMAIL_PWD:
        print('erro de autenticação')
        return
    print('montando a mensagem...')
    msg = criar_msg()
    if ANEXO:
        carregar_anexo(msg, ANEXO)
    enviar_email(msg)

if __name__ == '__main__':
    main()

# pequenos desafios:

'''
1. tente enviar anexos como imagem e o noticias.json que 
criamos no outro bot

2. combine o scraper da aula passada onde, após raspar 3 paginas,
envie um email com o top 5 noticias em um corpo de html, com titulo e link
das noticias e o json apenas com essas 5 noticias.

3. implemente os campos CC e CCO (msg['Cc'] e msg['Bcc']) e passe todos
os endereços como uma lista no parametro to_addrs no metodo sendmail().
'''
