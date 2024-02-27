# 📲  Enviador Automático do Cardápio do Restaurante Universitário
Este é um sistema desenvolvido em Python que facilita a entrega do cardápio do RU para estudantes da UEFS. O sistema é composto por três bots que trabalham juntos para fornecer o cardápio atualizado para os usuários. Os bots realizam tarefas como: gerenciar requisições enviadas ao WhatsApp; cadastrar novos usuários; buscar, extrair, limpar e salvar no banco de dados o cardápio semanal; enviar o cardápio diariamente para os assinantes. O sistema utiliza tecnologias como a API do WhatsApp, Flask e Pandas para realizar as tarefas necessárias. Além de possuir um sistema de notificação via e-mail que envia logs de cada procedimento ou erro para o desenvolvedor.

<br>


<div align="center">
<img src="https://github.com/micaelmz/micaelmz/blob/main/images/cruefs-project-bg.png"  width="100%"/>
</div>

<br>

### Versão 1.1
```
💡 NEW! - Adicionado a solução para o caso onde o cardápio não foi atuaiizado no site da propaae.
```

#### Metas e features:
- [x] Funcionar com os mais diversos tipos de cardápios, tamanho, cores.
- [ ] Notificação de erro por email para o administrador
- [ ] Código refatorado e refeito orientado a objetos (URGENTE)

<br>

# Modulos

## Scraping

Um bot de extração de dados, que realiza scraping no [site da propaae UEFS](http://propaae.uefs.br/modules/conteudo/conteudo.php?conteudo=15) todas as segundas-feiras em busca do link do PDF do cardápio semanal, então faz download do mesmo nos arquivos do servidor, após isso, as informações são extraídas em formato DataFrame Pandas usando Tabula-py, então o DataFrame é tratado para os dados serem armazenados em um servidor SQL do IBM DB2.

## WhatsApp Sender

Um bot de envio de mensagens que diariamente busca o cardápio do dia, na tabela do cardápio da semana, no servidor SQL da aplicação. Em seguida, é feita uma consulta à tabela de usuários, organizando uma mensagem para ser enviada para todos os usuários, exceto em finais de semana, quando somente aqueles que marcaram essa opção recebem a mensagem, o envio então é realizando utilizando a API do WhatsApp.

## Marketing

Um bot que busca por novos usuários cadastrados no banco de dados, então envia uma mensagem de boas vindas e divulga meu instagram, além de definir tais usuários como não mais novo.

## Flask API

A Flask API lida com soliticações por parte da API do WhatsApp, como mensagens recebidas, realizando tarefas como o cadastro de novos usuários.

<br>

## Links úteis
[Testar o bot via WhatsApp](https://wa.me/13138008608?text=começar)
