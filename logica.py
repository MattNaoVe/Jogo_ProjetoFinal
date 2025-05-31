import pygame
import pygame_gui

# inicialização do pygame
pygame.init()



#estados do jogo
#criação de coisas importwntes que nao mudaam(constantes) uso o padrao tudo maiusculo


#definir tasmanhos
largura_tela = 800
altura_tela = 600
boneco_largura = 64
boneco_altura = 64
x_boneco = largura_tela / 2 - boneco_largura / 2
y_boneco = altura_tela / 2 - boneco_altura / 2


# criar a tela
screen = pygame.display.set_mode((largura_tela , altura_tela))

#criar gerenciador pygame
gerente = pygame_gui.UIManager((largura_tela , altura_tela))












# loop principal do jogo
running = True
while running:
    # percorrendo os eventos
    for event in pygame.event.get():
        # verificando se o evento é do tipo QUIT
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                y_snake = y_snake - 10
                
            if event.key == pygame.K_s:
                
                y_snake = y_snake + 10
                
            if event.key == pygame.K_a:
                
                x_snake = x_snake - 10
               
            if event.key == pygame.K_d:
                
                x_snake = x_snake + 10
          
    screen.fill((0, 0, 0))  
    pygame.draw.rect(screen, (204, 153 , 255), [(x_boneco , y_boneco) , (boneco_altura, boneco_largura)])
    
    gerente.update(1/60)
    gerente.draw_ui(screen)
    
    #atualiando a tela
    pygame.display.flip()
    