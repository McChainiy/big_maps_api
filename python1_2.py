import requests
import pygame
import os
import time


def get_map(coords, size):
    #print(coords, size, l)
    res = requests.get("http://static-maps.yandex.ru/1.x/", params={
        "ll": coords,
        "l": l,
        'spn': str(size) + ',' + str(size),
        'pt': point
        })
    return res.content


def find_place(place):
    global coords, point, address
    res = requests.get("http://geocode-maps.yandex.ru/1.x/", params={
        'geocode': place,
        'format': 'json'
    })
    if not res:
        print('такого места нет')
        return
    json_response = res.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
    if not len(toponym) > 0:
        print('такого места нет')
        address = 'ТАКОГО МЕСТА НЕТ!'
        return
    address = toponym[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    if index:
        try:
            address = '{} #{}'.format(address, toponym[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['postal_code'])
        except KeyError:
            address = '{} #{}'.format(address, 'НЕТ ИНДЕКСА')
    toponym = toponym[0]["GeoObject"]
    coords = ','.join(toponym["Point"]["pos"].split())
    point = coords
    draw_screen()


def draw_screen(updatemap=True):
    if updatemap:
        mp = get_map(coords, size)  # errors may be
        os.remove('map.png')
        file = open('map.png', 'wb')
        try:
            file.write(mp)
            file.close()
        except:
            pass
    try:
        screen.blit(pygame.image.load('map.png'), (0, 0))
    except Exception:
        pass
    buttons.draw(screen)
    push_buttons.draw(screen)
    for box in input_boxes:
        box.draw(screen)
    font = pygame.font.SysFont('visitor', 18)
    txt = font.render(address, True, WHITE)
    screen.blit(txt, (3, 0))
    pygame.display.flip()


class Button(pygame.sprite.Sprite):
    def __init__(self, group, name, coords, width, height, turned=None):
        global l
        if group != None:
            super().__init__(group)
        self.width = width
        self.height = height
        self.name = name
        self.turned = turned
        if turned:
            l = name
        self.do_image()
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def do_image(self):
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        clr = GREEN if self.turned else GREY
        self.image.fill(clr)
        font = pygame.font.SysFont('visitor', 40)
        text = font.render(self.name, 1, (255, 255, 255))
        self.image.blit(text, (1, 1))

    def get_click(self, pos):
        global l, index
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.height + self.rect.y:
            if self.name == 'map' or self.name == 'sat':
                for i in buttons:
                    if i.name in ['map', 'sat']:
                        i.turned = False
                        i.do_image()
                self.turned = not self.turned
                if self.turned:
                    l = self.name
                self.do_image()
                return True
            elif self.name == 'Индекс':
                self.turned = not self.turned
                index = self.turned
                self.do_image()
                return True
        return False


class PushButton(pygame.sprite.Sprite):
    def __init__(self, group, name, coords, width, height, clr):
        super().__init__(group)
        self.width = width
        self.height = height
        self.name = name
        self.clr = clr
        self.do_image()
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def do_image(self):
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.image.fill(self.clr)
        font = pygame.font.SysFont('visitor', 36)
        text = font.render(self.name, 1, (255, 255, 255))
        self.image.blit(text, (1, 1))

    def get_click(self, pos):
        global point
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.height + self.rect.y:
            if self.name == 'Найти':
                return [input_box1.get_text(), 'text']
            elif self.name == 'Очистить':
                input_box1.get_text() #очищение текстового поля
                point = ''
                return [False, 'clear']
        return [False, False]


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.get_text()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)
        return False

    def get_text(self):
        text = self.text
        self.text = ''
        self.txt_surface = FONT.render(self.text, True, self.color)
        return text

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        whiterect = pygame.Rect(self.rect.x + 1, self.rect.y + 1, self.rect.width - 2, self.rect.height - 2)
        pygame.draw.rect(screen, WHITE, whiterect, 0)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)



l = 'sat'
pygame.init()

buttons = pygame.sprite.Group()
push_buttons = pygame.sprite.Group()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = pygame.Color('green')
GREY = pygame.Color('grey')
BLUE = pygame.Color('blue1')
YELLOW = pygame.Color('yellow3')

size = 1
#coords = input()
coords = '37.572260,55.794994'
address = ''
index = False
point = coords
mp = get_map(coords, size)
file = open('map.png', 'wb')
file.write(mp)
file.close()
screen = pygame.display.set_mode((600, 450))
Button(buttons, 'sat', [0, 250], 80, 40, turned=True)
Button(buttons, 'map', [0, 292], 80, 40)

Button(buttons, 'Индекс', [35, 180], 110, 40)

findbtn = PushButton(push_buttons, 'Найти', [0, 135], 80, 42, YELLOW)
clrbtn = PushButton(push_buttons, 'Очистить', [82, 135], 118, 42, BLUE)
input_box1 = InputBox(0, 100, 140, 32)
input_boxes = [input_box1]

draw_screen()

pygame.display.flip()
running = True
while running:
    for e in pygame.event.get():
        action_to_update_map = False
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_PAGEDOWN:
                if size <= 32:
                    size = size * 2
                action_to_update_map = True

            elif e.key == pygame.K_PAGEUP:
                size = size / 2
                action_to_update_map = True

            elif e.key == pygame.K_UP:
                coords = coords.split(',')
                coords[1] = float(coords[1]) + size / 2
                if coords[1] > 90:
                    coords[1] -= 180
                coords[1] = str(coords[1])
                coords = ','.join(coords)
                action_to_update_map = True

            elif e.key == pygame.K_DOWN:
                coords = coords.split(',')
                coords[1] = float(coords[1]) - size / 2
                if coords[1] < -90:
                    coords[1] += 180
                coords[1] = str(coords[1])
                coords = ','.join(coords)
                action_to_update_map = True

            elif e.key == pygame.K_LEFT:
                coords = coords.split(',')
                coords[0] = float(coords[0]) - size / 2
                if coords[0] < -180:
                    coords[0] += 360  # round!
                coords[0] = str(coords[0])
                coords = ','.join(coords)
                action_to_update_map = True

            elif e.key == pygame.K_RIGHT:
                coords = coords.split(',')
                coords[0] = float(coords[0]) + size / 2
                if coords[0] > 180:
                    coords[0] -= 360
                coords[0] = str(coords[0])
                coords = ','.join(coords)
                action_to_update_map = True
            if action_to_update_map:
                draw_screen()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            for i in buttons:
                if i.get_click(e.pos):
                    print('zasdf')
                    find_place(address)
                    draw_screen(False)
                    break
            for i in push_buttons:
                answ = i.get_click(e.pos)
                if answ[1] == 'text':
                    for box in input_boxes:
                        box.update()
                        box.draw(screen)
                    find_place(answ[0])
                    draw_screen()
                    break
                elif answ[1] == 'clear':
                    for box in input_boxes:
                        box.update()
                        box.draw(screen)
                    draw_screen()

        for box in input_boxes:
            text = box.handle_event(e)
            box.update()
            box.draw(screen)
            if text:
                find_place(text)
                break

        screen.fill(WHITE)

        draw_screen(False)
pygame.quit()
os.remove('map.png')

#37.572260,55.794994