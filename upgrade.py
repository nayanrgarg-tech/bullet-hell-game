class Upgrade:

    def __init__(self, name, description, rarity, max_stack, apply_effect):
        self.name = name
        self.description = description
        self.rarity = rarity
        self.max_stack = max_stack
        self.apply_effect = apply_effect
        self.current_stack = 0

    def get_rarity_color(self):
        """Return RGB color based on rarity"""
        if self.rarity == "Common":
            return (255, 255, 255)
        elif self.rarity == "Uncommon":
            return (0, 255, 0)
        elif self.rarity == "Rare":
            return (0, 128, 255)
        elif self.rarity == "Legendary":
            return (255, 128, 0)
        elif self.rarity == "Mythic":
            return (255, 0, 255)
        else:
            return (255, 255, 255)
    
    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_rarity(self):
        return self.rarity

    def get_max_stack(self):
        return self.max_stack