init -10 python:
    from enum import Flag, auto, Enum

    IMAGE_SIZE = 48

    class Params(Flag):
        NONE = 0
        IS_INTERACT = auto()
        DEFAULT = NONE
    
    class DoorSide(Enum):
        CURRENT = 0
        RIGHT = 1
        LEFT = 2

    class Direction(str, Enum):
        RIGHT = "right"
        UP = "up"
        LEFT = "left"
        DOWN = "down"
        NONE = "down"

    class SourceFile(Enum):
        def __init__(self, tag, file):
            self.file = file
            self.tag = tag
        
    class CharacterSourceFiles(SourceFile):
        CHARACTER_PREMADE_17 = "premade 17", "character/Premade_Character_48x48_17.png"
    
    class RoomSourceFiles(SourceFile):
        WALLS = "walls", "room/Room_Builder_3d_walls_48x48.png"
        FLOORS = "floors", "room/Room_Builder_Floors_48x48.png"

    class RoomTile(Enum):
        def __init__(self, char, loc):
            self.c = char
            self.x = loc[0]
            self.y = loc[1]
        
        @classmethod
        def getTile(cls, char):
            return [c for c in list(cls) if c.c == char][0]

    FLOOR_THEME_SIZE = (4,2)

    """
    012
    345
    """
    class FloorTiles(RoomTile):
        VOID = ' ', (-1,-1)
        TOP_LEFT = '0', (0,0)
        TOP = '1', (1,0)
        TOP_RIGHT = '2', (2,0)
        LEFT = '3', (0,1)
        MID = '4', (1,1)
        DARK = '5', (2,1)

    class FloorThemes(RoomTile):
        WOOD = 'wood', (0,5)

    WALL_THEME_SIZE = (8,7)

    """
    adjpPJDV
    bekqQKEW
    cflrRLFX
    AgmsSMGv
    BhntTNHw
    CiouUOIx
    """
    class WallTiles(RoomTile):
        VOID                            = ' ', (-1,-1)
        TOP_END_LEFT                    = 'a', (0,0)
        BOT_END_LEFT                    = 'b', (0,1)
        MID_END_LEFT                    = 'c', (0,2)
        TOP_END_RIGHT                   = 'A', (0,3)
        BOT_END_RIGHT                   = 'B', (0,4)
        MID_END_RIGHT                   = 'C', (0,5)
        TOP_LEFT_CORNER_OVERLAP_SHALLOW = 'd', (1,0)
        TOP_LEFT_CORNER_SHALLOW         = 'e', (1,1)
        MID_LEFT_CORNER_SHALLOW         = 'f', (1,2)
        BOT_LEFT_CORNER_SHALLOW         = 'g', (1,3)
        TOP_LEFT_EXTRUDE                = 'h', (1,4)
        BOT_LEFT_EXTRUDE                = 'i', (1,5)
        TOP_LEFT_CORNER                 = 'j', (2,0)
        BOT_LEFT_CORNER                 = 'k', (2,1)
        LEFT                            = 'l', (2,2)
        TOP_LEFT_ISLAND                 = 'm', (2,3)
        BOT_LEFT_ISLAND                 = 'n', (2,4)
        LEFT_BOT_CORNER                 = 'o', (2,5)
        TOP_LEFT_CORNER_OVERLAP         = 'p', (3,0)
        LEFT_BOT_CORNER_OVERLAP         = 'q', (3,1)
        TOP                             = 'r', (3,2)
        BOT                             = 's', (3,3)
        MID_END                         = 't', (3,4)
        BOT_B                           = 'u', (3,5)
        TOP_RIGHT_CORNER_OVERLAP        = 'P', (4,0)
        BOT_RIGHT_CORNER_OVERLAP        = 'Q', (4,1)
        TOP_1                           = 'R', (4,2)
        BOT_1                           = 'S', (4,3)
        MID                             = 'T', (4,4)
        BOT_B_1                         = 'U', (4,5)
        TOP_RIGHT_CORNER                = 'J', (5,0)
        BOT_RIGHT_CORNER                = 'K', (5,1)
        RIGHT                           = 'L', (5,2)
        TOP_RIGHT_ISLAND                = 'M', (5,3)
        BOT_RIGHT_ISLAND                = 'N', (5,4)
        RIGHT_BOT_CORNER                = 'O', (5,5)
        TOP_RIGHT_CORNER_OVERLAP_SHALLOW= 'D', (6,0)
        TOP_RIGHT_CORNER_SHALLOW        = 'E', (6,1)
        MID_RIGHT_CORNER_SHALLOW        = 'F', (6,2)
        BOT_RIGHT_CORNER_SHALLOW        = 'G', (6,3)
        TOP_RIGHT_EXTRUDE               = 'H', (6,4)
        BOT_RIGHT_EXTRUDE               = 'I', (6,5)
        TOP_RIGHT_ISLAND_SHALLOW        = 'V', (7,0)
        MID_RIGHT_ISLAND_SHALLOW        = 'W', (7,1) 
        BOT_RIGHT_ISLAND_SHALLOW        = 'X', (7,2)
        TOP_LEFT_ISLAND_SHALLOW         = 'v', (7,3)
        MID_LEFT_ISLAND_SHALLOW         = 'w', (7,4) 
        BOT_LEFT_ISLAND_SHALLOW         = 'x', (7,5)

    class WallThemes(RoomTile):
        BROWN = 'brown', (0,0)

    class CompositeAnimation:
        def __init__(self, name, imageAnimation):
            self.name=name
            self.imageAnimations = [imageAnimation]

        def add(self, *imageAnimations):
            self.imageAnimations += imageAnimations
            return self
        
        def buildDynamic(self, dynamicSourceFile):
            top = []
            bottom = []
            left = []
            right = []
            frames = []
            directions = self.imageAnimations[0].directions
            images = {}
            for anim in self.imageAnimations:
                frames.append(anim.frames)
                top.append(anim.yoffset)
                bottom.append(anim.yoffset + anim.height)
                left.append(anim.xoffset)
                right.append(anim.xoffset + anim.width)
                directions = [d for d in directions if d in anim.directions]
                images[anim] = anim.buildDynamic(dynamicSourceFile)

            frames = lcm(*frames)
            top = min(*top)
            bottom = max(*bottom)
            left = min(*left)
            right = max(*right)
            width = right-left
            height = bottom-top

            displayables = {}
            for dir in directions:
                displayables[dir] = {}
                for i in range(frames):
                    dis = []
                    for anim in self.imageAnimations:
                        dis += [(anim.xoffset, anim.yoffset), images[anim][dir][i % anim.frames]]
                    display[dir].append(Composite((width,height), *dis))
            return displayables


    class AnimData:
        def __init__(self,d=[Direction.NONE], f=1, x=0, y=0, r=0, c=0, w=IMAGE_SIZE, h=IMAGE_SIZE, t=0.16, xoffset=0, yoffset=0, pxls_tl = False):
            self.frames = f
            self.loc = [0, 0, w, h]
            self.x = 0
            self.y = 0
            self.df = t
            if pxls_tl is True:
                self.x = x
                self.y = y
            else:
                self.x = c * w
                self.y = r * h
            self.width = w
            self.height = h
            self.yoffset = yoffset
            self.xoffset = xoffset
            self.directions = d

    class ImageAnimation(Enum):
        def __init__(self, tag, data: AnimData):
            self.tag = tag
            self.frames = data.frames
            self.x = data.x
            self.y = data.y
            self.df = data.df
            self.width = data.width
            self.height = data.height
            self.yoffset = data.yoffset
            self.xoffset = data.xoffset
            self.directions = data.directions
            
        def buildDynamic(self, dynamicSourceFile):
            displayables = {}
            frame = 0
            for dir in self.directions:
                displayables[dir] = []
                for i in range(self.frames):
                    loc = (self.x + self.width * frame, self.y, self.width, self.height)
                    displayables[dir].append(Crop(loc, dynamicSourceFile))
                    frame += 1
            return displayables

    class CharAnimData(AnimData):
        def __init__(self, d=[Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN], h=IMAGE_SIZE*2, **kwargs):
            super().__init__(d=d, h=h, **kwargs)

    class CharacterAnimations(ImageAnimation):
        DEFAULT     = "",               CharAnimData()
        IDLE        = "idle",           CharAnimData(f=6, r=1)
        WALK        = "walk",           CharAnimData(f=6, r=2)
        SLEEP       = "sleep",          CharAnimData(f=6, r=3, d=[Direction.DOWN])
        SITTING     = "sitting",        CharAnimData(f=6, r=4, d=[Direction.RIGHT, Direction.LEFT])
        SIT         = "sit",            CharAnimData(f=6, r=5, d=[Direction.RIGHT, Direction.LEFT])
        PHONE       = "phone",          CharAnimData(f=12, r=6, d=[Direction.DOWN])
        PHONE_START = "phone start",    CharAnimData(f=3, r=6, d=[Direction.DOWN])
        PHONE_LOOP  = "phone loop",     CharAnimData(f=6, r=6, c=3, d=[Direction.DOWN])
        PHONE_END   = "phone end",      CharAnimData(f=3, r=6, c=9, d=[Direction.DOWN])
        BOOK        = "book",           CharAnimData(f=12, r=7, d=[Direction.DOWN])
        BOOK_LOOP   = "book loop",      CharAnimData(f=6, r=7, d=[Direction.DOWN])
        BOOK_FLIP   = "book flip",      CharAnimData(f=6, r=7, c=6, d=[Direction.DOWN])
        PUSH_TROLLEY= "push_trolley",   CharAnimData(f=6, r=8)
        TROLLEY     = "trolley",        CharAnimData(f=3, r=8, c=12, w=IMAGE_SIZE*2, yoffset=IMAGE_SIZE, xoffset=IMAGE_SIZE)
        PICK_UP     = "pick_up",        CharAnimData(f=12, r=9)
        GIFT        = "gift",           CharAnimData(f=10, r=10)
        LIFT        = "lift",           CharAnimData(f=14, r=11)
        THROW       = "throw",          CharAnimData(f=14, r=12)
        HIT         = "hit",            CharAnimData(f=6, r=13)
        PUNCH       = "punch",          CharAnimData(f=6, r=14)
        STAB        = "stab",           CharAnimData(f=6, r=15)
        KNIFE       = "knife",          CharAnimData(f=6, r=15, c=24)
        GUN_GRAB    = "gun grab",       CharAnimData(f=4, r=16)
        GUN_IDLE    = "gun idle",       CharAnimData(f=6, r=17)
        GUN_SHOOT   = "gun shoot",      CharAnimData(f=3, r=18)
        HURT        = "hurt",           CharAnimData(f=3, r=19)
    


    class Director:
        def __init__(self, dt=None):
            self.dt = dt
        
        def onLoop(self, trans, st, at):
            pass

    class AnimationDirector(Director):
        def __init__(self):
            super().__init__()
            self.displayables = {}
            self.displayable = None
            self.imageAnimations = []
            self.sourceFiles = []
            self.dir = Direction.DOWN
            self.frame = 0
            self.anim = None
            self.source = None
            self.queue = []
            self.redrawTime = 0.01

        def __setDisplayables(self, imageAnimations, sourceFiles, displayables):
            if(len(sourceFiles) <= 0 or len(imageAnimations) <= 0):
                raise IndexError("0 Length animation")
            self.displayables = displayables
            self.imageAnimations = imageAnimations
            self.sourceFiles = sourceFiles
            self.displayable = DynamicDisplayable(self.dynamicDisplayable_getCurrentFrame)
        
        def getDisplayable(self):
            return self.displayable

        def setAnimation(self, imageAnimation):
            if(not imageAnimation in self.imageAnimations):
                raise IndexError(str(imageAnimation)+" not contained in animations")
            self.setQueueAnimations(imageAnimation)
            self.resetAnimation()
            return self

        def setSource(self, sourceFile):
            if(not sourceFile in self.sourceFiles):
                raise IndexError(str(sourceFile)+" not contained in animations")
            self.source = sourceFile
            self.resetAnimation()
            return self

        def setQueueAnimations(self, *imageAnimations):
            self.queue = list(imageAnimations)[::-1]
            return self
        
        def setDirection(self, dir):
            self.dir = dir
            return self

        def resetAnimation(self):
            self.frame = 0
            self.__onNewAnimLoop()
            return self

        def __onNewAnimLoop(self):
            if(len(self.queue) > 0):
                self.__popQueue()
            pass

        def __popQueue(self):
            self.anim = self.queue.pop()
            self.dt = self.anim.df

        def onLoop(self, trans, st, at):
            super().onLoop(trans, st, at)
            self.increamentFrames(1)

        def increamentFrames(self, add=0):
            self.frame += add
            a,dir,f,dis = self.__getCurrentFrameInfo()
            b = f < self.frame
            self.frame = f
            if b: self.__onNewAnimLoop()
            return a,dir,f,dis

        def __iadd__(self, add):
            self.increamentFrames(add)

        def __getCurrentFrameInfo(self):
            anim = imageAnimations[0] if self.anim is None else self.anim
            dir = self.dir if self.dir in anim.directions else anim.directions[0]
            frame = self.frame % anim.frames
            print(anim, dir, frame)
            return (anim, dir, frame, self.displayables[anim][dir][frame])

        def dynamicDisplayable_getSourceFile(self, st, at):
            return (self.sourceFiles[0] if self.source is None else self.source.file, None)

        def dynamicDisplayable_getCurrentFrame(self, st, at):
            a,dir,f,d = self.__getCurrentFrameInfo()
            return d, self.redrawTime

    class AnimationDirectorFactory:
        def __init__(self):
            self.imageAnimations = []
            self.sourceFiles = []

        def setImageAnimations(self, *imageAnimations):
            self.imageAnimations = imageAnimations
            return self
        
        def setSourceFiles(self, *sourceFiles):
            self.sourceFiles = sourceFiles
            return self

        def build(self):
            director = AnimationDirector()
            dynamicSourceFile = DynamicDisplayable(director.dynamicDisplayable_getSourceFile)
            displayables = {}
            for anim in self.imageAnimations:
                displayables[anim] = anim.buildDynamic(dynamicSourceFile)
            director.__setDisplayables(self.imageAnimations, self.sourceFiles, displayables)
            return director

    class Collision:
        def __init__(self, x, y, w, h):
            self.collisions = []
            self.canMove = True
            self.tx = x
            self.bx = x + w
            self.ty = y
            self.by = y + h
        
        def collide(self, x, y, walkable):
            self.canMove = self.canMove and walkable
            self.collisions.append((x,y))
        
        def check(self, x, y, walkable):
            tx = x
            bx = x + IMAGE_SIZE
            ty = y
            by = y + IMAGE_SIZE

            cx = tx <= self.bx and bx >= self.tx
            cy = ty <= self.by and by >= self.ty

            if cx and cy:
                self.collide(x,y,walkable)

    
    class Map:
        def __init__(self, rows, columns, walkable):
            self.rows = rows
            self.columns = columns,
            self.walkable = walkable
            self.walls = None
            self.floors = None
        
        def setWalls(self, walls):
            self.walls = walls
        
        def getWalls(self):
            return self.walls

        def setFloors(self, floors):
            self.floors = floors

        def getFloors(self):
            return self.floors

        def testCollision(self, x, y, width, height):
            c = Collision(x,y,width,height)
            for i in range(rows):
                for j in range(columns):
                    c.check(j,i,self.walkable[i][j])
            return c

    class MapFactory:
        def __init__(self, rows, columns):
            self.rows = rows
            self.columns = columns
            self.floor = [[FloorTiles.VOID for _ in range(columns)] for _ in range(rows)]
            self.wall = [[WallTiles.VOID for _ in range(columns)] for _ in range(rows)]
            self.roof = [[WallTiles.VOID for _ in range(columns)] for _ in range(rows)]
            self.walkable = [[False for _ in range(columns)] for _ in range(rows)]

        def setWall(self, *values):
            for i in range(self.rows):
                for j in range(self.columns):
                    self.wall[i][j] = WallTiles.getTile(values[i][j])
                    self.walkable[i][j] = self.wall[i][j] == WallTiles.VOID
            return self

        def setRoof(self, *values):
            for i in range(rows):
                for j in range(columns):
                    self.roof[i][j] = WallTiles.getTile(values[i][j])
                    self.walkable[i][j] = self.roof[i][j] == WallTiles.VOID
            return self

        def setFloor(self, *values):
            for i in range(self.rows):
                for j in range(self.columns):
                    self.floor[i][j] = FloorTiles.getTile(values[i][j])
            return self

        def build(self, wtheme, ftheme):
            m = Map(self.rows, self.columns, self.walkable)
            wcompose = []
            for i in range(self.rows):
                for j in range(self.columns):
                    if self.wall[i][j] == WallTiles.VOID: continue
                    x = wtheme.x * WALL_THEME_SIZE[0] * IMAGE_SIZE + self.wall[i][j].x * IMAGE_SIZE
                    y = wtheme.y * WALL_THEME_SIZE[1] * IMAGE_SIZE + self.wall[i][j].y * IMAGE_SIZE

                    img = Crop((x, y, IMAGE_SIZE, IMAGE_SIZE), RoomSourceFiles.WALLS.file)
                    offset = (j * IMAGE_SIZE, i * IMAGE_SIZE)
                    wcompose += [offset, img]
            walls = Composite((self.columns * IMAGE_SIZE, self.rows * IMAGE_SIZE), *wcompose)
            m.setWalls(walls)
            fcompose = []
            for i in range(self.rows):
                for j in range(self.columns):
                    if self.floor[i][j] == FloorTiles.VOID: continue
                    x = ftheme.x * FLOOR_THEME_SIZE[0] * IMAGE_SIZE + self.floor[i][j].x * IMAGE_SIZE
                    y = ftheme.y * FLOOR_THEME_SIZE[1] * IMAGE_SIZE + self.floor[i][j].y * IMAGE_SIZE

                    img = Crop((x, y, IMAGE_SIZE, IMAGE_SIZE), RoomSourceFiles.FLOORS.file)
                    offset = (j * IMAGE_SIZE, i * IMAGE_SIZE)
                    fcompose += [offset, img]
            floors = Composite((self.columns * IMAGE_SIZE, self.rows * IMAGE_SIZE), *fcompose)
            m.setFloors(floors)
            return m



    class MovementDirector(Director):
        def __init__(self, m):
            super().__init__(0.03)
            self.x = 0
            self.y = 0
            self.speed = 0
            self.dir = Direction.DOWN
            self.sdir = Direction.DOWN
            self.map = m
            self.cxoffset = 0
            self.cyoffset = 0
            self.cwidth = IMAGE_SIZE
            self.cheight = IMAGE_SIZE

        def setDirection(self, dir, sdir=None):
            self.dir = dir
            self.sdir = dir if sdir is None else sdir
        
        def setSpeed(self, pixelsPerSecond=0):
            self.speed = pixelsPerSecond
        
        def setCollisionBox(xoffset = 0, yoffset = 0, width = IMAGE_SIZE, height = IMAGE_SIZE):
            self.cxoffset = xoffset
            self.cyoffset = yoffset
            self.cwidht = width
            self.cheight = height

        def move(self):
            sx = sy = self.speed * self.dt
            if self.speed != 0:
                if self.dir in [Direction.DOWN, Direction.UP]:
                    sy *= 1 if self.dir == Direction.DOWN else -1
                    if self.sdir in [Direction.LEFT, Direction.RIGHT]:
                        sx *= 1 if self.sdir == Direction.RIGHT else -1
                elif self.dir in [Direction.LEFT, Direction.RIGHT]:
                    sx *= 1 if self.dir == Direction.RIGHT else -1
                    if self.sdir in [Direction.UP, Direction.DOWN]:
                        sy *= 1 if self.sdir == Direction.DOWN else -1

                if sx != 0 and sy != 0:
                    sx *= 0.7
                    sy *= 0.7
            
            newx = self.x + sx
            newy = self.y + sy
            
            c = self.map.testCollision(newx + self.cxoffset, newy + self.cyoffset, self.cwidth, self.cheight)

            if c.canMove:
                self.x = newx
                self.y = newy            

        def onLoop(self, trans, st, at):
            super().onLoop(trans, st, at)
            return None

    class CharacterDirector(Director):
        def __init__(self, movementDirector, animationDirector):
            super().__init__(0.03)
            self.move = movementDirector
            self.anim = animationDirector
            self.dir = Direction.DOWN

        def onLoop(self, trans, st, at):
            super().onLoop(trans, st, at)
            return None

    class Entity:
        x = 0
        y = 0
    
    class AnimatedEntity(Entity):
        frame = 0
        
        def __init__(self):
            super().__init__()

        def updateDisplayable(self):
            raise NotImplemenetedError()

    class Door(AnimatedEntity):
        params: Params
        side: DoorSide
        add: Params
        remove: Params
        toggle: Params

        def __init__(self, side: DoorSide, params: Params, add = Params.NONE, remove = Params.NONE, toggle = Params.NONE):
            super().__init__()
            self.side = side
            self.params = Params
            self.add = add
            self.remove = remove
            self.toggle = toggle

        def select(self):
            return Door(DoorSide.CURRENT, ((self.params | self.add) & (~self.remove)) ^ self.toggle)

        def left(self, add = Params.NONE, remove = Params.NONE, toggle = Params.NONE):
            return Door(DoorSide.LEFT, self.params, add, remove, toggle)

        def right(self, add = Params.NONE, remove = Params.NONE, toggle = Params.NONE):
            return Door(DoorSide.RIGHT, self.params, add, remove, toggle)

    playerAnim = AnimationDirectorFactory().setSourceFiles(CharacterSourceFiles.CHARACTER_PREMADE_17).setImageAnimations(CharacterAnimations.WALK).build()
    playerAnim.setDirection(Direction.RIGHT).setAnimation(CharacterAnimations.WALK).setSource(CharacterSourceFiles.CHARACTER_PREMADE_17)
    thisMap = MapFactory(5,5).setWall(
        "jrrRJ",
        "kssSK",
        "l   L",
        "l   L",
        "ouuuO"
    ).setFloor(
        "     ",
        "     ",
        " 011 ",
        " 344 ",
        "     "
    ).build(WallThemes.BROWN, FloorThemes.WOOD)
    playerMove = MovementDirector(thisMap)
    playerChar = CharacterDirector(playerMove, playerAnim)

define door.current = Door(DoorSide.CURRENT, Params.DEFAULT)
define door.left = door.current.left()
define door.right = door.current.right()

transform loop(director):
    function director.onLoop
    pause director.dt
    repeat

transform characterLoop(cd):
    contains loop(cd.move)
    contains loop(cd.anim)
    contains loop(cd)

image img = playerAnim.getDisplayable()
image wall = thisMap.getWalls()
image floors = thisMap.getFloors()

label start:
    show floors at truecenter
    show wall at truecenter
    show img at truecenter, loop(playerAnim)
    "right"
    $ playerAnim.setDirection(Direction.LEFT)
    "left"
    $ playerAnim.setDirection(Direction.DOWN)
    "down"
    $ playerAnim.setDirection(Direction.UP)
    "up"
    return
