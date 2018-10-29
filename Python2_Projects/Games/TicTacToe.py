import random
from Tkinter import *
import ttk
import os
import json


class Tictactoe(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.top_frame = Frame(bg='black')
        self.top_frame.grid(row=0)

        self.save_location = os.path.join(os.environ.get('TMP').replace('AppData', 'Documents').split('Local')[0], 'Tic-Tac-Toe-Scores.txt')

        game_font = 'system'
        self.win_counter_x = 0
        self.win_counter_o = 0

        self.save_button = Button(self.top_frame, text='Save', command=self.save_score, bg='DarkGreen', fg='white', font=game_font + ' 10 bold', width=10)
        self.save_button.grid(row=0, column=0, sticky=W)

        self.load_save_button = Button(self.top_frame, text='Load', command=self.show_save, bg='DarkBlue', fg='white', font=game_font + ' 10 bold', width=10)
        self.load_save_button.grid(row=0, column=2, sticky=E)

        self.saved_score_label_text = StringVar()
        self.saved_score_label_text.set('')
        self.saved_score_label = Label(self.top_frame, textvariable=self.saved_score_label_text, bg='black', fg='yellow', font=game_font + ' 14 bold')
        self.saved_score_label.grid(row=0, column=1)

        self.win_count_label = Label(self.top_frame, bg='black', fg='white', font=game_font + ' 26 bold',
                                     text='X: ' + str(self.win_counter_x) + '    O: ' + str(self.win_counter_o), anchor="center")
        self.win_count_label.grid(row=1, column=1)

        self.frame = Frame(bg='black')
        self.frame.grid(row=1)


        button_height = 0
        button_width = 4
        button_font = game_font + ' 64 bold'

        self.s = ttk.Style()
        self.s.theme_use('classic')
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='limegreen', thickness=48)
        self.progress_value = 0
        self.progress_maxvalue = 1000
        self.progress_bar = ttk.Progressbar(self.frame, style='red.Horizontal.TProgressbar', length=520)
        self.progress_bar.grid(row=3, columnspan=3)
        self.progress_bar['maximum'] = self.progress_maxvalue

        self.victory_text = StringVar()
        self.victory_text.set('')
        self.victory_label = Label(self.frame, textvariable=self.victory_text, bg='black', fg='white',
                                   font=game_font + ' 26 bold')
        self.victory_label.grid(row=3, columnspan=3)

        self.alter_choice = True

        self.ttt_tl = StringVar()
        self.ttt_tl.set('')
        self.ttt_tm = StringVar()
        self.ttt_tm.set('')
        self.ttt_tr = StringVar()
        self.ttt_tr.set('')
        self.ttt_ml = StringVar()
        self.ttt_ml.set('')
        self.ttt_mm = StringVar()
        self.ttt_mm.set('')
        self.ttt_mr = StringVar()
        self.ttt_mr.set('')
        self.ttt_bl = StringVar()
        self.ttt_bl.set('')
        self.ttt_bm = StringVar()
        self.ttt_bm.set('')
        self.ttt_br = StringVar()
        self.ttt_br.set('')

        self.button_items = [
            (0, 0, self.ttt_tl, self.tl),
            (0, 1, self.ttt_tm, self.tm),
            (0, 2, self.ttt_tr, self.tr),
            (1, 0, self.ttt_ml, self.ml),
            (1, 1, self.ttt_mm, self.mm),
            (1, 2, self.ttt_mr, self.mr),
            (2, 0, self.ttt_bl, self.bl),
            (2, 1, self.ttt_bm, self.bm),
            (2, 2, self.ttt_br, self.br)
        ]
        for row, col, text, command in self.button_items:
            self.button = Button(self.frame, textvariable=text, height=button_height, width=button_width,
                                 fg='white', bg='black', font=button_font, command=command)
            self.button.grid(row=row, column=col)

    def save_score(self):
        self.the_file = open(self.save_location, 'w+')
        self.the_file.write('{"X": ' + str(self.win_counter_x) + ', "O": ' + str(self.win_counter_o) + '}')
        self.the_file.close()

    def show_save(self):
        try:
            self.the_file = open(self.save_location, 'r')
            saved_score = json.loads(self.the_file.read())
            self.saved_score_label_text.set('X: ' + str(saved_score['X']) + '    O: ' + str(saved_score['O']))
            self.the_file.close()
        except IOError:
            pass

    def tl(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_tl.set('X')
        else:
            self.ttt_tl.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def tm(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_tm.set('X')
        else:
            self.ttt_tm.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def tr(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_tr.set('X')
        else:
            self.ttt_tr.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def ml(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_ml.set('X')
        else:
            self.ttt_ml.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def mm(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_mm.set('X')
        else:
            self.ttt_mm.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def mr(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_mr.set('X')
        else:
            self.ttt_mr.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def bl(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_bl.set('X')
        else:
            self.ttt_bl.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def bm(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_bm.set('X')
        else:
            self.ttt_bm.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def br(self):
        if self.alter_choice is True:
            self.alter_choice = False
        elif self.alter_choice is False:
            self.alter_choice = True
        if self.alter_choice is False:
            self.ttt_br.set('X')
        else:
            self.ttt_br.set('O')
        self.progress_bar['value'] = 0
        self.victory_text.set('')
        self.victory_label.configure(bg='black')
        self.winner()

    def winner(self):
        if self.ttt_tl.get() == 'X' and self.ttt_tm.get() == 'X' and self.ttt_tr.get() == 'X':  # Top row
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_ml.get() == 'X' and self.ttt_mm.get() == 'X' and self.ttt_mr.get() == 'X':  # Middle row
            self.vicory_outcome()
            self.reset()
        elif self.ttt_bl.get() == 'X' and self.ttt_bm.get() == 'X' and self.ttt_br.get() == 'X':  # Bottom row
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() == 'X' and self.ttt_mm.get() == 'X' and self.ttt_br.get() == 'X':  # Diagonal top to bot
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tr.get() == 'X' and self.ttt_mm.get() == 'X' and self.ttt_bl.get() == 'X':  # Diagonal bot to top
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() == 'X' and self.ttt_ml.get() == 'X' and self.ttt_bl.get() == 'X':  # Left column
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tm.get() == 'X' and self.ttt_mm.get() == 'X' and self.ttt_bm.get() == 'X':  # Middle column
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tr.get() == 'X' and self.ttt_mr.get() == 'X' and self.ttt_br.get() == 'X':  # Right column
            self.x_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() == 'O' and self.ttt_tm.get() == 'O' and self.ttt_tr.get() == 'O':  # Top row
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_ml.get() == 'O' and self.ttt_mm.get() == 'O' and self.ttt_mr.get() == 'O':  # Middle row
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_bl.get() == 'O' and self.ttt_bm.get() == 'O' and self.ttt_br.get() == 'O':  # Bottom row
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() == 'O' and self.ttt_mm.get() == 'O' and self.ttt_br.get() == 'O':  # Diagonal top to bot
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tr.get() == 'O' and self.ttt_mm.get() == 'O' and self.ttt_bl.get() == 'O':  # Diagonal bot to top
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() == 'O' and self.ttt_ml.get() == 'O' and self.ttt_bl.get() == 'O':  # Left column
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tm.get() == 'O' and self.ttt_mm.get() == 'O' and self.ttt_bm.get() == 'O':  # Middle column
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tr.get() == 'O' and self.ttt_mr.get() == 'O' and self.ttt_br.get() == 'O':  # Right column
            self.o_vicory_outcome()
            self.reset()
        elif self.ttt_tl.get() <> '' and self.ttt_tm.get() <> '' and self.ttt_tr.get() <> '' and self.ttt_ml.get() <> '' and self.ttt_mm.get() <> '' and self.ttt_mr.get() <> '' and self.ttt_bl.get() <> '' and self.ttt_bm.get() <> '' and self.ttt_br.get() <> '':
            self.draw_game()
            self.reset()

    def x_vicory_outcome(self):
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='limegreen', thickness=48)
        self.progress_bar['value'] = self.progress_maxvalue
        self.victory_text.set('X WINS!')
        self.victory_label.configure(bg='limegreen', fg='black')
        self.win_counter_x += 1
        self.win_count_label.configure(text='X: ' + str(self.win_counter_x) + '    O: ' + str(self.win_counter_o))
        self.alter_choice = True

    def o_vicory_outcome(self):
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='limegreen', thickness=48)
        self.progress_bar['value'] = self.progress_maxvalue
        self.victory_text.set('O WINS!')
        self.victory_label.configure(bg='limegreen', fg='black')
        self.win_counter_o += 1
        self.win_count_label.configure(text='X: ' + str(self.win_counter_x) + '    O: ' + str(self.win_counter_o))
        self.alter_choice = True

    def draw_game(self):
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='yellow', thickness=48)
        self.progress_bar['value'] = self.progress_maxvalue
        self.victory_text.set('CAT\'S GAME!')
        self.victory_label.configure(bg='yellow', fg='black')
        self.alter_choice = True

    def reset(self):
        self.ttt_tl.set('')
        self.ttt_tm.set('')
        self.ttt_tr.set('')
        self.ttt_ml.set('')
        self.ttt_mm.set('')
        self.ttt_mr.set('')
        self.ttt_bl.set('')
        self.ttt_bm.set('')
        self.ttt_br.set('')


app = Tictactoe()
app.title('Tic Tac Toe')
app.iconbitmap('TTT.ico')
app.configure(bg='black')
app.mainloop()
