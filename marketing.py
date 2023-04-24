from twilio.rest import Client
import ibm_db
import ibm_db_dbi
import json

bot_sender_number = "13138008608"

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

    api_data = data['api']
    account_sid = api_data['account_sid']
    auth_token = api_data['auth_token']

    sql_names = db_data['sql_names'] # no sql injection here
    breakfast_table = sql_names['breakfast']
    lunch_table = sql_names['lunch']
    dinner_table = sql_names['dinner']
    users_table = sql_names['users']

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
    query = f"SELECT name, number FROM {users_table} WHERE NEW_USER = TRUE"
    stmt  = ibm_db.exec_immediate(conn, query)
    resultado = []
    row = ibm_db.fetch_both(stmt)
    while row:
        resultado.append({'name': row[0], 'number': row[1]})
        row = ibm_db.fetch_both(stmt)
    return resultado

def update_user_stats(user_number):
    query = f"""
            UPDATE {users_table}
            SET NEW_USER = FALSE
            WHERE NUMBER = '{user_number}'
            """
    try:
        ibm_db.exec_immediate(conn, query)
    except:
        pass

warning_msg = "Este projeto é independente e não possui vínculo oficial com a UEFS. É um projeto de aluno para aluno. Para mais informações, visite a página do projeto em meu site e siga-me no Instagram 😉."

new_user_numbers = get_new_user_numbers()
client = Client(account_sid, auth_token)

for user in new_user_numbers:
    welcome_msg = f"Bem vindo {user['name']}!\nVocê passará a receber o cardápio da UEFS diariamente."
    message = client.messages.create(
          from_=f'whatsapp:+{bot_sender_number}',
          to=f'whatsapp:+{user["number"]}',
          body=welcome_msg
    )
    message = client.messages.create(
          from_=f'whatsapp:+{bot_sender_number}',
          to=f'whatsapp:+{user["number"]}',
          body=warning_msg
    )

    update_user_stats(user["number"])