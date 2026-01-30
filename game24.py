"""
24 Card Game - An aesthetic poker card game
Draw 4 cards and use +, -, *, / to make 24!
"""

import pygame
import random
import math
import itertools
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

# High DPI support for macOS
if hasattr(pygame, 'SCALED'):
    FLAGS = pygame.SCALED | pygame.RESIZABLE
else:
    FLAGS = pygame.RESIZABLE

# Screen settings - Higher resolution
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT), FLAGS)
pygame.display.set_caption("24 Card Game")

# Colors - Aesthetic palette
DEEP_PURPLE = (30, 25, 55)
CARD_WHITE = (255, 252, 248)
CARD_CREAM = (252, 250, 245)
GOLD = (255, 200, 50)
SOFT_GOLD = (180, 140, 40)
BRIGHT_GOLD = (255, 220, 100)
CRIMSON = (160, 30, 50)
HEART_RED = (220, 40, 70)
ROYAL_BLUE = (45, 80, 160)
EMERALD = (30, 130, 70)
SOFT_PINK = (255, 180, 200)
DARK_PURPLE = (50, 20, 80)
CLUB_BLACK = (30, 30, 40)
SILVER = (180, 185, 195)
LIGHT_SILVER = (210, 215, 225)
SHADOW = (15, 12, 25)
MIDNIGHT = (20, 15, 35)

# Load system fonts that support card suits
def get_font(size, bold=False):
    """Get a font that works well across systems"""
    font_names = [
        'Arial',
        'Helvetica',
        'DejaVu Sans',
        'Liberation Sans',
        'Verdana',
        'Tahoma',
        None  # Pygame default
    ]
    for name in font_names:
        try:
            if name:
                font = pygame.font.SysFont(name, size, bold=bold)
            else:
                font = pygame.font.Font(None, size)
            return font
        except:
            continue
    return pygame.font.Font(None, size)

# Fonts - Larger for better resolution
TITLE_FONT = get_font(68, bold=True)
CARD_VALUE_FONT = get_font(72, bold=True)
CARD_SUIT_FONT = get_font(56)
CARD_CORNER_FONT = get_font(28, bold=True)
CARD_CORNER_SUIT_FONT = get_font(24)
BUTTON_FONT = get_font(24, bold=True)
INFO_FONT = get_font(30)
SMALL_FONT = get_font(26)
MESSAGE_FONT = get_font(34, bold=True)


class Suit(Enum):
    HEARTS = ("H", HEART_RED)
    DIAMONDS = ("D", HEART_RED)
    CLUBS = ("C", CLUB_BLACK)
    SPADES = ("S", CLUB_BLACK)

    def get_symbol(self):
        symbols = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        return symbols[self.value[0]]


@dataclass
class Card:
    value: int
    suit: Suit

    def get_display_value(self) -> str:
        if self.value == 1:
            return "A"
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        elif self.value == 13:
            return "K"
        return str(self.value)


class AnimatedCard:
    def __init__(self, card: Card, target_x: float, target_y: float, delay: float = 0):
        self.card = card
        self.x = WIDTH // 2
        self.y = -200
        self.target_x = target_x
        self.target_y = target_y
        self.width = 140
        self.height = 196
        self.rotation = random.uniform(-20, 20)
        self.target_rotation = random.uniform(-3, 3)
        self.scale = 0.3
        self.target_scale = 1.0
        self.alpha = 0
        self.glow_intensity = 0
        self.hover = False
        self.flip_progress = 0  # 0 = back, 1 = front
        self.revealed = False
        self.delay = delay
        self.time = 0
        self.bounce = 0

    def update(self, dt: float):
        self.time += dt
        if self.time < self.delay:
            return

        # Smooth movement with easing
        ease = 6 * dt
        self.x += (self.target_x - self.x) * ease
        self.y += (self.target_y - self.y) * ease
        self.rotation += (self.target_rotation - self.rotation) * ease
        self.scale += (self.target_scale - self.scale) * ease
        self.alpha = min(255, self.alpha + 600 * dt)

        # Flip animation
        if self.revealed and self.flip_progress < 1:
            self.flip_progress = min(1, self.flip_progress + 4 * dt)

        # Hover bounce effect
        if self.hover:
            self.bounce = min(1, self.bounce + 8 * dt)
        else:
            self.bounce = max(0, self.bounce - 6 * dt)

        # Glow effect
        target_glow = 1.0 if self.hover else 0.2
        self.glow_intensity += (target_glow - self.glow_intensity) * 8 * dt

    def draw(self, surface: pygame.Surface):
        if self.time < self.delay:
            return

        # Calculate flip scale (card appears to rotate in 3D)
        if self.flip_progress < 0.5:
            flip_scale = 1 - self.flip_progress * 2
            show_front = False
        else:
            flip_scale = (self.flip_progress - 0.5) * 2
            show_front = True

        # Hover bounce offset
        bounce_offset = -15 * self.bounce

        actual_width = max(4, int(self.width * self.scale * flip_scale))
        actual_height = int(self.height * self.scale)

        draw_x = self.x
        draw_y = self.y + bounce_offset

        # Draw glow
        if self.glow_intensity > 0.1:
            glow_size = int(25 * self.glow_intensity)
            for i in range(3):
                glow_alpha = int(40 * self.glow_intensity * (1 - i * 0.3))
                glow_surface = pygame.Surface((actual_width + glow_size * 2 * (i + 1),
                                               actual_height + glow_size * 2 * (i + 1)), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*GOLD[:3], glow_alpha),
                               (0, 0, glow_surface.get_width(), glow_surface.get_height()),
                               border_radius=18)
                surface.blit(glow_surface, (draw_x - actual_width // 2 - glow_size * (i + 1),
                                            draw_y - actual_height // 2 - glow_size * (i + 1)))

        # Draw shadow
        shadow_offset = 10 + int(5 * self.bounce)
        shadow_surface = pygame.Surface((actual_width + 10, actual_height + 10), pygame.SRCALPHA)
        shadow_alpha = 120 - int(40 * self.bounce)
        pygame.draw.rect(shadow_surface, (*SHADOW, shadow_alpha),
                        (0, 0, actual_width + 10, actual_height + 10), border_radius=14)
        surface.blit(shadow_surface, (draw_x - actual_width // 2 - 5 + shadow_offset,
                                      draw_y - actual_height // 2 - 5 + shadow_offset))

        # Create card surface
        card_surface = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)

        if not show_front:
            # Draw card back - elegant pattern
            pygame.draw.rect(card_surface, DARK_PURPLE, (0, 0, actual_width, actual_height), border_radius=12)
            pygame.draw.rect(card_surface, GOLD, (0, 0, actual_width, actual_height), 3, border_radius=12)

            # Inner pattern
            if actual_width > 30:
                margin = 10
                inner_rect = pygame.Rect(margin, margin, actual_width - margin * 2, actual_height - margin * 2)
                pygame.draw.rect(card_surface, SOFT_GOLD, inner_rect, 2, border_radius=8)

                # Diamond pattern in center
                if actual_width > 50:
                    cx, cy = actual_width // 2, actual_height // 2
                    size = min(actual_width, actual_height) // 4
                    points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
                    pygame.draw.polygon(card_surface, SOFT_GOLD, points, 2)
        else:
            # Draw card front
            pygame.draw.rect(card_surface, CARD_WHITE, (0, 0, actual_width, actual_height), border_radius=12)

            # Subtle inner shadow/border
            pygame.draw.rect(card_surface, LIGHT_SILVER, (0, 0, actual_width, actual_height), 2, border_radius=12)

            if actual_width > 50:
                # Draw card content
                symbol = self.card.suit.get_symbol()
                color = self.card.suit.value[1]
                value_text = self.card.get_display_value()

                # Scale fonts based on card size
                font_scale = flip_scale * self.scale

                # Center value - larger and bolder
                value_surf = CARD_VALUE_FONT.render(value_text, True, color)
                scaled_w = int(value_surf.get_width() * font_scale)
                scaled_h = int(value_surf.get_height() * font_scale)
                if scaled_w > 0 and scaled_h > 0:
                    value_surf = pygame.transform.smoothscale(value_surf, (scaled_w, scaled_h))
                    card_surface.blit(value_surf, (actual_width // 2 - value_surf.get_width() // 2,
                                                   actual_height // 3 - value_surf.get_height() // 2))

                # Large suit symbol in center
                suit_surf = CARD_SUIT_FONT.render(symbol, True, color)
                scaled_w = int(suit_surf.get_width() * font_scale)
                scaled_h = int(suit_surf.get_height() * font_scale)
                if scaled_w > 0 and scaled_h > 0:
                    suit_surf = pygame.transform.smoothscale(suit_surf, (scaled_w, scaled_h))
                    card_surface.blit(suit_surf, (actual_width // 2 - suit_surf.get_width() // 2,
                                                  actual_height * 2 // 3 - suit_surf.get_height() // 2))

                # Corner values - top left
                corner_value = CARD_CORNER_FONT.render(value_text, True, color)
                corner_suit = CARD_CORNER_SUIT_FONT.render(symbol, True, color)

                corner_scale = font_scale * 0.9
                if corner_scale > 0.3:
                    cv_w = max(1, int(corner_value.get_width() * corner_scale))
                    cv_h = max(1, int(corner_value.get_height() * corner_scale))
                    cs_w = max(1, int(corner_suit.get_width() * corner_scale))
                    cs_h = max(1, int(corner_suit.get_height() * corner_scale))

                    corner_value = pygame.transform.smoothscale(corner_value, (cv_w, cv_h))
                    corner_suit = pygame.transform.smoothscale(corner_suit, (cs_w, cs_h))

                    # Top left corner
                    card_surface.blit(corner_value, (8, 8))
                    card_surface.blit(corner_suit, (8, 8 + cv_h))

                    # Bottom right corner (rotated)
                    corner_value_rot = pygame.transform.rotate(corner_value, 180)
                    corner_suit_rot = pygame.transform.rotate(corner_suit, 180)
                    card_surface.blit(corner_suit_rot, (actual_width - 8 - cs_w, actual_height - 8 - cv_h - cs_h))
                    card_surface.blit(corner_value_rot, (actual_width - 8 - cv_w, actual_height - 8 - cv_h))

        # Apply alpha
        card_surface.set_alpha(int(self.alpha))

        # Blit card
        surface.blit(card_surface, (draw_x - actual_width // 2, draw_y - actual_height // 2))


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int], icon: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.base_color = color
        self.hover = False
        self.press_scale = 1.0
        self.enabled = True
        self.glow = 0
        self.pulse = 0

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos) and self.enabled
        target_glow = 1.0 if self.hover else 0
        self.glow += (target_glow - self.glow) * 12 * dt
        self.press_scale += (1.0 - self.press_scale) * 15 * dt
        self.pulse += dt * 3

    def draw(self, surface: pygame.Surface):
        # Glow effect
        if self.glow > 0.1 and self.enabled:
            for i in range(3):
                glow_rect = self.rect.inflate(int(25 * self.glow * (i + 1)), int(15 * self.glow * (i + 1)))
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_alpha = int(35 * self.glow * (1 - i * 0.3))
                pygame.draw.rect(glow_surface, (*self.base_color, glow_alpha),
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=25)
                surface.blit(glow_surface, glow_rect.topleft)

        # Shadow
        shadow_rect = self.rect.move(5, 5)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*SHADOW, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=18)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Button body
        if self.enabled:
            color = self.base_color
            if self.hover:
                color = tuple(min(255, c + 40) for c in self.base_color)
        else:
            color = tuple(c // 2 for c in self.base_color)

        scale_offset = int((1 - self.press_scale) * 10)
        scaled_rect = self.rect.inflate(-scale_offset * 2, -scale_offset * 2)

        # Gradient-like effect
        pygame.draw.rect(surface, color, scaled_rect, border_radius=18)

        # Highlight on top
        highlight_rect = pygame.Rect(scaled_rect.x + 4, scaled_rect.y + 4,
                                     scaled_rect.width - 8, scaled_rect.height // 2 - 4)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 30),
                        (0, 0, highlight_rect.width, highlight_rect.height), border_radius=14)
        surface.blit(highlight_surf, highlight_rect.topleft)

        # Border
        border_color = BRIGHT_GOLD if self.enabled else SILVER
        pygame.draw.rect(surface, border_color, scaled_rect, 3, border_radius=18)

        # Text
        text_color = CARD_WHITE if self.enabled else SILVER
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surf = BUTTON_FONT.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)

    def click(self):
        if self.enabled and self.hover:
            self.press_scale = 0.92
            return True
        return False


class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int],
                 velocity_range: float = 150, size_range: Tuple[float, float] = (4, 10)):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, velocity_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(50, 150)
        self.color = color
        self.life = 1.0
        self.size = random.uniform(*size_range)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-200, 200)

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 400 * dt  # Gravity
        self.vx *= 0.99  # Air resistance
        self.life -= dt * 0.7
        self.rotation += self.rot_speed * dt
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * self.life * self.life)
        size = max(1, int(self.size * self.life))

        particle_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)

        # Glowing particle
        pygame.draw.circle(particle_surf, (*self.color, alpha // 2), (size + 2, size + 2), size + 2)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (size + 2, size + 2), size)
        pygame.draw.circle(particle_surf, (255, 255, 255, alpha // 2), (size + 2, size + 2), size // 2)

        surface.blit(particle_surf, (self.x - size - 2, self.y - size - 2))


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1, 3)
        self.brightness = random.uniform(0.3, 1.0)

    def update(self, dt: float):
        self.phase += dt * self.speed

    def draw(self, surface: pygame.Surface):
        brightness = (math.sin(self.phase) + 1) / 2 * self.brightness
        alpha = int(80 + 175 * brightness)
        size = self.size * (0.8 + 0.4 * brightness)

        if size > 0.5:
            # Draw star with glow
            glow_size = int(size * 3)
            if glow_size > 0:
                star_surf = pygame.Surface((glow_size * 2 + 2, glow_size * 2 + 2), pygame.SRCALPHA)
                # Outer glow
                pygame.draw.circle(star_surf, (200, 220, 255, alpha // 4),
                                 (glow_size + 1, glow_size + 1), glow_size)
                # Inner bright point
                pygame.draw.circle(star_surf, (255, 255, 255, alpha),
                                 (glow_size + 1, glow_size + 1), max(1, int(size)))
                surface.blit(star_surf, (self.x - glow_size - 1, self.y - glow_size - 1))


def solve_24(numbers: List[int]) -> Optional[str]:
    """Find a solution to make 24 from 4 numbers using +, -, *, /"""
    ops = ['+', '-', '*', '/']
    ops_display = {'+': '+', '-': '-', '*': '×', '/': '÷'}

    def evaluate(a: float, b: float, op: str) -> Optional[float]:
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if abs(b) < 1e-10:
                return None
            return a / b
        return None

    def format_num(n):
        if float(n) == int(float(n)):
            return str(int(float(n)))
        return str(n)

    # Try all permutations of numbers
    for perm in itertools.permutations(numbers):
        a, b, c, d = [float(x) for x in perm]
        a_s, b_s, c_s, d_s = [str(int(x)) for x in perm]

        # Try all combinations of operators
        for op1, op2, op3 in itertools.product(ops, repeat=3):
            o1, o2, o3 = ops_display[op1], ops_display[op2], ops_display[op3]

            # Structure: ((a op1 b) op2 c) op3 d
            try:
                r1 = evaluate(a, b, op1)
                if r1 is not None:
                    r2 = evaluate(r1, c, op2)
                    if r2 is not None:
                        r3 = evaluate(r2, d, op3)
                        if r3 is not None and abs(r3 - 24) < 1e-9:
                            return f"(({a_s} {o1} {b_s}) {o2} {c_s}) {o3} {d_s}"
            except:
                pass

            # Structure: (a op1 (b op2 c)) op3 d
            try:
                r1 = evaluate(b, c, op2)
                if r1 is not None:
                    r2 = evaluate(a, r1, op1)
                    if r2 is not None:
                        r3 = evaluate(r2, d, op3)
                        if r3 is not None and abs(r3 - 24) < 1e-9:
                            return f"({a_s} {o1} ({b_s} {o2} {c_s})) {o3} {d_s}"
            except:
                pass

            # Structure: (a op1 b) op2 (c op3 d)
            try:
                r1 = evaluate(a, b, op1)
                r2 = evaluate(c, d, op3)
                if r1 is not None and r2 is not None:
                    r3 = evaluate(r1, r2, op2)
                    if r3 is not None and abs(r3 - 24) < 1e-9:
                        return f"({a_s} {o1} {b_s}) {o2} ({c_s} {o3} {d_s})"
            except:
                pass

            # Structure: a op1 ((b op2 c) op3 d)
            try:
                r1 = evaluate(b, c, op2)
                if r1 is not None:
                    r2 = evaluate(r1, d, op3)
                    if r2 is not None:
                        r3 = evaluate(a, r2, op1)
                        if r3 is not None and abs(r3 - 24) < 1e-9:
                            return f"{a_s} {o1} (({b_s} {o2} {c_s}) {o3} {d_s})"
            except:
                pass

            # Structure: a op1 (b op2 (c op3 d))
            try:
                r1 = evaluate(c, d, op3)
                if r1 is not None:
                    r2 = evaluate(b, r1, op2)
                    if r2 is not None:
                        r3 = evaluate(a, r2, op1)
                        if r3 is not None and abs(r3 - 24) < 1e-9:
                            return f"{a_s} {o1} ({b_s} {o2} ({c_s} {o3} {d_s}))"
            except:
                pass

    return None


class Game24:
    def __init__(self):
        self.deck: List[Card] = []
        self.current_cards: List[AnimatedCard] = []
        self.particles: List[Particle] = []
        self.stars: List[Star] = [Star() for _ in range(150)]
        self.draws_remaining = 13
        self.solution: Optional[str] = None
        self.show_solution = False
        self.message = ""
        self.message_timer = 0
        self.message_color = GOLD
        self.time = 0

        # Create buttons - larger and better spaced
        button_y = HEIGHT - 110
        button_width = 200
        button_height = 55
        spacing = 25
        total_width = button_width * 4 + spacing * 3
        start_x = (WIDTH - total_width) // 2

        self.draw_button = Button(start_x, button_y, button_width, button_height,
                                  "Draw Cards", ROYAL_BLUE)
        self.check_button = Button(start_x + button_width + spacing, button_y,
                                   button_width, button_height, "Check", EMERALD)
        self.show_button = Button(start_x + (button_width + spacing) * 2, button_y,
                                  button_width, button_height, "Show Answer", SOFT_GOLD)
        self.new_game_button = Button(start_x + (button_width + spacing) * 3, button_y,
                                      button_width, button_height, "New Game", CRIMSON)

        self.reset_deck()

    def reset_deck(self):
        """Create a fresh deck of 52 cards"""
        self.deck = []
        for suit in Suit:
            for value in range(1, 14):
                self.deck.append(Card(value, suit))
        random.shuffle(self.deck)
        self.draws_remaining = 13
        self.current_cards = []
        self.solution = None
        self.show_solution = False
        self.set_message("Welcome! Click 'Draw Cards' to start", BRIGHT_GOLD, 5)

    def set_message(self, text: str, color: Tuple[int, int, int], duration: float):
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def draw_cards(self):
        """Draw 4 cards from the deck"""
        if len(self.deck) < 4:
            self.set_message("Not enough cards! Start a new game", CRIMSON, 3)
            return

        self.current_cards = []
        self.show_solution = False

        # Calculate card positions - more spread out
        card_spacing = 180
        start_x = (WIDTH - card_spacing * 3) // 2
        card_y = HEIGHT // 2 - 30

        # Draw 4 cards with staggered animation
        numbers = []
        for i in range(4):
            card = self.deck.pop()
            numbers.append(card.value)

            animated_card = AnimatedCard(card, start_x + i * card_spacing, card_y, delay=i * 0.15)
            animated_card.revealed = True  # Start reveal immediately
            self.current_cards.append(animated_card)

        # Find solution
        self.solution = solve_24(numbers)
        self.draws_remaining -= 1

        # Spawn celebration particles from card positions
        for i, card in enumerate(self.current_cards):
            target_x = start_x + i * card_spacing
            for _ in range(15):
                self.particles.append(Particle(target_x, card_y,
                                              random.choice([GOLD, SOFT_GOLD, BRIGHT_GOLD, SOFT_PINK]),
                                              velocity_range=120))

        self.set_message(f"Cards drawn! {self.draws_remaining} draws remaining", BRIGHT_GOLD, 3)

    def check_solution_exists(self):
        """Check if a solution exists"""
        if not self.current_cards:
            self.set_message("Draw cards first!", CRIMSON, 3)
            return

        if self.solution:
            self.set_message("YES! A solution exists!", EMERALD, 4)
            # Celebration particles
            for card in self.current_cards:
                for _ in range(20):
                    self.particles.append(Particle(card.x, card.y,
                                                  random.choice([EMERALD, (100, 255, 150), BRIGHT_GOLD]),
                                                  velocity_range=180))
        else:
            self.set_message("NO solution possible with these cards", CRIMSON, 4)
            for card in self.current_cards:
                for _ in range(10):
                    self.particles.append(Particle(card.x, card.y, CRIMSON, velocity_range=80))

    def reveal_solution(self):
        """Show the solution"""
        if not self.current_cards:
            self.set_message("Draw cards first!", CRIMSON, 3)
            return

        self.show_solution = True
        if self.solution:
            self.set_message(f"Solution: {self.solution} = 24", BRIGHT_GOLD, 10)
            for card in self.current_cards:
                for _ in range(15):
                    self.particles.append(Particle(card.x, card.y, BRIGHT_GOLD, velocity_range=100))
        else:
            self.set_message("No solution exists for these cards", CRIMSON, 5)

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.time += dt

        # Update stars
        for star in self.stars:
            star.update(dt)

        # Update cards
        for card in self.current_cards:
            card.hover = False
            # Larger hit area for hover
            card_rect = pygame.Rect(card.x - card.width // 2 - 10,
                                   card.y - card.height // 2 - 10,
                                   card.width + 20, card.height + 20)
            if card_rect.collidepoint(mouse_pos):
                card.hover = True
            card.update(dt)

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update buttons
        for btn in [self.draw_button, self.check_button, self.show_button, self.new_game_button]:
            btn.update(dt, mouse_pos)

        # Update button states
        self.draw_button.enabled = len(self.deck) >= 4
        self.check_button.enabled = len(self.current_cards) == 4
        self.show_button.enabled = len(self.current_cards) == 4

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt

    def handle_click(self, pos: Tuple[int, int]):
        if self.draw_button.click():
            self.draw_cards()
        elif self.check_button.click():
            self.check_solution_exists()
        elif self.show_button.click():
            self.reveal_solution()
        elif self.new_game_button.click():
            self.reset_deck()
            # Reset particles for new game
            for _ in range(50):
                self.particles.append(Particle(WIDTH // 2, HEIGHT // 2,
                                              random.choice([CRIMSON, GOLD, SOFT_PINK]),
                                              velocity_range=200))

    def draw(self, surface: pygame.Surface):
        # Draw gradient background
        for y in range(0, HEIGHT, 2):
            ratio = y / HEIGHT
            r = int(DEEP_PURPLE[0] * (1 - ratio * 0.5) + MIDNIGHT[0] * ratio * 0.5)
            g = int(DEEP_PURPLE[1] * (1 - ratio * 0.5) + MIDNIGHT[1] * ratio * 0.5)
            b = int(DEEP_PURPLE[2] * (1 - ratio * 0.5) + MIDNIGHT[2] * ratio * 0.5)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
            pygame.draw.line(surface, (r, g, b), (0, y + 1), (WIDTH, y + 1))

        # Draw stars
        for star in self.stars:
            star.draw(surface)

        # Draw title (single, clean title)
        title_text = "24 Card Game"
        title_surf = TITLE_FONT.render(title_text, True, BRIGHT_GOLD)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 65))
        surface.blit(title_surf, title_rect)

        # Draw decorative line under title
        line_width = 300
        line_y = 105
        pygame.draw.line(surface, GOLD, (WIDTH // 2 - line_width // 2, line_y),
                        (WIDTH // 2 + line_width // 2, line_y), 2)
        # Decorative dots
        pygame.draw.circle(surface, GOLD, (WIDTH // 2 - line_width // 2 - 8, line_y), 4)
        pygame.draw.circle(surface, GOLD, (WIDTH // 2 + line_width // 2 + 8, line_y), 4)

        # Draw info
        info_text = f"Cards in deck: {len(self.deck)}   |   Draws remaining: {self.draws_remaining}"
        info_surf = INFO_FONT.render(info_text, True, LIGHT_SILVER)
        info_rect = info_surf.get_rect(center=(WIDTH // 2, 140))
        surface.blit(info_surf, info_rect)

        # Draw instructions
        instructions = "Use  +  -  x  /  to make all 4 cards equal 24   (J=11, Q=12, K=13, A=1)"
        inst_surf = SMALL_FONT.render(instructions, True, SOFT_PINK)
        inst_rect = inst_surf.get_rect(center=(WIDTH // 2, 175))
        surface.blit(inst_surf, inst_rect)

        # Draw cards
        for card in self.current_cards:
            card.draw(surface)

        # Draw card values below cards
        if self.current_cards and all(c.flip_progress > 0.5 for c in self.current_cards):
            values = [str(c.card.value) for c in self.current_cards]
            values_text = "Values:  " + "    ".join(values)
            values_surf = INFO_FONT.render(values_text, True, CARD_WHITE)
            values_rect = values_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 160))

            # Background for values
            bg_rect = values_rect.inflate(40, 16)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*SHADOW, 150), (0, 0, bg_rect.width, bg_rect.height), border_radius=10)
            surface.blit(bg_surf, bg_rect.topleft)
            surface.blit(values_surf, values_rect)

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw message
        if self.message_timer > 0 and self.message:
            # Fade in/out
            if self.message_timer > 0.5:
                alpha = min(255, int((self.message_timer - 0.3) * 400))
            else:
                alpha = int(self.message_timer * 510)

            alpha = max(0, min(255, alpha))

            msg_surf = MESSAGE_FONT.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 200))

            # Message background with glow
            bg_rect = msg_rect.inflate(60, 30)

            # Glow
            glow_surf = pygame.Surface((bg_rect.width + 20, bg_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.message_color, int(alpha * 0.2)),
                           (0, 0, bg_rect.width + 20, bg_rect.height + 20), border_radius=18)
            surface.blit(glow_surf, (bg_rect.x - 10, bg_rect.y - 10))

            # Background
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*SHADOW, int(alpha * 0.85)),
                           (0, 0, bg_rect.width, bg_rect.height), border_radius=15)
            pygame.draw.rect(bg_surf, (*self.message_color, int(alpha * 0.5)),
                           (0, 0, bg_rect.width, bg_rect.height), 2, border_radius=15)
            surface.blit(bg_surf, bg_rect.topleft)

            # Text
            msg_surf.set_alpha(alpha)
            surface.blit(msg_surf, msg_rect)

        # Draw buttons
        self.draw_button.draw(surface)
        self.check_button.draw(surface)
        self.show_button.draw(surface)
        self.new_game_button.draw(surface)


def main():
    clock = pygame.time.Clock()
    game = Game24()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.draw_cards()
                elif event.key == pygame.K_s:
                    game.reveal_solution()
                elif event.key == pygame.K_c:
                    game.check_solution_exists()
                elif event.key == pygame.K_n:
                    game.reset_deck()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                pass

        game.update(dt, mouse_pos)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
