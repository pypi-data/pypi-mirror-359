import simplygame as SG
x = 400
y = 300
running = True
pressed = False
keys = []
SG.create_window("test", 800,600)

while running:
    event = SG.recover_event()
    if event == 'exit':
        running = False
   
    img = SG.load_image('simply.png')

    SG.tick(60)
    SG.update()