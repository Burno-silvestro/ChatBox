from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QThread, QPropertyAnimation
from PyQt5 import QtCore
from PyQt5 import uic, QtWidgets
import sys
import ast
import socket
import hashlib
import gi
gi.require_version('Notify', '0.7')
from gi.repository import GLib, Notify

Notify.init("ChatBox")


iniziotab = '<table cellpadding="0" cellspacing="0" border="1" ><tr><td style="background-color: black"><table cellpadding="0" cellspacing="0" border="0"><tr><td>'
iniziotableft = '<table cellpadding="0" cellspacing="0" border="1" align="right"><tr><td style="background-color: #3c063d"><table cellpadding="0" cellspacing="0" border="0"><tr><td>'
finetab = '</td></tr></table></td></tr></table>'
special_charapter = ['!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
HOST = ''
PORT = 9092
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

stopThread = False
my_personal_id = ''
friend_nickname = ''
dictChat = {}

class receive_message(QThread):
    input_received = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()

        #flag per il thread
        self._is_running = True

    def run(self):
        #   ---   "main del thread"   ---   
        print('ascolto in background')
        while True:
            message = client.recv(1024)
            message = message.decode()
            if message == '':
                try:
                    client.connect((HOST, PORT))
                    print('riconnessione effettuata...')
                except Exception as errore:
                    print('riconnessione fallita', errore)
                    
            else:
                print('nuovo messaggio:', message)
            try:
                print('messaggio::: ', message)
                message = eval(message)
                self.input_received.emit(message)

            except:
                print('Il messaggio inviato non è del formato corretto', message)
                if message == '':
                    message = QMessageBox()
                    message.setText('Connection with server lost. Please reconnect')
                    message.exec_()
                    break


class loginWIN(QMainWindow):

    def __init__(self):
        super(loginWIN, self).__init__()
        uic.loadUi("login.ui", self)
        self.show()
        #self.setFixedWidth(399)
        #self.setFixedHeight(262)
        global HOST
        self.password.setEchoMode(QLineEdit.Password)
        self.btn_login.clicked.connect(self.login)
        self.btn_create.clicked.connect(self.create)
        self.ipaddr.setText('localhost')
        self.setFixedSize(393, 246)
        HOST = self.ipaddr.text()


    def login(self):
        if len(self.username.text()) != 0 and len(self.password.text()) != 0:
            #verifica le credenziali
            flag = True
            for carattere in self.username.text():
                for special in special_charapter:
                    if carattere == special:
                        flag = False
                        break
            if flag == False:
                message = QMessageBox()
                message.setText('The username field cannot contain special characters')
                message.exec_()
            else:
                flag = True
                for carattere in self.password.text():
                    for special in special_charapter:
                        if carattere == special:
                            flag = False
                            break
                
                if flag == True:
                    message = QMessageBox()
                    message.setText('The password field must contain special characters')
                    message.exec_()
                else:
                    global my_personal_id, HOST
                    HOST = self.ipaddr.text()
                    #calcolo hash e invio al server
                    username = self.username.text()
                    password = self.password.text()
                    numid = username + password
                    id = hashlib.md5(numid.encode()).hexdigest()
                    my_personal_id = id
                    #print('my_personal_id', my_personal_id)
                    messaggio = (id, 1)                  
                    try:
                        try:
                            client.connect((HOST, PORT))
                        except:
                            pass    
                        client.send(str(messaggio).encode('utf-8'))
                        print(id, username, password)
                        renspose = client.recv(1024)  
                        print('risposta server login: ', renspose)
                        #messaggi errore
                        renspose = eval(renspose)
                        print('renspose', renspose)
                        if renspose[0] == True:
                            if self.stay_connected.isChecked():
                                with open('settings.txt', 'w') as f:
                                    f.write(str([True, my_personal_id, renspose[2][0], self.ipaddr.text()]))
                            else:
                                with open('file.txt', 'w') as f:
                                    f.write('')

                            #login effettuato
                            widget.setFixedHeight(500)
                            widget.setFixedWidth(700)
                            screen = QDesktopWidget().screenGeometry()
                            width, height = screen.width(), screen.height()
                            widget.setMaximumSize(width, height)
                            
                            widget.setCurrentIndex(widget.currentIndex()+2) 

                            print('current index: ', widget.currentIndex()) 
                            if not renspose[2][0] == None:
                                renspose = eval(renspose[2][0])
                                for chats in renspose:
                                    print('chat', chats)
                                    dictChat[chats] = ''
                                    chat.comboChat.addItem(chats)
                            chat.my_thread.start()
                            #message = QMessageBox()
                            #message.setText(str(renspose[1]))
                            #message.exec_()
                        else:
                            #login NON effettuato
                            #client.close() #chiudo il canale di connessione
                            message = QMessageBox()
                            message.setText(str(renspose[1]))
                            message.exec_()
                            #client.close()
                    except Exception as errore:
                        message = QMessageBox()
                        message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
                        message.exec_()
        else:
            message = QMessageBox()
            message.setText('Please complete the form')
            message.exec_()

    def create(self):
        global HOST
        HOST = self.ipaddr.text()
        widget.setCurrentIndex(widget.currentIndex()+1)

class createWIN(QMainWindow):

    def __init__(self):
        super(createWIN, self).__init__()
        uic.loadUi("create.ui", self)
        self.show()
        #self.setFixedWidth(399)
        #self.setFixedHeight(262)
        self.password.setEchoMode(QLineEdit.Password)
        self.btn_login.clicked.connect(self.login)
        self.btn_create.clicked.connect(self.create)

    def create(self):
        if len(self.username.text()) != 0 and len(self.password.text()) != 0 and len(self.nickname.text()) != 0:
            flag = True
            for carattere in self.username.text():
                for special in special_charapter:
                    if carattere == special:
                        flag = False
                        break
            if flag == False:
                message = QMessageBox()
                message.setText('The username field cannot contain special characters')
                message.exec_()
            else:
                flag = True
                for carattere in self.password.text():
                    for special in special_charapter:
                        if carattere == special:
                            flag = False
                            break
                
                if flag == True:
                    message = QMessageBox()
                    message.setText('The password field must contain special characters')
                    message.exec_()
                else:
                    #calcolo hash e invio al server
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    username = self.username.text()
                    password = self.password.text()
                    numid = username + password
                    id = hashlib.md5(numid.encode()).hexdigest()
                    messaggio = (id, 0, self.nickname.text())
                    try:
                        client.connect((HOST, PORT))
                        client.send(str(messaggio).encode('utf-8'))
                        print(id, username, password)
                        renspose = client.recv(1024)
                        #client.close()
                        #messaggi
                        message = QMessageBox()
                        message.setText(str(renspose.decode()))
                        message.exec_()
                        message = QMessageBox()
                        message.setText('your username and password must remain secret please')
                        message.exec_()
                    except Exception as errore:
                        message = QMessageBox()
                        message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
                        message.exec_()
        else:
            message = QMessageBox()
            message.setText('Please complete the form')
            message.exec_()

    def login(self):
        widget.setCurrentIndex(widget.currentIndex()-1)

class chatWIN(QMainWindow):

    def __init__(self):
        super(chatWIN, self).__init__()
        uic.loadUi("chat.ui", self)
        self.show()
        #print('my personal id', my_personal_id)
        self.btn_send.clicked.connect(self.send)
        self.add_friend.clicked.connect(self.friend_request)
        self.main_Text = ''
        self.comboChat.currentIndexChanged.connect(self.changeChat)
        self.message.returnPressed.connect(self.invioKey)
        self.photo_btn.clicked.connect(self.photo_side_panel)
        self.options_btn.clicked.connect(self.options_side_panel)
        self.settings_btn.clicked.connect(self.settings_side_panel)

        #creo il mio thread
        self.my_thread = receive_message()
        self.my_thread.input_received.connect(self.new_message)

    def photo_side_panel(self):
        width = self.Photo_panel.width()
        if width == 0:
            Nwidth = 350
        else:
            Nwidth = 0

        print('width', width, 'Nwidth', Nwidth)

        self.animation = QPropertyAnimation(self.Photo_panel, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(Nwidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def settings_side_panel(self):
        width = self.settings.width()
        if width == 0:
            Nwidth = 350
        else:
            Nwidth = 0

        self.animation = QPropertyAnimation(self.settings, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(Nwidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def options_side_panel(self):
        width = self.options.width()
        if width == 0:
            Nwidth = 350
        else:
            Nwidth = 0

        self.animation = QPropertyAnimation(self.options, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(Nwidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def changeChat(self):
        chats = self.comboChat.currentText()
        self.mainText.setText(dictChat[chats])
        #print(chats)

    def startThread(self):
        self.my_thread.start()

    def stopThread(self):
        self.my_thread.terminate()

    def new_message(self, message):
        #in message è contenuto il nuovo messaggio arrivato
        print('nuovo messaggio ricevuto dal thread ', message, type(message))

        #   ---   resend   ---   

        if message[0] == 2:
            if type(message[1]) != list:
                message[1] = ast.literal_eval(message[1])
                print('message[1]', message, type(message[1]))
            for chats in message[1]:
                print('chat', chats)
                if not chats in dictChat:
                    #se la chiave NON è presente
                    dictChat[chats] = ''
                    chat.comboChat.addItem(chats)

        #   ---   friend request   ---   

        if message[0] == 4:
            global friend_nickname
            friend_nickname = message[1]
            print('friend nickname', friend_nickname)
            self.my_thread.terminate()
            self.my_thread = receive_message()
            self.my_thread.input_received.connect(self.new_message)
            #vado nella pagina di request
            friend_request.text.setText(str('You have a new friend request from the user ' + friend_nickname))
            widget.setCurrentIndex(widget.currentIndex()+1)
            self.my_thread.start()

        #   ---   messaggio   ---

        if message[0] == 5:
            #struttura messaggio dal server
            #(5, nickname_mittente, testo)
            
            #seleziono l'elemento del dizionario corrispondente alla persona
            testoChat = dictChat[message[1]]
            testoChat = testoChat + '<p>' + iniziotableft + "<span style='color:white;'>" + message[2] + '</span>' + finetab + '<\p>'
            dictChat[message[1]] = testoChat
            
            #"<p>Questa è una <span style='color:red;'>parola</span> <span style='color:yellow;'>colorata</span>.</p>"
            #self.mainText.setText("<span style='color: yellow;'>Questa è la mia frase in giallo!</span>")
            if message[1] == self.comboChat.currentText():
                self.mainText.setText(dictChat[message[1]])
                #si posiziona in basso
                scrollbar = self.mainText.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

            if not app.activeWindow() and not app.activeWindow() in [login, create, chat, friend_request]:
                print('pagina selezionata')
                notification = Notify.Notification.new(
                    "ChatBox",
                    "New message from " + str(message[1])
                )
                notification.show()
                #GLib.timeout_add_seconds(5, notification.close)
                #Notify.uninit()
            else:
                print('pagina NON selezionata')


    def send(self):
        if self.message.text() != '':
            #il messaggio non è vuoto
            #print(my_personal_id)
            self.my_thread.terminate()
            self.my_thread = receive_message()
            self.my_thread.input_received.connect(self.new_message)
            try:
                #struttura messaggio:
                #(personal_id, 5, nickname_destinatario, testo)
                messaggio = (my_personal_id, 5, self.comboChat.currentText(), str(self.message.text()))
                print('messaggio inviato: ', messaggio)
                client.send(str(messaggio).encode())

                #aggiorno il testo
                testoChat = dictChat[self.comboChat.currentText()]
                testoChat = testoChat + '<p>' + iniziotab + self.message.text() + finetab + '<\p>'
                dictChat[self.comboChat.currentText()] = testoChat
                self.mainText.setText('<html>' + dictChat[self.comboChat.currentText()] + '</html>')
                self.message.setText('')

                 
                '''
                <table cellpadding="0" cellspacing="0" border="1">
                <tr>
                    <td style="background-color: black">
                    <table cellpadding="0" cellspacing="0" border="0">
                        <tr>
                        <td>
                            Il tuo testo qui
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                </table>
                '''

                #si posiziona in basso
                scrollbar = self.mainText.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                #client.close()
            except Exception as errore:
                message = QMessageBox()
                message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
                message.exec_()
            self.my_thread.start()

    def invioKey(self):
        self.send()

    def friend_request(self):
        if self.nickname.text() != 0:
            #nickname inserito
            self.my_thread.terminate()
            self.my_thread = receive_message()
            self.my_thread.input_received.connect(self.new_message)
            try:
                client.connect((HOST, PORT))
            except:
                pass
            try:               
                messaggio = str((my_personal_id, 4, self.nickname.text()))
                client.send(str(messaggio).encode('utf-8'))
                renspose = client.recv(1024)
                message = QMessageBox()
                message.setText(renspose.decode())
                message.exec_()
            except Exception as errore:
                message = QMessageBox()
                message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
                message.exec_()
            self.my_thread.start()

class friend_requestWIN(QMainWindow):

    def __init__(self):
        super(friend_requestWIN, self).__init__()
        uic.loadUi("friend_request.ui", self)
        #self.show()
        print('friend_nickname request win', friend_nickname)
        self.btn_accept.clicked.connect(self.accept)
        self.btn_refuse.clicked.connect(self.refuse)

    def showtext(self):
        testo = self.text.text()
        testo += friend_nickname
        self.text.setText(testo)
    
    def accept(self):
        print('accepted')
        try:
            messaggio = (my_personal_id, 3, friend_nickname, 'accepted')
            client.send(str(messaggio).encode())
        except Exception as errore:
            message = QMessageBox()
            message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
            message.exec_()
        widget.setCurrentIndex(widget.currentIndex()-1)

    def refuse(self):
        print('refused')
        try:
            messaggio = (my_personal_id, 3, friend_nickname, 'refused')
            client.send(str(messaggio).encode())
        except Exception as errore:
            message = QMessageBox()
            message.setText('There was a problem connecting to the Server. Please try again!' + str(errore))
            message.exec_()
        widget.setCurrentIndex(widget.currentIndex()-1)

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
login = loginWIN()
create = createWIN()
chat = chatWIN()
friend_request = friend_requestWIN()
widget.addWidget(login)
widget.addWidget(create)
widget.addWidget(chat)
widget.addWidget(friend_request)
widget.setFixedSize(393, 246)
widget.show()
with open('settings.txt', 'r') as f:
    # leggi il contenuto del file
    content = f.read()
    print(content)
    if content != '':
        
        content = eval(content)
        if content[0] == True:
            #accesso consentito
            my_personal_id = content[1]
            HOST = content[3]
            try:
                client.connect((HOST, PORT))
            except:
                pass 
            client.send(str((my_personal_id, 1)).encode('utf-8'))
            renspose = client.recv(1024) 
            renspose = eval(renspose)
            if renspose[0]:
                #login effettuato
                chat.my_thread.start()
                widget.setFixedHeight(500)
                widget.setFixedWidth(700)
                screen = QDesktopWidget().screenGeometry()
                width, height = screen.width(), screen.height()
                widget.setMaximumSize(width, height)
                widget.setCurrentIndex(widget.currentIndex()+2)
                #chat.setFixedHeight(500)
                #chat.setFixedWidth(700)
                if content[2] != None:
                    chats = eval(content[2])
                    for chats in chats:
                        print('chat', chats)
                        dictChat[chats] = ''
                        chat.comboChat.addItem(chats)

sys.exit(app.exec_())