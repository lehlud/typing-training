import os
import sys
import time
import json
import names
import random
import curses
import threading
from termcolor import colored
from curses import wrapper

def char_at(string, index):
    try: return string[index]
    except: return None

def arr_to_str(arr):
    result = ''
    for index, element in enumerate(arr):
        if index == 0: result += str(element)
        else: result += ", " + str(element)
    return result

def main(stdscr):
    short_words = []
    long_words= []
    current_words = []

    score = 0
    global wpm
    wpm = 0
    typed_letters = 0
    correct_letters = 0
    
    filename = 'german_words'
    try:
        if sys.argv[1] == 'eng' or sys.argv == 'english':
            filename = 'english_words'
    except: pass
    for line in open(filename, 'r').readlines():
        word = line.strip()
        if len(word) > 8: long_words.append(word)
        else: short_words.append(word)
    
    def next_word():
        rnd = random.randint(0, 15)
        if rnd == 0:
            rnd = random.randint(0, 1)
            if rnd == 0: return names.get_first_name()
            return names.get_last_name()
        else:
            rnd = random.randint(0, 3)
            if rnd == 3: return random.choice(long_words)
            else: return random.choice(short_words)
    
    for i in range(5): current_words.append(next_word())

    def get_accuracy():
        try: return round(correct_letters / typed_letters * 100, 2)
        except: return 100.00

    def decr_wpm_timeout(timeout):
        try:
            time.sleep(timeout)
            global wpm
            wpm -= 1
        except: pass

    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS): curses.init_pair(i + 1, i, -1)
    curses.noecho()

    stdscr.addstr('score: 0, wpm: 0, accuracy: ' + str(get_accuracy()) + '%\n')
    stdscr.addstr('\n')
    stdscr.addstr(arr_to_str(current_words) + '\n')
    
    chars = ''
    wrong_indices = []
    corrected_indices = []
    overflow_chars = ''
    while(True):
        key = stdscr.get_wch()
        if key == 263 or key == '\x7f':
            y, x = stdscr.getyx();
            try:
                stdscr.move(y, x - 1);
                stdscr.clrtoeol();
                typed_letters -= 1
                if (index := x-1) in corrected_indices:
                    corrected_indices.remove(index)
                elif len(overflow_chars) > 0: 
                    overflow_chars = overflow_chars[:-1]
            except: pass

        elif key in '\n\t\v\r\f ':
            y, x = stdscr.getyx()
            if x == 0: continue
            try:
                stdscr.move(y, 0)
                stdscr.clrtoeol()
                stdscr.move(0, 0)
                stdscr.clrtoeol()
                c_letters_percent = round((len(current_words[0]) - len(wrong_indices) + len(corrected_indices) / len(current_words[0])) * 100, 2)
                if c_letters_percent > 80:
                    score += 1
                    wpm += 1
                    threading.Thread(target=decr_wpm_timeout, args=(60,), daemon=True).start()

                stdscr.addstr('score: ' + str(score) + ', wpm: ' + str(wpm) + ', accuracy: ')
                accuracy = get_accuracy()
                if accuracy >= 85: stdscr.addstr(str(accuracy), curses.color_pair(48))
                elif accuracy >= 70: stdscr.addstr(str(accuracy), curses.color_pair(204))
                else: stdscr.addstr(str(accuracy), curses.color_pair(198))
                stdscr.addstr('%\n')
                
                stdscr.move(1, 0)
                stdscr.clrtoeol()
 
                word = current_words[0]
                if x < len(word):
                    for i in range(x, len(word)):
                        typed_letters += 1
                        wrong_indices.append(i)
                for i in range(len(word)):
                    if i in wrong_indices:
                        if i in corrected_indices:
                            stdscr.addstr(word[i], curses.color_pair(204))
                        else:
                            stdscr.addstr(word[i], curses.color_pair(198))
                    else: stdscr.addstr(word[i], curses.color_pair(48))
               
                for c in overflow_chars:
                    stdscr.addstr(c, curses.color_pair(28))
                
                wrong_indices = []
                corrected_indices = []
                overflow_chars = ''
                current_words.pop(0)
                current_words.append(next_word())
                stdscr.move(2, 0)
                stdscr.clrtoeol()
                stdscr.addstr(arr_to_str(current_words))
                stdscr.move(y, 0)
            except: exit()

        elif not isinstance(key, str): pass
        else:
            index = stdscr.getyx()[1]
            orig_char = char_at(current_words[0], index)
            typed_letters += len(key)
            if index + 1 > len(current_words[0]):
                stdscr.addstr(key, curses.color_pair(28))
                overflow_chars += key
            elif key == orig_char:
                if index in wrong_indices:
                    correct_letters += 0.5
                    corrected_indices.append(index)
                    stdscr.addstr(key, curses.color_pair(204))
                else:
                    correct_letters += len(key)
                    stdscr.addstr(key, curses.color_pair(48))
            else:
                wrong_indices.append(index)
                stdscr.addstr(key, curses.color_pair(198))
    

if __name__ == '__main__':
    try: wrapper(main)
    except (KeyboardInterrupt): pass



