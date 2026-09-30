items = ["enemy", "enemy", "enemy", "enemy", "enemy", "dragon", "treasure", "power-up", "power-up"]

enemies = 0

for x in items:
    if x == "enemy":
        enemies += 1
    print(x)
    
print("Number of enemies", enemies)