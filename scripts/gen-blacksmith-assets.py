#!/usr/bin/env python3
"""
Procedural blacksmith-theme pixel-art generator for pixel-agents.

Writes PNGs into webview-ui/public/assets/ matching the exact decoder specs
(core/src/assets/pngDecoder.ts):
  - characters/char_N.png : 112x96, rows [down,up,right] x 7 frames of 16x32, alpha=0 empty
  - floors/floor_N.png    : 16x16 grayscale (colorized at runtime)
  - walls/wall_0.png       : 64x128 = 4x4 grid of 16x32 pieces, bitmask M at (M%4,M/4). N=1,E=2,S=4,W=8
  - furniture/<ID>/*.png + manifest.json
Pillow required.
"""
import os, json
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "webview-ui", "public", "assets")
ROOT = os.path.abspath(ROOT)

# ── Palette ──────────────────────────────────────────────────────
T = (0, 0, 0, 0)  # transparent
def C(h):
    h = h.lstrip("#")
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), 255)

IRON_D=C("2b2b31"); IRON=C("4a4a55"); IRON_L=C("70707d"); STEEL=C("9a9aa8")
WOOD_D=C("3f2914"); WOOD=C("6b4423"); WOOD_L=C("8a5a2b"); WOOD_HL=C("a9743b")
LEATH=C("5a3416"); LEATH_L=C("7c4a22")
EMBER=C("ff7a18"); EMBER_HOT=C("ffd24a"); EMBER_DEEP=C("d1400a"); EMBER_LOW=C("8a2606")
STONE_D=C("343439"); STONE=C("52525b"); STONE_L=C("6f6f79"); MORTAR=C("232327")
SKIN=C("d79a63"); SKIN_D=C("b3794a"); MOUTH=C("7a3b2a")
BLACK=C("1a1a1e"); GREY=C("808088")

def new(w,h): return Image.new("RGBA",(w,h),T)
def px(img,x,y,c):
    if 0<=x<img.width and 0<=y<img.height: img.putpixel((x,y),c)
def rect(img,x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): px(img,x,y,c)
def hline(img,x0,x1,y,c):
    for x in range(x0,x1+1): px(img,x,y,c)
def vline(img,x,y0,y1,c):
    for y in range(y0,y1+1): px(img,x,y,c)

def save(img,path):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    img.save(path)
    print("  wrote",os.path.relpath(path,ROOT))

# ══════════════════════════════════════════════════════════════════
# CHARACTERS — blacksmiths
# ══════════════════════════════════════════════════════════════════
# frame cols: 0,1,2 walk | 3,4 typing(hammer) | 5,6 reading(tongs+ingot)
# Bearded smith: hair/headband, beard, tunic sleeves, leather apron w/ straps,
# belt, trousers, boots, hammer & tongs. 16x32, feet at y30.
CHAR_PALETTES = [
    # tun/tunS tunic, ap/apS apron, hair, beard, skin/skinD, band headband
    dict(tun=C("6d4d2a"),tunS=C("53381d"),ap=LEATH,apS=C("3f2410"),hair=C("2a1a0e"),beard=C("3a2412"),skin=SKIN,skinD=SKIN_D,band=C("7c4a22")),
    dict(tun=C("3d5a3a"),tunS=C("2a3f28"),ap=LEATH,apS=C("3f2410"),hair=C("5a3416"),beard=C("6a4420"),skin=C("c8905a"),skinD=C("a06f3f"),band=None),
    dict(tun=C("6a2f2f"),tunS=C("4a2020"),ap=C("46484f"),apS=C("2f3036"),hair=C("d9c27a"),beard=C("c2ab63"),skin=SKIN,skinD=SKIN_D,band=C("2f3036")),
    dict(tun=C("34435e"),tunS=C("242f42"),ap=LEATH,apS=C("3f2410"),hair=C("8a8a92"),beard=C("9a9aa2"),skin=C("b6784a"),skinD=C("935e38"),band=None),
    dict(tun=C("5a4a6a"),tunS=C("3f3349"),ap=C("46484f"),apS=C("2f3036"),hair=C("1a1a1e"),beard=C("2a2a2e"),skin=C("8c5a34"),skinD=C("6e4526"),band=C("7c4a22")),
    dict(tun=C("7a6a2a"),tunS=C("57491d"),ap=LEATH,apS=C("3f2410"),hair=C("b03a1a"),beard=C("c24a24"),skin=SKIN,skinD=SKIN_D,band=None),
]

def draw_char_frame(dir_, col, p):
    """Return a 16x32 RGBA image for one frame."""
    im = new(16,32)
    hair,beard = p["hair"],p["beard"]
    skin,skinD = p["skin"],p["skinD"]
    tun,tunS,ap,apS = p["tun"],p["tunS"],p["ap"],p["apS"]
    band=p["band"]
    GLOVE=LEATH_L; TROUS=C("2e2620"); BELT=C("2a1a0e"); BUCKLE=IRON_L; BOOT=C("241a12")

    walk = col in (0,1,2)
    hammer = col in (3,4)
    tongs = col in (5,6)
    lphase = col if walk else 0            # 0 neutral,1,2 strides

    # ---- legs & boots (y 23-30) ----
    def leg(x0,x1,dy):
        rect(im,x0,23,x1,27+dy, TROUS)
        rect(im,x0-0,28+dy,x1,30, BOOT)     # boot
        px(im,x0,30,BLACK)
    if lphase==0:
        leg(5,6,0); leg(9,10,0)
    elif lphase==1:
        leg(4,5,-1); leg(10,11,1)           # left back, right fwd
    else:
        leg(5,6,1); leg(9,10,-1)

    # ---- torso: tunic + apron (y 12-24) ----
    rect(im,4,12,11,24, tun)                # tunic body
    hline(im,4,11,12,tunS)                  # shoulder shade
    vline(im,4,12,24,tunS)
    if dir_=="up":
        # back: apron straps cross (X)
        for k in range(6):
            px(im,5+k,13+k,apS); px(im,10-k,13+k,apS)
        rect(im,5,20,10,24, apS)            # waist tie
    else:
        rect(im,5,14,10,23, ap)             # apron bib
        vline(im,5,14,23,apS); vline(im,10,14,23,apS)
        hline(im,5,10,23,apS)
        px(im,5,14,apS); px(im,10,14,apS)
        # straps up to shoulders
        px(im,5,13,apS); px(im,6,12,apS); px(im,9,12,apS); px(im,10,13,apS)
        px(im,7,17,LEATH_L); px(im,9,20,LEATH_L)  # apron highlights
    # belt
    hline(im,4,11,24,BELT); px(im,7,24,BUCKLE); px(im,8,24,BUCKLE)

    # ---- arms ----
    def upper(x0,x1,y0,y1): rect(im,x0,y0,x1,y1,tun)     # sleeve
    def fore(x0,x1,y0,y1):  rect(im,x0,y0,x1,y1,skin)    # forearm

    if dir_=="right":
        # side profile facing right. back arm behind (dark), front arm acts.
        rect(im,4,13,5,19,tunS)              # back arm sleeve
        px(im,4,20,skinD)
        if hammer:
            up = (col==3)
            fore(10,12,(12 if up else 17),(15 if up else 19))
            px(im,10,16,GLOVE)
            draw_hammer(im,12,(10 if up else 20),"side")
        elif tongs:
            bob=col-5
            fore(10,11,17+bob,20+bob); px(im,11,20+bob,GLOVE)
            draw_tongs(im,12,18+bob,"side")
        else:
            sw = -1 if col==2 else (1 if col==1 else 0)  # arm swing
            upper(10,11,13,17); fore(10,11,17,20+sw)
    else:
        # front (down) / back (up)
        # left arm
        upper(3,4,13,17); fore(3,4,17,20)
        # right arm
        if dir_=="down" and hammer:
            if col==3:
                upper(11,12,11,15); fore(11,12,8,11)
                draw_hammer(im,11,6,"up"); px(im,11,7,GLOVE)
            else:
                upper(11,12,13,17); fore(11,12,17,21); px(im,11,21,GLOVE)
                draw_hammer(im,11,22,"down")
        elif dir_=="down" and tongs:
            bob=col-5
            upper(11,12,13,17); fore(11,12,17,20+bob); px(im,11,20+bob,GLOVE)
            draw_tongs(im,12,19+bob,"down")
        else:
            sw = -1 if col==2 else (1 if col==1 else 0)
            upper(11,12,13,17); fore(11,12,17,20+sw)
            if dir_=="down":  # left arm swing opposite
                fore(3,4,17,20-sw)

    # ---- head (y 3-12) ----
    if dir_=="up":
        rect(im,5,4,10,11, hair)            # back of head = hair
        if band: hline(im,5,10,6,band)
        rect(im,6,11,9,12, skinD)           # nape
    elif dir_=="down":
        rect(im,5,5,10,11, skin)            # face
        rect(im,5,3,10,5, hair)             # hair top
        px(im,4,5,hair); px(im,11,5,hair); px(im,4,6,hair); px(im,11,6,hair)
        if band: hline(im,5,10,5,band)
        px(im,6,8,BLACK); px(im,9,8,BLACK)  # eyes
        px(im,7,9,skinD)                    # nose shade
        # beard covers lower face + sides
        rect(im,5,10,10,12, beard); px(im,4,9,beard); px(im,11,9,beard)
        px(im,7,11,MOUTH); px(im,8,11,MOUTH)
        px(im,5,7,skinD); px(im,10,7,skinD) # cheek shade
    else:  # right profile
        rect(im,5,5,10,11, skin)
        rect(im,5,3,10,5, hair); px(im,5,5,hair); px(im,4,5,hair)
        rect(im,4,6,4,8,hair)               # back hair
        if band: hline(im,5,10,5,band)
        px(im,9,8,BLACK)                    # eye
        px(im,11,8,skin); px(im,11,9,skinD) # nose bump
        rect(im,6,10,11,12, beard)          # beard forward
        px(im,7,11,MOUTH)

    return im

def draw_hammer(im,x,y,orient):
    if orient=="up":                     # head at top, handle down
        vline(im,x,y+2,y+8,WOOD); px(im,x,y+5,WOOD_L)
        rect(im,x-2,y,x+2,y+1,IRON); rect(im,x-2,y,x+2,y,IRON_L)
        px(im,x-2,y+1,IRON_D); px(im,x+2,y+1,IRON_D)
    elif orient=="down":                 # striking down
        vline(im,x,y-6,y-1,WOOD)
        rect(im,x-2,y,x+2,y+1,IRON); px(im,x-2,y,IRON_L)
    else:                                # side
        vline(im,x-1,y,y+5,WOOD)
        rect(im,x,y-2,x+2,y+1,IRON); px(im,x+2,y-2,IRON_L); px(im,x,y+1,IRON_D)

def draw_tongs(im,x,y,orient):
    if orient=="side":
        hline(im,x,x+2,y,IRON); hline(im,x,x+2,y+2,IRON)
        px(im,x+3,y+1,EMBER_HOT); px(im,x+4,y+1,EMBER)   # glowing bar
        px(im,x+3,y,EMBER_HOT)
    else:
        vline(im,x,y,y+2,IRON); px(im,x-1,y,IRON); px(im,x+1,y,IRON)
        px(im,x,y+3,EMBER_HOT); px(im,x,y+4,EMBER)
        px(im,x-1,y+3,EMBER_HOT); px(im,x+1,y+3,EMBER_HOT)

def build_characters():
    print("characters:")
    dirs=["down","up","right"]
    for i,p in enumerate(CHAR_PALETTES):
        sheet=new(112,96)
        for d,dname in enumerate(dirs):
            for col in range(7):
                fr=draw_char_frame(dname,col,p)
                sheet.paste(fr,(col*16,d*32),fr)
        save(sheet, os.path.join(ROOT,"characters",f"char_{i}.png"))

# ══════════════════════════════════════════════════════════════════
# FLOORS — grayscale patterns (colorized at runtime)
# ══════════════════════════════════════════════════════════════════
def g(v): return (v,v,v,255)
def build_floors():
    print("floors:")
    tiles=[]
    # 0 flagstone
    def flag():
        im=new(16,16); rect(im,0,0,15,15,g(150))
        for (x0,y0,x1,y1) in [(0,0,7,7),(8,0,15,6),(0,8,6,15),(7,8,15,15)]:
            rect(im,x0,y0,x1,y1,g(150))
        # mortar seams
        hline(im,0,15,7,g(90)); vline(im,7,0,7,g(90)); vline(im,8,8,15,g(90))
        # speckle
        px(im,3,3,g(170)); px(im,11,4,g(130)); px(im,4,11,g(165)); px(im,12,12,g(135))
        return im
    # 1 cobblestone
    def cobble():
        im=new(16,16); rect(im,0,0,15,15,g(95))
        for cy in (2,10):
            for cx in (2,9):
                rect(im,cx,cy,cx+4,cy+4,g(150))
                px(im,cx,cy,g(175)); px(im,cx+4,cy+4,g(120))
        return im
    # 2 wood planks
    def planks():
        im=new(16,16); rect(im,0,0,15,15,g(140))
        hline(im,0,15,5,g(95)); hline(im,0,15,11,g(95))
        for y in (0,6,12):
            for x in range(0,16,2): px(im,x,y+2,g(155))
        vline(im,8,0,4,g(100)); vline(im,4,6,10,g(100)); vline(im,12,12,15,g(100))
        return im
    # 3 dirt/soot
    def dirt():
        im=new(16,16); rect(im,0,0,15,15,g(80))
        import random; random.seed(3)
        for _ in range(40):
            x=random.randint(0,15); y=random.randint(0,15); px(im,x,y,g(random.choice([60,70,95,105])))
        return im
    # 4 brick
    def brick():
        im=new(16,16); rect(im,0,0,15,15,g(130))
        hline(im,0,15,3,g(80)); hline(im,0,15,7,g(80)); hline(im,0,15,11,g(80)); hline(im,0,15,15,g(80))
        vline(im,7,0,3,g(80)); vline(im,3,4,7,g(80)); vline(im,11,4,7,g(80)); vline(im,7,8,11,g(80)); vline(im,3,12,15,g(80)); vline(im,11,12,15,g(80))
        return im
    # 5 ash/gravel
    def gravel():
        im=new(16,16); rect(im,0,0,15,15,g(110))
        import random; random.seed(5)
        for _ in range(55):
            x=random.randint(0,15); y=random.randint(0,15); px(im,x,y,g(random.choice([85,95,130,145])))
        return im
    for fn in (flag,cobble,planks,dirt,brick,gravel):
        tiles.append(fn())
    for i,im in enumerate(tiles):
        save(im, os.path.join(ROOT,"floors",f"floor_{i}.png"))

# ══════════════════════════════════════════════════════════════════
# WALLS — stone masonry autotile, 16 pieces (16x32, bottom-anchored)
# ══════════════════════════════════════════════════════════════════
def build_walls():
    print("walls:")
    sheet=new(64,128)
    for mask in range(16):
        n=bool(mask&1); e=bool(mask&2); s=bool(mask&4); w=bool(mask&8)
        piece=new(16,32)
        # top face (rows 0-7) = wall top / crenellation, body (8-31) = stone face
        # body stone
        rect(piece,0,0,15,31,STONE)
        # brick coursing on the face (rows 8..31)
        for y in range(8,32,4):
            hline(piece,0,15,y,MORTAR)
        offset=0
        for y in range(10,32,8):
            # stagger vertical mortar
            for x in range(0,16,8):
                vline(piece,(x+offset)%16,y,y+3,MORTAR)
            offset=4-offset if offset==0 else 0
        # highlight speckles
        px(piece,3,12,STONE_L); px(piece,11,18,STONE_L); px(piece,6,26,STONE_D); px(piece,13,10,STONE_D)
        # top cap (rows 0-7): lighter stone rim
        rect(piece,0,0,15,7,STONE_D)
        rect(piece,1,1,14,6,STONE)
        hline(piece,1,14,1,STONE_L)
        # Edge treatment when NOT connected: draw darker border/pillar edge
        if not w:  # west open
            vline(piece,0,0,31,STONE_D); vline(piece,1,8,31,MORTAR)
        if not e:  # east open
            vline(piece,15,0,31,STONE_D); vline(piece,14,8,31,MORTAR)
        if not n:  # north open — emphasize top rim
            hline(piece,0,15,0,BLACK); hline(piece,1,14,1,STONE_L)
        if not s:  # south open — base shadow line
            hline(piece,0,15,31,BLACK)
        ox=(mask%4)*16; oy=(mask//4)*32
        sheet.paste(piece,(ox,oy),piece)
    save(sheet, os.path.join(ROOT,"walls","wall_0.png"))

# ══════════════════════════════════════════════════════════════════
# FURNITURE
# ══════════════════════════════════════════════════════════════════
def furn_dir(name):
    d=os.path.join(ROOT,"furniture",name); os.makedirs(d,exist_ok=True); return d

def write_manifest(name, data):
    with open(os.path.join(furn_dir(name),"manifest.json"),"w") as f:
        json.dump(data,f,indent=2)
    print("  manifest",name)

def single(name,label,category,w,h,fw,fh,draw, **extra):
    im=new(w,h); draw(im)
    save(im, os.path.join(furn_dir(name),f"{name}.png"))
    m=dict(id=name,name=label,category=category,type="asset",file=f"{name}.png",
           width=w,height=h,footprintW=fw,footprintH=fh)
    m.update(extra)
    write_manifest(name,m)

def build_furniture():
    print("furniture:")
    # ANVIL 1x1
    def d_anvil(im):
        rect(im,3,10,12,13, IRON)       # base
        rect(im,5,13,10,15, IRON_D)
        rect(im,4,7,11,9, IRON_L)       # top face
        rect(im,2,7,4,8, IRON_L)        # horn
        px(im,2,7,STEEL); hline(im,4,11,7,STEEL)
        rect(im,6,9,9,10, IRON_D)
    single("ANVIL","Anvil","misc",16,16,1,1,d_anvil,canPlaceOnSurfaces=True)

    # FORGE 2x2 hearth with fire
    def d_forge(im):
        rect(im,1,14,30,31, STONE_D)     # stone base
        rect(im,3,16,28,30, STONE)
        for x in range(3,29,4): px(im,x,22,MORTAR)
        rect(im,2,2,29,15, STONE_D)      # chimney hood
        rect(im,4,4,27,13, BLACK)        # opening
        # fire bed
        rect(im,8,16,23,22, EMBER_LOW)
        rect(im,10,17,21,21, EMBER_DEEP)
        rect(im,12,17,19,20, EMBER)
        rect(im,14,17,17,19, EMBER_HOT)
        px(im,13,15,EMBER); px(im,17,14,EMBER_HOT); px(im,15,13,EMBER)
        # hood rim
        hline(im,2,29,2,IRON); hline(im,2,29,15,IRON_D)
    single("FORGE","Forge","misc",32,32,2,2,d_forge,backgroundTiles=1)

    # QUENCH_BARREL storage (tall)
    def d_barrel(im):
        rect(im,3,6,12,22, WOOD)
        vline(im,3,6,22,WOOD_D); vline(im,12,6,22,WOOD_D)
        for x in range(4,12):
            px(im,x,6,WOOD_L)
        hline(im,3,12,9,IRON_D); hline(im,3,12,19,IRON_D)  # iron bands
        rect(im,4,6,11,8, C("2f5f6f"))   # water top
        px(im,6,7,C("4a8090")); px(im,9,7,C("4a8090"))
        rect(im,4,23,11,24, WOOD_D)
    single("QUENCH_BARREL","Quench Barrel","storage",16,26,1,2,d_barrel)

    # CRATE storage
    def d_crate(im):
        rect(im,2,4,13,15, WOOD)
        rect(im,2,4,13,5, WOOD_L); vline(im,2,4,15,WOOD_D); vline(im,13,4,15,WOOD_D)
        # X planks
        for i in range(10):
            px(im,3+i,5+i,WOOD_D); px(im,12-i,5+i,WOOD_D)
        hline(im,2,13,15,WOOD_D)
    single("CRATE","Crate","storage",16,16,1,1,d_crate,canPlaceOnSurfaces=True)

    # TOOL_RACK (wall)
    def d_toolrack(im):
        rect(im,1,2,14,4, WOOD)          # board
        # hanging tools: hammer, tongs, pick
        vline(im,3,4,11,WOOD_L); rect(im,2,11,4,12,IRON)     # hammer
        vline(im,7,4,12,IRON); px(im,6,12,IRON); px(im,8,12,IRON)  # tongs
        vline(im,11,4,10,WOOD_L); rect(im,10,4,13,5,IRON_L)  # pick head
        hline(im,1,14,2,WOOD_D)
    single("TOOL_RACK","Tool Rack","wall",16,16,1,1,d_toolrack,canPlaceOnWalls=True)

    # WEAPON_RACK decor (tall)
    def d_weaprack(im):
        rect(im,1,26,14,29, WOOD_D)      # stand base
        vline(im,2,2,26,WOOD); vline(im,13,2,26,WOOD)
        hline(im,1,14,3,WOOD)
        # swords
        vline(im,5,4,24,STEEL); rect(im,4,22,6,24,WOOD_L); hline(im,3,7,20,IRON) # crossguard
        vline(im,10,4,24,IRON_L); rect(im,9,22,11,24,WOOD_L); hline(im,8,12,20,IRON)
        px(im,5,4,C("ffffff")); px(im,10,4,STEEL)
    single("WEAPON_RACK","Weapon Rack","decor",16,30,1,2,d_weaprack)

    # GRINDSTONE misc
    def d_grind(im):
        rect(im,3,12,12,15, WOOD_D)      # frame legs
        vline(im,3,9,15,WOOD); vline(im,12,9,15,WOOD)
        # wheel
        rect(im,5,6,10,11, STONE_L)
        rect(im,6,5,9,12, STONE_L)
        rect(im,7,7,8,10, STONE_D)       # hub
        px(im,7,6,STONE); px(im,8,11,STONE)
        px(im,10,6,EMBER_HOT)            # spark
    single("GRINDSTONE","Grindstone","misc",16,16,1,1,d_grind)

    # BELLOWS misc
    def d_bellows(im):
        # triangular bellows side view
        for i in range(6):
            hline(im,3,12-i,6+i,LEATH)
        rect(im,11,7,14,11, WOOD)        # handle block
        vline(im,2,6,10,WOOD_D)          # nozzle
        px(im,1,8,IRON)
        hline(im,3,10,9,LEATH_L)
    single("BELLOWS","Bellows","misc",16,16,1,1,d_bellows)

    # STOOL chairs (2-way rotation: front + side)
    def d_stool_front(im):
        rect(im,4,6,11,9, WOOD)          # seat
        rect(im,4,6,11,6, WOOD_L)
        vline(im,5,9,14,WOOD_D); vline(im,10,9,14,WOOD_D)  # legs
        px(im,5,14,BLACK); px(im,10,14,BLACK)
    def d_stool_side(im):
        rect(im,5,6,10,9, WOOD)
        vline(im,6,9,14,WOOD_D); vline(im,9,9,14,WOOD_D)
    stool=furn_dir("STOOL")
    imf=new(16,16); d_stool_front(imf); save(imf,os.path.join(stool,"STOOL_FRONT.png"))
    ims=new(16,16); d_stool_side(ims); save(ims,os.path.join(stool,"STOOL_SIDE.png"))
    write_manifest("STOOL", dict(id="STOOL",name="Stool",category="chairs",type="group",
        groupType="rotation",rotationScheme="3-way-mirror",canPlaceOnWalls=False,
        canPlaceOnSurfaces=False,backgroundTiles=0,members=[
            dict(type="asset",id="STOOL_FRONT",file="STOOL_FRONT.png",width=16,height=16,footprintW=1,footprintH=1,orientation="front"),
            dict(type="asset",id="STOOL_SIDE",file="STOOL_SIDE.png",width=16,height=16,footprintW=1,footprintH=1,orientation="side",mirrorSide=True),
        ]))

    # WORKBENCH (desks category, 2-way like DESK) — smiths sit/work here
    def d_bench_front(im):
        rect(im,0,10,47,31, WOOD)        # top
        rect(im,0,10,47,12, WOOD_L)
        for x in range(0,48,3): px(im,x,11,WOOD_HL)
        rect(im,2,20,45,31, WOOD_D)      # apron/legs
        vline(im,3,12,31,WOOD_D); vline(im,44,12,31,WOOD_D)
        # tools on top
        rect(im,8,6,11,9,IRON)           # small anvil
        px(im,7,7,IRON_L)
        rect(im,20,7,24,9,STONE_L)       # whetstone
        vline(im,34,4,9,WOOD_L); rect(im,33,4,36,5,IRON)  # upright hammer
        px(im,40,7,EMBER_HOT)            # ember
    def d_bench_side(im):
        rect(im,0,10,15,31, WOOD)
        rect(im,0,10,15,12, WOOD_L)
        rect(im,2,20,13,31, WOOD_D)
        vline(im,3,12,31,WOOD_D); vline(im,12,12,31,WOOD_D)
    wb=furn_dir("WORKBENCH")
    a=new(48,32); d_bench_front(a); save(a,os.path.join(wb,"WORKBENCH_FRONT.png"))
    b=new(16,64); d_bench_side(b)
    # extend side top pattern down (reuse simple)
    save(b,os.path.join(wb,"WORKBENCH_SIDE.png"))
    write_manifest("WORKBENCH", dict(id="WORKBENCH",name="Workbench",category="desks",type="group",
        groupType="rotation",rotationScheme="2-way",canPlaceOnWalls=False,
        canPlaceOnSurfaces=False,backgroundTiles=1,members=[
            dict(type="asset",id="WORKBENCH_FRONT",file="WORKBENCH_FRONT.png",width=48,height=32,footprintW=3,footprintH=2,orientation="front"),
            dict(type="asset",id="WORKBENCH_SIDE",file="WORKBENCH_SIDE.png",width=16,height=64,footprintW=1,footprintH=4,orientation="side"),
        ]))

    # SHELF storage (reused as tool/ingot shelf) 2 wide
    def d_shelf(im):
        rect(im,0,2,31,31, WOOD)
        rect(im,0,2,31,3, WOOD_L)
        hline(im,0,31,13,WOOD_D); hline(im,0,31,22,WOOD_D)
        vline(im,0,2,31,WOOD_D); vline(im,31,2,31,WOOD_D)
        # ingots / jars
        for x in (3,8,20,26): rect(im,x,8,x+3,12,IRON_L)
        for x in (4,14,24): rect(im,x,16,x+3,21,C("6a8a3a"))
        rect(im,10,24,20,30, WOOD_L)     # crate on bottom
    single("SHELF","Shelf","storage",32,32,2,2,d_shelf,backgroundTiles=1)

    # BARREL storage small
    def d_barrel2(im):
        rect(im,3,4,12,15, WOOD)
        vline(im,3,4,15,WOOD_D); vline(im,12,4,15,WOOD_D)
        rect(im,3,4,12,5, WOOD_L)
        hline(im,3,12,7,IRON_D); hline(im,3,12,12,IRON_D)
        # arrows/rods sticking out
        vline(im,5,0,4,WOOD_L); vline(im,8,1,4,IRON_L); vline(im,10,0,4,WOOD_L)
    single("BARREL","Barrel","storage",16,16,1,1,d_barrel2,canPlaceOnSurfaces=True)

    # WALL_TORCH (wall) — light source
    def d_torch(im):
        rect(im,6,7,9,15, WOOD)          # bracket handle
        rect(im,5,4,10,7, IRON_D)        # holder
        rect(im,6,0,9,4, EMBER_DEEP)     # flame
        rect(im,6,0,9,2, EMBER)
        px(im,7,0,EMBER_HOT); px(im,8,1,EMBER_HOT)
    single("WALL_TORCH","Wall Torch","wall",16,16,1,1,d_torch,canPlaceOnWalls=True)

    # HORSESHOE_SIGN decor (small wall)
    def d_sign(im):
        rect(im,2,3,13,11, WOOD_D)
        rect(im,3,4,12,10, WOOD)
        # horseshoe
        for x,y in [(6,5),(9,5),(5,6),(10,6),(5,7),(10,7),(6,8),(9,8),(7,9),(8,9)]:
            px(im,x,y,IRON_L)
        vline(im,7,3,3,WOOD_D)
    single("HORSESHOE_SIGN","Sign","decor",16,16,1,1,d_sign,canPlaceOnWalls=True)

    # HAY_BALE decor/misc
    def d_hay(im):
        rect(im,2,6,13,15, C("b89838"))
        rect(im,2,6,13,7, C("d4b850"))
        for y in range(8,15,2): hline(im,2,13,y,C("9a7f2e"))
        vline(im,5,6,15,C("9a7f2e")); vline(im,10,6,15,C("9a7f2e"))
    single("HAY_BALE","Hay Bale","decor",16,16,1,1,d_hay,canPlaceOnSurfaces=True)

    # COAL_PILE misc
    def d_coal(im):
        for (x,y,c) in [(4,12,BLACK),(6,11,C("2a2a30")),(8,12,BLACK),(10,11,C("2a2a30")),
                        (5,13,BLACK),(7,13,C("1a1a1e")),(9,13,BLACK),(11,13,C("2a2a30")),
                        (6,14,BLACK),(8,14,BLACK),(10,14,BLACK),(4,14,C("2a2a30")),(12,14,BLACK)]:
            rect(im,x,y,x+1,y+1,c)
        px(im,7,11,EMBER_HOT); px(im,9,12,EMBER)   # glowing coals
    single("COAL_PILE","Coal Pile","misc",16,16,1,1,d_coal,canPlaceOnSurfaces=True)

    # INGOT_PILE misc — stacked iron ingots
    def d_ingots(im):
        for (x,y) in [(3,12),(7,12),(11,12)]:
            rect(im,x,y,x+3,y+2,IRON_L); hline(im,x,x+3,y,STEEL); px(im,x+3,y+2,IRON_D)
        rect(im,5,9,8,11,IRON_L); hline(im,5,8,9,STEEL); px(im,8,11,IRON_D)  # top ingot
    single("INGOT_PILE","Iron Ingots","storage",16,16,1,1,d_ingots,canPlaceOnSurfaces=True)

    # WATER_TROUGH storage (2 wide) — for cooling
    def d_trough(im):
        rect(im,0,6,31,15, WOOD)
        rect(im,0,6,31,7, WOOD_L)
        rect(im,2,7,29,11, C("2f5f6f"))          # water
        hline(im,3,28,8,C("4a8090")); px(im,10,9,C("6aa0b0")); px(im,20,10,C("6aa0b0"))
        vline(im,0,6,15,WOOD_D); vline(im,31,6,15,WOOD_D); hline(im,0,31,15,WOOD_D)
        hline(im,0,31,13,IRON_D)                  # band
    single("WATER_TROUGH","Water Trough","storage",32,16,2,1,d_trough)

    # LANTERN (wall) — hanging light
    def d_lantern(im):
        vline(im,7,0,2,IRON)                      # hook
        rect(im,5,3,10,4, IRON_D)                 # top cap
        rect(im,5,4,10,11, IRON)                  # frame
        rect(im,6,5,9,10, EMBER_HOT)              # glow
        rect(im,7,6,8,9, C("ffffff"))
        vline(im,5,4,11,IRON_D); vline(im,10,4,11,IRON_D)
        rect(im,5,11,10,12, IRON_D)
    single("LANTERN","Lantern","wall",16,16,1,1,d_lantern,canPlaceOnWalls=True)

    # SWORD_DISPLAY (wall) — crossed swords plaque
    def d_swords(im):
        rect(im,2,2,13,13, WOOD_D); rect(im,3,3,12,12, WOOD)
        for i in range(9):
            px(im,3+i,3+i,STEEL); px(im,12-i,3+i,IRON_L)   # crossed blades
        hline(im,4,8,10,IRON); hline(im,7,11,10,IRON)      # guards
        px(im,7,7,EMBER_HOT)                                # center rivet glow
    single("SWORD_DISPLAY","Sword Display","decor",16,16,1,1,d_swords,canPlaceOnWalls=True)

    # NOTICE_BOARD decor — standing quest/work-orders board
    def d_board(im):
        vline(im,3,15,23,WOOD_D); vline(im,4,15,23,WOOD_D)      # posts
        vline(im,11,15,23,WOOD_D); vline(im,12,15,23,WOOD_D)
        rect(im,1,2,14,16, WOOD_D)                               # frame
        rect(im,2,3,13,15, C("caa36a"))                         # cork/parchment back
        # pinned notes
        rect(im,3,5,6,9, C("efe6d0")); px(im,4,4,IRON_L)        # note 1 + pin
        rect(im,8,4,12,8, C("f2ecd8")); px(im,10,3,IRON_L)      # note 2
        rect(im,4,11,8,14, C("e6dcc0")); px(im,6,10,IRON_L)     # note 3
        rect(im,9,10,12,14, C("efe6d0")); px(im,10,10,IRON_L)   # note 4
        # scribble lines on notes
        hline(im,3,5,6,C("9a8a5a")); hline(im,3,5,7,C("9a8a5a"))
        hline(im,8,11,5,C("9a8a5a")); hline(im,9,11,6,C("9a8a5a"))
        rect(im,0,16,15,17, WOOD_L)                              # top ledge shade
    single("NOTICE_BOARD","Work Board","decor",16,24,1,1,d_board)

    # ── Tavern ───────────────────────────────────────────────
    BOTTLE=[C("3a6a3a"),C("6a3a3a"),C("3a3a6a"),C("6a6a2e"),C("5a3a6a")]
    ALE=C("c9922e"); FOAM=C("f0e6c0")

    # BAR_COUNTER 3-wide bar with back shelf of bottles + mugs on top
    def d_bar(im):
        rect(im,0,0,47,9, WOOD_D)                 # back shelf
        rect(im,1,1,46,8, C("2f2016"))
        for i,x in enumerate(range(3,45,4)):
            b=BOTTLE[i%len(BOTTLE)]; rect(im,x,3,x+1,7,b); px(im,x,2,C("caa36a"))
        rect(im,0,10,47,13, WOOD_L)               # counter top
        hline(im,0,47,10,WOOD_HL)
        for x in (7,22,37):                        # mugs on counter
            rect(im,x,8,x+2,10,ALE); hline(im,x,x+2,7,FOAM)
        rect(im,0,14,47,27, WOOD)                  # front
        for x in range(0,48,4): vline(im,x,14,27,WOOD_D)
        hline(im,0,47,13,WOOD_HL); hline(im,0,47,27,WOOD_D)
    single("BAR_COUNTER","Bar Counter","misc",48,28,3,1,d_bar)

    # KEG of ale with a tap
    def d_keg(im):
        rect(im,2,3,13,15, WOOD); rect(im,2,3,13,4, WOOD_L)
        vline(im,2,3,15,WOOD_D); vline(im,13,3,15,WOOD_D)
        hline(im,2,13,7,IRON_D); hline(im,2,13,12,IRON_D)
        rect(im,6,16,9,17,IRON); px(im,7,17,ALE)   # tap + drip
    single("KEG","Keg","storage",16,18,1,1,d_keg)

    # BAR_STOOL — walkable decor (backgroundTiles) so NPCs can sit on it
    def d_barstool(im):
        rect(im,5,8,10,10, WOOD_L); px(im,5,8,WOOD); px(im,10,8,WOOD)
        vline(im,7,10,14,WOOD_D); vline(im,8,10,14,WOOD_D)
        hline(im,5,10,14,WOOD_D)
    single("BAR_STOOL","Bar Stool","decor",16,16,1,1,d_barstool,backgroundTiles=1)

    # MUG of ale (surface item)
    def d_mug(im):
        rect(im,4,6,10,13,ALE); rect(im,4,4,10,6,FOAM)
        vline(im,11,7,11,C("8a6a2e")); px(im,11,8,C("8a6a2e"))
        rect(im,4,6,10,13,ALE); hline(im,4,10,13,C("9a6f22"))
    single("MUG","Mug of Ale","decor",16,16,1,1,d_mug,canPlaceOnSurfaces=True)

    # TAVERN_SIGN — wall mug sign
    def d_tavsign(im):
        rect(im,2,2,13,13,WOOD_D); rect(im,3,3,12,12,WOOD)
        rect(im,5,6,9,11,ALE); rect(im,5,5,9,6,FOAM)
        vline(im,10,7,10,C("8a6a2e"))
    single("TAVERN_SIGN","Tavern Sign","wall",16,16,1,1,d_tavsign,canPlaceOnWalls=True)

    # CARD_TABLE — green-felt table with card fans + coins
    def d_cardtable(im):
        rect(im,0,6,31,15, WOOD); rect(im,0,6,31,7, WOOD_L)
        rect(im,2,7,29,13, C("2f5a3a"))          # felt
        rect(im,2,16,4,19,WOOD_D); rect(im,27,16,29,19,WOOD_D)  # legs
        rect(im,5,8,9,12, C("f0ece0")); rect(im,6,8,10,12, C("f0ece0"))
        px(im,7,9,C("a02020"))
        rect(im,21,8,25,12, C("f0ece0")); px(im,23,9,C("20208a"))
        px(im,15,10,C("ffd24a")); px(im,16,11,C("ffd24a")); px(im,14,11,C("d1a02a"))
    single("CARD_TABLE","Card Table","misc",32,20,2,1,d_cardtable)

    # DRUM
    def d_drum(im):
        rect(im,3,7,12,14, C("8a3a2a")); rect(im,3,6,12,8, C("e0d8c0"))
        hline(im,3,12,10,C("caa36a")); hline(im,3,12,12,C("caa36a"))
        vline(im,5,4,7,WOOD_L); vline(im,10,4,7,WOOD_L)   # sticks
    single("DRUM","Drum","decor",16,16,1,1,d_drum)

    # LUTE
    def d_lute(im):
        rect(im,3,8,9,13, WOOD); px(im,3,8,WOOD_D); px(im,9,13,WOOD_D)
        rect(im,5,10,7,11, C("2a1a0e"))          # sound hole
        vline(im,9,3,8,WOOD_L); vline(im,10,3,8,WOOD_L); px(im,10,3,WOOD_D)
        vline(im,6,9,12,C("caa36a"))             # strings
    single("LUTE","Lute","decor",16,16,1,1,d_lute)

def remove_office_furniture():
    print("removing office-only furniture:")
    office=["PC","WHITEBOARD","COFFEE","COFFEE_TABLE","SOFA","CUSHIONED_CHAIR","CUSHIONED_BENCH",
            "LARGE_PAINTING","SMALL_PAINTING","SMALL_PAINTING_2","HANGING_PLANT","CACTUS","CLOCK",
            "DOUBLE_BOOKSHELF","BOOKSHELF","DESK","BIN","LARGE_PLANT","PLANT","PLANT_2","POT",
            "TABLE_FRONT","SMALL_TABLE","COFFEE_TABLE","WOODEN_CHAIR","WOODEN_BENCH","TABLE"]
    import shutil
    for n in office:
        d=os.path.join(ROOT,"furniture",n)
        if os.path.isdir(d):
            shutil.rmtree(d); print("  removed",n)

if __name__=="__main__":
    build_characters()
    build_floors()
    build_walls()
    build_furniture()
    remove_office_furniture()
    print("DONE")
