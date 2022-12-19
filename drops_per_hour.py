# Re-implemented in Python
import logging
import math
import random
from dataclasses import dataclass

from termcolor import colored



class TileEntityCrop:
    def __init__(self, crop, biome, height=124, surrounding_blocks=0, can_see_sky=True, dirt_under=3, hydrated_farmland=True):
        self.crop = crop
        self.biome = biome
        self.height = height
        self.surrounding_blocks = surrounding_blocks # num blocks reducing air quality
        self.can_see_sky = can_see_sky
        self.dirt_under = dirt_under # number of dirt under
        self.hydrated_farmland = hydrated_farmland # true/false - is it on hydrated farmland

        self.growthPoints = 0
        self.nutrientStorage = 0
        self.waterStorage = 0

        self.tickCounter = 0


    def __repr__(self):
        return str(vars(self))


    def tick(self):
        tickRate = 20 # TODO: (Low priority)

        self.crop.tick()
        if self.crop.canGrow():
            self.growthPoints += self.calcGrowthRate()

        if (self.growthPoints >= self.crop.growthDuration()):
            self.growthPoints = 0
            self.crop.size += 1
        
        self.nutrientStorage = max(0, self.nutrientStorage - 1)
        self.waterStorage = max(0, self.waterStorage - 1)

        self.tickCounter += 1


    def calcGrowthRate(self):
        base = 3 + random.randint(0, 6) + self.crop.statGrowth

        need = (self.crop.tier - 1) * 4 + self.crop.statGrowth + self.crop.statGain + self.crop.statResistance
        need = max(0, need)

        have = self.crop.weightInfluences(
            self.getHumidity(),
            self.getNutrients(),
            self.getAirQuality() * 5,
        )

        if have >= need:
            base *= (100 + (have - need)) / 100
            base = int(base)
        else:
            # Make weed
            neg = (need - have) * 4

            if neg <= 100:
                logging.debug(colored('Stat too low but cannot grow weed', 'yellow'))
            else:
                logging.debug(colored('Stat too low and can grow weed', 'red'))

            if (neg > 100 and random.randint(0, 31) > self.crop.statResistance):
                self.reset() # TODO:
            else:
                base *= (100 - neg) / 100
                base = int(base)
                base = max(0, base)
        
        return base
    

    def getHumidity(self):
        value = self.getHumidityBiomeBonus()

        if self.hydrated_farmland:
            value += 2

        if self.waterStorage >= 5:
            value += 2
        
        value += (self.waterStorage + 24) / 25
        return value
    

    def getHumidityBiomeBonus(self):
        # TODO: Not sure if this is accurate
        return self.biome.rainfall

    
    def getNutrients(self):
        value = self.getNutrientBiomeBonus()

        dirt_bonus = self.dirt_under
        dirt_bonus = min(3, dirt_bonus)
        dirt_bonus = max(0, dirt_bonus)
        value += self.dirt_under

        value += (self.nutrientStorage + 19) / 20
        return value
    
    
    def getNutrientBiomeBonus(self):
        return self.biome.nutrient


    def getAirQuality(self):
        value = 0

        # If height >= 124, height_modifier is the max of 4
        height_modifier = (self.height - 64) // 15
        height_modifier = min(4, height_modifier)
        height_modifier = max(0, height_modifier)
        value += height_modifier

        fresh = 9
        fresh -= self.surrounding_blocks
        fresh = max(0, fresh)

        value += fresh // 2

        if self.can_see_sky:
            value += 2

        return value
    
    
    def harvestAutomated(self):
        pass
        


class CropCard:
    def __init__(self, growth, gain, resistance):
        self.statGrowth = growth
        self.statGain = gain
        self.statResistance = resistance
        self.tier = -1
        self.size = 0


    def __repr__(self):
        return str(vars(self))


    def weightInfluences(self, humidity, nutrient, air_quality):
        return humidity + nutrient + air_quality
    

    def tick(self):
        pass




class CropStickreed(CropCard):
    def __init__(self, growth, gain, resistance):
        super().__init__(growth, gain, resistance)
        self.name = 'stickreed'
        self.tier = 4

    def canGrow(self):
        return self.size < 4

    def weightInfluences(self, humidity, nutrient, air_quality):
        return humidity*1.2 + nutrient + air_quality*0.8
    
    def growthDuration(self):
        return (400 if self.size == 4 else 100)


@dataclass
class Biome:
    name: str
    rainfall: int
    nutrient: int



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    crop = CropStickreed(23, 31, 0)
    biome = Biome('tropical rainforest', 1, 10)
    te = TileEntityCrop(crop, biome)

    te.waterStorage = 200
    te.nutrientStorage = 200

    print(te)
    while crop.canGrow() and te.tickCounter < 100:
        te.tick()
        print(te)
    print(te.tickCounter)