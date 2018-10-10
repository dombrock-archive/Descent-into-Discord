# Descent into Discord
## A multi-user RPG for Discord using discord.py
 
### Try:
https://discord.gg/78Xj6AQ [It's possible that the bot will be offline. Feel free to request that it be turned on!]
### Install:
Requires python 3 and discord.py
```
pip install discord
```
Make sure to put your own API key into the ```did_api_key.py``` file in the root of the game directory.

### Key Features:
-Supports a potentially unlimited amount of players

-Full mod support. Everything from enemies and items to character traits and environmental descriptions are modable with ZERO coding experience.

-Asynchronous player turns. No waiting around. 

-Simple yet deep gameplay loop. The game is easy to learn but that does not hold back the depth. 

### About the game:
'Descent into Discord' was created for a personal "game jam" by myself (Mathieu Dombrock) in the summer of 2017. My goal was to create a fun text based RPG for my friends and I during the break between my summer and fall quarters. Originally the scope of this game was VERY small and about 80% of the features that the game has now were not originally planned. This is the main reason that the code is so gross and the lists are nonsensical. Originally, the game was not even planned to be open-source let alone public. 
 
### Known Issues:
The game might be fun but reading the code is not. The code is very fragile.
 
A lot of the text is not written in the correct person and refers to the player when it should refer to the players avatar. 
 
### Dev Server:
Join the development discussion at: 

https://discord.gg/kyAZw56

### Current Commands:

```
?!bot 
--Turns the bot on and off.
?Run 
--Run Away!
?_u 
--Unregisters a player.
?a 
--Attacks
?g 
--Grabs and item on the floor. '?g item-name' to grab. Supports multiple item names separated by a space.
?help 
--Displays Help!
?l 
--Looks around.
?m 
--Access merchant. '?m' to view items and '?m item-name' to buy.
?q 
--Quaff a potion.
?reg 
--Registers a new player. '?reg player-name' to register.
?s 
--Checks your player's status.
?save 
--Just save the game!
?t 
--Travel to a new area.
```

Note: The Command Key, in this case '?' can be easily changed from within the code to make sure that there is no conflict with other bots. 

