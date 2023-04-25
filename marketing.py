#TODO Rodar a cada 1h procurando por membros com a tag novo, entao enviar a mensagem de boas vindas e a do meu instagram, entao remover a tag de membro novo
from twilio.rest import Client
import ibm_db
import ibm_db_dbi

# KEYS AND TOKENS, HACKERS PLEASE DON'T STEAL MY STUFF
account_sid = 'ACb6f8299c4f7f5346cb82156b9757b0d9'
auth_token = 'ba290548eaf75db8e618d4c48dae3103'
dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "BLUDB"
dsn_hostname = "9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud"            # e.g.: "dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net"
dsn_port = "32459"
dsn_protocol = "TCPIP"
dsn_uid = "mhp73098"
dsn_pwd = "3L2bV4fA5aIrWk0Q"
dsn_security = "SSL"


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

new_user_numbers = get_new_user_numbers()
client = Client(account_sid, auth_token)

for user in new_user_numbers:
    welcome_msg = f"Bem vindo {user['name']}!\nVocê passará a receber o cardápio da UEFS diariamente."
    message = client.messages.create(
          from_='whatsapp:+13138008608',
          to=f'whatsapp:+{user["number"]}',
          body=welcome_msg
    )
    message = client.messages.create(
          from_='whatsapp:+13138008608',
          to=f'whatsapp:+{user["number"]}',
          body=warning_msg
    )

    update_user_stats(user["number"])

print(f"{len(new_user_numbers)} novos usuarios.")