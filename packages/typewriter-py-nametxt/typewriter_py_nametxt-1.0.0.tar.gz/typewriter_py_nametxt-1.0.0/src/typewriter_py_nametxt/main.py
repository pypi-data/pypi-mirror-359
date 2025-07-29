from time import sleep
import random, sys

class Typewriter:

    color = {
        'end': '\033[0m', # End Color Line

        'red': '\x1b[1;31m',
        'green': '\x1b[1;32m',
        'yellow': '\x1b[1;33m',
        'blue': '\x1b[1;34m',
        'magenta': '\x1b[1;35m',
        'cyan': '\x1b[1;36m',

        'red_bg': '\x1b[1;37;41m',
        'green_bg': '\x1b[1;37;42m',
        'yellow_bg': '\x1b[1;37;43m',
        'blue_bg': '\x1b[1;37;44m',
        'magenta_bg': '\x1b[1;37;45m',
        'cyan_bg': '\x1b[1;37;46m'        
    }

    def get_random_color(): return random.choice(list(Typewriter.color.values()))
    
    def print_line(string, **kwargs):

        '''
            Prints characters of a given string one at a time

            Arguments:
                string (str): The string to print
                speed (float -> milliseconds): How quickly the characters should be printed
                pause (float -> seconds): Time to take before continuing execution 
                new_line (bool): If the printing should end with a line break
                color (str): Which color to wrap the string with

            Defaults:
                new_line: True
                speed: 30ms
                pause: 0.5s
                color: None
        '''
        
        new_line = kwargs.get('new_line', True)
        color = kwargs.get('color', None)
        pause = kwargs.get('pause', 0.5)
        speed = kwargs.get('speed', 30)
        
        if color is not None: string = f'{color}{string}{Typewriter.color['end']}'
            
        for char in string:
            print(char, end = '', flush = True)
            sleep(speed / 1000)
            sys.stdout.flush() # Clear buffer

        if pause: sleep(pause)
        if new_line: print()