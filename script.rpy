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
    
    class ObjectSourceFiles(SourceFile):
        FIREPLACE = "fireplace", "room/objects/fireplace.png"
        CAT = "cat", "room/objects/cat.png"

    class DoorSourceFiles(SourceFile):
        GLASS_LEFT = "glass left", "room/doors/glass_left.png"
        GLASS_RIGHT = "glass right", "room/doors/glass_right.png"

    class SpriteTheme(Enum):
        def __new__(cls, tag, kwargs):
            value = len(cls.__members__) + 1
            obj = builtins.object.__new__(cls)
            obj._value_ = value
            return obj

        def __init__(self, tag, kwargs):
            self.tag = tag
            self.__setup(**kwargs)

        def __setup(self, x = 0, y = 0, r = 0, c = 0, src = None):
            self.x = x + c * IMAGE_SIZE
            self.y = y + r * IMAGE_SIZE
            self.source = src

    class VoidTheme(SpriteTheme):
        VOID = '', dict() # This one will cause image to not be drawn

    class StaticSpriteThemes(SpriteTheme):
        NONE = "none", dict() # This one will cause image to use source

    class Sprite(Enum):
        
        def __new__(cls, char, kwargs):
            obj = builtins.object.__new__(cls)
            obj._value_ = char
            return obj

        def __init__(self, char, kwargs):
            self.c = char
            self.__setup(**kwargs)
        
        def __setup(self, 
                x=0, y=0, r=0, c=0, w=IMAGE_SIZE, h=IMAGE_SIZE, anchorx=0, anchory=0,
                f = 1, df = (1,0), themes = StaticSpriteThemes, src = None, isVoid = False,
                up=0, down=0, left=0, right=0, none=0,
                upy=0, downy=0, lefty=0, righty=0, noney=0,
                upx=0, downx=0, leftx=0, rightx=0, nonex=0
            ):
            self.x = x + c * IMAGE_SIZE
            self.y = y + r * IMAGE_SIZE
            self.isVoid = isVoid
            self.src_override = src

            self.width = w if not isVoid else 0
            self.height = h if not isVoid else 0
            self.themes = themes if not isVoid else VoidTheme
            self.frames = f if not isVoid else 1
            self.dframe = df
            self.directional_offsets = {
                Direction.NONE: (nonex + df[0] * none * f, noney + df[1] * none * f),
                Direction.UP:   (upx + df[0] * up * f, upy + df[1] * up * f),
                Direction.DOWN: (downx + df[0] * down * f, downy + df[1] * down * f),
                Direction.LEFT: (leftx + df[0] * left * f, lefty + df[1] * left * f),
                Direction.RIGHT:(rightx + df[0] * right * f, righty + df[1] * right * f)
            }
            self.anchorx=anchorx
            self.anchory=anchory

        def position(self, fromPos=(0,0)):
            return fromPos[0]-self.anchorx, fromPos[1]-self.anchory

        def buildNull(self, *args, **kwargs):
            return Null(self.width, self.height)

        def buildStaticHandler(self):
            return StaticSpriteRenderHandler(self)

        def buildStatic(self, theme, frame = 0, direction=Direction.NONE, nullable=True):
            if self.isVoid or self.themes == VoidTheme or theme == VoidTheme.VOID or theme is None:
                if nullable:
                    return None
                else:
                    return Null(self.width, self.height)

            x = theme.x + self.x + frame * self.width * self.dframe[0] + self.directional_offsets[direction][0] * self.width
            y = theme.y + self.y + frame * self.height * self.dframe[1] + self.directional_offsets[direction][1] * self.height
            source = self.src_override.file if self.src_override is not None else theme.source.file
            img = Crop((x,y, self.width, self.height), source)
            return img
            
        @classmethod
        def _missing_(cls, value):
            return None

    class StaticSpriteTiles(Sprite):
        VOID = ' ', dict(isVoid=True)
        FIREPLACE = 'f', dict(h=IMAGE_SIZE*3,w=IMAGE_SIZE*2,anchory=IMAGE_SIZE*2,f=4,themes=StaticSpriteThemes,src=ObjectSourceFiles.FIREPLACE)
        CAT = 'c', dict(w=IMAGE_SIZE*3,f=12,themes=StaticSpriteThemes,src=ObjectSourceFiles.CAT)

    class StairTopThemes(SpriteTheme):
        GREY    = "grey",   dict(r=0,c=0)
        SILVER  = "silver", dict(r=6,c=0)
        BEIGE   = "beige",  dict(r=0,c=6)
        BROWN   = "brown",  dict(r=6,c=6)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 
    
    class StairBotThemes(SpriteTheme):
        GREY    = "grey",   dict(c=0)
        SILVER  = "silver", dict(c=6)
        BEIGE   = "beige",  dict(c=3)
        BROWN   = "brown",  dict(c=9)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, r=4, src = RoomSourceFiles.INTERIOR)) 
    
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
        VOID = ' ', dict(isVoid=True)
        STAIR_U4_LEFT   = 'r', dict(r=0,c=1,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U4_MID    = 'f', dict(r=0,c=0,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U4_RIGHT  = 'v', dict(r=0,c=2,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U3_LEFT   = 'e', dict(r=1,c=4,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_U3_MID    = 'd', dict(r=1,c=3,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_U3_RIGHT  = 'c', dict(r=1,c=5,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_D2_LEFT   = 'w', dict(r=0,c=1,h=IMAGE_SIZE*2,themes=StairBotThemes)
        STAIR_D2_MID    = 's', dict(r=0,c=0,h=IMAGE_SIZE*2,themes=StairBotThemes)
        STAIR_D2_RIGHT  = 'x', dict(r=0,c=2,h=IMAGE_SIZE*2,themes=StairBotThemes)

        STMAT_U4        = 'R', dict(r=0,c=0,w=IMAGE_SIZE*2,h=IMAGE_SIZE*4,themes=StairCarpetThemes)
        STMAT_U3        = 'E', dict(r=1,c=2,w=IMAGE_SIZE*2,h=IMAGE_SIZE*3,themes=StairCarpetThemes)
        STMAT_D2        = 'W', dict(r=4,c=0,w=IMAGE_SIZE*2,h=IMAGE_SIZE*2,themes=StairCarpetThemes)

        FLOORMAT_1      = 'm', dict(c=0,themes=FloorMatThemes)
        FLOORMAT_2      = 'M', dict(c=1,w=IMAGE_SIZE*2,themes=FloorMatThemes)

    class FloorThemes(SpriteTheme):
        WOOD = 'wood', dict(c=0,r=10)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.FLOORS))   

    """
    012
    345
    """
    class FloorTiles(Sprite):
        VOID = ' ', dict(isVoid=True)

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
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.BORDERS,x=2*IMAGE_SIZE))
    
    class BorderTiles(Sprite):
        VOID = ' ', dict(isVoid=True)
        
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
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.WALLS))

    """
    adjpPJDV
    bekqQKEW
    cflrRLFX
    AgmsSMGv
    BhntTNHw
    CiouUOIx
    """
    class WallTiles(Sprite):
        VOID = ' ', dict(isVoid=True)

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

    class DoorThemes(SpriteTheme):
        GLASS_LEFT = "glass left", dict(src=DoorSourceFiles.GLASS_LEFT)
        GLASS_RIGHT = "glass right", dict(src=DoorSourceFiles.GLASS_RIGHT)

    class DoorSprites(Sprite):
        VOID = ' ', dict(isVoid=True)

        OPEN = "open", dict(c=4)
        CLOSED = "closed", dict(c=0)
        OPENING = "opening", dict(c=0, f=4)
        CLOSING = "closing", dict(c=4, f=4)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, h=IMAGE_SIZE*3, themes=DoorThemes, anchory=IMAGE_SIZE*2))

    class CharacterThemes(SpriteTheme):
        PREMADE_17 = 'premade 17', dict(src=CharacterSourceFiles.CHARACTER_PREMADE_17)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs)) 

    class CharacterAnimations(Sprite):
        VOID = ' ', dict(isVoid=True)

        DEFAULT     = "default",        dict()
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
            kwargs = setDefault(kwargs, themes=CharacterThemes, r=0, h=2*IMAGE_SIZE, none=0, right=0, up=1, left=2, down=3)
            kwargs['r'] *= 2
            super().__init__(tag, kwargs) 

    class SpriteRenderHandler:
        def __init__(self, sprite):
            self.frame = 0
            self.theme = VoidTheme.VOID
            self.direction = Direction.NONE
            self.dir_offset = sprite.directional_offsets[self.direction]
            self.displayable = None
            self.sprite = sprite

        def build(self, frame=0, theme=VoidTheme.VOID, direction=Direction.NONE, position=(0,0)):
            self.sprite, self.theme, self.direction, self.dir_offset, self.frame, pos, change = self.subBuild(frame, theme, direction, position)
            if change: 
                self.displayable = self.sprite.buildStatic(self.theme,self.frame,self.direction,nullable=False)
            return (self.sprite.position(pos), self.displayable), change

        def subBuild(self, frame, theme, direction, position):
            return (position, None), False

    class StaticSpriteRenderHandler(SpriteRenderHandler):
        def __init__(self, sprite):
            super().__init__(sprite)
            self.isNone = sprite.themes == VoidTheme
            self.notDynamic = sprite.frames <= 1 and len(sprite.themes) <= 1
            if self.notDynamic:
                for i in list(Direction):
                    if sprite.directional_offsets[i] != self.dir_offset:
                        self.notDynamic = False
                        break
        
        def subBuild(self, frame, theme, direction, position):
            if self.notDynamic and (self.isNone or self.displayable != None):
                return self.sprite, self.theme, self.direction, self.dir_offset, self.frame, position, False
            frame %= self.sprite.frames
            dir_offset = self.sprite.directional_offsets[direction]
            same = (theme,frame,dir_offset) == (self.theme,self.frame,self.dir_offset) and self.displayable is not None
            return self.sprite, theme, direction, dir_offset, frame, position, (not same)
    
    class DynamicSpriteRenderHandler(SpriteRenderHandler):
        def __init__(self, default=StaticSpriteTiles.VOID, getTheme=None, getFrame=None, getDirection=None, getSprite=None, getPosition=None, **kwargs):
            super().__init__(default)
            self.default = default
            self.getTheme = getTheme
            self.getFrame = getFrame
            self.getDirection = getDirection
            self.getSprite = getSprite
            self.getPosition = getPosition
            self.kwargs = kwargs
        
        def subBuild(self, frame, theme, direction, position=(0,0)):
            s = self.default if self.getSprite is None else self.getSprite(**self.kwargs)
            if s == None: s = self.default
            t = theme if self.getTheme is None else self.getTheme(sprite=s, **self.kwargs)
            d = direction if self.getDirection is None else self.getDirection(sprite=s, theme=t, **self.kwargs)
            f = frame if self.getFrame is None else self.getFrame(sprite=s, theme=t, direction=d, **self.kwargs)
            p = position if self.getPosition is None else self.getPosition(sprite=s, theme=t, direction=d, frame=f, **self.kwargs)
            print(self.default, s, f, d, p, t)   
            dir_offset = s.directional_offsets[d]
            f %= s.frames
            same = (s,t,dir_offset,f) == (self.sprite, self.theme, self.dir_offset, self.frame) and self.displayable is not None
            return s, t, d, dir_offset, f, p, (not same)

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
        def __init__(self, getPosition=None, x=0,y=0,r=0,c=0):
            super().__init__(FRAME_LENGTH)
            self.theme = VoidTheme.VOID
            self.frame = 0
            self.dir = Direction.NONE
            self.anims = []
            self.position = (x + c*IMAGE_SIZE, y + r*IMAGE_SIZE)
            self.getPos = getPosition
            self.handler = DynamicSpriteRenderHandler(
                getTheme=self.getTheme, 
                getFrame=self.getFrame, 
                getDirection=self.getDirection, 
                getSprite=self.getSprite, 
                getPosition=self.getPosition
            )
            self.listener = None
            self.listenerKwargs = dict()
        
        def getPosition(self, **kwargs):
            if self.getPos is not None:
                return self.getPos()
            else:
                return self.position

        def getHandler(self):
            return self.handler

        def getDirection(self, **kwargs):
            return self.dir

        def getFrame(self, **kwargs):
            return self.frame

        def getTheme(self, **kwargs):
            return self.theme

        def getSprite(self, **kwargs):
            return self.anims[0] if len(self.anims) > 0 else None

        def setDirection(self, direction):
            self.dir = direction
            return self
        
        def setTheme(self, theme):
            self.theme = theme
            return self

        def setAnimations(self, *anims):
            self.onCompleteAnim()
            self.anims = list(anims)
            self.frame = 0
            self.onStartAnim()
            return self
        
        def addAnimations(self, *anims):
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
            if self.listener is not None:
                self.listener(anim, start=False, complete=True, **self.kwargs)

        def onStartAnim(self):
            anim = self.anims[0] if len(self.anims) > 0 else None
            if self.listener is not None:
                self.listener(anim, start=True, complete=False, **self.kwargs)

        def setListener(self, listener=None, **kwargs):
            self.listener=listener
            self.listenerKwargs = kwargs
            return self

        def interupt(self, anim):
            self.onCompleteAnim()
            self.anims.insert(0,anim)
            self.frame = 0
            self.onStartAnim()
            return self

        def incrementFrames(self, frames=1):
            anim = self.getSprite()
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
    renpy.add_layer("dynamic", above="master")
    renpy.add_layer("below", above="master")

    class MapReferenceLayer(Enum):
        DYNAMIC=0
        ABOVE=1,
        BELOW=2

    class MapReference:
        def __init__(self, m, handler, layer, refId):
            self.map = m
            self.handler = handler
            self.layer = layer
            self.refId = refId
            self.active = True
        
        def remove(self):
            m.removeReference(self)
    

    class Interactions(Enum):
        VOID = ' ', True
        WALL = '0', False
        LDOOR_L = 'l', None
        LDOOR_R = 'L', None
        RDOOR_L = 'r', None
        RDOOR_R = 'R', None
        I_LDOOR_L = 'i', True
        I_LDOOR_R = 'I', True
        I_RDOOR_L = 'j', True
        I_RDOOR_R = 'J', True

        def __new__(cls, char, walkable):
            obj = builtins.object.__new__(cls)
            obj._value_ = char
            return obj

        def __init__(self, char, walkable):
            self.walkable = walkable


    MAP_FRAME_RATE = 0.03

    class Map(Director):

        def __init__(self):
            super().__init__(FRAME_LENGTH)
            self.dynams = dict()
            self.frame = 0

        def init(self, rows, columns, b=None, d=None, a=None, i=None):
            self.rows = rows
            self.columns = columns
            self.belows = b
            self.aboves = a
            if d is not None:
                self.dynams = d
            self.interactions = i
            self.belowDis = DynamicDisplayable(self.build, MapReferenceLayer.BELOW)
            self.aboveDis = DynamicDisplayable(self.build, MapReferenceLayer.ABOVE)
            self.dynamDis = DynamicDisplayable(self.build, MapReferenceLayer.DYNAMIC)

        def addToLayer(self, layerRef, i=0, j=0, sprite=None, handler=None, refId=""):
            if layerRef == MapReferenceLayer.DYNAMIC:
                return self.addDynamic(handler, refId)
            layer = self.belows if layerRef == MapReferenceLayer.BELOW else self.aboves if layerRef == MapReferenceLayer.ABOVE else None
            if layer is None: None
            if handler is None: handler = sprite.buildStaticHandler()
            ref = MapReference(self, handler, layerRef, (i,j))
            layer.append([(i,j,handler)])
            return ref
        
        def addDynamic(self, handler, refId):
            ref = MapReference(self, handler, MapReferenceLayer.DYNAMIC, refId)
            self.dynams[refId] = handler
            return ref

        def removeReference(self, ref):
            if not ref.active:
                return
            ref.active = False
            if ref.layer == MapReferenceLayer.BELOW:
                self.belows[ref.refId[0]][ref.refId[1]].remove(ref.handler)
            elif ref.layer == MapReferenceLayer.ABOVE:
                self.aboves[ref.refId[0]][ref.refId[1]].remove(ref.handler)
            elif ref.layer == MapReferenceLayer.DYNAMIC:
                self.dynams.pop(ref.refId)

        def getLayer(self, layerRef):
            if layerRef == MapReferenceLayer.BELOW:
                return self.belowDis
            elif layerRef == MapReferenceLayer.ABOVE:
                return self.aboveDis
            elif layerRef == MapReferenceLayer.DYNAMIC:
                return self.dynamDis

        def getTheme(self, handler):
            if handler.sprite.themes is None:
                return StaticSpriteThemes.NONE
            return list(handler.sprite.themes)[0]

        def getInteraction(self, i, j):
            return self.interactions[i][j]

        def setInteraction(self, i, j, interaction):
            self.interactions[i][j] = interaction

        def build(self, st, at, layerRef):
            if layerRef == MapReferenceLayer.DYNAMIC:
                return self.buildDynamics(st, at)

            layer = self.belows if layerRef == MapReferenceLayer.BELOW else self.aboves if layerRef == MapReferenceLayer.ABOVE else None
            if layer is None: return Null(), None
            
            compose = []
            for l in layer:
                for i,j,handler in l:
                    offset = (j * IMAGE_SIZE, i * IMAGE_SIZE)
                    img,change = handler.build(
                        theme=self.getTheme(handler),
                        frame=self.frame,
                        position = offset
                    )
                    if img is None or img[1] is None: continue
                    compose.extend(img)
            return Composite((self.columns * IMAGE_SIZE, self.rows*IMAGE_SIZE), *compose), MAP_FRAME_RATE
        
        def buildDynamics(self, st, at):
            compose = []
            for refId in self.dynams:
                handler = self.dynams[refId]
                img,change = handler.build(frame=self.frame)
                if img is None or img[1] is None: continue
                compose.extend(img)
            return Composite((self.columns * IMAGE_SIZE, self.rows*IMAGE_SIZE), *compose), MAP_FRAME_RATE


        def onLoopSub(self, trans, st, at):
            self.frame += 1

        def getCollisions(self, px, py, pw, ph): 
            x = px / IMAGE_SIZE
            y = py / IMAGE_SIZE
            x2 = (px + pw) / IMAGE_SIZE
            y2 = (py + ph) / IMAGE_SIZE
            
            tl = int(x),int(y)
            br = int(x2), int(y2)
            collisions = []
            walkable = True
            for i in range(tl[1], min(br[1]+1, self.rows)):
                for j in range(tl[0], min(br[0]+1, self.columns)):
                    inter = self.interactions[i][j]
                    w = inter.walkable
                    if w is None:
                        if inter == Interactions.LDOOR_L:
                            w = door.left.isLeftOpen()
                        elif inter == Interactions.LDOOR_R:
                            w = door.left.isRightOpen()
                        elif inter == Interactions.RDOOR_L:
                            w = door.right.isLeftOpen()
                        elif inter == Interactions.RDOOR_R:
                            w = door.right.isRightOpen()
                    walkable &= w
                    collisions.append((i,j,self.interactions[i][j]))
            
            return collisions, walkable

    class MapFactory:
        def __init__(self, rows, columns):
            self.rows = rows
            self.columns = columns
            self.belows = []
            self.aboves = []
            self.interactions = [[Interactions.VOID for _ in range(columns)] for _ in range(rows)]

        def addBelowLayer(self, fromCls, *values):
            self.__addLayer(self.belows, *values, fromCls=fromCls)
            return self
        
        def addAboveLayer(self, fromCls, *values):
            self.__addLayer(self.aboves, *values, fromCls=fromCls)
            return self
        
        def addAbove(self, i, j, sprite):
            self.aboves.append([(i,j,sprite)])
            return self
        
        def addBelow(self, i, j, sprite):
            self.belows.append([(i,j,sprite)])
            return self

        def __addLayer(self, layer, *values, fromCls=None):
            l = []
            for i in range(self.rows):
                for j in range(self.columns):
                    img = None
                    if fromCls is not None:
                        img = fromCls(values[i][j])
                    else:
                        img = values[i][j]
                    if img.themes != VoidTheme and not img.isVoid:
                        l.append((i,j,img))
            layer.append(l)

        def setInteractions(self, *values):
            for i in range(self.rows):
                for j in range(self.columns):
                    self.interactions[i][j] = Interactions(values[i][j])
            return self

        def build(self, m=None):
            if m is None:
                m = Map()
            
            belows = [[(i,j,sprite.buildStaticHandler()) for (i,j,sprite) in layer] for layer in self.belows]
            aboves = [[(i,j,sprite.buildStaticHandler()) for (i,j,sprite) in layer] for layer in self.aboves]

            m.init(
                self.rows, self.columns, 
                i=self.interactions, 
                b=belows,
                a=aboves
            )
            return m



    class MovementDirector(Director):
        def __init__(self, m):
            super().__init__(0.02)
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

        def getPosition(self, **kwargs):
            return int(self.x), int(self.y)

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

        def getInteracting(self):
            return self.map.getCollisions(self.x + self.cxoffset, self.y + self.cyoffset, self.cwidth, self.cheight)[0]

        def onLoopSub(self, trans, st, at):
            self.move()
            trans.pos = (int(self.x), int(self.y))
            return None

    class CharacterDirector(Director):
        def __init__(self, movementDirector, animationDirector):
            super().__init__(0.02)
            self.move = movementDirector
            self.anim = animationDirector
            self.facing = Direction.DOWN
            self.move.setSpeed(IMAGE_SIZE * 3)
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
            for x,y,i in self.move.getInteracting():
                if i == Interactions.I_LDOOR_L:
                    door.left.openLeft()
                elif i == Interactions.I_LDOOR_R:
                    door.left.openRight()
                elif i == Interactions.I_RDOOR_L:
                    door.right.openLeft()
                elif i == Interactions.I_RDOOR_R:
                    door.right.openRight()

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
            self.rightOpen = False
            self.leftOpen = False
            self.animDirector = None

        def isLeftOpen(self):
            return self.leftOpen
        
        def isRightOpen(self):
            return self.rightOpen

        def openLeft(self):
            if not self.leftOpen:
                self.animDirector[0].setAnimations(DoorSprites.OPENING, DoorSprites.OPEN)
            else:
                self.animDirector[0].setAnimations(DoorSprites.CLOSING, DoorSprites.CLOSED)
            self.leftOpen = not self.leftOpen
        
        def openRight(self):
            if not self.rightOpen:
                self.animDirector[1].setAnimations(DoorSprites.OPENING, DoorSprites.OPEN)
            else:
                self.animDirector[1].setAnimations(DoorSprites.CLOSING, DoorSprites.CLOSED)
            self.rightOpen = not self.rightOpen

        def select(self):
            return Door(DoorSide.CURRENT, ((self.params | self.add) & (~self.remove)) ^ self.toggle)

        def left(self, add = Params.NONE, remove = Params.NONE, toggle = Params.NONE):
            return Door(DoorSide.LEFT, self.params, add, remove, toggle)

        def right(self, add = Params.NONE, remove = Params.NONE, toggle = Params.NONE):
            return Door(DoorSide.RIGHT, self.params, add, remove, toggle)
        
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
        "  rv      rv  ",
        "              ",
        "              ",
        "              ",
        "              ",
        "  M       M   ",
        "              ",
        "              ",
        "              ",
        "      wx      ",
        "              ",
        "              "
    ).addBelowLayer(CondoInteriorTiles,
        "  R       R   ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "      W       ",
        "              ",
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
    ).addBelowLayer(StaticSpriteTiles,
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "      f       ",
        "              ",
        "              ",
        "              ",
        "              ",
        " c            ",
        "              "
    ).setInteractions(
        "00  000000  00",
        "00  000000  00",
        "00  000000  00",
        "00  000000  00",
        "00lL000000rR00",
        "0 iI  00  jJ 0",
        "0            0",
        "0            0",
        "0            0",
        "0    0  0    0",
        "0000 0  0    0",
        "000000  000000"
    ).build()
    playerMove = MovementDirector(thisMap).setCollisionBox(0, IMAGE_SIZE * 1.5, IMAGE_SIZE, IMAGE_SIZE * 0.5).start()
    playerAnim = AnimationDirector(playerMove.getPosition).setTheme(CharacterThemes.PREMADE_17).start()

    doorLeftAnimLeft = AnimationDirector(r=4,c=2).setTheme(DoorThemes.GLASS_LEFT).setAnimations(DoorSprites.CLOSED)
    doorLeftAnimRight = AnimationDirector(r=4,c=3).setTheme(DoorThemes.GLASS_RIGHT).setAnimations(DoorSprites.CLOSED)
    doorRightAnimLeft = AnimationDirector(r=4,c=10).setTheme(DoorThemes.GLASS_LEFT).setAnimations(DoorSprites.CLOSED)
    doorRightAnimRight = AnimationDirector(r=4,c=11).setTheme(DoorThemes.GLASS_RIGHT).setAnimations(DoorSprites.CLOSED)
    doorLeftAnimLeftRef = thisMap.addDynamic(doorLeftAnimLeft.getHandler(), "doorLeftAnimLeft")
    doorLeftAnimRightRef = thisMap.addDynamic(doorLeftAnimRight.getHandler(), "doorLeftAnimRight")
    doorRightAnimLeftRef = thisMap.addDynamic(doorRightAnimLeft.getHandler(), "doorRightAnimLeft")
    doorRightAnimRightRef = thisMap.addDynamic(doorRightAnimRight.getHandler(), "doorRightAnimRight")

    playerDisplayableReference = thisMap.addDynamic(playerAnim.getHandler(), "player")
    player = CharacterDirector(playerMove, playerAnim)

define door.current = Door(DoorSide.CURRENT, Params.DEFAULT)
define door.left = door.current.left()
define door.right = door.current.right()
init python:
    door.left.animDirector = (doorLeftAnimLeft, doorLeftAnimRight)
    door.right.animDirector = (doorRightAnimLeft,doorRightAnimRight)

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

image a = thisMap.getLayer(MapReferenceLayer.ABOVE)
image b = thisMap.getLayer(MapReferenceLayer.BELOW)
image d = thisMap.getLayer(MapReferenceLayer.DYNAMIC)
image loopIt = Null()

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
    show b at truecenter onlayer below
    show d at truecenter onlayer dynamic
    show a at truecenter onlayer above
    show loopIt at characterLoop(player.start()) as player
    show loopIt at loop(thisMap.start()) as map
    show loopIt at loop(doorLeftAnimLeft.start()) as ldl
    show loopIt at loop(doorLeftAnimRight.start()) as ldr
    show loopIt at loop(doorRightAnimLeft.start()) as rdl
    show loopIt at loop(doorRightAnimRight.start()) as rdr
    
    "right"
    $ playerAnim.setDirection(Direction.LEFT)
    "left"
    $ playerAnim.setDirection(Direction.DOWN)
    "down"
    $ playerAnim.setDirection(Direction.UP)
    "up"
    return
