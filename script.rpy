init -10 python:
    from enum import Flag, auto, Enum
    import builtins
    from math import floor, ceil

    IMAGE_SIZE = 48
    FRAME_LENGTH = 0.16

    class Params(Flag):
        NONE = 0
        IS_INTERACT = auto()
        DEFAULT = NONE
    
    class DoorSide(Enum):
        CURRENT = 0
        RIGHT = 1
        LEFT = 2

    class Direction(Enum):
        NONE = 0
        RIGHT = 1
        UP = 2
        LEFT = 3
        DOWN = 4


    def setDefault(d, **kwargs):
        for k in kwargs:
            if k not in d:
                d[k] = kwargs[k]
        return d

    class SourceFile(Enum):
        def __new__(cls, tag, file):
            obj = builtins.object.__new__(cls)
            obj._value_ = tag
            return obj
            
        def __init__(self, tag, file):
            self.file = f"{IMAGE_SIZE}/{file}"
            self.tag = tag

    class CharacterSourceFiles(SourceFile):
        CHARACTER_PREMADE_17 = "premade 17", "character/Premade_Character_17.png"
    
    class RoomSourceFiles(SourceFile):
        WALLS = "walls", "room/Room_Builder_3d_walls.png"
        FLOORS = "floors", "room/Room_Builder_Floors.png"
        BORDERS = "borders", "room/Room_Builder_borders.png"
        INTERIOR = "interior", "room/Condominium_Black_Shadow.png"

    class SpriteTheme(Enum):
        def __new__(cls, tag, kwargs):
            value = len(cls.__members__) + 1
            obj = builtins.object.__new__(cls)
            obj._value_ = value
            return obj

        def __init__(self, tag, kwargs):
            self.tag = tag
            self.__setup(**kwargs)

        def __setup(self, x = None, y = None, r = None, c = None, w = IMAGE_SIZE, h = IMAGE_SIZE, xoffset=0, yoffset=0, src = None, refreshRate = 1):
            self.x = 0
            self.y = 0

            if x is not None:
                self.x = x
            elif c is not None:
                self.x = c * w + xoffset
            
            if y is not None:
                self.y = y
            elif r is not None:
                self.y = r * h + yoffset
            
            self.source = src
            self.refreshRate = refreshRate

    class NoTheme(SpriteTheme):
        NONE = 'default', dict(x=0,y=0)

    class SpriteDynamicDisplayableBuilder:
        def __init__(self, layer, getTheme, getFrame=None, getDirection=None):
            self.getTheme = getTheme
            self.getFrame = getFrame
            self.getDirection = getDirection
            self.layer = layer
        
        def __call__(self, st, at, sprite):
            theme = self.getTheme(st, at, sprite)
            frame = (self.getFrame(st, at, sprite, theme) if self.getFrame else 0) % sprite.frames
            direction = self.getDirection(st, at, sprite, theme) if self.getDirection else Direction.NONE
            return sprite.buildStatic(self.layer, theme, frame=frame, direction=direction, nullable=False), theme.refreshRate

    class Sprite(Enum):
        def __new__(cls, char, kwargs):
            obj = builtins.object.__new__(cls)
            obj._value_ = char
            return obj

        def __init__(self, char, kwargs):
            self.c = char
            self.__setup(**kwargs)
        
        def __setup(self, 
                x=None, y=None, r=None, c=None, width = IMAGE_SIZE, height = IMAGE_SIZE, 
                f = 1, df = (1,0), themes = NoTheme, src = None,
                up=0, down=0, left=0, right=0, none=0,
                upy=0, downy=0, lefty=0, righty=0, noney=0,
                upx=0, downx=0, leftx=0, rightx=0, nonex=0
            ):
            self.x = 0
            self.y = 0
            self.src_override = src
            if x is not None:
                self.x = x
            elif c is not None:
                self.x = c*width
            
            if y is not None:
                self.y = y
            elif r is not None:
                self.y = r*height

            self.width = width
            self.height = height
            self.themes = themes
            self.frames = f
            self.dframe = df
            self.directional_offsets = {
                Direction.NONE: (nonex + df[0] * none * f, noney + df[1] * none * f),
                Direction.UP:   (upx + df[0] * up * f, upy + df[1] * up * f),
                Direction.DOWN: (downx + df[0] * down * f, downy + df[1] * down * f),
                Direction.LEFT: (leftx + df[0] * left * f, lefty + df[1] * left * f),
                Direction.RIGHT:(rightx + df[0] * right * f, righty + df[1] * right * f)
            }
            
        def buildDynamic(self, layer, getTheme, getFrame=None, getDirection=None, nullable=True):
            if self.themes == NoTheme or self.themes == None:
                if nullable:
                    return None
                else:
                    return Null(self.width, self.height)

            func = SpriteDynamicDisplayableBuilder(layer, getTheme, getFrame, getDirection)
            return DynamicDisplayable(func, self)

        def buildStatic(self, layer, theme, frame = 0, direction=Direction.NONE, nullable=True):
            if theme == NoTheme.NONE or theme is None:
                if nullable:
                    return None
                else:
                    return Null(self.width, self.height)

            x = theme.x + self.x + frame * self.width * self.dframe[0] + self.directional_offsets[direction][0] * self.width
            y = theme.y + self.y + frame * self.height * self.dframe[1] + self.directional_offsets[direction][1] * self.height
            source = self.src_override.file if self.src_override is not None else theme.source.file
            img = Crop((x,y, self.width, self.height), source)
            return img
    
    
    class StaticSpriteThemes(SpriteTheme):
        NONE    = "none", dict(src=None)

    class StaticSpriteTiles(Sprite):
        VOID = '', dict()

    class StairTopThemes(SpriteTheme):
        GREY    = "grey",   dict(r=0,c=0)
        SILVER  = "silver", dict(r=6,c=0)
        BEIGE   = "beige",  dict(r=0,c=6)
        BROWN   = "brown",  dict(r=6,c=6)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 
    
    class StairBotThemes(SpriteTheme):
        GREY    = "grey",   dict(c=0)
        SILVER  = "silver", dict(c=2)
        BEIGE   = "beige",  dict(c=1)
        BROWN   = "brown",  dict(c=3)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, r=4, w=3 * IMAGE_SIZE, src = RoomSourceFiles.INTERIOR)) 
    
    class StairCarpetThemes(SpriteTheme):
        RED = "red", dict(c=12)
        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 

    class FloorMatThemes(SpriteTheme):
        LIGHT   = "light",  dict(r=6,c=13)
        MID     = "mid",    dict(r=7,c=13)
        DARK    = "dark",   dict(r=8,c=13)
        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 

    class CondoInteriorTiles(Sprite):
        VOID                    = ' ', dict(c=-1,r=-1,themes=NoTheme)

        STAIR_U4_M0 = 'a', dict(r=0,c=0,themes=StairTopThemes)
        STAIR_U4_L0 = 'b', dict(r=0,c=1,themes=StairTopThemes)
        STAIR_U4_R0 = 'c', dict(r=0,c=2,themes=StairTopThemes)
        STAIR_U4_M1 = 'd', dict(r=1,c=0,themes=StairTopThemes)
        STAIR_U4_L1 = 'e', dict(r=1,c=1,themes=StairTopThemes)
        STAIR_U4_R1 = 'f', dict(r=1,c=2,themes=StairTopThemes)
        STAIR_U3_M0 = 'g', dict(r=1,c=3,themes=StairTopThemes)
        STAIR_U3_L0 = 'h', dict(r=1,c=4,themes=StairTopThemes)
        STAIR_U3_R0 = 'i', dict(r=1,c=5,themes=StairTopThemes)
        STAIR_U4_M2 = 'j', dict(r=2,c=0,themes=StairTopThemes)
        STAIR_U4_L2 = 'k', dict(r=2,c=1,themes=StairTopThemes)
        STAIR_U4_R2 = 'l', dict(r=2,c=2,themes=StairTopThemes)
        STAIR_U3_M1 = 'm', dict(r=2,c=3,themes=StairTopThemes)
        STAIR_U3_L1 = 'n', dict(r=2,c=4,themes=StairTopThemes)
        STAIR_U3_R1 = 'o', dict(r=2,c=5,themes=StairTopThemes)
        STAIR_U4_M3 = 'p', dict(r=3,c=0,themes=StairTopThemes)
        STAIR_U4_L3 = 'q', dict(r=3,c=1,themes=StairTopThemes)
        STAIR_U4_R3 = 'r', dict(r=3,c=2,themes=StairTopThemes)
        STAIR_U3_M2 = 's', dict(r=3,c=3,themes=StairTopThemes)
        STAIR_U3_L2 = 't', dict(r=3,c=4,themes=StairTopThemes)
        STAIR_U3_R2 = 'u', dict(r=3,c=5,themes=StairTopThemes)
        STAIR_D2_M0 = '0', dict(r=0,c=0,themes=StairBotThemes)
        STAIR_D2_L0 = '1', dict(r=0,c=1,themes=StairBotThemes)
        STAIR_D2_R0 = '2', dict(r=0,c=2,themes=StairBotThemes)
        STAIR_D2_M1 = '3', dict(r=1,c=0,themes=StairBotThemes)
        STAIR_D2_L1 = '4', dict(r=1,c=1,themes=StairBotThemes)
        STAIR_D2_R1 = '5', dict(r=1,c=2,themes=StairBotThemes)

        STMAT_U4_L0 = 'B', dict(r=0,c=0,themes=StairCarpetThemes)
        STMAT_U4_R0 = 'C', dict(r=0,c=1,themes=StairCarpetThemes)
        STMAT_U4_L1 = 'E', dict(r=1,c=0,themes=StairCarpetThemes)
        STMAT_U4_R1 = 'F', dict(r=1,c=1,themes=StairCarpetThemes)
        STMAT_U3_L0 = 'H', dict(r=1,c=2,themes=StairCarpetThemes)
        STMAT_U3_R0 = 'I', dict(r=1,c=3,themes=StairCarpetThemes)
        STMAT_U4_L2 = 'K', dict(r=2,c=0,themes=StairCarpetThemes)
        STMAT_U4_R2 = 'L', dict(r=2,c=1,themes=StairCarpetThemes)
        STMAT_U3_L1 = 'N', dict(r=2,c=2,themes=StairCarpetThemes)
        STMAT_U3_R1 = 'O', dict(r=2,c=3,themes=StairCarpetThemes)
        STMAT_U4_L3 = 'Q', dict(r=3,c=0,themes=StairCarpetThemes)
        STMAT_U4_R3 = 'R', dict(r=3,c=1,themes=StairCarpetThemes)
        STMAT_U3_L2 = 'T', dict(r=3,c=2,themes=StairCarpetThemes)
        STMAT_U3_R2 = 'U', dict(r=3,c=3,themes=StairCarpetThemes)
        STMAT_D2_L0 = '6', dict(r=4,c=0,themes=StairCarpetThemes)
        STMAT_D2_R0 = '7', dict(r=4,c=1,themes=StairCarpetThemes)
        STMAT_D2_L1 = '8', dict(r=5,c=0,themes=StairCarpetThemes)
        STMAT_D2_R1 = '9', dict(r=5,c=1,themes=StairCarpetThemes)

        FLOORMAT_1  = 'v', dict(c=0,themes=FloorMatThemes)
        FLOORMAT_2L = 'w', dict(c=1,themes=FloorMatThemes)
        FLOORMAT_2R = 'x', dict(c=2,themes=FloorMatThemes)

    class FloorThemes(SpriteTheme):
        WOOD = 'wood', dict(c=0,r=5)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, w = 4 * IMAGE_SIZE, h = 2 * IMAGE_SIZE, src = RoomSourceFiles.FLOORS))   

    """
    012
    345
    """
    class FloorTiles(Sprite):
        VOID        = ' ', dict(c=-1,r=-1,themes=NoTheme)
        TOP_LEFT    = '0', dict(c= 0,r= 0)
        TOP         = '1', dict(c= 1,r= 0)
        TOP_RIGHT   = '2', dict(c= 2,r= 0)
        LEFT        = '3', dict(c= 0,r= 1)
        MID         = '4', dict(c= 1,r= 1)
        DARK        = '5', dict(c= 2,r= 1)

        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=FloorThemes))
    
    class BorderThemes(SpriteTheme):
        WHITE = "white", dict(c=0,r=0)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, w = 11 * IMAGE_SIZE, h = 5 * IMAGE_SIZE, src = RoomSourceFiles.BORDERS,xoffset=2*IMAGE_SIZE))
    
    class BorderTiles(Sprite):
        VOID                    = ' ', dict(c=-1,r=-1,themes=NoTheme)
        WALL_R_OPEN_TB          = 'a', dict(r=0,c=0)
        WALL_L_OPEN_TB          = 'b', dict(r=0,c=1)
        BLOCK_CLOSED            = 'f', dict(r=0,c=5)
        BLOCK_T_OPEN_BL         = 'h', dict(r=0,c=7)
        BLOCK_T_OPEN_BLR        = 'i', dict(r=0,c=8)
        BLOCK_T_OPEN_BR         = 'j', dict(r=0,c=9)
        WALL_T_OPEN_L           = 'k', dict(r=1,c=0)
        WALL_T_OPEN_R           = 'l', dict(r=1,c=1)
        WALL_TR_OPEN_BL_TOP_T   = 'm', dict(r=1,c=2)
        WALL_TL_OPEN_BR_TOP_T   = 'n', dict(r=1,c=3)
        WALL_R_OPEN_B_CORNER_T  = 'o', dict(r=1,c=4)
        WALL_T_OPEN_LR          = 'p', dict(r=1,c=5)
        WALL_L_OPEN_B_CORNER_T  = 'q', dict(r=1,c=6)
        BLOCK_OPEN_TB           = 's', dict(r=1,c=8)
        BLOCK_OPEN_B            = 't', dict(r=1,c=9)
        BLOCK_OPEN_B_1          = 'A', dict(r=2,c=0)
        BLOCK_OPEN_B_2          = 'B', dict(r=2,c=1)
        BLOCK_OPEN_B_3          = 'C', dict(r=2,c=2)
        WALL_L_OPEN_TB_1        = 'E', dict(r=2,c=4)
        WALL_R_OPEN_TB_1        = 'G', dict(r=2,c=6)
        BLOCK_OPEN_BR_OWALL_L   = 'H', dict(r=2,c=7)
        BLOCK_OPEN_BRL          = 'I', dict(r=2,c=8)
        BLOCK_OPEN_BL_OWALL_R   = 'J', dict(r=2,c=9)
        WALL_TL_OPEN_TBR_TOP_T  = 'K', dict(r=3,c=0)
        WALL_TR_OPEN_TBL_TOP_T  = 'L', dict(r=3,c=1)
        WALL_T_OPEN_T           = 'M', dict(r=3,c=2)
        WALL_CORNER_TR_OPEN_TR  = 'O', dict(r=3,c=4)
        WALL_T_OPEN_LR_1        = 'P', dict(r=3,c=5)
        WALL_CORNER_TL_OPEN_TL  = 'Q', dict(r=3,c=6)
        BLOCK_OPEN_TBR          = 'R', dict(r=3,c=7)
        BLOCK_OPEN              = 'S', dict(r=3,c=8)
        BLOCK_OPEN_TBL          = 'T', dict(r=3,c=9)


        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=BorderThemes))

    class WallThemes(SpriteTheme):
        BROWN = 'brown', dict(c=0,r=0)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, w = 8 * IMAGE_SIZE, h = 7 * IMAGE_SIZE, src = RoomSourceFiles.WALLS))

    """
    adjpPJDV
    bekqQKEW
    cflrRLFX
    AgmsSMGv
    BhntTNHw
    CiouUOIx
    """
    class WallTiles(Sprite):
        VOID                            = ' ', dict(c=-1,r=-1,themes=NoTheme)
        TOP_END_LEFT                    = 'a', dict(c= 0,r= 0)
        BOT_END_LEFT                    = 'b', dict(c= 0,r= 1)
        MID_END_LEFT                    = 'c', dict(c= 0,r= 2)
        TOP_END_RIGHT                   = 'A', dict(c= 0,r= 3)
        BOT_END_RIGHT                   = 'B', dict(c= 0,r= 4)
        MID_END_RIGHT                   = 'C', dict(c= 0,r= 5)
        TOP_LEFT_CORNER_OVERLAP_SHALLOW = 'd', dict(c= 1,r= 0)
        TOP_LEFT_CORNER_SHALLOW         = 'e', dict(c= 1,r= 1)
        MID_LEFT_CORNER_SHALLOW         = 'f', dict(c= 1,r= 2)
        BOT_LEFT_CORNER_SHALLOW         = 'g', dict(c= 1,r= 3)
        TOP_LEFT_EXTRUDE                = 'h', dict(c= 1,r= 4)
        BOT_LEFT_EXTRUDE                = 'i', dict(c= 1,r= 5)
        TOP_LEFT_CORNER                 = 'j', dict(c= 2,r= 0)
        BOT_LEFT_CORNER                 = 'k', dict(c= 2,r= 1)
        LEFT                            = 'l', dict(c= 2,r= 2)
        TOP_LEFT_ISLAND                 = 'm', dict(c= 2,r= 3)
        BOT_LEFT_ISLAND                 = 'n', dict(c= 2,r= 4)
        LEFT_BOT_CORNER                 = 'o', dict(c= 2,r= 5)
        TOP_LEFT_CORNER_OVERLAP         = 'p', dict(c= 3,r= 0)
        LEFT_BOT_CORNER_OVERLAP         = 'q', dict(c= 3,r= 1)
        TOP                             = 'r', dict(c= 3,r= 2)
        BOT                             = 's', dict(c= 3,r= 3)
        MID_END                         = 't', dict(c= 3,r= 4)
        BOT_B                           = 'u', dict(c= 3,r= 5)
        TOP_RIGHT_CORNER_OVERLAP        = 'P', dict(c= 4,r= 0)
        BOT_RIGHT_CORNER_OVERLAP        = 'Q', dict(c= 4,r= 1)
        TOP_1                           = 'R', dict(c= 4,r= 2)
        BOT_1                           = 'S', dict(c= 4,r= 3)
        MID                             = 'T', dict(c= 4,r= 4)
        BOT_B_1                         = 'U', dict(c= 4,r= 5)
        TOP_RIGHT_CORNER                = 'J', dict(c= 5,r= 0)
        BOT_RIGHT_CORNER                = 'K', dict(c= 5,r= 1)
        RIGHT                           = 'L', dict(c= 5,r= 2)
        TOP_RIGHT_ISLAND                = 'M', dict(c= 5,r= 3)
        BOT_RIGHT_ISLAND                = 'N', dict(c= 5,r= 4)
        RIGHT_BOT_CORNER                = 'O', dict(c= 5,r= 5)
        TOP_RIGHT_CORNER_OVERLAP_SHALLOW= 'D', dict(c= 6,r= 0)
        TOP_RIGHT_CORNER_SHALLOW        = 'E', dict(c= 6,r= 1)
        MID_RIGHT_CORNER_SHALLOW        = 'F', dict(c= 6,r= 2)
        BOT_RIGHT_CORNER_SHALLOW        = 'G', dict(c= 6,r= 3)
        TOP_RIGHT_EXTRUDE               = 'H', dict(c= 6,r= 4)
        BOT_RIGHT_EXTRUDE               = 'I', dict(c= 6,r= 5)
        TOP_RIGHT_ISLAND_SHALLOW        = 'V', dict(c= 7,r= 0)
        MID_RIGHT_ISLAND_SHALLOW        = 'W', dict(c= 7,r= 1) 
        BOT_RIGHT_ISLAND_SHALLOW        = 'X', dict(c= 7,r= 2)
        TOP_LEFT_ISLAND_SHALLOW         = 'v', dict(c= 7,r= 3)
        MID_LEFT_ISLAND_SHALLOW         = 'w', dict(c= 7,r= 4) 
        BOT_LEFT_ISLAND_SHALLOW         = 'x', dict(c= 7,r= 5)

        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=WallThemes))

    class CharacterThemes(SpriteTheme):
        PREMADE_17 = 'premade 17', dict(src=CharacterSourceFiles.CHARACTER_PREMADE_17)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, refreshRate=0.01, x=0, y=0)) 

    class CharacterAnimations(Sprite):
        DEFAULT     = "",               dict()
        IDLE        = "idle",           dict(f=6, r=1)
        WALK        = "walk",           dict(f=6, r=2)
        SLEEP       = "sleep",          dict(f=6, r=3, right=0, up=0, left=0, down=0)
        SITTING     = "sitting",        dict(f=6, r=4, right=0, up=0, left=1, down=1)
        SIT         = "sit",            dict(f=6, r=5, right=0, up=0, left=1, down=1)
        PHONE       = "phone",          dict(f=12, r=6, right=0, up=0, left=0, down=0)
        PHONE_START = "phone start",    dict(f=3, r=6, right=0, up=0, left=0, down=0)
        PHONE_LOOP  = "phone loop",     dict(f=6, r=6, c=3, right=0, up=0, left=0, down=0)
        PHONE_END   = "phone end",      dict(f=3, r=6, c=9, right=0, up=0, left=0, down=0)
        BOOK        = "book",           dict(f=12, r=7, right=0, up=0, left=0, down=0)
        BOOK_LOOP   = "book loop",      dict(f=6, r=7, right=0, up=0, left=0, down=0)
        BOOK_FLIP   = "book flip",      dict(f=6, r=7, right=0, up=0, left=0, down=0)
        PUSH_TROLLEY= "push_trolley",   dict(f=6, r=8)
        # TROLLEY     = "trolley",        dict(f=3, r=8, c=12, width=IMAGE_SIZE*2, yoffset=IMAGE_SIZE, xoffset=IMAGE_SIZE)
        PICK_UP     = "pick_up",        dict(f=12, r=9)
        GIFT        = "gift",           dict(f=10, r=10)
        LIFT        = "lift",           dict(f=14, r=11)
        THROW       = "throw",          dict(f=14, r=12)
        HIT         = "hit",            dict(f=6, r=13)
        PUNCH       = "punch",          dict(f=6, r=14)
        STAB        = "stab",           dict(f=6, r=15)
        KNIFE       = "knife",          dict(f=6, r=15, c=24)
        GUN_GRAB    = "gun grab",       dict(f=4, r=16)
        GUN_IDLE    = "gun idle",       dict(f=6, r=17)
        GUN_SHOOT   = "gun shoot",      dict(f=3, r=18)
        HURT        = "hurt",           dict(f=3, r=19)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, themes=CharacterThemes, width=IMAGE_SIZE, height=2*IMAGE_SIZE, none=0, right=0, up=1, left=2, down=3)) 

    class Director:
        def __init__(self, dt=None):
            self.dt = dt
            self.running = False
        
        def start(self):
            self.running = True
            return self

        def pause(self):
            self.running = False
            return self

        def onLoop(self, trans, st, at):
            if not self.running: return
            self.onLoopSub(trans, st, at)
        
        def onLoopSub(self, trans, st, at):
            pass

    DEFAULT_DISPLAYABLE = Null()

    class AnimationDirector(Director):
        def __init__(self):
            super().__init__(FRAME_LENGTH)
            self.theme = NoTheme.NONE
            self.frame = 0
            self.dir = Direction.NONE
            self.anims = []
            self.displayable = DynamicDisplayable(self.__getDisplayable)
            self.displayables = {}

        def getDirection(self, st, at, sprite, theme):
            return self.dir

        def getFrame(self, st, at, sprite, theme):
            return self.frame

        def getTheme(self, st, at, sprite):
            return self.theme

        def loadAnimations(self, *animations):
            for anim in animations:
                if not anim in self.displayables:
                    self.displayables[anim] = anim.buildDynamic(None, self.getTheme, self.getFrame, self.getDirection, nullable=False)
            return self

        def getCurrentAnim(self):
            return self.anims[0] if len(self.anims) > 0 else None

        def __getDisplayable(self, st, at):
            return self.displayables.get(self.getCurrentAnim(), DEFAULT_DISPLAYABLE), self.theme.refreshRate
            
        def getDisplayable(self):
            return self.displayable

        def setDirection(self, direction):
            self.dir = direction
            return self
        
        def setTheme(self, theme):
            self.theme = theme
            return self

        def setAnimations(self, *anims):
            self.loadAnimations(*anims)
            self.onCompleteAnim()
            self.anims = list(anims)
            self.frame = 0
            self.onStartAnim()
            return self
        
        def addAnimations(self, *anims):
            self.loadAnimations(*anims)
            self.anims += list(anims)
            return self
        
        def reset(self):
            self.onCompleteAnim()
            self.frame = 0
            self.onStartAnim()
            return self

        def next(self, reset=False):
            self.onCompleteAnim()
            if reset: self.frame = 0
            if len(self.anims) > 1:
                self.anims.pop(0)
            self.onStartAnim()
            return self

        def onCompleteAnim(self):
            anim = self.anims[0] if len(self.anims) > 0 else None

        def onStartAnim(self):
            anim = self.anims[0] if len(self.anims) > 0 else None

        def interupt(self, anim):
            self.loadAnimations(anim)
            self.onCompleteAnim()
            self.anims.insert(0,anim)
            self.frame = 0
            self.onStartAnim()
            return self

        def incrementFrames(self, frames=1):
            anim = self.getCurrentAnim()
            frame = self.frame + frames
            if not anim is None:
                frame %= anim.frames
            if frame < self.frame:
                self.next()
            self.frame = frame
            return self

        def onLoopSub(self, trans, st, at):
            self.incrementFrames()

    renpy.add_layer("above", above="master")
    renpy.add_layer("player", above="master")
    renpy.add_layer("below", above="master")

    class Map:

        def init(self, rows, columns, b=None, p=None, a=None, w=None):
            self.rows = rows
            self.columns = columns
            self.below = b
            self.above = a
            self.player = p
            self.walkable = w

        def getAboveLayer(self):
            return self.above

        def getPlayerLayer(self):
            return self.player
        
        def getBelowLayer(self):
            return self.below

        def getTheme(self, st, at, sprite):
            if sprite.themes is None:
                return StaticSpriteThemes.NONE
            return list(sprite.themes)[0]

        def getCollisions(self, px, py, pw, ph): 
            x = px / IMAGE_SIZE
            y = py / IMAGE_SIZE
            x2 = (px + pw) / IMAGE_SIZE
            y2 = (py + ph) / IMAGE_SIZE
            
            tl = int(x),int(y)
            br = int(x2), int(y2)
            collisions = []
            walkable = True
            for j in range(tl[0], min(br[0]+1, self.columns)):
                for i in range(tl[1], min(br[1]+1, self.rows)):
                    collisions.append((j,i))
                    walkable &= self.walkable[i][j]
            
            print(x, y, x2, y2, pw / IMAGE_SIZE, ph / IMAGE_SIZE, tl, br, collisions, walkable)
            return collisions, walkable

    class MapFactory:
        def __init__(self, rows, columns):
            self.rows = rows
            self.columns = columns
            self.belows = []
            self.players = []
            self.aboves = []
            self.walkable = [[False for _ in range(columns)] for _ in range(rows)]

        def addBelowLayer(self, fromCls, *values):
            self.belows.append(self.__createLayer(*values, fromCls=fromCls))
            return self
        
        def addAboveLayer(self, fromCls, *values):
            self.aboves.append(self.__createLayer(*values, fromCls=fromCls))
            return self

        def addPlayerLayer(self, fromCls, *values):
            self.players.append(self.__createLayer(*values, fromCls=fromCls))
            return self

        def __createLayer(self, *values, fromCls=None):
            l = [[StaticSpriteTiles.VOID for _ in range(self.columns)] for _ in range(self.rows)]
            for i in range(self.rows):
                for j in range(self.columns):
                    if fromCls is not None:
                        l[i][j] = fromCls(values[i][j])
                    else:
                        l[i][j] = values[i][j]
            return l
        
        def setWalkable(self, *values):
            for i in range(self.rows):
                for j in range(self.columns):
                    self.walkable[i][j] = bool(int(values[i][j]))
            return self

        def __buildLayer(self, m, layer):
            ls = []
            for l in layer:
                compose = []
                for i in range(self.rows):
                    for j in range(self.columns):
                        img = l[i][j].buildDynamic(None, m.getTheme)
                        if img is None: continue
                        offset = (j * IMAGE_SIZE, i * IMAGE_SIZE)
                        compose += [offset, img]
                ls.append(Composite((self.columns * IMAGE_SIZE, self.rows * IMAGE_SIZE), *compose))
            c = []
            for l in ls:
                c.append((0,0))
                c.append(l)
            return Composite((self.columns * IMAGE_SIZE, self.rows * IMAGE_SIZE), *c)

        def build(self, m=None):
            if m is None:
                m = Map()
            m.init(
                self.rows, self.columns, 
                w=self.walkable, 
                a=self.__buildLayer(m, self.aboves), 
                b=self.__buildLayer(m, self.belows), 
                p=self.__buildLayer(m, self.players)
            )
            return m



    class MovementDirector(Director):
        def __init__(self, m):
            super().__init__(0.03)
            self.x = 4 * IMAGE_SIZE
            self.y = 4 * IMAGE_SIZE
            self.speed = 0
            self.dirs = []
            self.map = m
            self.cxoffset = 0
            self.cyoffset = 0
            self.cwidth = IMAGE_SIZE
            self.cheight = IMAGE_SIZE

        def setDirection(self, *dirs):
            self.dirs = list(dirs)
        
        def setSpeed(self, pixelsPerSecond=0):
            self.speed = pixelsPerSecond
        
        def setCollisionBox(self, xoffset = 0, yoffset = 0, width = IMAGE_SIZE, height = IMAGE_SIZE):
            self.cxoffset = int(xoffset)
            self.cyoffset = int(yoffset)
            self.cwidth = int(width)
            self.cheight = int(height)
            return self

        def move(self):
            sx = sy = 0
            s = self.speed * self.dt
            if self.speed != 0:
                if Direction.UP in self.dirs:
                    sy -= s
                if Direction.DOWN in self.dirs:
                    sy += s
                if Direction.RIGHT in self.dirs:
                    sx += s
                if Direction.LEFT in self.dirs:
                    sx -= s

                if sx != 0 and sy != 0:
                    sx *= 0.7
                    sy *= 0.7
            
            newx = self.x + sx
            newy = self.y + sy
            
            c,w = self.map.getCollisions(newx + self.cxoffset, newy + self.cyoffset, self.cwidth, self.cheight)
            
            if w:
                self.x = newx
                self.y = newy

        def onLoopSub(self, trans, st, at):
            self.move()
            trans.pos = (int(self.x), int(self.y))
            return None

    class CharacterDirector(Director):
        def __init__(self, movementDirector, animationDirector):
            super().__init__(0.03)
            self.move = movementDirector
            self.anim = animationDirector
            self.facing = Direction.DOWN
            self.move.setSpeed(IMAGE_SIZE * 2)
            self.anim.setDirection(self.facing)
            self.moving = True
            self.dirs = []
            self.__updateMoving()
        
        def onDirKeyPress(self, direction):
            if direction not in self.dirs: self.dirs.append(direction)
            self.__updateMoving()
        
        def onDirKeyRelease(self, direction):
            self.dirs.remove(direction)
            self.__updateMoving()

        def onInteract(self):
            self.anim.interupt(CharacterAnimations.HIT)

        def __updateMoving(self):
            self.dirs = [d for d in self.dirs if d != Direction.NONE]

            self.move.setDirection(*self.dirs)

            moving = len(self.dirs) > 0

            if moving and not self.facing in self.dirs:
                self.facing = self.dirs[0]
                self.anim.setDirection(self.facing)
                    
            if not moving and self.moving:
                self.anim.setAnimations(CharacterAnimations.IDLE)
            elif moving and not self.moving:
                self.anim.setAnimations(CharacterAnimations.WALK)
            
            self.moving = moving

        def onLoopSub(self, trans, st, at):
            return None

    class Door:
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
        

    playerAnim = AnimationDirector().loadAnimations(CharacterAnimations.WALK, CharacterAnimations.IDLE, CharacterAnimations.HIT).setTheme(CharacterThemes.PREMADE_17).start()
    thisMap = MapFactory(12,14).addBelowLayer(FloorTiles,
        "              ",
        "              ",
        "              ",
        "  34      34  ",
        "  34      34  ",
        " 024111111244 ",
        " 344444444444 ",
        " 344444444444 ",
        " 344444444444 ",
        " 3444 34 3444 ",
        " 3444 34 3444 ",
        "              "
    ).addBelowLayer(WallTiles,
        "              ",
        " jrRJ    jrRJ ",
        " k  K    k  K ",
        "jA  arrrrA  aJ",
        "kB  bssssB  bK",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "ouuuu   uuuuuO"
    ).addBelowLayer(CondoInteriorTiles,
        "  kl      kl  ",
        "  ef      ef  ",
        "  kl      kl  ",
        "  qr      qr  ",
        "  wx      wx  ",
        "              ",
        "              ",
        "              ",
        "      wx      ",
        "      12      ",
        "      45      ",
        "              "
    ).addBelowLayer(CondoInteriorTiles,
        "  KL      KL  ",
        "  EF      EF  ",
        "  KL      KL  ",
        "  QR      QR  ",
        "  wx      wx  ",
        "              ",
        "              ",
        "              ",
        "      wx      ",
        "      67      ",
        "      89      ",
        "              "
    ).addAboveLayer(WallTiles,
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "     h  H     ",
        "     i  I     ",
        "     i  I     ",
        "     ouuO     "
    ).setWalkable(
        "00110000001100",
        "00110000001100",
        "00110000001100",
        "00110000001100",
        "00110000001100",
        "01111111111110",
        "01111111111110",
        "01111111111110",
        "01111111111110",
        "01111011011110",
        "01111011011110",
        "00000011000000"
    ).build()
    playerMove = MovementDirector(thisMap).setCollisionBox(0, IMAGE_SIZE * 1.5, IMAGE_SIZE, IMAGE_SIZE * 0.5).start()
    player = CharacterDirector(playerMove, playerAnim).start()

define door.current = Door(DoorSide.CURRENT, Params.DEFAULT)
define door.left = door.current.left()
define door.right = door.current.right()

transform loop(director):
    function director.onLoop
    pause director.dt
    repeat

transform characterLoop(cd):
    parallel:
        loop(cd.move)
    parallel:
        loop(cd.anim)
    parallel:
        loop(cd)

image img = playerAnim.getDisplayable()
image a = thisMap.getAboveLayer()
image b = thisMap.getBelowLayer()
image p = thisMap.getPlayerLayer()

screen keymap_screen():
    zorder 9999
    key "keydown_K_d"   action Function(player.onDirKeyPress, Direction.RIGHT, _update_screens=False)
    key "keyup_K_d"     action Function(player.onDirKeyRelease, Direction.RIGHT, _update_screens=False)
    key "keydown_K_a"   action Function(player.onDirKeyPress, Direction.LEFT, _update_screens=False)
    key "keyup_K_a"     action Function(player.onDirKeyRelease, Direction.LEFT, _update_screens=False)
    key "keydown_K_w"   action Function(player.onDirKeyPress, Direction.UP, _update_screens=False)
    key "keyup_K_w"     action Function(player.onDirKeyRelease, Direction.UP, _update_screens=False)
    key "keydown_K_s"   action Function(player.onDirKeyPress, Direction.DOWN, _update_screens=False)
    key "keyup_K_s"     action Function(player.onDirKeyRelease, Direction.DOWN, _update_screens=False)
    key "keydown_K_e"   action Function(player.onInteract, _update_screens=False)

label start:
    show screen keymap_screen
    #camera player:
    #    perspective True
    #    zzoom True
    show b at topleft onlayer below
    show p at topleft onlayer player
    show img at characterLoop(player) onlayer player
    show a at topleft onlayer above
    
    "right"
    $ playerAnim.setDirection(Direction.LEFT)
    "left"
    $ playerAnim.setDirection(Direction.DOWN)
    "down"
    $ playerAnim.setDirection(Direction.UP)
    "up"
    return
