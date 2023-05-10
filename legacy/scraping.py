from bs4 import BeautifulSoup
import requests
import pandas as pd
import ibm_db
import tabula
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
import json


today_date = datetime.datetime.utcnow() - datetime.timedelta(hours=3)

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


def send_email_to_admin(kind, information=None):
    # Open the HTML file and read its content
    with open(f'emails/{kind}.html', 'r') as f:
        html = f.read()
    if kind == "erro":
        html = html.replace("[DATA_E_HORA]", today_date.strftime("%d/%m/%Y %H:%M:%S"))
        html = html.replace("[LOCAL_ERRO]", information['where'])
        html = html.replace("[MENSAGEM_ERRO]", information['error_log'])
    elif kind == "report":
        pass
        # TODO
    subject = f'Relatório de {kind.capitalize()} - CRUEFS'
    # Create a MIME message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    # Attach the HTML content to the message
    msg.attach(MIMEText(html, 'html'))
    # Connect to SMTP server and send email
    with smtplib.SMTP('smtp.zoho.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, password_email)
        smtp.sendmail(sender_email, receiver_email, msg.as_string())
        print(f'{kind.capitalize()} email sent successfully.')


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
    today_week = today_date.strftime("%U")
    if last_upated_week == today_week:
        return True
    else:
        return False


if today_date.weekday() != 0 and menu_updated_yet():
    print("O menu já foi atualizado essa semana!")
    exit(0)

# ====================== WEB SCRAPING DO PDF ======================
endpoint = "http://www.propaae.uefs.br/modules/conteudo/conteudo.php?conteudo=15"
response = requests.get(endpoint)
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# Busca a tag 'img' pela atributo 'alt' e navega para o elemento pai 'a' usando o método .parent
img_tag = soup.find('img', {'alt': 'Cardápio'})
link_tag = img_tag.parent
link = link_tag['href']

# Faz a solicitação HTTP para a URL e salva o conteúdo da resposta em um arquivo local
response = requests.get(link)
with open('cardapio.pdf', 'wb') as f:
    f.write(response.content)

menu_filename = link.split('/')[-1].replace('.pdf', '')
df_last_update = pd.read_csv("last_update.csv")

if df_last_update['filename'][0] == menu_filename:
    print("Menu ainda não atualizado pela propaae.")
    exit()

# ====================== EXTRACÃO DE DADOS DO PDF ======================

# Lê a tabela na primeira página do arquivo PDF usando a área definida acima
df = tabula.read_pdf("cardapio.pdf", pages=1, output_format='dataframe')[0]

df = df.applymap(lambda x: str(x).upper())
column_name = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']

def find_missing_item(uncomplete_row):
    mask = df.apply(lambda row: all(item in row.values for item in uncomplete_row), axis=1)
    selected_rows = df[mask]
    original_row = selected_rows.values.tolist()[0]
    missing_item_index = original_row.index(uncomplete_row[0])
    missed_item = original_row[missing_item_index-1]
    return missed_item

# ------------------------ CAFÉ DA MANHÃ ------------------------
# Encontra onde tem "BEBIDA" no DataFrame (começo do cardapio)
start_row, start_column = np.where(df == 'BEBIDA')
# pega somente a PRIMEIRA OCORRENCIA, pq tem bebida em outros cantos tbm
start_column = start_column[0]+1
start_row = start_row[0]

end_column = start_column+len(column_name)
end_row = start_row+5

# Começa dropando as colunas irrelevantes que tem no pdf, no caso a primeira coluna e as 2 primeiras linhas
df_breakfast = df.iloc[start_row:end_row+1]
df_breakfast = df_breakfast.iloc[:, start_column:end_column]
df_breakfast.columns = column_name

df_breakfast = df_breakfast.reset_index(drop=True)
df_breakfast = df_breakfast.applymap(lambda x: x.replace('\r', ' '))
# customizando o breakfast, arrumando alguns nomes por padronização e colocando a coluna nome como index
df_breakfast.index = ['BEBIDA', 'PÃO', 'PROTEINA', 'RAIZ', 'FRUTA', 'VEGETARIANO']

mask = df_breakfast['DOMINGO'] == 'NAN'
rows_with_nan = df_breakfast[mask]
df_breakfast.loc[mask] = df_breakfast.loc[mask].shift(periods=1, axis='columns', fill_value='NAN')

uncomplete_rows = df_breakfast[mask].values
where_are_missing_itens = df_breakfast[mask].index
found_values = []
for uncomplete_row in uncomplete_rows:
    found_values.append(find_missing_item(uncomplete_row[1:]))
for index, item in enumerate(where_are_missing_itens):
    df_breakfast["SEGUNDA"][item] = found_values[index]

# ------------------------ ALMOÇO ------------------------
# Encontra onde tem "BEBIDA" no DataFrame (começo do cardapio)
mask = df.applymap(lambda x: isinstance(x, str) and 'ACOMPANHAME' in x.upper())
start_row, start_column = np.where(mask)
# pega somente a PRIMEIRA OCORRENCIA, pq tem bebida em outros cantos tbm
start_column = start_column[0]+1
start_row = start_row[0]

end_column = start_column+len(column_name)
end_row = start_row+9

# Começa dropando as colunas irrelevantes que tem no pdf, no caso a primeira coluna e as 2 primeiras linhas
df_lunch = df.iloc[start_row:end_row+1]
df_lunch = df_lunch.iloc[:, start_column:end_column]
df_lunch.columns = column_name

df_lunch = df_lunch.reset_index(drop=True)
df_lunch = df_lunch.applymap(lambda x: x.replace('\r', ' '))
# customizando o breakfast, arrumando alguns nomes por padronização e colocando a coluna nome como index
df_lunch.index = ['ACOMPANHAMENTO_1', 'ACOMPANHAMENTO_2', 'GUARNIÇÃO', 'SALADA_COZIDA', 'SALADA_CRUA',
    'PROTEINA', 'OPÇÃO', 'FRUTA', 'VEGETARIANO', 'SUCO']

mask = df_lunch['DOMINGO'] == 'NAN'
rows_with_nan = df_lunch[mask]
df_lunch.loc[mask] = df_lunch.loc[mask].shift(periods=1, axis='columns', fill_value='NAN')

uncomplete_rows = df_lunch[mask].values
where_are_missing_itens = df_lunch[mask].index
found_values = []
for uncomplete_row in uncomplete_rows:
    found_values.append(find_missing_item(uncomplete_row[1:]))
for index, item in enumerate(where_are_missing_itens):
    df_lunch["SEGUNDA"][item] = found_values[index]

# ------------------------ JANTAR ------------------------
# Encontra onde tem "BEBIDA" no DataFrame (começo do cardapio)
start_row, start_column = np.where(df == 'SOPA')
# pega somente a PRIMEIRA OCORRENCIA, pq tem bebida em outros cantos tbm
start_column = start_column[0]+1
start_row = start_row[0]-4

end_column = start_column+len(column_name)
end_row = start_row+6

# Começa dropando as colunas irrelevantes que tem no pdf, no caso a primeira coluna e as 2 primeiras linhas
df_dinner = df.iloc[start_row:end_row+1]
df_dinner = df_dinner.iloc[:, start_column:end_column]

df_dinner.columns = column_name

df_dinner = df_dinner.reset_index(drop=True)
df_dinner = df_dinner.applymap(lambda x: x.replace('\r', ' '))
# customizando o breakfast, arrumando alguns nomes por padronização e colocando a coluna nome como index
df_dinner.index = ['PÃO', 'BEBIDA', 'RAIZ', 'PROTEINA', 'SOPA', 'VEGETARIANO', 'PROTEINA_VEGETARIANO']

mask = df_dinner['DOMINGO'] == 'NAN'
rows_with_nan = df_dinner[mask]
df_dinner.loc[mask] = df_dinner.loc[mask].shift(periods=1, axis='columns', fill_value='NAN')

uncomplete_rows = df_dinner[mask].values
where_are_missing_itens = df_dinner[mask].index
found_values = []
for uncomplete_row in uncomplete_rows:
    found_values.append(find_missing_item(uncomplete_row[1:]))
for index, item in enumerate(where_are_missing_itens):
    df_dinner["SEGUNDA"][item] = found_values[index]

# ====================== ENVIO PARA O BANCO DE DADOS ======================
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

def insert_on_table(meal, foods):
    days = ['NOME', 'SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']
    query = f"""
    INSERT INTO {project_code_name}_{meal.upper()}_{tables_nickname}
    ({', '.join(days)})
    VALUES ({', '.join(map(lambda f: f"'{f}'", foods))})
    """
    ibm_db.exec_immediate(conn, query)

def reset_tables():
    query = f"TRUNCATE {breakfast_table} IMMEDIATE;"
    ibm_db.exec_immediate(conn, query)
    query = f"TRUNCATE {lunch_table} IMMEDIATE;"
    ibm_db.exec_immediate(conn, query)
    query = f"TRUNCATE {dinner_table} IMMEDIATE;"
    ibm_db.exec_immediate(conn, query)
    print("Clear!")


reset_tables()

# breakfast
for i, row in df_breakfast.iterrows():
    row_list = row.tolist()
    row_list.insert(0, i)
    insert_on_table("breakfast", row_list)
print("breakfast updated!")

# lunch
for i, row in df_lunch.iterrows():
    row_list = row.tolist()
    row_list.insert(0, i)
    insert_on_table("lunch", row_list)
print("lunch updated!")

# dinner
for i, row in df_dinner.iterrows():
    row_list = row.tolist()
    row_list.insert(0, i)
    insert_on_table("dinner", row_list)
print("dinner updated!")
ibm_db.close(conn)

df_last_update.loc[0, 'filename'] = menu_filename
df_last_update.loc[0, 'datetime'] = today_date.strftime("%d-%m-%Y %H:%M")
df_last_update.to_csv("last_update.csv", index=False)
print("Menu atualizado.")