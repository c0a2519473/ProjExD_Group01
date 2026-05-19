import pygame as pg
import random
import sys
import os

pg.init()
WIDTH, HEIGHT = 900, 600
os.chdir(os.path.dirname(os.path.abspath(__file__)))
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("大富豪（4人 GUI 完全版）")
clock = pg.time.Clock()

font = pg.font.SysFont("meiryo", 24)

# -------------------------
# カードの準備
# -------------------------
suits = ["♠", "♥", "♦", "♣"]
ranks = list(range(3, 15))  # 3〜A
rank_name = {11:"J", 12:"Q", 13:"K", 14:"A"}

def card_to_text(card):
    s, r = card
    return f"{s}{r if r <= 10 else rank_name[r]}"

def create_deck():
    deck = [(s, r) for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

# -------------------------
# CPUの行動
# -------------------------
def cpu_play(hand, field):
    if len(hand) == 0:
        return None

    if field is None:
        card = min(hand, key=lambda c: c[1])
        hand.remove(card)
        return card

    valid = [c for c in hand if c[1] > field[1]]
    if not valid:
        return None

    card = min(valid, key=lambda c: c[1])
    hand.remove(card)
    return card

# -------------------------
# カード描画（プレイヤー用）
# -------------------------
def draw_card(x, y, card, selected=False):
    s, r = card
    rect = pg.Rect(x, y, 60, 90)

    pg.draw.rect(screen, (255, 255, 255), rect)
    border = (0, 200, 0) if selected else (0, 0, 0)
    pg.draw.rect(screen, border, rect, 3)

    color = (0, 0, 0) if s in ["♠", "♣"] else (200, 0, 0)
    rank_text = str(r) if r <= 10 else rank_name[r]

    # 左上
    text1 = font.render(f"{s}{rank_text}", True, color)
    screen.blit(text1, (x + 3, y + 2))

    # 右下（文字サイズに合わせて調整）
    text2 = font.render(f"{s}{rank_text}", True, color)
    tw, th = text2.get_size()
    screen.blit(text2, (x + 60 - tw - 3, y + 90 - th - 2))

    return rect

# -------------------------
# プレイヤー手札（2段）
# -------------------------
def draw_player_hand(hand):
    rects = []
    for i, card in enumerate(hand):
        row = i // 10
        col = i % 10
        x = 50 + col * 70
        y = 400 + row * 100
        rect = draw_card(x, y, card)
        rects.append((rect, card))
    return rects

# -------------------------
# PASS ボタン
# -------------------------
def draw_pass_button():
    rect = pg.Rect(700, 450, 150, 60)
    pg.draw.rect(screen, (200, 50, 50), rect)
    pg.draw.rect(screen, (255, 255, 255), rect, 3)

    text = font.render("PASS", True, (255, 255, 255))
    screen.blit(text, (740, 470))

    return rect

# -------------------------
# リザルト画面
# -------------------------
rank_name_list = ["あなた", "CPU1", "CPU2", "CPU3"]

def show_result_screen(finished):
    running = True

    if finished[0] == 0:
        result_text = "YOU WIN!"
        result_color = (255, 215, 0)
    else:
        result_text = "YOU LOSE..."
        result_color = (255, 80, 80)

    while running:
        screen.fill((20, 20, 20))

        title = font.render("GAME RESULT", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        result = font.render(result_text, True, result_color)
        screen.blit(result, (WIDTH//2 - result.get_width()//2, 140))

        y = 220
        for i, p in enumerate(finished):
            text = font.render(f"{i+1}位：{rank_name_list[p]}", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 50

        ok_rect = pg.Rect(WIDTH//2 - 75, 500, 150, 50)
        pg.draw.rect(screen, (80, 80, 200), ok_rect)
        pg.draw.rect(screen, (255, 255, 255), ok_rect, 3)

        ok_text = font.render("OK", True, (255, 255, 255))
        screen.blit(ok_text, (WIDTH//2 - ok_text.get_width()//2, 515))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if ok_rect.collidepoint(mx, my):
                    running = False

# -------------------------
# メインゲーム
# -------------------------
def play_game():
    deck = create_deck()

    hands = [
        deck[0:13],
        deck[13:26],
        deck[26:39],
        deck[39:52],
    ]

    for h in hands:
        h.sort(key=lambda c: c[1])

    field = None
    message = ""
    finished = []

    turn = 0
    last_player = 0
    pass_count = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if turn == 0 and event.type == pg.MOUSEBUTTONDOWN:
                mx, my = event.pos

                pass_rect = draw_pass_button()
                if pass_rect.collidepoint(mx, my):
                    message = "あなたはパスした"
                    pass_count += 1
                    turn = 1
                    continue

                rects = draw_player_hand(hands[0])
                for rect, card in rects:
                    if rect.collidepoint(mx, my):
                        if field is None or card[1] > field[1]:
                            hands[0].remove(card)
                            field = card
                            message = f"あなたは {card_to_text(card)} を出した"

                            last_player = 0
                            pass_count = 0

                            turn = 1
                        else:
                            message = "そのカードは出せません"
                        break

        if turn != 0:

            if len(hands[turn]) == 0:
                turn = (turn + 1) % 4
                continue

            pg.time.wait(300)

            card = cpu_play(hands[turn], field)
            if card:
                field = card
                message = f"CPU{turn} は {card_to_text(card)} を出した"
                last_player = turn
                pass_count = 0
            else:
                message = f"CPU{turn} はパスした"
                pass_count += 1

            turn = (turn + 1) % 4

        if pass_count >= 3:
            field = None
            message = "場が流れた！"
            turn = last_player
            pass_count = 0

        for i in range(4):
            if len(hands[i]) == 0 and i not in finished:
                finished.append(i)

        if len(finished) == 3:
            show_result_screen(finished)
            break

        screen.fill((0, 120, 0))

        if field:
            draw_card(WIDTH//2 - 30, HEIGHT//2 - 45, field)

        draw_player_hand(hands[0])

        screen.blit(font.render(f"CPU1：{len(hands[1])}枚", True, (255, 255, 255)), (WIDTH//2 - 80, 30))
        screen.blit(font.render(f"CPU2：{len(hands[2])}枚", True, (255, 255, 255)), (50, 150))
        screen.blit(font.render(f"CPU3：{len(hands[3])}枚", True, (255, 255, 255)), (WIDTH - 180, 150))

        draw_pass_button()

        msg = font.render(message, True, (255, 255, 255))
        screen.blit(msg, (50, 300))

        pg.display.update()
        clock.tick(60)

# -------------------------
# 実行
# -------------------------
play_game()
