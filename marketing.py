#TODO Rodar a cada 1h procurando por membros com a tag novo, entao enviar a mensagem de boas vindas e a do meu instagram, entao remover a tag de membro novo
from twilio.rest import Client
import ibm_db
import ibm_db_dbi
import json
import time

# KEYS AND TOKENS, HACKERS PLEASE DON'T STEAL MY STUFF
with open('client_secret.json') as f:
    data = json.load(f)
    db_data = data['db']

    dsn_driver = db_data['dsn_driver']
    dsn_database = db_data['dsn_database']
    dsn_hostname = db_data['dsn_hostname']
    dsn_port = db_data['dsn_port']
    dsn_protocol = db_data['dsn_protocol']
    dsn_uid = db_data['dsn_uid']
    dsn_pwd = db_data['dsn_pwd']
    dsn_security = db_data['dsn_security']

    email_data = data['email']
    sender_email = email_data['login']
    password_email = email_data['password']
    receiver_email = email_data['receiver_email']

    sql_names = data['sql_names'] # no sql injection here
    project_code_name = sql_names['project_code_name']
    breakfast_table = sql_names['breakfast']
    lunch_table = sql_names['lunch']
    dinner_table = sql_names['dinner']
    users_table = sql_names['users']
    tables_nickname = sql_names['tables_nickname']

    api_data = data['api']
    account_sid = api_data['account_sid']
    auth_token = api_data['auth_token']


# ====================== PEGA A LISTA DE USUARIOS ======================
dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security)
try:
    conn = ibm_db.connect(dsn, "", "")
    print ("Connected to database: ", dsn_database, "as user: ", dsn_uid, "on host: ", dsn_hostname)
except:
    send_email_to_admin('erro', information={"where":"Conexão ao banco de dados", "error_log":ibm_db.conn_errormsg()})


def get_new_user_numbers():
    query = "SELECT name, number FROM CRUEFS_USERS WHERE NEW_USER = 1"
    stmt  = ibm_db.exec_immediate(conn, query)
    resultado = []
    row = ibm_db.fetch_both(stmt)
    while row:
        resultado.append({'name': row[0], 'number': row[1]})
        row = ibm_db.fetch_both(stmt)
    return resultado


def get_users_numbers():
    query = f"SELECT number FROM {users_table}"
    stmt  = ibm_db.exec_immediate(conn, query)
    resultado = []
    row = ibm_db.fetch_both(stmt)
    while row:
        resultado.append(row[0])
        row = ibm_db.fetch_both(stmt)
    return resultado


def update_user_stats(user_number):
    query = f"""
            UPDATE CRUEFS_USERS
            SET NEW_USER = FALSE
            WHERE NUMBER = '{user_number}'
            """
    try:
        ibm_db.exec_immediate(conn, query)
    except:
        pass

warning_msg = "Este projeto é independente e não possui vínculo oficial com a UEFS. É um projeto de aluno para aluno. Para mais informações, visite a página do projeto em meu site e siga-me no Instagram 😉."

aviso_restricao = "Peço desculpas pela inatividade do nosso bot. Descobri que o envio de mensagens em massa no WhatsApp é limitado pelas políticas da plataforma e, devido ao grande número de usuários, o bot ficou restrito. Mas, se você me enviar uma mensagem primeiro, posso responder normalmente, enquanto eu trabalho em uma solução para voltar a ser automático.\n\nPara solicitar o cardápio, basta enviar *cardápio de hoje* a qualquer momento. E para receber o cardápio da refeição atual, tente enviar *cardápio de agora*. _Esta segunda opção pode, ou não, já estar disponível, então por favor, tente para verificar._\n\nAgradeço pela sua compreensão e colaboração."

new_user_numbers = get_new_user_numbers()
client = Client(account_sid, auth_token)

user_numbers = get_users_numbers()

errors = 0
sucess = 0

for number in user_numbers:
    message = client.messages.create(
          from_=f'whatsapp:+13138008608',
          to=f'whatsapp:+{number}',
          body=aviso_restricao
    )
    time.sleep(0.1)
    if str(message.status).lower() in ['undelivered', 'failed', 'cancelled', 'rejected', 'blocked', 'invalid']:
        errors += 1
    else:
        sucess += 1
print(f"Dos {len(user_numbers)} usuarios, foram enviados {sucess} mensagens com sucesso e {errors} falharam!")


# message = client.messages.create(
#           from_='whatsapp:+13138008608',
#           to=f'whatsapp:+557592709130',
#           body=aviso_restricao
#     )
