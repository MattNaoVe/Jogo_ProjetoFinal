import pygame
import pygame_gui
import random
import sys
import time
from pygame.locals import *
from PIL import Image, ImageSequence

# Inicialização
pygame.init()
pygame.mixer.init()  # Inicializa o mixer de áudio
pygame.display.set_caption('Escape Room')

# Configurações
largura_tela, altura_tela = 800, 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
gerente = pygame_gui.UIManager((largura_tela, altura_tela))
tempo = pygame.time.Clock()

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
verde = (0, 255, 0)
azul = (0, 0, 255)
dourado = (255, 215, 0)
cinza = (150, 150, 150)  # Cor para texto nas fases escuras

# Carregar sons
pygame.mixer.music.load('PirateBay8.mp3')  # Música de fundo
som_sucesso = pygame.mixer.Sound('acerto.mp3')  # Som ao passar de sala

# Configurações de áudio
VOLUME_MUSICA = 0.5  # 50% do volume
pygame.mixer.music.set_volume(VOLUME_MUSICA)

# Estados do jogo
MENU, DIFICULDADE, GAME, CODE_INPUT, GAME_OVER, VITORIA = 0, 1, 2, 3, 4, 5

# Configurações do jogador
tamanho_jogador = 64
posicao_jogador = [largura_tela//2 - tamanho_jogador//2, altura_tela//2 - tamanho_jogador//2]
velocidade_jogador = 5

# Carregar animação GIF para o jogador
def carregar_gif(caminho):
    frames = []
    with Image.open(caminho) as img:
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")
            frame = frame.resize((tamanho_jogador, tamanho_jogador), Image.LANCZOS)
            frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode))
    return frames

# Carregar os quadros do GIF
quadros_jogador = carregar_gif("sprite_frente_andando.gif")
quadro_atual = 0
tempo_animacao = 0.1  # Tempo entre quadros em segundos
tempo_passado = 0  # Acumulador de tempo

# Criar fundos progressivamente mais escuros para cada sala
imagens_fundo = []
cores_fundo = [
    (100, 100, 100),   # Sala 1 - Cinza médio
    (80, 80, 80),      # Sala 2
    (60, 60, 60),      # Sala 3
    (40, 40, 40),      # Sala 4
    (20, 20, 20),      # Sala 5
    (0, 0, 0)          # Sala 6 - Preto total
]

for cor in cores_fundo:
    fundo = pygame.Surface((largura_tela, altura_tela))
    fundo.fill(cor)
    
    # Adicionar detalhes sutis nas salas mais claras
    if cor[0] > 40:  # Apenas para as salas mais claras
        for x in range(0, largura_tela, 40):
            for y in range(0, altura_tela, 40):
                pygame.draw.rect(fundo, (cor[0]+20, cor[1]+20, cor[2]+20), (x, y, 20, 20), 1)
    
    imagens_fundo.append(fundo)

# Variáveis do jogo
estado_atual = MENU
sala_atual = 1
dificuldade = ""
tempo_limite = 600
tempo_inicial = 0
codigo_resolver = ""
codigo_inserido = ""
questao_puzzle = ""
solucao_puzzle = ""

# Fontes
fonte_pequena = pygame.font.SysFont('Arial', 24)
fonte_media = pygame.font.SysFont('Arial', 32)
fonte_larga = pygame.font.SysFont('Arial', 48)

# Elementos da UI
def criar_botao(x, y, text, visible=True):
    btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((x, y), (200, 50)), 
        text=text, 
        manager=gerente
    )
    btn.visible = visible
    return btn

jogar_btn = criar_botao(300, 200, 'Jogar')
facil_btn = criar_botao(300, 300, 'Fácil', False)
normal_btn = criar_botao(300, 400, 'Normal', False)
dificil_btn = criar_botao(300, 500, 'Difícil', False)

entrada_de_codigo_btn = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((300, 350), (200, 50)), 
    manager=gerente
)
entrada_de_codigo_btn.hide()

enviar_btn = criar_botao(300, 420, 'Confirmar', False)
continuar_btn = criar_botao(300, 400, 'Continuar', False)
reiniciar_btn = criar_botao(300, 500, 'Reiniciar', False)

# Gerar puzzles
def generate_puzzle(room):
    if room == 1:
        a = random.randint(10, 20)
        b = random.randint(10, 20)
        return {'q': f"{a} + {b} = ?", 's': str(a + b)}
    elif room == 2:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        return {'q': f"{a} × {b} = ?", 's': str(a * b)}
    elif room == 3:
        a = random.randint(10, 20)
        b = random.randint(10, 20)
        return {'q': f"{a} x {b} = ?", 's': str(a * b)}
    elif room == 4:
        a = random.randint(10, 20)
        b = random.randint(10, 20)
        return {'q': f"{a} - {b} = ?", 's': str(a - b)}
    elif room == 5:
        num = random.choice([9, 16, 25, 36, 49, 64, 81, 100])
        return {'q': f"√{num} = ?", 's': str(int(num**0.5))}
    else:
        num = random.choice([9, 16, 25, 36, 49, 64, 81, 100])
        return {'q': f"√{num} = ?", 's': str(int(num**0.5))}

# Configurar sala
def configurar_sala(room, diff):
    global codigo_resolver, questao_puzzle, solucao_puzzle, imagem_porta, entrada_de_codigo_btn
    
    puzzle = generate_puzzle(room)
    questao_puzzle = puzzle['q']
    solucao_puzzle = puzzle['s']
    codigo_resolver = solucao_puzzle  # Todas as salas usam a solução como código

    # Definir tamanho da porta
    tamanho_porta = max(16, 100 - (room - 1) * 14)  # Diminuir de 100 a 16
    imagem_porta = pygame.image.load('porta_s.png').convert_alpha()
    imagem_porta = pygame.transform.scale(imagem_porta, (32, 32))

    # Definir posição aleatória da porta
    porta_x = random.randint(0, largura_tela - tamanho_porta)
    porta_y = random.randint(0, altura_tela - tamanho_porta)
    
    print(f"\n--- SALA {room} ---")
    print(f"Pergunta: {questao_puzzle}")
    print(f"Código: {codigo_resolver}")

    # Atualizar a posição do campo de entrada de código
    entrada_de_codigo_btn.relative_rect.topleft = (porta_x, porta_y + tamanho_porta + 10)

    # Atualizar a posição da porta
    return porta_x, porta_y

def desenhar_sala(porta_pos):
    # Desenhar o fundo da sala atual
    tela.blit(imagens_fundo[sala_atual - 1], (0, 0))
    
    # Desenhar a porta
    tela.blit(imagem_porta, porta_pos)
    
    # Desenhar o jogador (sprite GIF)
    global quadro_atual, tempo_passado
    tempo_passado += tempo.tick(60) / 1000.0  # Atualiza o tempo passado
    if tempo_passado > tempo_animacao:
        quadro_atual = (quadro_atual + 1) % len(quadros_jogador)  # Muda para o próximo quadro
        tempo_passado = 0  # Reseta o tempo passado

    tela.blit(quadros_jogador[quadro_atual], posicao_jogador)
    
    # Ajustar cor do texto conforme o fundo
    cor_texto = cinza if sala_atual >= 4 else branco  # Mais claro nas salas escuras
    
    # Renderizar a pergunta com quebra de linha se necessário
    questao_linhas = [questao_puzzle[i:i+30] for i in range(0, len(questao_puzzle), 30)]
    for i, line in enumerate(questao_linhas):
        texto = fonte_pequena.render(line, True, cor_texto)
        tela.blit(texto, (50, 150 + i*30))
    
    texto_sala = fonte_pequena.render(f"Sala {sala_atual}/6", True, cor_texto)
    tempo_restante = max(0, tempo_limite - (time.time() - tempo_inicial))
    tempo_texto = fonte_pequena.render(f"Tempo: {int(tempo_restante//60):02d}:{int(tempo_restante%60):02d}", True, cor_texto)
    tela.blit(texto_sala, (20, 20))
    tela.blit(tempo_texto, (20, 50))
    
    # Dica quando perto da porta
    if (abs(posicao_jogador[0] - porta_pos[0]) < 50 and 
        abs(posicao_jogador[1] - porta_pos[1]) < 50):
        dica = fonte_pequena.render("Pressione E para inserir código", True, cor_texto)
        tela.blit(dica, (largura_tela//2 - dica.get_width()//2, 100))

def resetar_jogo():
    global estado_atual, sala_atual, posicao_jogador, tempo_inicial, dificuldade
    
    estado_atual = MENU
    sala_atual = 1
    dificuldade = ""
    posicao_jogador = [largura_tela//2 - tamanho_jogador//2, altura_tela//2 - tamanho_jogador//2]
    tempo_inicial = 0
    
    jogar_btn.show()
    facil_btn.hide()
    normal_btn.hide()
    dificil_btn.hide()
    entrada_de_codigo_btn.hide()
    enviar_btn.hide()
    continuar_btn.hide()
    reiniciar_btn.hide()

# Loop principal
running = True
porta_pos = (0, 0)  # Inicializar a posição da porta

# Iniciar a música de fundo
pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop

while running:
    time_delta = tempo.tick(60)/1000.0
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        gerente.process_events(event)
        
        if estado_atual == GAME and event.type == KEYDOWN:
            if event.key == K_e and (abs(posicao_jogador[0] - porta_pos[0]) < 50 and 
                                     abs(posicao_jogador[1] - porta_pos[1]) < 50):
                estado_atual = CODE_INPUT
                entrada_de_codigo_btn.show()
                enviar_btn.show()
                entrada_de_codigo_btn.focus()
                entrada_de_codigo_btn.set_text("")
            
            if event.key == K_LEFT:
                posicao_jogador[0] = max(0, posicao_jogador[0] - velocidade_jogador)
            if event.key == K_RIGHT:
                posicao_jogador[0] = min(largura_tela - tamanho_jogador, posicao_jogador[0] + velocidade_jogador)
            if event.key == K_UP:
                posicao_jogador[1] = max(0, posicao_jogador[1] - velocidade_jogador)
            if event.key == K_DOWN:
                posicao_jogador[1] = min(altura_tela - tamanho_jogador, posicao_jogador[1] + velocidade_jogador)
            
            if event.key == K_r and estado_atual in [GAME_OVER, VITORIA]:
                resetar_jogo()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == jogar_btn:
                estado_atual = DIFICULDADE
                jogar_btn.hide()
                facil_btn.show()
                normal_btn.show()
                dificil_btn.show()
            
            elif event.ui_element in [facil_btn, normal_btn, dificil_btn]:
                dificuldade = ["easy", "normal", "hard"][[facil_btn, normal_btn, dificil_btn].index(event.ui_element)]
                estado_atual = GAME
                tempo_limite = 120 if dificuldade == "easy" else (60 if dificuldade == "normal" else 30)
                tempo_inicial = time.time()
                facil_btn.hide()
                normal_btn.hide()
                dificil_btn.hide()
                porta_pos = configurar_sala(sala_atual, dificuldade)  # Atualiza a posição da porta
            
            elif event.ui_element == enviar_btn:
                input_code = entrada_de_codigo_btn.get_text().strip()
                
                if input_code == codigo_resolver:
                    if sala_atual < 6:
                        sala_atual += 1
                        posicao_jogador = [largura_tela//2 - tamanho_jogador//2, altura_tela//2 - tamanho_jogador//2]
                        entrada_de_codigo_btn.hide()
                        enviar_btn.hide()
                        porta_pos = configurar_sala(sala_atual, dificuldade)  # Atualiza a posição da porta
                        if som_sucesso:  # Tocar som ao passar de sala
                            som_sucesso.play()
                        estado_atual = GAME
                    elif sala_atual == 6:
                        estado_atual = VITORIA
                        entrada_de_codigo_btn.hide()
                        enviar_btn.hide()
                        reiniciar_btn.show()
                else:
                    # Feedback visual para código errado
                    mensagem_erro = fonte_pequena.render("Código incorreto!", True, vermelho)
                    tela.blit(mensagem_erro, (350, 300))
                    pygame.display.flip()
                    pygame.time.delay(800)
            
            elif event.ui_element == reiniciar_btn:
                resetar_jogo()
    
    # Atualizações contínuas
    if estado_atual == GAME:
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            posicao_jogador[0] = max(0, posicao_jogador[0] - velocidade_jogador)
        if keys[K_RIGHT]:
            posicao_jogador[0] = min(largura_tela - tamanho_jogador, posicao_jogador[0] + velocidade_jogador)
        if keys[K_UP]:
            posicao_jogador[1] = max(0, posicao_jogador[1] - velocidade_jogador)
        if keys[K_DOWN]:
            posicao_jogador[1] = min(altura_tela - tamanho_jogador, posicao_jogador[1] + velocidade_jogador)
        
        # Verificar tempo esgotado
        if time.time() - tempo_inicial > tempo_limite:
            estado_atual = GAME_OVER
            continuar_btn.hide()
            reiniciar_btn.show()
    
    # Renderização
    tela.fill(preto)
    
    if estado_atual == MENU:
        titulo = fonte_larga.render("ESCAPE ROOM", True, verde)
        tela.blit(titulo, (largura_tela//2 - titulo.get_width()//2, 100))
    
    elif estado_atual == DIFICULDADE:
        titulo = fonte_larga.render("SELECIONE A DIFICULDADE", True, branco)
        tela.blit(titulo, (largura_tela//2 - titulo.get_width()//2, 100))
    
    elif estado_atual == GAME:
        desenhar_sala(porta_pos)
    
    elif estado_atual == CODE_INPUT:
        desenhar_sala(porta_pos)
        pygame.draw.rect(tela, (70, 70, 70), (250, 250, 300, 250))
        titulo = fonte_media.render("INSIRA O CÓDIGO", True, branco)
        tela.blit(titulo, (largura_tela//2 - titulo.get_width()//2, 260))
        
        if entrada_de_codigo_btn.get_text():
            texto_codigo = fonte_media.render(entrada_de_codigo_btn.get_text(), True, branco)
            tela.blit(texto_codigo, (largura_tela//2 - texto_codigo.get_width()//2, 320))
    
    elif estado_atual == GAME_OVER:
        mensagem = fonte_larga.render("TEMPO ESGOTADO!", True, vermelho)
        reiniciar = fonte_media.render("Clique em Reiniciar para voltar ao menu", True, branco)
        tela.blit(mensagem, (largura_tela//2 - mensagem.get_width()//2, 200))
        tela.blit(reiniciar, (largura_tela//2 - reiniciar.get_width()//2, 300))
    
    elif estado_atual == VITORIA:
        mensagem = fonte_larga.render("VOCÊ ESCAPOU!", True, dourado)
        parabens = fonte_media.render("Parabéns! Você completou todas as salas.", True, branco)
        reiniciar = fonte_media.render("Clique em Reiniciar para voltar ao menu", True, branco)
        tela.blit(mensagem, (largura_tela//2 - mensagem.get_width()//2, 200))
        tela.blit(parabens, (largura_tela//2 - parabens.get_width()//2, 300))
        tela.blit(reiniciar, (largura_tela//2 - reiniciar.get_width()//2, 350))
    
    gerente.update(time_delta)
    gerente.draw_ui(tela)
    pygame.display.flip()

pygame.quit()
sys.exit()
