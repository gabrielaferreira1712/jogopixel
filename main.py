import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Tela
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Super Meow Bros - Desafio Python")
FPS = 60

# Paleta de Cores Fofa & Retrô
CEU_PASTEL = (173, 216, 250)
NUVEM_BRANCA = (255, 250, 250)
GRAMA_VERDE = (119, 221, 119)
TERRA_MARROM = (181, 137, 112)
LARANJA_GATO = (255, 165, 79)
CREME_GATO = (255, 235, 205)
ROSA_ORELHA = (255, 182, 193)
AZUL_PEIXE = (100, 180, 255)
DOURADO_PEIXE = (255, 215, 0)
BLOCO_AMARELO = (255, 204, 102)
BLOCO_BORDA = (160, 100, 40)
CINZA_RATO = (140, 140, 150)
PRETO = (30, 30, 30)
VERMELHO_VIDA = (255, 90, 110)

# Fontes
FONTE_PIXEL = pygame.font.SysFont("Courier New", 24, bold=True)
FONTE_TITULO = pygame.font.SysFont("Courier New", 42, bold=True)

# --- MATRIZES DE PIXEL ART (Desenhadas via código!) ---
SPRITE_GATO = [
    "..L......L..",
    ".LPL....LPL.",
    ".LLLLLLLLLL.",
    "LLLLLLLLLLLL",
    "LLPLLLLLLPLL",
    "LLLLLLLLLLLL",
    "LL.LLLLLL.LL",
    "LLLL.PP.LLLL",
    ".LLLLLLLLLL.",
    "..CCCCCCCC..",
    ".LLLLLLLLLL.",
    ".LL.LLLL.LL.",
]

SPRITE_PEIXE = [
    ".......BB...",
    "......BBBB..",
    "..BBBBBBBBB.",
    ".BBBBBBBBBBB",
    "BBBBBBPBBBBB",
    ".BBBBBBBBBBB",
    "..BBBBBBBBB.",
    "......BBBB..",
    ".......BB...",
]

SPRITE_CORACAO = [
    ".VV..VV.",
    "VVVVVVVV",
    "VVVVVVVV",
    ".VVVVVV.",
    "..VVVV..",
    "...VV...",
]

def desenhar_pixel_art(superficie, matriz, x, y, escala, mapa_cores, inverter=False):
    for linha_idx, linha in enumerate(matriz):
        linha_atual = linha[::-1] if inverter else linha
        for col_idx, char in enumerate(linha_atual):
            if char in mapa_cores:
                cor = mapa_cores[char]
                rect = pygame.Rect(x + col_idx * escala, y + linha_idx * escala, escala, escala)
                pygame.draw.rect(superficie, cor, rect)

# --- CLASSES DO JOGO ---
class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.vel_y = 0
        self.velocidade = 5
        self.pulando = False
        self.olhando_direita = True
        self.vidas = 3
        self.pontos = 0
        self.invencivel = 0

    def atualizar(self, plataformas, blocos_surpresa, peixes):
        teclas = pygame.key.get_pressed()
        dx = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -self.velocidade
            self.olhando_direita = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = self.velocidade
            self.olhando_direita = True
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and not self.pulando:
            self.vel_y = -15
            self.pulando = True

        # Gravidade
        self.vel_y += 0.8
        if self.vel_y > 12:
            self.vel_y = 12
        dy = self.vel_y

        # Colisão Horizontal
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        for plat in plataformas + blocos_surpresa:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                elif dx < 0:
                    self.rect.left = plat.rect.right

        # Colisão Vertical
        self.rect.y += dy
        self.pulando = True
        for plat in plataformas:
            if self.rect.colliderect(plat.rect):
                if dy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.pulando = False
                elif dy < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        # Colisão com Blocos Surpresa (Estilo Bloco ? do Mario)
        for bloco in blocos_surpresa:
            if self.rect.colliderect(bloco.rect):
                if dy > 0:
                    self.rect.bottom = bloco.rect.top
                    self.vel_y = 0
                    self.pulando = False
                elif dy < 0:
                    self.rect.top = bloco.rect.bottom
                    self.vel_y = 0
                    if not bloco.usado:
                        bloco.usado = True
                        # Faz aparecer um peixinho dourado em cima do bloco!
                        peixes.append(Peixe(bloco.rect.x + 6, bloco.rect.y - 40, dourado=True))

        if self.invencivel > 0:
            self.invencivel -= 1

    def desenhar(self, tela, camera_x):
        if self.invencivel % 10 < 5:  # Efeito piscar ao levar dano
            cores = {'L': LARANJA_GATO, 'P': ROSA_ORELHA, 'C': CREME_GATO}
            desenhar_pixel_art(
                tela, SPRITE_GATO, self.rect.x - camera_x, self.rect.y, 4, cores, not self.olhando_direita
            )

class Plataforma:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)

    def desenhar(self, tela, camera_x):
        r = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(tela, TERRA_MARROM, r)
        pygame.draw.rect(tela, GRAMA_VERDE, (r.x, r.y, r.width, 12))
        pygame.draw.rect(tela, PRETO, r, 2)

class BlocoSurpresa:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 44)
        self.usado = False

    def desenhar(self, tela, camera_x):
        r = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        cor = (180, 170, 160) if self.usado else BLOCO_AMARELO
        pygame.draw.rect(tela, cor, r)
        pygame.draw.rect(tela, BLOCO_BORDA, r, 4)
        if not self.usado:
            texto = FONTE_PIXEL.render("?", True, BLOCO_BORDA)
            tela.blit(texto, (r.x + 14, r.y + 8))

class Peixe:
    def __init__(self, x, y, dourado=False):
        self.rect = pygame.Rect(x, y, 36, 27)
        self.dourado = dourado
        self.coletado = False

    def desenhar(self, tela, camera_x):
        if not self.coletado:
            cor_corpo = DOURADO_PEIXE if self.dourado else AZUL_PEIXE
            cores = {'B': cor_corpo, 'P': PRETO}
            desenhar_pixel_art(tela, SPRITE_PEIXE, self.rect.x - camera_x, self.rect.y, 3, cores)

class InimigoRato:
    def __init__(self, x, y, limite_esq, limite_dir):
        self.rect = pygame.Rect(x, y, 40, 28)
        self.vel = 2
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir

    def atualizar(self):
        self.rect.x += self.vel
        if self.rect.left <= self.limite_esq or self.rect.right >= self.limite_dir:
            self.vel *= -1

    def desenhar(self, tela, camera_x):
        r = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.ellipse(tela, CINZA_RATO, r)
        pygame.draw.circle(tela, ROSA_ORELHA, (r.x + 8, r.y + 4), 6)
        pygame.draw.circle(tela, ROSA_ORELHA, (r.x + 32, r.y + 4), 6)
        pygame.draw.circle(tela, PRETO, (r.x + (30 if self.vel > 0 else 10), r.y + 12), 3)

# --- FUNÇÃO PRINCIPAL ---
def main():
    clock = pygame.time.Clock()
    gato = Jogador(100, 400)

    # Construção da Fase (Estilo Mario)
    plataformas = [
        Plataforma(0, 520, 900, 80),
        Plataforma(1000, 520, 800, 80),
        Plataforma(1900, 520, 900, 80),
        Plataforma(300, 380, 160, 25),
        Plataforma(620, 300, 180, 25),
        Plataforma(1150, 380, 200, 25),
        Plataforma(1480, 280, 180, 25),
        Plataforma(2050, 370, 220, 25),
    ]

    blocos_surpresa = [
        BlocoSurpresa(220, 360),
        BlocoSurpresa(690, 170),
        BlocoSurpresa(1230, 240),
        BlocoSurpresa(2140, 230),
    ]

    peixes = [
        Peixe(340, 340), Peixe(390, 340),
        Peixe(660, 260), Peixe(720, 260),
        Peixe(1050, 480), Peixe(1100, 480),
        Peixe(1520, 240), Peixe(1580, 240),
        Peixe(2100, 330), Peixe(2170, 330),
    ]

    inimigos = [
        InimigoRato(450, 492, 350, 850),
        InimigoRato(1200, 492, 1050, 1750),
        InimigoRato(2000, 492, 1920, 2500),
    ]

    bandeira_final = pygame.Rect(2650, 320, 20, 200)
    estado = "JOGANDO"

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and estado != "JOGANDO":
                if evento.key == pygame.K_r:
                    main()  # Reinicia o jogo

        if estado == "JOGANDO":
            gato.atualizar(plataformas, blocos_surpresa, peixes)

            # Câmera segue o gatinho
            camera_x = max(0, gato.rect.x - 250)

            # Coletar Peixes (substituindo cogumelos/moedas)
            for peixe in peixes:
                if not peixe.coletado and gato.rect.colliderect(peixe.rect):
                    peixe.coletado = True
                    gato.pontos += 50 if peixe.dourado else 10
                    if peixe.dourado and gato.vidas < 5:
                        gato.vidas += 1  # Peixe dourado dá +1 vida!

            # Atualizar Inimigos
            for rato in inimigos[:]:
                rato.atualizar()
                if gato.rect.colliderect(rato.rect):
                    # Se pular em cima do rato, derrota ele!
                    if gato.vel_y > 0 and gato.rect.bottom <= rato.rect.centery + 10:
                        inimigos.remove(rato)
                        gato.vel_y = -10
                        gato.pontos += 30
                    elif gato.invencivel == 0:
                        gato.vidas -= 1
                        gato.invencivel = 60

            # Verificar queda no buraco ou fim das vidas
            if gato.rect.y > ALTURA:
                gato.vidas = 0
            if gato.vidas <= 0:
                estado = "GAME_OVER"

            # Verificar Vitória (Arranhador / Bandeira Final)
            if gato.rect.colliderect(bandeira_final):
                estado = "VITORIA"

        # --- DESENHO NA TELA ---
        TELA.fill(CEU_PASTEL)

        # Nuvens fofas no fundo
        for nx in range(100, 3000, 450):
            pygame.draw.circle(TELA, NUVEM_BRANCA, (nx - int(camera_x * 0.5), 100), 30)
            pygame.draw.circle(TELA, NUVEM_BRANCA, (nx + 30 - int(camera_x * 0.5), 90), 35)
            pygame.draw.circle(TELA, NUVEM_BRANCA, (nx + 60 - int(camera_x * 0.5), 100), 30)

        for plat in plataformas:
            plat.desenhar(TELA, camera_x)
        for bloco in blocos_surpresa:
            bloco.desenhar(TELA, camera_x)
        for peixe in peixes:
            peixe.desenhar(TELA, camera_x)
        for rato in inimigos:
            rato.desenhar(TELA, camera_x)

        # Bandeira Final (Poste com Peixe no topo)
        pygame.draw.rect(TELA, PRETO, (bandeira_final.x - camera_x, bandeira_final.y, 8, 200))
        pygame.draw.polygon(TELA, ROSA_ORELHA, [
            (bandeira_final.x + 8 - camera_x, bandeira_final.y),
            (bandeira_final.x + 68 - camera_x, bandeira_final.y + 20),
            (bandeira_final.x + 8 - camera_x, bandeira_final.y + 40)
        ])

        gato.desenhar(TELA, camera_x)

        # HUD (Pontuação e Vidas)
        texto_pontos = FONTE_PIXEL.render(f"PEIXES: {gato.pontos}", True, PRETO)
        TELA.blit(texto_pontos, (20, 20))

        for i in range(gato.vidas):
            desenhar_pixel_art(TELA, SPRITE_CORACAO, 20 + i * 35, 55, 3, {'V': VERMELHO_VIDA})

        # Telas de Fim de Jogo
        if estado == "GAME_OVER":
            msg = FONTE_TITULO.render("MIAU... FIM DE JOGO!", True, VERMELHO_VIDA)
            sub = FONTE_PIXEL.render("Pressione 'R' para tentar novamente", True, PRETO)
            TELA.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 220))
            TELA.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 280))
        elif estado == "VITORIA":
            msg = FONTE_TITULO.render("PURR-FEITO! VOCE VENCEU!", True, (40, 160, 80))
            sub = FONTE_PIXEL.render(f"Pontuacao Final: {gato.pontos} | Pressione 'R'", True, PRETO)
            TELA.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 220))
            TELA.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 280))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()