import random
import tkinter as tk
from tkinter import font          #Tkinter biblioteket används för grafiken i boarddisplay klassen.
from typing import NamedTuple    # Används för våra logik klasser Player och Move, tuples
from itertools import cycle      # Sparar en iterator och ger tillbaka en kopia när "den tar slut"
#Menu title



#Spelare, pjäser och förflyttning
class Player(NamedTuple):              #Label för symbolen X/O. Color för färgen. Fylls i DEFAULT_PLAYERS
    label: str
    color: str


class Move(NamedTuple):          # Koordinaterna för cellerna i displayen som används. Alltså förflyttningen.
    row: int    
    col: int
    label: str = ''

BOARD_SIZE = 3        #Storlek på brädan, EJ grafik
DEFAULT_PLAYERS = (Player(label='X', color='black'), Player(label='O', color ='red' )) 
#Spelet, logiken         
class TicTacToeGame(tk.Tk):
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self.players = cycle(players)            #itertools cycle för tuple
        self.board_size = board_size             #storlek
        self.current_player = next(self.players)#Spelaren som kör
        self.winner_combo = []                   #Kombinationen av celler för 'tre i rad' seger
        self._current_moves = []                 #Hur många gånger man har kört
        self._has_winner = False                 #Variabel om man har vunnit eller inte
        self._winning_combos = []                #Lista för kombinationer i cellerna som betyder seger
        self.cpu_enabled = False
        self._setup_board() 


    def _setup_board(self):
        self._current_moves = [[Move(row, col)for col in range(self.board_size)]
                               for row in range(self.board_size)]
        self._winning_combos = self._get_winning_combos()       #ger return value till _winning_combos


    def _get_winning_combos(self):          #Metoden som bestämmer seger genom kombinationerna
        rows = [[(move.row, move.col)for move in row] for row in self._current_moves]
        columns = [list(col)for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j]for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]
    
    def is_valid_move (self, move):
        row, col =  move.row, move.col     # tar row och column koordinaterna från spelarens input
        move_was_not_played = self._current_moves[row][col].label =='' #Kollar om cellen är tom
        no_winner = not self._has_winner    #kollar om ingen har vunnit ännu
        return no_winner and move_was_not_played

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:    #Loop över seger kombinationer
            results = set(self._current_moves[n][m].label for n,m in combo)
            is_win =(len(results) == 1) and ('' not in results) # Kollar om senaste move är tre-i-rad seger
            if is_win:                                          #ifall seger, loopen bryts
                self._has_winner = True
                self.winner_combo = combo
                break 
    def has_winner(self):
        return self._has_winner
    def is_tied(self):                              #metoden ger attribut till is_tied
        no_winner = not self._has_winner
        played_moves = (move.label for row in  self._current_moves for move in row)
        return no_winner and all (played_moves)
    def toggle_player(self):                        #metoden ger attribut till toggle_player
        self.current_player = next(self.players)
    def reset_game(self):                              #Kod logiken för reset, efter pjäserna
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
                self._has_winner = False                      #Reseten byter till "ingen vinnare"
                self.winner_combo = []                         #Reseten gör en tom lista
    def random_CPU(self):                          #Metod för CPU
        avaible_moves = [move for row in self._current_moves for move in row if move.label == '']
        if avaible_moves:
            random_move = random.choice(avaible_moves)
            return Move(random_move.row, random_move.col, self.current_player.label)
        return None

    
#Brädan , Grafiken 
class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title('Tic-Tac-Toe Spel')    #Titeln i windows titel bar
        self.cells = {}    # en dikt som ska ha cellerna i brädan
        self.game = game
        self.create_menu()
        self.boarddisplay()
        self.boardgrid()
        
    def create_menu(self):         #Det här kommer att vara vår meny
        menu_bar = tk.Menu(master= self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label='Kör igen', command=self.reset_board) #Brädan körs om
        file_menu.add_separator()
        file_menu.add_command(label='Kör mot CPU', command=self.enable_cpu)
        file_menu.add_separator()
        file_menu.add_command(label='Avsluta', command=quit)   #Kommer att komma till quit() funktionen
        menu_bar.add_cascade(label='File', menu=file_menu)

    def play (self, event): # Den här metoden tar all logik in till självaste UI grafiken
        clicked_btn = event.widget
        row, col = self.cells[clicked_btn]
        move = Move(row, col, self.game.current_player.label)
        if self.game.is_valid_move(move):
            self._update_button(clicked_btn)
            self.game.process_move(move)
            if self.game.is_tied():
                self._update_display(msg = ' Oavgjort ', color = 'blue')
            elif self.game.has_winner():
                self._highlight_cells()
                msg = f'{self.game.current_player.label} har vunnit'
                color = self.game.current_player.color
                self._update_display(msg, color)
            else:
                self.game.toggle_player()
                msg = f'{self.game.current_player.label}s tur'
                self._update_display(msg)

                if self.game.cpu_enabled and self.game.current_player.label == 'O':
                    self.after(500, self.play_cpu)          #0.5 sekunders delay på CPUs turn så vi kan se

    def play_cpu(self):                                       #CPU randoms logik
        if self.game.has_winner() or self.game.is_tied():     #ser till att cpu inte kör om spelet är slut
            return
        cpu_move = self.game.random_CPU() 
        if cpu_move and self.game.is_valid_move(cpu_move):
            for button, (row, col) in self.cells.items():
                if (row, col) == (cpu_move.row, cpu_move.col):
                    self._update_button(button)
                    break
            self.game.process_move(cpu_move)
            if self.game.is_tied():
                self._update_display(msg= 'Oavgjort', color='blue')
            elif self.game.has_winner():
                self._highlight_cells()
                msg = f'{self.game.current_player.label} har vunnit'
                color = self.game.current_player.color
                self._update_display(msg, color)

            else: 
                self.game.toggle_player()
                self._update_display(f'{self.game.current_player.label}s tur')
    def enable_cpu(self):                               #när vi switchar från spelare till CPU

        self.game.cpu_enabled = True
        self.reset_board()
        self._update_display(msg='CPU ON')


    def boarddisplay(self): #Displayen
        display_frame = tk.Frame(master=self) # Frame håller displayen. Master sätts till self argument
        display_frame.pack(fill=tk.X) 
        self.display = tk.Label(master=display_frame, text='Tre-i-rad',
        font=font.Font(size=28, weight='bold'))     #Font, fontens storlek och text innanför.
        self.display.pack()

    def boardgrid(self): #Grid och celler
        grid_frame = tk.Frame(master=self) #Håller spelets celler i själva brädan. Vi använder grid.
        grid_frame.pack()
        for row in range(self.game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self.game.board_size):#For loopen för knapparna. Just nu 3x3

                button = tk.Button(
                master=grid_frame, 
                text='', font=font.Font(size=36, weight='bold'), width = 3, height = 2, 
                fg='black', bg= 'lightblue',  activebackground='blue', activeforeground='white' #Färger på knappar
               )
            
                self.cells[button] = (row, col)          #Alla knappars position innanför for loopen
                button.bind('<Button-1>', self.play)
                button.grid(row=row, column= col, padx= 5, pady = 5, sticky='nsew')

    def _update_button(self, clicked_btn):
        clicked_btn.config(text = self.game.current_player.label)
        clicked_btn.config(fg=self.game.current_player.color)

    def _update_display(self, msg, color ='black'): #Tkinter widget text och färg istället för config()
        self.display['text'] = msg
        self.display['fg'] = color
    def _highlight_cells(self):
        for button, coordinates in self.cells.items():
            if coordinates in self.game.winner_combo:
                button.config(highlightbackground = 'red')
    def reset_board(self):            #Reset metoden för displayen
        self.game.reset_game()
        self._update_display(msg='Redo?')  #Går tillbaka till "redo?"
        for button in self.cells.keys():  #Går tillbaka till loopen över knapparna
            button.config(highlightbackground= 'lightblue')
            button.config(text='')
            button.config(fg='black')
def main():
    game = TicTacToeGame()           # Hanterar spelets logik
    board = TicTacToeBoard(game)     # Tar spelets logik till brädan
    
    board.mainloop() # startar spelets loop

if __name__ == '__main__': #Gör så att man kan starta main() när man kör programmet
    main()


#files for hiscore
