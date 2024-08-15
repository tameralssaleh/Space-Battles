import pygame

class Button:
    def __init__(self, text, x, y, width, height, font, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovering = False

    def draw(self, surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mouse_x, mouse_y)
        button_color = self.hover_color if self.hovering else self.color

        pygame.draw.rect(surface, button_color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_x, mouse_y):
        return self.rect.collidepoint(mouse_x, mouse_y)
    
class LevelButton:
    def __init__(self, id, x, y, width, height, font, color, hover_color):
        self.id = id
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.enabled = True
        self.text = self.font.render(str(id), True, (255, 255, 255))

    def draw(self, window):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(window, self.hover_color, self.rect)
        else:
            pygame.draw.rect(window, self.color, self.rect)
        
        window.blit(self.text, (self.rect.x + (self.rect.width - self.text.get_width()) // 2, self.rect.y + (self.rect.height - self.text.get_height()) // 2))

    def is_clicked(self, mouse_x, mouse_y):
        return self.rect.collidepoint(mouse_x, mouse_y)

