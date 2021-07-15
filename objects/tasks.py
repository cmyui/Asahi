import time
import asyncio

from constants.privs import Privileges
from objects.player import Player
from packets import writer
from . import glob
from cmyui import log

donors = None
frozen = None

async def prepare_tasks():
    global donors
    global frozen
    donors = await glob.db.fetch(f'SELECT * FROM users WHERE priv & {Privileges.Supporter}')
    frozen = await glob.db.fetch(f'SELECT * FROM users WHERE priv & {Privileges.Frozen}')

async def expired_donor():
    while True: # this sux   
        for user in donors:
            if user['donor_end'] < time.time(): # donor expired
                log(f"Removing {user['name']}'s expired donor.")
                
                if (p := glob.players_id.get(user['id'])):
                    p.enqueue(writer.serverRestart(0)) # login will handle the removal, we just need to force a relog
                    continue # go to next player
                    
                # user isn't online, we'll remove it ourselves
                user_priv = Privileges(user['priv'])
                user_priv &= ~Privileges.Supporter
                await glob.db.execute(f'UPDATE users SET priv = %s WHERE id = %s', [int(user_priv), user['id']])
                
        await asyncio.sleep(600) # run every 10 mins
        
async def freeze_timers():
    while True: # this sux v2  
        for user in frozen:
            if user['freeze_timer'] < time.time(): # freeze timer passed
                log(f'Restricting {user["name"]} as their freeze timer expired.')
                
                if (p := glob.players_id.get(user['id'])):
                    p.enqueue(writer.serverRestart(0)) # login will handle restriction for us
                    continue # next player
                    
                # restrict is a bit more complicated, we'll use player object from sql
                p = await Player.from_sql(user['id'])
                p.remove_priv(Privileges.Frozen)
                await p.restrict(reason='Expired freeze timer')
                
        await asyncio.sleep(600) # run every 10 mins