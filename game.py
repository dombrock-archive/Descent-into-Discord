import discord
import os
import re
import random
import requests
import json
import pickle
import pprint
import did_api_key

client = discord.Client()

active = True
mock  = False

memories = [] #holds player data
memories_file = 'memories.pk'

enemies_dir = "enemies"
items_dir = "items"
effects_dir = "effects"
enviro_dir = "environments"
traits_dir = "traits"

enemies = []
enemy_list = []

floor = []

enviroment = " "
enviro_list = []

items_list = []

effects_list = []
traits_list = []
levels = [0,30,100,150,200,300,400,500,1000]

bot_command = "?"


active_encounter = False
allow_skip = False

for_sale = []

supply_run = 0
merchant_gone = 3

@client.event
async def on_message(message):

    global active, mock, memories, memories_file, bot_command,enemies, floor, enviroment, enviro_list, items_list, active_encounter, unregistered_message, for_sale, traits_list, supply_run, merchant_gone, enemies_dir, items_dir,effects_dir
    tag = '{0.author.mention} : \n'.format(message)
    unregistered_message = tag+"It seems that you are not registered?"
    help_list = []
    #msgin = re.findall(r"[\w']+", message.content)
    msgin_original = message.content #some functions need case sensitive input
    msgin = message.content.lower()
    msgin = msgin.split(" ")
    msgin_original = msgin_original.split(" ")

    print(msgin)

    def GText(text):
        text = "```css\n"+text+"\n```"
        return text

    def OText(text):
        text = "```fix\n"+text+"\n```"
        return text

    def BText(text):
        text = "```md\n#    "+text+"\n```"
        return text

    def SText(text):
        text = "```\n"+text+"\n```"
        return text

    def save_data():    
        with open(memories_file, 'wb') as fi:
        # dump your data into the file
            pickle.dump(memories, fi)

    def find_user():
        i = 0
        for x in memories:
            if x[0] == tag:
                user = i
                return user               
            i = i + 1
        print("CANT FIND USER!")
        return "none"
        
    def roll_die(dice):
        result = []
        dice  = dice.split("d")
        newsum = 0
        for x in range(int(dice[0])):
            roll = random.randrange( 0, int(dice[1])) +1
            result.append(roll)
            print("roll: "+str(dice)+": "+str(roll))
        for x in result:
            newsum = newsum + x
            print("new sum: "+str(newsum))
            average = newsum / len(result)

        return newsum

    def level_up(exp, user_var):
        i = 0
        levelup = 0
        current_level = memories[user_var][7]
        for x in levels:
            if exp > levels[i]:
                if user_var !="none":
                    user_var = int(user_var)
                    levelup = levelup +1
            i = i +1
        if current_level < levelup:
            gainhp = 10
            if(memories[user_var][13] == "hp"):
                gainhp = gainhp + memories[user_var][14]
            memories[user_var][8] = memories[user_var][8] + gainhp
            memories[user_var][2] = memories[user_var][8]#fill health
        return levelup

    def cmd(input):
        if ((bot_command+input) == msgin[0]):
            print(">>found command exact match\n>>"+msgin[0]+"\n\n")
            return True

    def death_check(user_var):
        #make sure we have an int or none
        if user_var !="none":
            user_var = int(user_var)
            if memories[user_var][2] <= 0:
                return True
            else:
                return False
        else:
            return False

    def GenForSale():
        nfor_sale = []
        for x in range(10):
            nitem = list(random.choice(items_list))
            nfor_sale.append([nitem[0],nitem[3]])
            print("GEN SALES:   "+nitem[0]+" - "+str(nitem[3]))
        for x in range(2):
            nitem = list(random.choice(traits_list))
            nfor_sale.append([nitem[0],nitem[4]])
            print("GEN SALES:   "+nitem[0]+" - "+str(nitem[4]))
        print(str(for_sale))
        return nfor_sale

    def GetItem(user, item):
        memories[user][3] = item[0]
        memories[user][4] = item[1]
        memories[user][9] = item[2]
        memories[user][12] = item[4]

    def GetTrait(user, triat):
        memories[user][11] = triat[0] #trait name
        memories[user][13] = triat[1]#trait tag
        memories[user][14] = triat[2]#trait lvl
        memories[user][15] = triat[3]#trait desc
            

    def SupplyRun():
        global merchant_gone, supply_run
        if merchant_gone > 0:
            merchant_gone = merchant_gone -1
        if supply_run > 5:
            supply_run = 0
            merchant_gone = 3
        else:
            supply_run = supply_run+1

    if message.author == client.user:
        return

    user = find_user() #all other instances of this command are bad!

    #Bot On/Off
    help_list.append(["!bot","Turns the bot on and off."])
    if (cmd("!bot")) and (death_check(user)==False):
        active = not active
        msgout = 'Bot on = ' + str(active)
        await client.send_message(message.channel, msgout)

    #Checks if bot should respond
    if  active == False:
        return

    #Sample Function
    help_list.append(["save","Just save the game!"])
    if (cmd("save")):
        msgout = GText('@HERE - GAME HAS BEEN SAVED')
        save_data()
        await client.send_message(message.channel, msgout)

    #Merchant
    help_list.append(["m","Access merchant. '"+bot_command+"m' to view items and '"+bot_command+"m item-name' to buy."])
    if (cmd("m")):
        print("sale list"+str(for_sale))
        user = find_user()   
        msgout = ""
        if(user != "none"):
            if merchant_gone > 0:
                msgout=tag+GText("The merchant has traveled back to town (wherever that is) for more supplies. He should be back in about "+str(merchant_gone)+" hour(s)(whatever that means)...")
            else:
                if len(msgin) < 2: #just show sale_list list
                    sale_list = ""
                    i= 0
                    for x in for_sale:
                        if i > 9:#displaying trait gems
                            sale_list += SText(x[0]+" (Trait Gem) -- $"+str(x[1])+"\n")
                        else:
                            sale_list += SText(x[0]+" -- $"+str(x[1])+"\n")
                        i = i +1
                    msgout += tag+GText("You approach the merchant and ask to see his wares.")+"__**For Sale:**__\n"+sale_list
                else: #buy something
                    found = False
                    mhas = False
                    for x in for_sale:
                        if msgin[1] == x[0]:
                            mhas = True
                    i = 0
                    for x in traits_list:
                        if msgin[1] == x[0] and found == False and mhas == True:
                            found = True
                            item_cost = x[4]
                            if memories[user][13] == "price":#lower price
                                item_cost = item_cost -memories[user][14]
                                if item_cost < 0:
                                    item_cost = 0
                            if memories[user][10]>=item_cost:
                                memories[user][10] = memories[user][10] - item_cost
                                GetTrait(user, x)
                                msgout = tag+GText(memories[user][1]+" bought "+x[0]+" trait gem. As soon as you posses the gem it disappears, but you can feel its power coursing through your veins. ")
                                if memories[user][13] == "price":
                                    msgout += GText("\n The merchant cut you a pretty sweet deal. He must feel sorry for you.")
                            else:
                                msgout = tag+GText("The merchant says you do not have enough gold for that and that he is not a bank.")
                    for x in items_list:
                        if msgin[1] == x[0] and found == False and mhas == True:
                            found = True
                            item_cost = x[3]
                            if memories[user][13] == "price":#lower price
                                item_cost = item_cost -memories[user][14]
                                if item_cost < 0:
                                    item_cost = 0
                            if memories[user][10]>=item_cost:
                                memories[user][10] = memories[user][10] - item_cost
                                drop = memories[user][3]
                                floor.append(drop)
                                GetItem(user, x)
                                msgout = tag+GText("You bought the "+x[0]+" and dropped your "+drop+". The merchant reminds you of his no returns policy and and wishes you a quick and painless death death.")
                                if memories[user][13] == "price":
                                    msgout += GText("\n The merchant cut you a pretty sweet deal. He must feel sorry for you.")
                            else:
                                msgout = tag+GText("The merchant says you do not have enough gold for that and that he is not a bank.")
                        elif found == False:
                            msgout=tag+GText("The merchant says that he doesn't have any "+msgin[1]+".")
                        i = i+1

        else:
            msgout += unregistered_message
        await client.send_message(message.channel, msgout)


    #Register Player
    help_list.append(["reg","Registers a new player. '"+bot_command+"reg player-name' to register."])
    if (cmd("reg")):
        story = "\nSTORY:\nOne day you happen upon a mysterious Discord server. People seem to be playing some kind of RPG... You are not sure exactly what is going on here (or maybe you are) but you decide to register an account.\nYou choose the name "
        story += msgin[1]
        story += ". I guess that will work but I was expecting something a little more creative to be honest...\n\nAnyways, once you log in you are gifted control of an avatar. Your avatar informs you that they have recently fallen through a sinkhole and are stuck in this world of mythos, fantasy and discord. They request your help to survive. They also inform you that the way that you should help them survive is by issuing them commands and communicating with other players effectively to avoid discord (they seem quite optimistic if not a bit naive). Additionally, they inform you that cooperation with other players is the key to saving not only them but their avatar companions and the very world they inhabit.\n\n"
        story += "*Your avatar is injured from the fall but luckily they were carrying some basic provisions when they fell*.\n\n"
        story += "dis·cord - noun *'A lack of concord or harmony between persons or things, a lack of harmony between notes sounding together.'*.\n\n"
        story += "Your Descent into Discord can be prolonged but not avoided.\n\n"
        # 0 player-tag , 1 name, 2 HP, 3 item, 4 damage, 5 potions, 6 XP, 7 lvl, 8 max HP, 9 effect, 10 gold, 11 trait, 12 wep acc, 13 trait type, 14 trait level, 15 trait desc
        #                0   1        2   3         4   5 6 7 8  9       10 11    12 13      14 15                                              
        memories.append([tag,msgin[1],7,'dagger', '1d4',5,0,1,20,"steel",9,"noob",95,"price",2,"Items from the shop cost 2 less gold."])

        msgout = tag+GText("Registered "+msgin[1]+"\nWelcome to your Descent into Discord. I will be your Dungeon Master.\n"+story)
        msgout += "\n\nSay:\n"+SText(bot_command+"help")+"\nFor a list of commands."
        await client.send_message(message.channel, msgout)

    #Unregister player
    help_list.append(["_u","Unregisters a player."])
    if (cmd("_u")):
        user = find_user()    
        if(user != "none"):
            print(user)
            del memories[user]
            msgout = tag+"UNREGISTERED!"
        else:
            msgout = unregistered_message
        await client.send_message(message.channel, msgout)

    #Check player Status
    help_list.append(["s","Checks your player's status."])
    if (cmd("s")):
        user = find_user()    
        if(user != "none"):
            print(user)
            msgout = tag
            msgout += SText("NAME: "+memories[user][1])
            msgout += SText("\nHP: "+str(memories[user][2])+"/"+str(memories[user][8]))
            msgout += SText("\nITEM: "+memories[user][3]+" - "+memories[user][4]+" - "+memories[user][9]+" - "+str(memories[user][12])+"%")
            msgout += SText("\nPOTIONS: "+str(memories[user][5]))
            msgout += SText("\nEXP: "+str(memories[user][6]))
            msgout += SText("\nLVL: "+str(memories[user][7]))
            msgout += SText("\nTRAIT: \""+memories[user][11]+"\" ("+str(memories[user][15])+")")
            msgout += SText("\nGOLD: "+str(memories[user][10]))
        else:
            msgout = unregistered_message      
        await client.send_message(message.channel, msgout)

    #TRAVEL
    help_list.append(["t","Travel to a new area."])
    if (cmd("t")) and (death_check(user)==False):
        user = find_user()
        print(user)
        if(user != "none"):
            SupplyRun()
            if (random.randrange(0,10)+1) > 4:
                enemy_encounter = True
            else:
                enemy_encounter = False
            if enemy_encounter == False and active_encounter == False:
                enviroment = random.choice(enviro_list)
                floor = []
                for_sale = GenForSale()
                msgout = "@here "+GText("The party travels to a new area and encounters no monsters.")
            elif active_encounter == False or allow_skip == True:
                active_encounter = True
                floor = []
                for_sale = GenForSale()
                selected = False
                while selected == False:
                    enemies= list(random.choice(enemy_list))
                    print(str(enemy_list))
                    if enemies[4] > (memories[user][7]+1): # if enemy level is more than 1 above the user
                        enemies= list(random.choice(enemy_list))
                    else:
                        selected = True
                enviroment = random.choice(enviro_list)
                msgout = "@here "+GText("NEW ENCOUNTER!\n")+SText(enemies[0])+SText("HP: "+str(enemies[1]))+SText("ATK: "+str(enemies[2]))+SText("LVL: "+str(enemies[4]))
            else:
                msgout = tag+GText("You can not travel now. There are enemies nearby.")
        else:
            msgout = unregistered_message      
        await client.send_message(message.channel, msgout)

    #Look around the room
    help_list.append(["l","Looks around."])
    if (cmd("l")) and (death_check(user)==False):
        user = find_user()    
        if(user != "none"):
            print(user)
            if (enemies != []):
                msgout = tag+GText(enviroment)+"\n\n__**ENEMIES:**__\n"+SText(enemies[0])+SText("HP: "+str(enemies[1]))+SText("Atk: "+str(enemies[2]))+SText("LVL: "+str(enemies[4]))+SText("Holding:\n"+', '.join(enemies[3]))+SText("Description: \n"+enemies[5])+SText("Type(s): \n"+', '.join(enemies[6]))
            else:
                msgout = tag+GText(enviroment)+GText("\n There are no visible enemies...")
            msgout+= "\n\n__**Floor:**__ "+SText(', '.join(floor))
        else:
            msgout = unregistered_message      
        await client.send_message(message.channel, msgout)

    #Attack
    help_list.append(["a","Attacks"])
    if (cmd("a")) and (death_check(user)==False):
        user = find_user()    
        if(user != "none"):
            print(user)
            msgout = ""
            user_attack = roll_die(memories[user][4])
            multiplier = 1
            if memories[user][13] == "base":
                multiplier = memories[user][14]
            special_multi = 1.5
            SE = False
            if memories[user][13] == "special":
                special_multi = memories[user][14] 
            for x in effects_list:
                if x[0] == memories[user][9]:
                    for y in x[1]:
                        if y in enemies[6]:
                            SE = True
                            multiplier = multiplier * special_multi
            hit_chance = memories[user][12]
            if memories[user][13] == "acc":
                print("acc effect!")
                print(str(hit_chance))
                hit_chance = hit_chance + memories[user][14]
                print("became "+str(hit_chance)) 
            if random.randrange(0,100) > hit_chance:
                hit = False
                msgout += tag+SText("Swings at the enemy but their weapon is too unwieldy. ")
            else:
                hit = True
            if hit == True:
                user_attack = user_attack *multiplier
                msgout += tag+OText(memories[user][1]+" attack(s) for "+str(user_attack)+" damage!")
                if SE == True:
                    msgout += SText("\n"+memories[user][9]+" was SUPER EFFECTIVE and gained a x"+str(multiplier)+" multiplier!\n")
                if memories[user][13] == "base":
                    msgout += SText("\n"+memories[user][11]+" caused an x"+str(memories[user][14])+" multiplier!\n")
                enemies[1] = enemies[1] - user_attack#hurt enemy
                memories[user][6] = memories[user][6] + user_attack #gain xp
                msgout += SText("\n\n"+enemies[0]+" HP: "+str(enemies[1]))

            l_check = level_up(memories[user][6],user)
            if memories[user][7] < l_check:
                memories[user][7] = l_check
                msgout += tag+SText("Leveled Up!\n\n")
 
            if enemies[1] > 0:
                ehit_chance = enemies[7]
                if memories[user][13] == "agility":
                    print("agility effect!")
                    print(str(ehit_chance))
                    ehit_chance = ehit_chance - memories[user][14]
                    print("became "+str(ehit_chance))
                if random.randrange(0,100) > ehit_chance:
                    hit = False
                    msgout += SText("\nEnemy attack does not make contact.")
                else:
                    hit = True
                if hit == True:
                    enemy_attack = roll_die(enemies[2])
                    memories[user][2] = memories[user][2] - enemy_attack#hurt player
                    msgout += OText("\n\n"+enemies[0]+" counters for "+str(enemy_attack)+" damage!")
                if death_check(user):
                    floor.append(memories[user][3])
                    msgout += "\n\n\n\n@here"+GText(memories[user][1]+"HAS FALLEN IN COMBAT!!!!")
            else:
                active_encounter = False
                xgold = random.randrange(0,enemies[4])+1
                dgold = []
                for x in enemies[3]:
                    floor.append(x)
                for x in range(xgold):
                    dgold.append("gold")
                    floor.append("gold")
                msgout += OText("\n\n"+enemies[0]+" Die(s)!")
                msgout += SText("\n\n"+enemies[0]+" Drop(s):\n"+', '.join(enemies[3])+"\n"+', '.join(dgold))
                enemies = []

        else:
            msgout = unregistered_message      
        await client.send_message(message.channel, msgout)

    #RUN!!!!
    help_list.append(["Run","Run Away!"])
    if (cmd("run")) and (death_check(user)==False):
        user = find_user()
        print(user)     
        msgout = ""
        if(user != "none"):
            enemy_attack = roll_die(enemies[2])
            memories[user][2] = memories[user][2] - enemy_attack#hurt player
            msgout = tag+GText(memories[user][1]+" acts as a distraction taking "+str(enemy_attack)+" damage!"+'\n@here The party flees!!')
            if death_check(user):
                        msgout += GText("\n\n"+tag+"HAS FALLEN PROTECTING THE PARTY!!!!")
            active_encounter = False
            enemies = []
            enviroment = random.choice(enviro_list)
            floor = []
        else:
            msgout = unregistered_message
        await client.send_message(message.channel, msgout)

    #Quaff potion
    help_list.append(["q","Quaff a potion."])
    if (cmd("q")) and (death_check(user)==False):
        user = find_user()   
        msgout = ""
        if(user != "none"):
            print(user)
            if memories[user][5] > 0:
                memories[user][5] = memories[user][5] - 1#use up a potion
                memories[user][2] = memories[user][2] + 5#adds health
                memories[user][6] = memories[user][6] + 5 #gain xp
                l_check = level_up(memories[user][6],user)
                if memories[user][7] < l_check:
                    memories[user][7] = l_check
                    msgout += tag+SText("Leveled Up!\n\n")
                if memories[user][2] > memories[user][8]:
                    memories[user][2] = memories[user][8]
                msgout += tag+GText(" uses a potion and now has "+str(memories[user][2])+"/"+str(memories[user][8])+" HP.")
            else:
                msgout += tag+SText(" You have no potions!")
        else:
            msgout += unregistered_message      
        await client.send_message(message.channel, msgout)

    #Grab
    help_list.append(["g","Grabs and item on the floor. '"+bot_command+"g item-name' to grab. Supports multiple item names separated by a space."])
    if (cmd("g")) and (death_check(user)==False):
        for x in msgin[1:]:
            user = find_user()    
            if(user != "none"): 
                print(user)
                item = x
                i = 0
                found = False
                for x in floor:
                    if item in x and item != "":
                        if item == "potion" and found == False:
                            found = True
                            del floor[i]
                            msgout = tag+GText(memories[user][1]+" grabs "+item)
                            memories[user][5] = memories[user][5] + 1
                        elif item == "gold" and found == False:
                            found = True
                            print(str(floor))
                            print(i)
                            del floor[i]
                            print(str(floor))
                            msgout = tag+GText(memories[user][1]+" grabs "+item)
                            memories[user][10] = memories[user][10] + 1
                        else:
                            for x in items_list:
                                print("searching for "+item)
                                print("checking against "+x[0])
                                if item == x[0] and x[0] in floor and found == False:
                                    print("matched with "+x[0])
                                    found = True
                                    del floor[i]
                                    msgout = tag+GText(memories[user][1]+" grabs "+item+" and drops "+memories[user][3]+".")
                                    floor.append(memories[user][3])
                                    GetItem(user, x)

                    i = i + 1 
                if found == False:
                    msgout = tag+GText("There appears to be no "+item+" in this room...")

            else:
                msgout = unregistered_message      
            await client.send_message(message.channel, msgout)

    help_list.append(["help","Displays Help!"])
    if (cmd("help")):
        msgout = "Descent into Discord - ALPHA\n\nA Discord Dungeon Crawler for any number of players written in Python 3\n\n"
        for x in sorted(help_list):
            msgout += GText(bot_command+' \n'.join(x).replace("\n", "\n--")+"\n\n")
        await client.send_message(message.channel, msgout)

    if (death_check(user)==True):
        msgout = tag + "You are dead..."
        await client.send_message(message.channel, msgout)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#list control
def generate_enemy_list():
    # 0     1   2       3        4    5     6         7 
    # name, hp, attack, [drops], lvl, desc, weakness, acc
    global enemy_list, enemies_dir
    test = []
    for filename in os.listdir(enemies_dir):
        nenemy = []
        print("Loading enemy: "+filename)
        abfile = enemies_dir+"/"+filename
        ndata = open(abfile, "r")
        ndata = ndata.read().split("\n")
        test.append(ndata)
        nenemy.append(ndata[0])
        nenemy.append(int(ndata[1]))
        nenemy.append(ndata[2])
        nenemy.append(list(ndata[3].split(",")))
        nenemy.append(int(ndata[4]))
        nenemy.append(ndata[5])
        nenemy.append(list(ndata[6].split(",")))
        nenemy.append(int(ndata[7]))
        enemy_list.append(nenemy)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(test)

def generate_enviro_list():
    global enviro_list, enviro_dir
    test = []
    for filename in os.listdir(enviro_dir):
        nenviro = []
        print("Loading item: "+filename)
        abfile = enviro_dir+"/"+filename
        ndata = open(abfile, "r")
        ndata = ndata.read().split("\n")
        test.append(ndata)
        nenviro = ndata[0]
        enviro_list.append(nenviro)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(test)



def generate_items_list():
    global items_list, items_dir
    test = []
    for filename in os.listdir(items_dir):
        nitem = []
        print("Loading item: "+filename)
        abfile = items_dir+"/"+filename
        ndata = open(abfile, "r")
        ndata = ndata.read().split("\n")
        test.append(ndata)
        nitem.append(ndata[0])
        nitem.append(ndata[1])
        nitem.append(ndata[2])
        nitem.append(int(ndata[3]))
        nitem.append(int(ndata[4]))
        items_list.append(nitem)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(items_list)


def generate_effects_list():
    global effects_list, effects_dir
    test = []
    for filename in os.listdir(effects_dir):
        neffect = []
        print("Loading item: "+filename)
        abfile = effects_dir+"/"+filename
        ndata = open(abfile, "r")
        ndata = ndata.read().split("\n")
        test.append(ndata)
        neffect.append(ndata[0])
        print(ndata[0])
        neffect.append(list(ndata[1].split(",")))
        print(str(ndata[1]))
        effects_list.append(neffect)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(effects_list)

def generate_traits_list():
    global traits_list, traits_dir
    test = []
    for filename in os.listdir(traits_dir):
        ntrait = []
        print("Loading item: "+filename)
        abfile = traits_dir+"/"+filename
        ndata = open(abfile, "r")
        ndata = ndata.read().split("\n")
        test.append(ndata)
        ntrait.append(ndata[0])
        ntrait.append(ndata[1])
        ntrait.append(float(ndata[2]))
        ntrait.append(ndata[3])
        ntrait.append(int(ndata[4]))
        traits_list.append(ntrait)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(traits_list)
def LoadData():
    global memories
    memories = [] #holds player data
    print("Loading Data...")
    try:
        with open(memories_file, 'rb') as fi:
            memories = pickle.load(fi)
    except IOError:
        open(memories_file,'w+')
    print(str(memories))

#init
generate_enemy_list()
generate_enviro_list()
generate_items_list()
generate_effects_list()
generate_traits_list()

LoadData() #causing errors if no data is written 

client.run(did_api_key.api_key)

