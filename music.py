import pygame, pygame.locals, random, os

path = os.path.split(os.path.abspath(__file__))[0]+"/Resources/Sounds/"

pygame.init()
def play_sound(sound):
    if pygame.mixer:
        pygame.mixer.music.load(path+sound)
        pygame.mixer.music.play(1)
def start_background_music(music):
    if pygame.mixer:
        pygame.mixer.music.load(path+"Background Music/"+music)
        pygame.mixer.music.play(-1)
