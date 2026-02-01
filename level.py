import pygame
import random

class Level:
    level = 1

    #method to increase level
    @classmethod
    def increase_level(cls):
        cls.level += 1

    #method to get current level
    @classmethod
    def get_level(cls):
        return cls.level
    
    #method to reset level
    @classmethod
    def reset_level(cls):
        cls.level = 1

