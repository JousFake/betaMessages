from tkinter import *
import subprocess
import threading

messages = 0

def start():
    global messages
    text = memo.get(1.0, END)
    #thread = threading.Thread(target=AddPlayer(screen, x,y))
    #thread.start()
    messages = subprocess.Popen(["pythonw", "messages.pyw", text])
    #messages.wait()

def stop():
    global messages
    if messages != 0:
        messages.terminate()

window = Tk()
window.title("Бот рассылки сообщений v0.1")
window.geometry('400x250')
my_frame = Frame(window, width=400, height=250) 
my_frame.grid()

lbl = Label(window, text="Текст сообщения:", font=("Arial Bold", 24))
lbl.place(x=50,y=0)
memo = Text(width=49, height=8, bg="white", fg='black', wrap=WORD)
memo.place(x=0,y=40)

buttonStart = Button(window, text="Запуск", command=start)
buttonStart.grid(column=0, row=0)
buttonStart.place(x=140, y=180)

buttonStop = Button(window, text="Стоп", command=stop)
buttonStop.grid(column=0, row=0)
buttonStop.place(x=200, y=180)

window.mainloop()
