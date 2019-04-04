import requests
import pygame
import os


def get_map(coords, size):
    res = requests.get("http://static-maps.yandex.ru/1.x/", params={
        "ll": coords,
        "l": "map",
        'spn': str(size) + ',' + str(size),
        'pt': coords
        })
    # print(res.url)
    return res.content


size = 1
coords = input()
mp = get_map(coords, size)
file = open('map.png', 'wb')
file.write(mp)
file.close()
pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load('map.png'), (0, 0))
pygame.display.flip()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_PAGEDOWN:
                if size <= 32:
                    size = size * 2
            elif e.key == pygame.K_PAGEUP:
                size = size / 2
            elif e.key == pygame.K_UP:
                coords = coords.split(',')
                coords[1] = float(coords[1]) + size / 2
                if coords[1] > 90:
                    coords[1] = 90
                coords[1] = str(coords[1])
                coords = ','.join(coords)

            elif e.key == pygame.K_DOWN:
                coords = coords.split(',')
                coords[1] = float(coords[1]) - size / 2
                if coords[1] < -90:
                    coords[1] = -90
                coords[1] = str(coords[1])
                coords = ','.join(coords)


            elif e.key == pygame.K_LEFT:
                coords = coords.split(',')
                coords[0] = float(coords[0]) - size / 2
                if coords[0] < -180:
                    coords[0] += 360  # round!
                coords[0] = str(coords[0])
                coords = ','.join(coords)

            elif e.key == pygame.K_RIGHT:
                coords = coords.split(',')
                coords[0] = float(coords[0]) + size / 2
                if coords[0] > 180:
                    coords[0] -= 360
                coords[0] = str(coords[0])
                coords = ','.join(coords)
            # print(coords)
            mp = get_map(coords, size)  # errors may be
            os.remove('map.png')
            file = open('map.png', 'wb')
            try:
                file.write(mp)
                file.close()
                screen.blit(pygame.image.load('map.png'), (0, 0))
            except:
                pass
                # print('Не хорошечно')
            pygame.display.flip()
pygame.quit()
os.remove('map.png')

