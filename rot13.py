def main(input_string):
    out = ''
    for c in input_string:
        n = ord(c) - ord('a')
        if n < 0 or n >= 26:
            out += c
            continue
        rot = (n + 14) % 26
        out += chr(rot + ord('a'))
    return out

def loop():
    try:
        while True:
            print main("you.just.lost.the.game")
    except KeyboardInterrupt:
        print "Finished"

if __name__ == "__main__":
    import sys
    input_string = ' '.join(sys.argv[1:]).lower()
    main(input_string)
