import pygame
pygame.init()
from skill import *

# colors
BLACK = (  0,   0,   0)
GREY  = (128, 128, 128)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700
CLOCK = pygame.time.Clock()
FPS = 30
TIME_PASSED = CLOCK.tick(FPS) / 1000.0

SCROLL_SPEED = 6

TECH_MECH_SPRITE_WIDTH = 35
TECH_MECH_SPRITE_HEIGHT = 48
ANIMATION_FRAMES = {Walker: 16,
                    Faller: 16,
                    Driller: 4,
                    Jackhammerer: 4,
                    Grappler: 1,
                    Cautioner: 1,
                    Detonator: 1}
GRAPPLER_RANGE = 150

GAME_HOTKEYS = {}
from gameHotkeys import loadGameHotkeys
loadGameHotkeys()
EDITOR_HOTKEYS = {}
NUM_HOTKEY_PANELS = SCREEN_HEIGHT // 50 - 3

SKILLS = [MagnetBoots,
          Energizer,
          Detonator,
          Cautioner,
          Grappler,
          Driller,
          GravityReverser,
          Jackhammerer]
SKILL_PANEL_WIDTH = 50
SKILL_PANEL_HEIGHT = 100
NUMBER_OF_SKILL_PANELS = SCREEN_WIDTH // SKILL_PANEL_WIDTH
SKILL_WIDTH = 27
SKILL_HEIGHT = 26

STRING_SKILL_CONVERSIONS = {"Walker": Walker,
                            "Faller": Faller,
                            "Driller": Driller,
                            "Jackhammerer": Jackhammerer,
                            "Grappler": Grappler,
                            "Cautioner": Cautioner,
                            "Detonator": Detonator,
                            "GravityReverser": GravityReverser,
                            "Energizer": Energizer,
                            "MagnetBoots": MagnetBoots}

SKILL_STRING_CONVERSIONS = {Walker: "Walker",
                            Faller: "Faller",
                            Driller: "Driller",
                            Jackhammerer: "Jackhammerer",
                            Grappler: "Grappler",
                            Cautioner: "Cautioner",
                            Detonator: "Detonator",
                            GravityReverser: "GravityReverser",
                            Energizer: "Energizer",
                            MagnetBoots: "MagnetBoots"}

MULTIPLAYER_COLORS = {0: "green",
                      1: "red"}

TERRAIN_PANEL_LENGTH = 100
NUM_TERRAIN_PANELS = 5

PORT = 50000
