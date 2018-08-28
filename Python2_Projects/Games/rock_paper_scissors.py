import random
from Tkinter import *
from PIL import Image, ImageTk
import ttk
import tkMessageBox

app = Tk()
app.background_color = 'burlywood2'
app.bad_good_colors = ['forest green', 'brown4']
app.title("Rock / Paper / Scissors")
app.configure(background=app.background_color)
app.iconbitmap('rps.ico')
app.window_width = 845
app.window_height = 500
app.geometry(str(app.window_width) + 'x' + str(app.window_height) + '+200+200')
app.hp_max = 1000
app.hp_current = app.hp_max / 2

app.options = ['Rock', 'Paper', 'Scissors']
app.counter = [0, 0]
image_width, image_height = 100, 100

rock_image = Image.open('rock_hand.png')
rock_image = rock_image.resize((image_width, image_height), Image.ANTIALIAS)
app.rock = ImageTk.PhotoImage(rock_image)

paper_image = Image.open('paper_hand.png')
paper_image = paper_image.resize((image_width, image_height), Image.ANTIALIAS)
app.paper = ImageTk.PhotoImage(paper_image)

scissors_image = Image.open('scissors_hand.png')
scissors_image = scissors_image.resize((image_width, image_height), Image.ANTIALIAS)
app.scissors = ImageTk.PhotoImage(scissors_image)


def winner(user_choice):
    computer_choice = random.choice(app.options)
    if user_choice == 'Rock' and computer_choice == 'Scissors':
        return ["Rock", "Scissors", "You win!"]
    elif user_choice == 'Rock' and computer_choice == 'Paper':
        return ["Rock", "Paper", "You lose..."]
    elif user_choice == 'Rock' and computer_choice == 'Rock':
        return ["Rock", "Rock", "Draw"]
    elif user_choice == 'Paper' and computer_choice == 'Scissors':
        return ["Paper", "Scissors", "You lose..."]
    elif user_choice == 'Paper' and computer_choice == 'Paper':
        return ["Paper", "Paper", "Draw"]
    elif user_choice == 'Paper' and computer_choice == 'Rock':
        return ["Paper", "Rock", "You win!"]
    elif user_choice == 'Scissors' and computer_choice == 'Scissors':
        return ["Scissors", "Scissors", "Draw"]
    elif user_choice == 'Scissors' and computer_choice == 'Paper':
        return ["Scissors", "Paper", "You win!"]
    elif user_choice == 'Scissors' and computer_choice == 'Rock':
        return ["Scissors", "Rock", "You lose..."]


def beenClicked():
    outcome_list = winner(userThrow.get())
    user_pick = outcome_list[0]
    computer_pick = outcome_list[1]
    outcome = outcome_list[2]

    # Populates the images for showing what the user and computer picked
    if user_pick == 'Rock':
        users_choice.configure(image=app.rock)
    elif user_pick == 'Paper':
        users_choice.configure(image=app.paper)
    elif user_pick == 'Scissors':
        users_choice.configure(image=app.scissors)

    if computer_pick == 'Rock':
        computers_choice.configure(image=app.rock)
    elif computer_pick == 'Paper':
        computers_choice.configure(image=app.paper)
    elif computer_pick == 'Scissors':
        computers_choice.configure(image=app.scissors)
    # Does things based on if we win or lose each round
    if 'win' in outcome:
        app.counter[0] += 1
        app.hp_current += random.randrange(40, 100)
    elif 'lose' in outcome:
        app.counter[1] += 1
        app.hp_current -= random.randrange(40, 100)

    score_label.set('Wins: ' + str(app.counter[0]) + '\nLoses: ' + str(app.counter[1]))
    user_name_label.set('Player 1')
    computer_name_label.set('CPU')

    if app.hp_current > 0 and app.hp_current < app.hp_max:
        outcome_label.set(outcome + '\n')
    elif app.hp_current >= app.hp_max:
        outcome_label.set('YOU WIN THE GAME\n')
        app.hp_current = app.hp_max / 2
        users_choice.configure(image='')
        computers_choice.configure(image='')
        score_label.set('')
        user_name_label.set('')
        computer_name_label.set('')
        app.counter[0] = 0
        app.counter[1] = 0
        tkMessageBox.showinfo("VICTORY!", "YOU WIN THE GAME\nPlay again...")
        outcome_label.set('Select one of the options, then RO-SHAM-BO!')
    else:
        outcome_label.set('GAME OVER\n')
        app.hp_current = app.hp_max / 2
        users_choice.configure(image='')
        computers_choice.configure(image='')
        score_label.set('')
        user_name_label.set('')
        computer_name_label.set('')
        app.counter[0] = 0
        app.counter[1] = 0
        tkMessageBox.showinfo("DEFEAT!", "GAME OVER\nTry again...")
        outcome_label.set('Select one of the options, then RO-SHAM-BO!')

    hp_bar['value'] = app.hp_current

    # Change hp bar color if below half hp
    if app.hp_current < app.hp_max / 2:
        s.configure("red.Horizontal.TProgressbar", background=app.bad_good_colors[1])
    else:
        s.configure("red.Horizontal.TProgressbar", background=app.bad_good_colors[0])

    # This will change the color based on if we are winning or losing
    if app.counter[0] > app.counter[1]:
        score.configure(bg=app.bad_good_colors[0])
    else:
        score.configure(bg=app.bad_good_colors[1])


score_label = StringVar()
score_label.set('')
score = Label(app, textvariable=score_label, bg='#002888', fg='white', font="none 18 bold")
score.grid(row=0, columnspan=3, sticky=W)

users_choice = Label(app, bg=app.background_color, fg='white')
users_choice.grid(row=1, column=0, sticky=N)

user_name_label = StringVar()
user_name_label.set('')
user_name = Label(app, textvariable=user_name_label, bg=app.background_color, fg='gray26', font="none 14 bold")
user_name.grid(row=2, column=0, sticky=S)

computers_choice = Label(app, bg=app.background_color, fg='white')
computers_choice.grid(row=1, column=2, sticky=N)

computer_name_label = StringVar()
computer_name_label.set('')
computer_name = Label(app, textvariable=computer_name_label, bg=app.background_color, fg='gray26', font="none 14 bold")
computer_name.grid(row=2, column=2, sticky=S)

outcome_label = StringVar()
outcome_label.set('Select one of the options, then RO-SHAM-BO!')
who_wins_label = Label(app, textvariable=outcome_label, height=4, bg=app.background_color, fg='gray26', font="none 24 bold")
who_wins_label.grid(row=3, columnspan=3)

radio_options = [
    (app.options[0], app.options[0]),
    (app.options[1], app.options[1]),
    (app.options[2], app.options[2])
]

userThrow = StringVar()
userThrow.set(None)
col = 0
for text, value in radio_options:
    b = Radiobutton(app, text=text, value=value, variable=userThrow, bg='#003300', fg='white', font="none 18 bold", indicatoron=0, width=18, selectcolor='#118111')
    b.grid(row=4, column=col, sticky=W)
    col += 1

throw_button = Button(app, text='RO-SHAM-BO!', width=15, command=beenClicked, bg='darkgreen', fg='white', font="none 18 bold")
throw_button.grid(row=5, column=1, padx=5, pady=15)

exit_button = Button(app, text='Exit', command=exit, bg='#333333', fg='white', font="none 18 bold")
exit_button.grid(row=5, column=2, padx=5, pady=15, sticky=SE)

s = ttk.Style()
s.theme_use('classic')
s.configure('red.Horizontal.TProgressbar', troughcolor='white', background=app.bad_good_colors[0])
hp_bar = ttk.Progressbar(app, style="red.Horizontal.TProgressbar", orient='horizontal', length=800)
hp_bar.grid(row=6, columnspan=3)
hp_bar['value'] = app.hp_current
hp_bar['maximum'] = app.hp_max

app.mainloop()

## Thoughts on things to add
# Something that keeps a record of a personal best
