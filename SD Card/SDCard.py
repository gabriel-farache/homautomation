from machine import SD

def mountSDCard():
    try:
        os.stat('/sd')
    except OSError:
        print('Mounting SD Card\n')
        sd = SD()
        sd.init()
        os.mount(sd, '/sd')

    print('SD Card mounted')
