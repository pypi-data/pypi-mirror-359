from secrypto.source.key import Key

def decrypt(encryption: str, key: Key | dict[str, list[str]]):
    if not encryption:
        return ''

    base = ''
    temp = ''

    alts = key.key if isinstance(key, Key) else key
    for z in encryption:
        for y in alts.values():
            if z in y:
                base += list(alts.keys())[list(alts.values()).index(y)]

    str_order = base[-4:]
    base = base[:-4]

    for a in str_order:
        if a == 'a':
            base = base.replace('²', '¹').replace('³', '¹').replace('⁴', '¹').replace('⁵', '¹').replace('⁶', '¹').replace('⁷', '¹').replace('⁸', '¹').replace('⁹', '¹')
            base = base[:-1].split('¹')
            temp = ''.join(chr(int(z)) for z in base)
        elif a == 'o':
            base = base.replace('A', '9').replace('B', '9').replace('C', '9').replace('D', '9').replace('E', '9').replace('F', '9').replace('G', '9')
            base = base[:-1].split('9')
            temp = ''.join(chr(int(z, 8)) for z in base)
        elif a == 'b':
            base = base.replace('3', '2').replace('4', '2').replace('5', '2').replace('6', '2').replace('7', '2').replace('8', '2')
            base = base[:-1].split('2')
            temp = ''.join(chr(int(z, 2)) for z in base)
        elif a == 'h':
            base = base.replace('i', 'h').replace('g', 'h').replace('j', 'h').replace('k', 'h').replace('l', 'h').replace('m', 'h').replace('n', 'h')
            base = base[:-1].split('h')
            temp = ''.join(chr(int(z, 16)) for z in base)

        base = temp
        temp = ''

    return base
