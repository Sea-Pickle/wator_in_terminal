import time,random,colorsys,os
from vector_class import vec3,vec2
os.system("")
print("\x1b[0;0H\x1b[2J\x1b[?25l")


#== SIM CONFIG ==#
w,h = 30,30
INITIAL_PREY_COUNT = 10
PREY_REPRODUCTION_TIME = 3

INITIAL_PREDATOR_COUNT = 10
INITIAL_PREDATOR_ENERGY_VALUE = 10
PREDATOR_FOOD_VALUE = 4
PREDATOR_REPRODUCTION_ENERGY = 30
PREDATOR_REPRODUCTION_LIFE = 15

PREDATOR_REPRODUCTION_MODE = 1 #0 - energy, 1 - life
MAX_ORGANISMS = 200
STEP_DELAY = 0.02
#== RENDER CONFIG ==#
USE_GENERATIONAL_COLORS = True
GENERATIONAL_COLOR_DRIFT = 50
INITIAL_GENERATIONAL_COLOR = vec3(150,150,150)
MIN_GENERATIONAL_COLOR = vec3(30,30,30)
MAX_GENERATIONAL_COLOR = vec3(180,180,180)
USE_DOUBLEWIDE_CHARS = False
PREY_COLOR = "60f197"
PREY_CHAR = "#"
PREDATOR_COLOR = "ffffff"
PREDATOR_CHAR = "x"

HUNTING_COLOR = "ff0000"
BACKGROUND_COLOR = "222222"
ORGANISM_NAMES = [
    "Prey",
    "Predators"
]
#== CONFIG END ==#
organisms = []
def gen_random_color_rgb(minimum=10,maximum=255):
    color = [random.uniform(minimum,maximum) for _ in range(3)]
    return vec3(color)
def gen_random_color_hsv():
    return vec3(random.uniform(0,1),1,1)
directions = [
    vec2(0,-1),
    vec2(1,0),
    vec2(0,1),
    vec2(-1,0)
]
class organism:
    @classmethod
    def get_prey(cls):
        return [i for i in organisms if i.type == 0]

    @classmethod
    def get_predators(cls):
        return [i for i in organisms if i.type == 1]

    @classmethod
    def get_counts(cls):
        prey_count = len(organism.get_prey())
        predator_count = len(organism.get_predators())
        return prey_count,predator_count

    @classmethod
    def get_positions(cls,type=-1):
        if type==-1:
            return {i.pos:i for i in organisms}
        else:
            return {i.pos:i for i in organisms if i.type == type}

    @classmethod
    def balance(cls):
        prey_count,predator_count = organism.get_counts()
        if prey_count > predator_count:
            prey = organism.get_prey()
            for _ in range(10):
                r = random.randint(0,len(prey)-1)
                prey[r].die()
        if predator_count > prey_count:
            predators = organism.get_predators()
            for _ in range(10):
                r = random.randint(0,len(predators)-1)
                predators[r].die()

    def __init__(self,pos,type):
        self.pos = pos
        self.type = type

        if self.type == 1:
            self.hunting = 0
            self.energy = INITIAL_PREDATOR_ENERGY_VALUE

        elif self.type == 0 and USE_GENERATIONAL_COLORS:
            self.color = INITIAL_GENERATIONAL_COLOR

        self.life = random.randint(0,3)
        organisms.append(self)

    def __repr__(self):
        return f"{ORGANISM_NAMES[self.type]}(pos: {self.pos}, life: {self.life})"

    def die(self):
        if self in organisms:
            organisms.remove(self)

    def reproduce(self):
        new_organism = organism(self.pos,self.type)
        if self.type == 0 and USE_GENERATIONAL_COLORS:
            color_offset = gen_random_color_rgb(-GENERATIONAL_COLOR_DRIFT,GENERATIONAL_COLOR_DRIFT)
            new_organism.color+=color_offset
            new_organism.color=new_organism.color.clamp(MIN_GENERATIONAL_COLOR,MAX_GENERATIONAL_COLOR)
        self.life = 0
        return new_organism

    def update(self):
        organism_positions = organism.get_positions()
        new_positions = [self.pos+i for i in directions]
        unoccupied_positions = [i for i in new_positions if i not in organism_positions]

        if self.type==0: #Prey
            if self.life >= PREY_REPRODUCTION_TIME:
                if len(organisms)<MAX_ORGANISMS:
                    self.reproduce()
            else:
                self.life +=1

            if unoccupied_positions:
                self.pos = random.choice(unoccupied_positions)

        if self.type==1: #Predator
            if PREDATOR_REPRODUCTION_MODE == 0:
                if self.energy >= PREDATOR_REPRODUCTION_ENERGY:
                    if len(organisms)<MAX_ORGANISMS:
                        self.reproduce()
                else:
                    self.life +=1
            elif PREDATOR_REPRODUCTION_MODE == 1:
                if self.life >= PREDATOR_REPRODUCTION_ENERGY:
                    if len(organisms)<MAX_ORGANISMS:
                        self.reproduce()
                else:
                    self.life +=1
            prey_positions = organism.get_positions(0)
            hunting_positions = [i for i in new_positions if i in prey_positions]
            new_positions = [i for i in new_positions if i not in organism_positions]

                
            if self.energy <= 0:
                self.die()

            if hunting_positions:
                new_pos = random.choice(hunting_positions)
                prey = prey_positions[new_pos]
                prey.die()
                self.energy += PREDATOR_FOOD_VALUE
                self.pos = new_pos
                self.hunting = 1
            elif unoccupied_positions:
                self.pos = random.choice(unoccupied_positions)
                self.hunting = 0
            else:
                self.hunting = 0
            self.energy -= 1
        self.pos %= vec2(w,h)


def color_from_rgb(r=0, g=0, b=0, mode="fg", color_array=None):
    if color_array is not None:
        r, g, b = color_array
    r,g,b = int(r),int(g),int(b)
    if mode == "fg":
        mode = 38
    if mode == "bg":
        mode = 48
    return f"\x1b[{mode};2;{r};{g};{b}m"

def color_from_hsv(h=0, s=0, v=0, mode="fg", color_array=None):
    if color_array is not None:
        h, s, v = color_array
    r, g, b = [int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v)]
    return color_from_rgb(r, g, b, mode)

def hex_to_rgb(h):
    return [int(h[i : i + 2], 16) for i in range(0, 6, 2)]

def color_from_hexcode(h, mode="fg"):
    return color_from_rgb(color_array=hex_to_rgb(h), mode=mode)

for i in range(INITIAL_PREY_COUNT):
    new_prey = organism(vec2(random.randint(0,w),random.randint(0,h)),0)

for i in range(INITIAL_PREDATOR_COUNT):
    new_predator = organism(vec2(random.randint(0,w),random.randint(0,h)),1)
    new_predator.energy = random.randint(10,25)

def render():
    if USE_DOUBLEWIDE_CHARS:
        background_ch = color_from_hexcode(BACKGROUND_COLOR)+" .\x1b[0m"
        
    else:
        background_ch = color_from_hexcode(BACKGROUND_COLOR)+".\x1b[0m"
    prey_count,predator_count = organism.get_counts()
    s = []
    organism_positions = organism.get_positions()
    for y in range(h):
        if y!=0:
            s+=["\n"]
        for x in range(w):
            ch = background_ch
            if vec2(x,y) in organism_positions:
                instance = organism_positions[vec2(x,y)]
                if instance.type == 0:
                    if USE_GENERATIONAL_COLORS:
                        color = color_from_rgb(color_array=instance.color)
                    else:
                        color = color_from_hexcode(PREY_COLOR)
                    organism_ch = PREY_CHAR
                if instance.type == 1:
                    if instance.hunting:
                        color = color_from_hexcode(HUNTING_COLOR)
                    else:
                        color = color_from_hexcode(PREDATOR_COLOR)
                    organism_ch = PREDATOR_CHAR
                if USE_DOUBLEWIDE_CHARS:
                    organism_ch*=2  
                ch = f"{color}{organism_ch}\x1b[0m"
            s+=[ch]
    print("".join(s))
    print(f"{ORGANISM_NAMES[0]}: {prey_count}, {ORGANISM_NAMES[1]}: {predator_count}   \x1b[0;0H")
render()

while True:
    for i in organisms:
        i.update()
    if len(organisms)>=MAX_ORGANISMS-10:
        organism.balance()
    render()
    time.sleep(STEP_DELAY)