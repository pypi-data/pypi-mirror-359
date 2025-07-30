# secretrandom 2.1 RELEASE

import random
import secrets
import string
from decimal import Decimal


shuffled_digits_for_unprdictibility = string.digits + string.digits + string.digits


def randpwd(length, strength='strong'):
    match strength.strip():
        case 'strong':
            characters = list(string.ascii_letters + string.digits + string.punctuation)
            random.shuffle(characters)
            password = ''
            for _ in range(length-1):
                password += secrets.choice(characters)
            password += random.choice(characters)
            return password
        case 'weak':
            teenage_shit_passwords = ['l0v3ly','cut3b0i','iluvu','bestie123','yolo$','sw@g123','unicornz','xoxo','g@mergirl','f0rtNite','rockstar$','crush123','lolpass','tikt0kking','selfie$','queenB','snapchat1','123iloveyou','noobmaster','b@dB0i','bruh123','hearts4u','coolkid$','sk8rboi','partytime','star$truck','g1ggle$','p@ssie','omg123','dr@m@queen']
            return random.choice(teenage_shit_passwords)
        case _:
            raise SyntaxError('Invalid argument. Perhaps you mean\'t "strong" or "weak"?')
        
def randcode(length):
    code = ''
    code += random.choice(shuffled_digits_for_unprdictibility)
    for _ in range(length):
        code += secrets.choice(shuffled_digits_for_unprdictibility)
    return code

def randint(from_this, to_this, step=1):
    the_repeating_number_to_loop = random.choice(shuffled_digits_for_unprdictibility)
    for _ in range(random.randint(1, 22)):
        num = random.randrange(from_this, to_this+1, step)
    return num

def randflt(from_this, to_this):
    for _ in range(randint(2, 23)):
        float = random.uniform(from_this, to_this)
    return float

def choice(i):
    for _ in range(randint(1, 5)):
        random.shuffle(i)
    return secrets.choice(i)

def shuffle(i):
    for _ in range(randint(4, 25)):
        random.shuffle(i)
    return i

def ver():
    return 'secretrandom v2.1 RELEASE\nOFFICIAL RELEASE by Annoying-mous.\nMore information at https://pypi.org/project/secretrandom/'
