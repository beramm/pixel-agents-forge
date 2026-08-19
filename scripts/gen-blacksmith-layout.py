#!/usr/bin/env python3
"""Default layout: FORGE room (top) + TAVERN room (bottom), joined by a hallway."""
import os, json, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","webview-ui","public","assets"))
COLS, ROWS = 21, 22
EMPTY, WALL = 255, 0
FLAG, COBBLE, PLANK, SOOT, BRICK, GRAVEL = 1,2,3,4,5,6

DIV = 11                       # divider wall row between the two rooms
DOOR = (9, 10)                 # doorway columns (hallway) through the divider

tiles=[EMPTY]*(COLS*ROWS)
def idx(c,r): return r*COLS+c
def setf(c,r,v): tiles[idx(c,r)]=v

for r in range(ROWS):
    for c in range(COLS):
        if r in (0,ROWS-1) or c in (0,COLS-1):
            v=EMPTY
        elif r in (1,ROWS-2) or c in (1,COLS-2):
            v=WALL
        elif r==DIV:
            v = FLAG if c in DOOR else WALL      # divider wall w/ doorway
        else:
            v=FLAG
        setf(c,r,v)

# ── Floor zones ──────────────────────────────────────────────────
# Forge room (rows 2..10)
for r in range(2,6):
    for c in range(2,9): setf(c,r,SOOT)          # soot near the forge
for r in range(3,10):
    for c in range(10,18):
        if tiles[idx(c,r)]==FLAG: setf(c,r,PLANK)  # workshop floor
# Tavern room (rows 12..19): wooden floor
for r in range(12,20):
    for c in range(2,19):
        if tiles[idx(c,r)]==FLAG: setf(c,r,PLANK)
for r in range(12,15):
    for c in range(2,9): setf(c,r,FLAG)          # stone under the bar

tileColors=[None]*(COLS*ROWS)

furniture=[]
_seq=[0]
def add(t,c,r):
    _seq[0]+=1
    furniture.append(dict(uid=f"f-{int(time.time()*1000)}-{_seq[0]:04d}",type=t,col=c,row=r))

# ══ FORGE ROOM (rows 2..10) ══════════════════════════════════════
add("FORGE",3,2); add("BELLOWS",2,4); add("COAL_PILE",2,6)
add("ANVIL",6,4); add("INGOT_PILE",6,6)
add("QUENCH_BARREL",8,3); add("WATER_TROUGH",8,5)
add("GRINDSTONE",4,8)
add("WORKBENCH_FRONT",11,3); add("STOOL_FRONT",12,6)
add("WORKBENCH_FRONT",15,3); add("STOOL_FRONT",16,6)
add("WORKBENCH_FRONT",11,7); add("STOOL_FRONT",12,10)
add("SHELF",17,2)
add("WEAPON_RACK",17,8)
add("NOTICE_BOARD",14,9)
# forge wall-mounted (top wall row 1)
add("LANTERN",2,1); add("WALL_TORCH",5,1); add("HORSESHOE_SIGN",8,1)
add("TOOL_RACK",11,1); add("SWORD_DISPLAY",14,1); add("WALL_TORCH",17,1)

# ══ TAVERN ROOM (rows 12..19) ════════════════════════════════════
# 6-wide bar (two counters), bartenders spawn behind (row 12) in code.
add("BAR_COUNTER",2,13); add("BAR_COUNTER",5,13)
# sit tiles auto = row 14 (cols 2..7); stools sit one row in front (row 15)
for c in range(2,8): add("BAR_STOOL",c,15)
add("KEG",8,13); add("KEG",8,14)
# card table + (card seats auto to its left/right)
add("CARD_TABLE",11,16)
# band (musicians spawn just above each instrument in code)
add("DRUM",15,18); add("LUTE",17,18)
# tavern decor
add("HAY_BALE",13,18); add("CRATE",14,18)
# divider-wall decorations facing the tavern (avoid doorway cols 9,10)
add("TAVERN_SIGN",4,DIV); add("WALL_TORCH",7,DIV)
add("LANTERN",13,DIV); add("WALL_TORCH",16,DIV)

layout=dict(version=1,cols=COLS,rows=ROWS,layoutRevision=1,
            tiles=tiles,tileColors=tileColors,furniture=furniture)
out=os.path.join(ROOT,"default-layout-1.json")
with open(out,"w") as f: json.dump(layout,f)
print("wrote",out,"furniture",len(furniture))
