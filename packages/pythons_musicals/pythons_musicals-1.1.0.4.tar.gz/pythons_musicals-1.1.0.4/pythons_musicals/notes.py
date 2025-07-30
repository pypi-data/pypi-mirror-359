import pygame

class load():
    """Этот класс загружает ноты(введите ноту
do, re etc.),потом ноты готовы к исполнению 
спомощью метода play()."""
    def __init__(self, note):
        pygame.init()
        self.note = note
        self.sound = pygame.mixer.Sound("zvuk-notyi-"+ self.note +".wav")

    def play(self):
        self.sound.play()
