serialize = lambda x : ''.join(x).encode()

def decode_Baudot_Code(code: str) -> bytes:
    ITA2 = "00011 11001 01110 01001 00001 01101 11010 10100 00110 01011 01111 10010 11100 01100 11000 10110 10111 01010 00101 10000 00111 11110 10011 11101 10101 10001".split()
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    worddict = {a : b for a, b in zip(ITA2, alphabet)}
    code = code.split()
    word = [worddict[binary] for binary in code]
    return serialize(word)

def decode_Guitar_Code(code: str) -> bytes:
    chords = 'x02220 x24442 x32010 xx0232 022100 133211 320003'.split()
    alphabet = 'A B C D E F G'.split()
    worddict = {a : b for a, b in zip(chords, alphabet)}
    code = code.split()
    word = [worddict[c] for c in code]
    return serialize(word)

def decode_LEET(code: str) -> bytes:
    worddict = {
        '4' : 'A', '8' : 'B', '(' : 'C', '3' : 'E', '6' : 'G', '#' : 'H', '1' : 'L', '!' : 'I', '<' : 'C', '0' : 'O', '5' : 'S', '2' : 'S', '7' : 'T'
    }
    word = [worddict[ch] if ch in worddict else ch for ch in code]
    return serialize(word)

def decode_Chuck_Norris_Unary_Code(code: str) -> bytes:
    worddict = { '0' : '1', '00' : '0' }
    code = code.split()
    binary = ''
    for i in range(0, len(code), 2):
        com, length = worddict[code[i]], len(code[i + 1])
        binary += com * length
    
    assert len(binary) % 7 == 0
    word = []
    for i in range(0, len(binary), 7):
        word.append(chr(int(binary[i:i+7], 2)))

    return serialize(word)

def decode_Shanker_Speech_Defect(code: str) -> bytes:
    worddict = {a : b for a, b in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'DFGHJKLMNUOPQRSTIVWXYZBACE')}
    word = [worddict[ch] for ch in code]
    return serialize(word)

def decode_Trithemius_Code(code: str) -> bytes:
    word = []
    for i, ch in enumerate(code):
        if ch.isalpha():
            shift = i + 3
            if ch.isupper():
                ch = chr(((ord(ch) - ord('A') - shift) % 26) + ord('A'))
            else:
                ch = chr(((ord(ch) - ord('a') - shift) % 26) + ord('a'))
        
        word.append(ch)

    return serialize(word)

def decode_Wabun_Code(code: str) -> bytes:
    katakana = "a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa wi n we wo kya kyu kyo sha shu sho cha chu cho nya nyu nyo hya hyu hyo mya myu myo rya ryu ryo ga gi gu ge go gya gyu gyo za ji zu ze zo ja ju jo da ji zu de do ja ju jo ba bi bu be bo bya byu byo pa pi pu pe po pya pyu DAKUTEN HANDAKUTEN".split()
    morsecode = "--.--   .-   ..-   -.---   .-...   .-..   -.-..   ...-   -.--   ----   -.-.-   --.-.   ---.-   .---.   ---.   -.   ..-.   .--.   .-.--   ..-..   .-.   -.-.   ....   --.-   ..--   -...   --..-   --..   .   -..   -..-   ..-.-   -   -...-   -..-.   .--   -..--   --   ...   --.   -.--.   ---   .-.-   -.-   .-..-   .-.-.   .--..   .---   -.-.. .--   -.-.. -..--   -.-.. --   --.-. .--   --.-. -..--   --.-. --   ..-. .--   ..-. -..--   ..-. --   -.-. .--   -.-. -..--   -.-. --   --..- .--   --..- -..--   --..- --   ..-.- .--   ..-.- -..--   ..-.- --   --. .--   --. -..--   --. --   .-.. ..   -.-.. ..   ...- ..   -.-- ..   ---- ..   -.-.. .. .--   -.-.. .. -..--   -.-.. .. --   -.-.- ..   ..-. ..   .--. ..   .---. ..   ---. ..   ..-. .. .--   ..-. .. -..--   ..-. .. --   -. ..   ..-. ..   .--. ..   .-.-- ..   ..-.. ..   ..-. .. .--   ..-. .. -..--   ..-. .. --   -... ..   --..- ..   --.. ..   . ..   -.. ..   --..- .. .--   --..- .. -..--   --..- .. --   -... ..--.   --..- ..--.   --.. ..--.   . ..--.   -.. ..--.   --..- ..--. .--   --..- ..--. -..--  ..  ..--.".split('   ')
    worddict = {a : b for a, b in zip(morsecode, katakana)}
    ismorse = lambda x: all(ch in ['.', '-'] for ch in x)
    code = code.split()
    word = []
    for morse in code:
        if ismorse(morse):
            dec = worddict[morse]
            if dec in ("DAKUTEN", "HANDAKUTEN"):
                morse = word.pop() + ' ' + morse
                dec = worddict[morse]
            
            morse = dec
        
        word.append(morse.upper())
    
    return serialize(word)

def decode_NATO_Code(code: str) -> bytes:
    worddict = {
        'Alfa': 'A', 'Bravo': 'B', 'Charlie': 'C', 'Delta': 'D', 'Echo': 'E', 'Foxtrot': 'F', 'Golf': 'G', 'Hotel': 'H', 'India': 'I', 'Juliett': 'J', 'Kilo': 'K', 'Lima': 'L', 'Mike': 'M', 'November': 'N', 'Oscar': 'O', 'Papa': 'P', 'Quebec': 'Q', 'Romeo': 'R', 'Sierra': 'S', 'Tango': 'T', 'Uniform': 'U', 'Victor': 'V', 'Whiskey': 'W', 'X-ray': 'X', 'Yankee': 'Y', 'Zulu': 'Z', 'Zero': '0', 'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5', 'Six': '6', 'Seven': '7', 'Eight': '8', 'Nine': '9'
    }
    code = code.split()
    word = [worddict[ch] for ch in code]
    return serialize(word).title()

def decode_Latin_Gibberish(code: str) -> bytes:
    return code[:-2][::-1].encode()

def decode_Morbit_Code(code: str) -> bytes:
    worddict1 = ['', '..', './', '/-', '//', '-.', '--', '/.', '-/', '.-']
    worddict2 = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
        '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', '...-': 'V',
        '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z',
        '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
        '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    }
    morsecode = [worddict1[int(n)] for n in code]
    morsecode = serialize(morsecode).decode().split('/')
    word = [worddict2[morse] if len(morse) > 0 else '' for morse in morsecode]
    return serialize(word)

def get_func(hint: str):
    func_dict = {
        "Hendrix would have had it... ": decode_Guitar_Code, 
        "1337 ...": decode_LEET, 
        "He can snap his toes, and has already counted to infinity twice ...": decode_Chuck_Norris_Unary_Code, 
        "Did you realy see slumdog millionaire ?": decode_Shanker_Speech_Defect, 
        "Born in 1462 in Germany...": decode_Trithemius_Code, 
        "It looks like Morse code, but ... ": decode_Wabun_Code, 
        "": decode_NATO_Code, 
        "what is this charabia ???": decode_Latin_Gibberish, 
        "He can't imagine finding himself in CTF 150 years later...": decode_Baudot_Code, 
        "A code based on pairs of dots and dashes. Think of a mix of Morse code and numbers... (AZERTYUIO)": decode_Morbit_Code, 
    }
    return func_dict[hint]

if __name__ == "__main__":
    print(decode_Wabun_Code("."))