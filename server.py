import socket
import multiprocessing
import mysql.connector
from setup import setupDB

setupdb = setupDB()

HOST = '192.168.178.28'
PORT = 9092
server = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST,  PORT))
server.listen(5)

def add(user_id, nickname):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    #password="password",
    database="ChatBox"
    )
    mycursor = db.cursor()
    sql = "INSERT INTO users (user_id, nickname) values (%s, %s)"
    values = (user_id, nickname)
    mycursor.execute(sql, values)
    db.commit()

def research(user_id=None, nickname=None):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    #password="password",
    database="ChatBox"
    )
    sql = "SELECT * FROM users WHERE user_id = %s"
    value = (str(user_id),)
    mycursor = db.cursor()
    mycursor.execute(sql, value)
    result = mycursor.fetchone()
    #il primo dato del return stabilisce se l'utente esiste mentre il secondo se il nickname esiste
    #print(user_id, nickname)
    #print('result', result)
    if nickname == None:
        #solo utente inserito
        if result:
            #dato presente nel database
            #l'utente già è registrato
            return True, False
        else:
            #urente non presente nel database
            return False, False
    else:
        #se il nickname è stato inserito
        if result:
            #dato presente nel database
            #l'utente già è registrato
            return True, False
        else:
            sql = "SELECT * FROM users WHERE nickname = %s"
            value = (str(nickname),)
            mycursor.execute(sql, value)
            result = mycursor.fetchone()
            #print('resultnick', result)
            if result:
                return False, True
                #il nickname già esiste
            else:
                #l'utente e il nickname non esistono
                return False, False 


def connection():
    def risposta(messageris, queue):

        #   ---   registration ---

        if messageris[1] == 0:
            print('entrato login')
            print(messageris[0], messageris[1], messageris[2])
            user, nick = research(user_id=messageris[0], nickname=messageris[2])
            if user == False and nick == False:
                #se i dati inseriti non sono già presenti nel database
                add(str(messageris[0]), str(messageris[2]))
                print('registrazione avvenuta, ciao ', messageris[2])
                client.send(f"Your registration has been successful".encode('utf-8'))
            elif user == False and nick == True:
                #il nickname già esiste
                client.send(f"Your nickname is already used".encode('utf-8'))
            elif user == True:
                #l'utente già è registrato
                client.send(f"The user already exists".encode('utf-8'))


        #   ---   login   ---

        if messageris[1] == 1:
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            #password="password",
            database="ChatBox"
            )
            mycursor = db.cursor()
            #cerca la lista degli amici all'interno del database
            sql = "SELECT friend_list FROM users WHERE user_id = %s"
            value = (messageris[0],)
            mycursor.execute(sql, value)
            friend_list = mycursor.fetchone()
            print('friend_list', friend_list,type(friend_list))

            user, nick = research(user_id=messageris[0])
            if user == True:
                client.send((f"(True, 'Login was successful', " + str(friend_list) + f")").encode('utf-8'))
                information.append('signed')
                print('login avvenuto')
            else:
                client.send(f"(False, 'User not found')".encode('utf-8'))
                print('login rifiutato')


        #   ---   accept friend requests   ---

        if messageris[1] == 3:
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            #password="password",
            database="ChatBox"
            )
            mycursor = db.cursor()

            flag_control = True

            if messageris[3] == 'accepted':
                print('la richiesta di amicizia è stata accettata')
                #controllo che gli utenti esistono
                sql = "SELECT * FROM users WHERE nickname = %s"
                value = (messageris[2],)
                mycursor.execute(sql, value)
                row = mycursor.fetchone()

                if not row:
                    #se il l'utente del nickname NON esiste
                    print('nickname NON esiste')
                    flag_control = False
                else:
                    id_friend = row[1]

                sql = "SELECT * FROM users WHERE user_id = %s"
                value = (messageris[0],)
                mycursor.execute(sql, value)
                row = mycursor.fetchone()

                mittente_nickname = ''

                if not row:
                    #se il mittente NON esiste
                    print('mittente NON esiste')
                    flag_control = False
                else:
                    mittente_nickname = row[2]

                if flag_control:
                    #entrambi gli uenti esistono
                    sql = 'SELECT friend_list FROM users WHERE user_id = %s'
                    value = (messageris[0],)
                    mycursor.execute(sql, value)
                    friend_list = mycursor.fetchone()

                    print('friend_list[0]', friend_list[0])

                    if friend_list[0] != None:
                        #se la lista di amicizie non è vuota
                        #print('la lista di amicizie non è vuota')
                        #print('friend_list, ', friend_list)
                        friend_list = eval(friend_list[0])
                        
                        if not messageris[2] in friend_list:
                            friend_list.append(messageris[2])

                        sql = "UPDATE users SET friend_list = %s WHERE user_id = %s"
                        value = (str(friend_list), messageris[0])
                        mycursor.execute(sql, value)
                        db.commit()

                    else:
                        #se la lista di amici è vuota
                        #print('la lista di amici e vuota')
                        sql = "UPDATE users SET friend_list = %s WHERE user_id = %s"
                        value = (str([messageris[2]]), messageris[0])
                        friend_list = [messageris[2]]
                        mycursor.execute(sql, value)
                        db.commit()
                    
                    client.send(str((2, friend_list)).encode())

                    # - aggiorniamo il database del secondo utente - 


                    sql = 'SELECT friend_list FROM users WHERE nickname = %s'
                    value = (messageris[2],)
                    mycursor.execute(sql, value)
                    friend_list = mycursor.fetchone()

                    print('friend_list', friend_list)

                    if friend_list[0] != None:
                        #se la lista di amicizie non è vuota
                        #print('la lista di amicizie non è vuota')
                        print('friend_list, ', friend_list)
                        friend_list = eval(friend_list[0])
                        
                        if not mittente_nickname in friend_list:
                            friend_list.append(mittente_nickname)

                        sql = "UPDATE users SET friend_list = %s WHERE nickname = %s"
                        value = (str(friend_list), messageris[2])
                        mycursor.execute(sql, value)
                        db.commit()

                    else:
                        #se la lista di amici è vuota
                        #print('la lista di amici e vuota')
                        sql = "UPDATE users SET friend_list = %s WHERE nickname = %s"
                        value = (str([mittente_nickname]), messageris[2])
                        mycursor.execute(sql, value)
                        friend_list = str([mittente_nickname])
                        db.commit()

                    #ritrasmettiamo la lista degli amici

                    queue.put((True, id_friend, ('resend', friend_list)))
   

        #   ---   friend request   ---

        if messageris[1] == 4:
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            #password="password",
            database="ChatBox"
            )
            mycursor = db.cursor()
            #cerca il code_id dell'utente nuovo
            sql = "SELECT * FROM users WHERE nickname = %s"
            value = (str(messageris[2]),)
            mycursor.execute(sql, value)
            row = mycursor.fetchone()

            #cerca il nickname dell'utente attuale
            sql = "SELECT nickname FROM users WHERE user_id = %s"
            value = (str(messageris[0]),)
            mycursor = db.cursor()
            mycursor.execute(sql, value)
            mynickname = mycursor.fetchone()

            print(row, messageris[2])

            if row:
                id_friend = row[1]
                print("L'utente " + str(row[2]) + ' esiste!', id_friend)
                #print(client)
                client.send(str("Request successfully sent to the user: " + str(messageris[2])).encode())
                online_user = []
                queue.put((True, id_friend, ('friend_request', messageris[0])))
            else:
                print("L'utente " + messageris[2] + ' NON esiste!')
                client.send(f"The user entered does not exist".encode('utf-8'))

        #   ---   message   ---

        if messageris[1] == 5:
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            #password="password",
            database="ChatBox"
            )

            #ricavo il nickname del mittente
            sql = "SELECT nickname FROM users WHERE user_id = %s"
            value = (str(messageris[0]),)
            mycursor = db.cursor()
            mycursor.execute(sql, value)
            nickname = mycursor.fetchone()

            #ricavo lo user_id del destinatario
            sql = "SELECT user_id FROM users WHERE nickname = %s"
            value = (str(messageris[2]),)
            mycursor = db.cursor()
            mycursor.execute(sql, value)
            id_friend = mycursor.fetchone()

            #struttura messaggio:
            #(personal_id, 5, nickname_destinatario, testo)
            
            queue.put((True, id_friend[0], ('message', nickname[0], messageris[3])))

    user_id = []
    def listen_messages(queue, information):
        while True:
            print('ascolto nuovi messaggi in background...')
            message = client.recv(1024)
            message = message.decode()
            if message != '':
                print('nuovi messaggi:', message)
                message = eval(message)
                user_id = message[0]
                information.append(('user_id', user_id))
                risposta(message, queue)
            else:
                #il messaggio è vuoto e quindi la connessione è stata interrotta
                print('connessione interrotta')
                break   

    #setup
    manager = multiprocessing.Manager()
    information = manager.list()
    listen = multiprocessing.Process(target=listen_messages, args=(queue, information))
    print('sto ascoltando...')
    client,  address = server.accept()
    queue.put((True, 'main', 'new_connection'))
    listen.start()
    print('nuova connessione')
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    #password="password",
    database="ChatBox"
    )
    signed = False
    while True: 
        if not listen.is_alive():
            #il processo listen è terminato e ciò significa che la connessione è stata interrotta
            queue.put((True, 'main', 'connection terminated'))
            break
        
        if len(information) != 0:
            #ci sono messaggi
            inf = information[0]
            print(information)
            if inf[0] == 'user_id':
                #il messaggio contiene l'user id della sessione
                user_id = inf[1]
            if inf == 'signed':
                signed = True
            information.remove(inf)

        if signed:
            if not queue.empty():
                #se la coda non è vuota
                messaggio_coda = queue.get()
                #print('messaggio_coda', messaggio_coda, type(messaggio_coda))
                if messaggio_coda[0] == False:
                    #il messaggio è di un thread privato
                    queue.put(messaggio_coda)
                else:
                    #il messaggio è pubblico
                    print('my personal id', user_id, 'messaggio coda', messaggio_coda)
                    if messaggio_coda[1] == user_id:
                        #il messaggio privato è per il nostro thread
                        print('il messaggio è per il thread corrente', messaggio_coda)

                        #   ---   friend request   ---

                        if messaggio_coda[2][0] == 'friend_request':
                            #il messaggio è una richiesta di amicizia
                            print('richiesta amicizia ricevuta')
                            #friend_request(messaggio_coda[2][1])

                            # - mando richiesta amicizia - 

                            id = messaggio_coda[2][1]
                            sql = "SELECT * FROM users WHERE user_id = %s"
                            value = (str(id),)
                            mycursor = db.cursor()
                            mycursor.execute(sql, value)
                            result = mycursor.fetchone()
                            print('result: ', result, type(result))
                            nickname = result[2]
                            if listen.is_alive():
                                listen.terminate()
                            client.send(str((4, nickname)).encode())
                            listen = multiprocessing.Process(target=listen_messages, args=(queue, information))
                            listen.start()
                        
                        #   ---   message   ---   

                        if messaggio_coda[2][0] == 'message':

                            print('messaggio ricevuto')

                            #struttura messaggio coda
                            #(flag, id_friend, ('message', nickname_mittente, testo))
                            if listen.is_alive():
                                listen.terminate()
                            client.send(str((5, messaggio_coda[2][1], messaggio_coda[2][2])).encode())
                            listen = multiprocessing.Process(target=listen_messages, args=(queue, information))
                            listen.start()

                        #   ---   resend friend list   ---   

                        if messaggio_coda[2][0] == 'resend':
                            if listen.is_alive():
                                listen.terminate()
                            client.send(str((2, messaggio_coda[2][1])).encode())
                            listen = multiprocessing.Process(target=listen_messages, args=(queue, information))
                            listen.start()


                    else:
                        queue.put(messaggio_coda)

queue = multiprocessing.Queue()
lista_processi = []
lista_processi.append(multiprocessing.Process(target=connection))
lista_processi[0].start()

#loop del main
while True:
    if not queue.empty():
        #se la coda non è vuota
        messaggio_coda = queue.get()
        if messaggio_coda[0] == True:
            #il messaggio è pubblico
            if messaggio_coda[1] == 'main':
                #il messaggio è per il flusso princilape
                print('il messaggio è per il flusso principale', messaggio_coda)
                if messaggio_coda[2] == 'new_connection':
                    #un processo si è collegato
                    
                    
                    #crea u nuovo thread di ascolto e lo avvia
                    lista_processi.append(multiprocessing.Process(target=connection))
                    lista_processi[len(lista_processi)-1].start()
                    print('nuovo processo...')
            else:
                queue.put(messaggio_coda)
        else:
            #il messaggio è privato
            queue.put(messaggio_coda)

    for connessione in lista_processi:
        #verefica lo stato di tutti i processi
        if not connessione.is_alive():
            lista_processi.remove(connessione)
            print('un processo eliminato')