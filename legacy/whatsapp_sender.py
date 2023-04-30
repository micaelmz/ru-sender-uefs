from bs4 import BeautifulSoup
import requests
import datetime
from twilio.rest import Client
import ibm_db
import pandas as pd
import ibm_db_dbi
import json
import time


# ====================== Carregando variaveis ======================
datetime_now = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
weekday = datetime_now.weekday()
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

    sql_names = data['sql_names'] # no sql injection here
    breakfast_table = sql_names['breakfast']
    lunch_table = sql_names['lunch']
    dinner_table = sql_names['dinner']
    users_table = sql_names['users']

day_names = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']
day_name_today = day_names[weekday]


def is_weekend():
    return weekday >= 5


def menu_updated_yet():
    df = pd.read_csv('last_update.csv')
    if len(df) == 0:
        df.loc[0, 'filename'] = 'placeholder'
        df.loc[0, 'datetime'] = "01-01-1990 00:00"
        df.to_csv('last_update.csv', index=False)
        return False
    last_updated_date_str = df['datetime'][0]
    # check if the "datetime" in the format strftime("%d-%m-%Y %H:%M") is the weekyear as same as today
    last_updated_date = datetime.datetime.strptime(last_updated_date_str, "%d-%m-%Y %H:%M")
    last_upated_week = last_updated_date.strftime("%U")
    today_week = datetime_now.strftime("%U")
    if last_upated_week == today_week:
        return True
    else:
        return False

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


def get_user_numbers():
    if is_weekend():
        query = f"SELECT number FROM {users_table} WHERE ON_WEEKENDS = TRUE"
    else:
        query = f"SELECT number FROM {users_table}"
    stmt  = ibm_db.exec_immediate(conn, query)
    resultado = []
    row = ibm_db.fetch_both(stmt)
    while row:
        resultado.append(row[0])
        row = ibm_db.fetch_both(stmt)
    return resultado

def get_tables(table_name):
    pconn = ibm_db_dbi.Connection(conn)
    sql = f"SELECT * FROM {table_name}"
    df = pd.read_sql(sql, pconn)
    df = df.set_index('NOME')
    return df


user_numbers = get_user_numbers()
df_breakfast = get_tables(breakfast_table)
df_lunch = get_tables(lunch_table)
df_dinner = get_tables(dinner_table)

# if menu_updated_yet():
#     msg_day = day_name_today
#     msg_date = datetime_now.strftime("%d/%m")
# else:
#     msg_day = day_name_today+" DA SEMANA PASSADA"
#     msg_date = "propaae não atualizou"

msg_day = day_name_today
msg_date = datetime_now.strftime("%d/%m")

#old_menu_msg = f"""*📜 Cardápio do RU {day_name_today} ({datetime_now.strftime("%d/%m")}).*\n\n*🕗 Café da manhã*\n☕ _Bebida:_ {df_breakfast[day_name_today]['BEBIDA']}\n🍖 _Proteína:_ {df_breakfast[day_name_today]['PROTEINA']}\n🥔 _Raíz ou farináceo:_ {df_breakfast[day_name_today]['RAIZ']}\n🍎 _Fruta:_ {df_breakfast[day_name_today]['FRUTA']}\n🥦 _Ovolactovegetariano:_ {df_breakfast[day_name_today]['VEGETARIANO']}\n\n*🕛 Almoço*\n🍽 _Acompanhamento 1:_ {df_lunch[day_name_today]['ACOMPANHAMENTO_1']}\n🥣 _Acompanhamento 2:_ {df_lunch[day_name_today]['ACOMPANHAMENTO_2']}\n🍜 _Guarnição:_ {df_lunch[day_name_today]['GUARNIÇÃO']}\n🥗 _Salada Cozida:_ {df_lunch[day_name_today]['SALADA_COZIDA']}\n🥒 _Salada Crua:_ {df_lunch[day_name_today]['SALADA_CRUA']}\n🍖 _Proteína:_ {df_lunch[day_name_today]['PROTEINA']}\n🥓 _Opção:_ {df_lunch[day_name_today]['OPÇÃO']}\n🍎 _Fruta:_ {df_lunch[day_name_today]['FRUTA']}\n🧃 _Suco:_ {df_lunch[day_name_today]['SUCO']}\n🥦 _Ovolactovegetariano:_ {df_lunch[day_name_today]['VEGETARIANO']}\n\n*🕘 Janta*\n☕ _Bebida:_ {df_dinner[day_name_today]['BEBIDA']}\n🍖 _Proteína:_ {df_dinner[day_name_today]['PROTEINA']}\n🥔 _Raíz ou farináceo:_ {df_dinner[day_name_today]['RAIZ']}\n🍵 _Sopa:_ {df_dinner[day_name_today]['SOPA']}\n🥦 _Ovolactovegetariano:_ {df_dinner[day_name_today]['PROTEINA_VEGETARIANO']+" + "+df_dinner[day_name_today]['VEGETARIANO']}"""
menu_msg = f"""*📜 Cardápio do RU {msg_day} ({msg_date}).*\n\n*🕗 Café da manhã*\n☕ _Bebida:_ {df_breakfast[day_name_today]['BEBIDA'].title()}\n🍖 _Proteína:_ {df_breakfast[day_name_today]['PROTEINA'].title()}\n🥔 _Raíz ou farináceo:_ {df_breakfast[day_name_today]['RAIZ'].title()}\n🍎 _Fruta:_ {df_breakfast[day_name_today]['FRUTA'].title()}\n🥦 _Ovolactovegetariano:_ {df_breakfast[day_name_today]['VEGETARIANO'].title()}\n\n*🕛 Almoço*\n🍽 _Acompanhamento 1:_ {df_lunch[day_name_today]['ACOMPANHAMENTO_1'].title()}\n🥣 _Acompanhamento 2:_ {df_lunch[day_name_today]['ACOMPANHAMENTO_2'].title()}\n🍜 _Guarnição:_ {df_lunch[day_name_today]['GUARNIÇÃO'].title()}\n🥗 _Salada Cozida:_ {df_lunch[day_name_today]['SALADA_COZIDA'].title()}\n🥒 _Salada Crua:_ {df_lunch[day_name_today]['SALADA_CRUA'].title()}\n🍖 _Proteína:_ {df_lunch[day_name_today]['PROTEINA'].title()}\n🥓 _Opção:_ {df_lunch[day_name_today]['OPÇÃO'].title()}\n🍎 _Fruta:_ {df_lunch[day_name_today]['FRUTA'].title()}\n🧃 _Suco:_ {df_lunch[day_name_today]['SUCO'].title()}\n🥦 _Ovolactovegetariano:_ {df_lunch[day_name_today]['VEGETARIANO'].title()}\n\n*🕘 Janta*\n☕ _Bebida:_ {df_dinner[day_name_today]['BEBIDA'].title()}\n🍖 _Proteína:_ {df_dinner[day_name_today]['PROTEINA'].title()}\n🥔 _Raíz ou farináceo:_ {df_dinner[day_name_today]['RAIZ'].title()}\n🍵 _Sopa:_ {df_dinner[day_name_today]['SOPA'].title()}\n🥦 _Ovolactovegetariano:_ {df_dinner[day_name_today]['PROTEINA_VEGETARIANO'].title()+" + "+df_dinner[day_name_today]['VEGETARIANO'].title()}"""



client = Client(account_sid, auth_token)

errors = 0
sucess = 0

for number in user_numbers:
    message = client.messages.create(
          from_=f'whatsapp:+{bot_sender_number}',
          to=f'whatsapp:+{number}',
          body=menu_msg
    )
    time.sleep(0.1)
    if str(message.status).lower() in ['undelivered', 'failed', 'cancelled', 'rejected', 'blocked', 'invalid']:
        errors += 1
    else:
        sucess += 1
print(f"Dos {len(user_numbers)} usuarios, foram enviados {sucess} mensagens com sucesso e {errors} falharam!")


# message = client.messages.create(
#       from_=f'+{bot_sender_number}',
#       to=f'+557592709130',
#       body="Olá pessoal, "
#       )
# print(message.status)

ibm_db.close(conn)