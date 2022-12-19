# Re-implemented in Python
import math
import random
from dataclasses import dataclass


class TileEntityCrop:
    def __init__(self, crop, biome, height, surrounding_blocks):
        self.crop = crop
        self.biome = biome
        self.height = height
        self.surrounding_blocks = surrounding_blocks

        self.growthPoints = 0
        self.nutrientStorage = 0
        self.waterStorage = 0


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
            base *= (100 + (have - need))/100
        else:
            # Make weed
            neg = (need - have) * 4
            if (neg > 100 and random.randint(0, 31) > self.crop.statResistance):
                self.reset() # TODO:
            else:
                base *= (100 - neg) / 100
                base = max(0, base)
        
        return base
    

    def getHumidity(self):
        value = self.getHumidityBiomeBonus()

        # FIXME: Some unknown modification for humidity
        # if (this.field_145850_b.func_72805_g(this.field_145851_c, this.field_145848_d - 1, this.field_145849_e) >= 7) {
        #     value += 2;
        # }

        if self.waterStorage >= 5:
            value += 2
        
        value += (self.waterStorage + 24) / 25
        return value
    

    def getHumidityBiomeBonus(self):
        # TODO: Not sure if this is accurate
        return self.biome.rainfall

    
    def getNutrients(self):
        value = self.getNutrientBiomeBonus()

        # FIXME: Some unknown modification for nutrients
        # for(int i = 2; i < 5 && this.field_145850_b.func_147439_a(this.field_145851_c, this.field_145848_d - i, this.field_145849_e) == Blocks.field_150346_d; ++i) {
        #     ++value;
        # }

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

        # FIXME: Unknown modification for air quality
        # if (this.field_145850_b.func_72937_j(this.field_145851_c, this.field_145848_d + 1, this.field_145849_e)) {
        #     value += 2;
        # }
        return value
        


class CropCard:
    def __init__(self, growth, gain, resistance):
        self.statGrowth = growth
        self.statGain = gain
        self.statResistance = resistance
        self.tier = -1
        self.size = 0


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
    crop = CropStickreed(23, 31, 0)
    biome = Biome('tropical rainforest', 1, 10)
    te = TileEntityCrop(crop, biome, 128, 0)

    te.waterStorage = 200
    te.nutrientStorage = 200

    print(te)
    te.tick()
    print(te)