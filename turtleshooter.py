import turtle, time, random, keyboard, tkinter, base64, zlib
from tkinter import messagebox

global money, ammo, shots, bullet_speed, firerate, last_score, score
money = 0
last_money = 0
score = 0
last_score = 0
level = 1
ammo = 15
shots = 0
bullet_speed = 200
firerate = 0.35

def start(new):
    global t, text, screen, canvas, score, level, enemies, bosses, bullets, bCooldown, last_time, running, drawtext, shoot, add_enemy, add_boss, create_save, parse_save, paused
    t = turtle.Turtle()
    t.shape("classic")
    t.color("green")
    t.penup()
    t.speed(0)
    text = turtle.Turtle()
    text.hideturtle()
    text.penup()
    screen = turtle.Screen()

    # center the window
    screen.update()  # make sure window size is calculated
    root = screen._root  # get the underlying Tk window

    window_width = 800
    window_height = 800

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    screen.bgcolor("lightgreen")
    canvas = screen.getcanvas()
    screen.tracer(0)
    # for some reason python is a bitch and i need to make basically every single variable global

    enemies = []
    bosses = []
    bullets = []
    global boss_bullets
    boss_bullets = []

    def add_enemy(x, y):
        e = enemy(x, y)
        enemies.append(e)
    def add_boss(x, y, size, hp, spawn, spawns_enemies, moves, min_grapes, max_grapes, cooldown, xplode):
        b = boss(x, y, size, hp, spawn, spawns_enemies, moves, min_grapes, max_grapes, cooldown, xplode)
        bosses.append(b)

    def drawtext(p, x, y, a, i):
        text.goto(x, y)
        text.write(p, align=a, font=("Arial", 16, i))

    def shoot():
        b = bullet()
        bullets.append(b)

    def create_save(level, ammo, bullet_speed, firerate, money, score):
        savecode = f"{level}:{ammo}:{bullet_speed}:{firerate:.2f}${money}:{score}"
        savecode = zlib.compress(savecode.encode())
        savecode = base64.b32encode(savecode).decode()
        savecode = savecode[::-1]
        return savecode

    global hp_bar
    hp_bar = turtle.Turtle()
    hp_bar.hideturtle()
    hp_bar.penup()
    hp_bar.speed(0)

    class bullet:
        def __init__(self):
            self.t = turtle.Turtle()
            self.t.shape("circle")
            self.t.shapesize(0.5, 0.5)
            self.t.color("yellow")
            self.t.penup()
            self.t.speed(0)
            self.t.goto(t.xcor(), t.ycor())
            self.t.setheading(t.heading())
            self.spawntime = time.time()
        
        def move(self):
            global bullet_speed
            self.t.fd(dt*bullet_speed)
            for e in enemies:
                if self.t.distance(e.t) < 20:
                    e.t.hideturtle()
                    enemies.remove(e)
                    self.t.hideturtle()
                    bullets.remove(self)
                    global score, money
                    score += 1
                    if random.randint(1, 5) == 1:
                        money += 3
                    else:
                        money += 1
                    return
            for b in bosses:
                if self.t.distance(b.t) < 20:
                    b.hp -= 1
                    self.t.hideturtle()
                    bullets.remove(self)
                    if b.hp <= 0:
                        b.t.hideturtle()
                        bosses.remove(b)
                        score += 5
                        money += 5
                        for i in range(b.spawn):
                            add_enemy(b.t.xcor() + random.randint(-50, 50), b.t.ycor() + random.randint(-50, 50))
                        if b.size > 4:
                            add_boss(b.t.xcor() + random.randint(-50, 50), b.t.ycor() + random.randint(-50, 50), 4, 20, 10, False, True, 8, 10, 1.5, False)
                            add_boss(b.t.xcor() + random.randint(-50, 50), b.t.ycor() + random.randint(-50, 50), 4, 20, 10, False, True, 8, 10, 1.5, False)

                    return
            if abs(self.t.xcor()) > 820 or abs(self.t.ycor()) > 820:
                self.t.hideturtle()
                bullets.remove(self)
                return
            if self.spawntime + 3 <= time.time():
                self.t.hideturtle()
                bullets.remove(self)
                return
            
    def parse_save(savecode):
        parsedsave = savecode[::-1]
        parsedsave = base64.b32decode(parsedsave.encode())
        parsedsave = zlib.decompress(parsedsave).decode()
        level, ammo, bullet_speed, firerate_money, score = parsedsave.split(":")
        firerate, money = firerate_money.split("$")
        return int(level), int(ammo), int(bullet_speed), float(firerate), int(money), int(score)

    class BossBullet:
        def __init__(self, x, y, angle, speed):
            self.t = turtle.Turtle()
            self.t.shape("circle")
            self.t.shapesize(0.4, 0.4)
            self.t.color("purple")
            self.t.penup()
            self.t.speed(0)
            self.t.goto(x, y)
            self.t.setheading(angle)
            self.speed = speed

        def move(self):
            self.t.fd(dt * self.speed)
            if self.t.distance(t) < 4:
                # player hit
                global score, money
                a = screen.textinput("game over", f"you died! your score: {score}. do you want to try again? (y/n)")
                if a == "y":
                    screen.clearscreen()
                    start(False)
                    money = last_money
                    score = last_score
                else:
                    global running, level, ammo, bullet_speed, firerate
                    level += 1
                    save = create_save(level, ammo, bullet_speed, firerate, money, score)
                    screen._root.clipboard_clear()
                    screen._root.clipboard_append(save)
                    messagebox.showinfo("ok", f"your savecode is {save}, it's already on your clipboard, so just paste it.")
                    running = False

            if abs(self.t.xcor()) > 820 or abs(self.t.ycor()) > 820:
                self.t.hideturtle()
                boss_bullets.remove(self)

    class enemy:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.t = turtle.Turtle()
            self.t.shape("turtle")
            self.t.color("red")
            self.t.penup()
            self.t.speed(0)
            self.t.goto(self.x, self.y)
            self.last_shot = time.time()
        
        def move(self):
            self.t.setheading(self.t.towards(t.xcor(), t.ycor()))
            self.t.fd(dt*50)
            if time.time() - self.last_shot >= (3+random.uniform(-0.5, 0.5)):
                angle = self.t.towards(t.xcor(), t.ycor()) + random.randint(-20,20)
                boss_bullets.append(BossBullet(self.t.xcor(), self.t.ycor(), angle, 145))
                self.last_shot = time.time()
    class boss:
        def __init__(self, x, y, size, hp, spawn, spawns_enemies, moves, min_grapes, max_grapes, cooldown, xplode):
            self.last_shot = time.time()
            self.x = x
            self.y = y
            self.hp = hp
            self.max_hp = hp
            self.last_regen = time.time()
            self.speed = 25
            self.spawn = spawn
            self.enraged = False
            self.size = size
            self.t = turtle.Turtle()
            self.t.shape("turtle")
            self.t.shapesize(size, size)
            self.t.color("red")
            self.t.penup()
            self.t.speed(0)
            self.t.goto(self.x, self.y)
            self.spawns_enemies = spawns_enemies
            self.last_spawn = time.time()
            self.moves = moves
            self.min_grapes = min_grapes
            self.max_grapes = max_grapes
            self.cooldown = cooldown
            self.xplode = xplode
            self.xplode_time = 0
            self.xcount = 0

        def move(self):
            self.t.setheading(self.t.towards(t.xcor(), t.ycor()))
            if self.hp <= self.max_hp / 2:
                self.t.color("orange")
                self.speed = 70
                self.enraged = True
            else:
                if self.enraged:
                    # the point of this is to make the boss remember what you did.
                    self.t.color("#ff4500") # orange-red
                    self.speed = 40
            if (self.moves): self.t.fd(dt*self.speed)

            if self.enraged:
                if time.time() - self.last_regen >= 1.5:
                    if self.hp < self.max_hp:
                        self.hp += 1
                    self.last_regen = time.time()
            else:
                if time.time() - self.last_regen >= 2:
                    if self.hp < self.max_hp:
                        self.hp += 1
                    self.last_regen = time.time()
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            if self.spawns_enemies:
                if time.time() - self.last_spawn >= 5:
                    self.t.bk(60)
                    add_boss(0, 0, 1.5, 2, 0, False, True, 2, 5, 0.25, False)
                    self.t.fd(60)
                    self.last_spawn = time.time()

            if time.time() - self.last_shot >= self.cooldown:
                # this one change made the game feel like touhou lmao
                angle = random.randint(0, 360)
                a = random.randint(self.min_grapes, self.max_grapes)
                for i in range(a):
                    angle += 360 / a
                    boss_bullets.append(BossBullet(self.t.xcor(), self.t.ycor(), angle, 240))
                    self.last_shot = time.time()
            if time.time() - self.xplode_time >= 5 and self.xplode:
                if self.xcount < 10:
                    angle = random.randint(0, 360)
                    for i in range(24):
                        angle += i * 360 / 24
                        boss_bullets.append(BossBullet(self.t.xcor(), self.t.ycor(), angle, 240))
                    self.xplode_time += 0.125
                    self.xcount += 1
                else:
                    self.xplode_time = time.time()
                    self.xcount = 0

            hp_bar.goto(self.t.xcor(), self.t.ycor() + 20)
            hp_bar.write(f"HP: {self.hp}", align="center", font=("Arial", 12, "normal"))

    if new:
        messagebox.showinfo("welcome!", "welcome to turtle shooter!")
        b = screen.textinput("save", "do you have a savecode?, if so, paste it here, if not, leave this blank.")
        if b != "" and b is not None:
            level, ammo, bullet_speed, firerate, money, score = parse_save(b)      
        a = ""
        while a != "y" and a != "n":
            a = screen.textinput("tutorial", "do you want to start the tutorial? (y/n)")
            if a == "y":
                messagebox.showinfo("tutorial", "use WASD to move")
                messagebox.showinfo("tutorial", "use the mouse to aim")
                messagebox.showinfo("tutorial", "press space to shoot")
                messagebox.showinfo("tutorial", "you get money for killing enemies, use it to buy upgrades in the shop")
                messagebox.showinfo("tutorial", "there are 35 levels, GL.")


    bCooldown = -0.5
    last_time = time.time()
    running = True
    paused = True
    global waveclear_time, last_collision_check
    waveclear_time = None
    last_collision_check = 0

    if level == 35:
        messagebox.showinfo("you made it", "good job. you made it.")
        messagebox.showinfo("oh no", "but your run ends here.")
        messagebox.showinfo("oh no", "it's time to die.")
        add_boss(random.randint(-300, 300), random.randint(200, 300), 5, 50, 50, True, False, 12, 17, 0.75, True)
    else:
        for i in range(5+(level*3)):
            add_enemy(random.randint(-300, 300), random.randint(200, 300))
        if level % 10 == 0:
            add_boss(random.randint(-300, 300), random.randint(200, 300),4,20,10, False, True, 8, 10, 1.5, False)
        elif level % 4 == 0:
            add_boss(random.randint(-300, 300), random.randint(200, 300),2,10,5, False, True, 5, 7, 2, False)
    paused = False
start(True)
while running:
    hp_bar.clear()
    text.clear()
    cur_time = time.time()
    dt = cur_time - last_time
    last_time = cur_time
    if not paused:
        if keyboard.is_pressed('w'):
            t.fd(dt*70)
        if keyboard.is_pressed('s'):
            t.bk(dt*70)
        if keyboard.is_pressed('a'):
            t.lt(90)
            t.fd(dt*70)
            t.rt(90)
        if keyboard.is_pressed('d'):
            t.rt(90)
            t.fd(dt*70)
            t.lt(90)

        if keyboard.is_pressed('space'):
            if ammo <= shots:
                bCooldown = time.time() + 1.5
                shots = 0
            if time.time() - bCooldown > firerate:
                bCooldown = time.time()
                shoot()
                shots += 1
        # get mouse pointer position relative to the turtle canvas (pixels)
        rootx = canvas.winfo_rootx()
        rooty = canvas.winfo_rooty()
        pointer_x = canvas.winfo_pointerx() - rootx
        pointer_y = canvas.winfo_pointery() - rooty
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        # convert canvas (pixel) coords (origin top-left) to turtle coords (origin center)
        tx = pointer_x - (width / 2)
        ty = (height / 2) - pointer_y
        t.setheading(t.towards(tx, ty))

        for i in enemies:
            i.move()
            if i.t.distance(t) < 20:
                a = screen.textinput("game over", f"you died! your score: {score}. do you want to try again? (y/n)")
                if a == "y":
                    screen.clearscreen()
                    start(False)
                    money = last_money
                    score = last_score
                elif a == "n":
                    level += 1
                    save = create_save(level, ammo, bullet_speed, firerate, money, score)
                    screen._root.clipboard_clear()
                    screen._root.clipboard_append(save)
                    messagebox.showinfo("ok", f"your savecode is {save}, it's already on your clipboard, so just paste it.")
                    running = False
        # enemy-enemy collision resolution
        for i in range(len(enemies)):
            for j in range(i + 1, len(enemies)):
                e1 = enemies[i]
                e2 = enemies[j]
                if e1.t.distance(e2.t) < 20:  # too close
                    # push them apart
                    orig_angle1 = e1.t.heading()
                    orig_angle2 = e2.t.heading()
                    angle = e1.t.towards(e2.t.xcor(), e2.t.ycor())
                    e1.t.setheading(angle + 180)
                    e2.t.setheading(angle)
                    e1.t.fd(dt * 30)
                    e2.t.fd(dt * 30)
                    e1.t.setheading(orig_angle1)
                    e2.t.setheading(orig_angle2)

        for i in bosses:
            i.move()
            if i.t.distance(t) < 20:
                a = screen.textinput("game over", f"you died! your score: {score}. do you want to try again? (y/n)")
                if a == "y":
                    screen.clearscreen()
                    start(False)
                    money = last_money
                    score = last_score
                elif a == "n":
                    level += 1
                    save = create_save(level, ammo, bullet_speed, firerate, money, score)
                    screen._root.clipboard_clear()
                    screen._root.clipboard_append(save)
                    messagebox.showinfo("ok", f"your savecode is {save}, it's already on your clipboard, so just paste it.")
                    running = False
        for i in bullets:
            i.move()
        for i in boss_bullets:
            i.move()
    elif keyboard.is_pressed('q'):
        running = False
    if enemies == [] and bosses == []:
        if waveclear_time is None:
            waveclear_time = time.time()

        elif time.time() - waveclear_time >= 1:
                paused = True
                waveclear_time = None
                if level + 1 > 35:
                    messagebox.showinfo("congratulations!", "you beat the game! thanks for playing :)")
                    break
                messagebox.showinfo("you win!", "you win!")
                a = screen.textinput("next level", "do you want to go to the next level? (y/n)")
                if a == "y":
                    t.goto(0,0)
                    level += 1
                    choice = ""
                    while choice != "4":
                        choice = screen.textinput("shop", 
                            "choose an upgrade:\n"
                            "1: +1 ammo (costs $10)\n"
                            "2: faster bullets (costs $15)\n"
                            "3: faster fire rate (costs $20)\n"
                            "4: exit shop\n"
                        )
                        if choice == "1":
                            if money >= 10:
                                money -= 10
                                ammo += 1
                            else:
                                messagebox.showinfo("haha", "lmao u broke")
                        elif choice == "2":
                            if money >= 15:
                                money -= 15
                                bullet_speed += 20
                            else:
                                messagebox.showinfo("haha", "lmao u broke")
                        elif choice == "3":
                            if firerate > 0.2:
                                if money >= 20:
                                    money -= 20
                                    firerate -= 0.1
                                else:
                                    messagebox.showinfo("haha", "lmao u broke")
                            else:
                                messagebox.showinfo("max", "max fire rate reached")
                        else:
                            pass
                    
                    last_money = money
                    last_score = score
                    cur_time = time.time()
                    last_time = cur_time
                    if level == 35:
                        messagebox.showinfo("you made it", "good job. you made it.")
                        messagebox.showinfo("oh no", "but your run ends here.")
                        messagebox.showinfo("oh no", "it's time to die.")
                        add_boss(random.randint(-300, 300), random.randint(200, 300), 5, 70, 50, True, False, 12, 17, 0.75, True)
                    else:
                        for i in range(5+(level*3)):
                            add_enemy(random.randint(-300, 300), random.randint(200, 300))
                        if level % 10 == 0:
                            add_boss(random.randint(-300, 300), random.randint(200, 300),4,20,10, False, True, 8, 10, 1.5, False)
                        elif level % 4 == 0:
                            add_boss(random.randint(-300, 300), random.randint(200, 300),2,10,5, False, True, 5, 7, 2, False)
                    paused = False
                elif a == "n":
                    level += 1
                    save = create_save(level, ammo, bullet_speed, firerate, money, score)
                    screen._root.clipboard_clear()
                    screen._root.clipboard_append(save)
                    screen._root.update()
                    messagebox.showinfo("ok", f"your savecode is {save}, it's already on your clipboard, so just paste it.")
                    running = False

    drawtext("Score: " + str(score), -390, 370, "left", "normal")
    drawtext("Money: $" + str(money), 0, 370, "center", "normal")
    drawtext("Level: " + str(level), 390, 370, "right", "normal")
    drawtext("Ammo: " + str(ammo-shots) + "/" + str(ammo), 390, -370, "right", "italic")

    screen.update()