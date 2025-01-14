from discord.ext import commands, tasks
from discord import Status, ActivityType, Activity
from cmyui.logging import log, Ansi
from random import choice

from objects import glob

class asahiBot(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @tasks.loop(minutes=1)
    async def set_status(self) -> None:
        statuses = [
            {'type': ActivityType.watching, 'message': f'over {len(glob.players) - 1} online user(s)'},
            {'type': ActivityType.playing, 'message': "with Asahi's code"}
        ]

        status = choice(statuses)
        activity = Activity(type=status['type'], name=status['message'])

        await self.bot.change_presence(status=Status.dnd, activity=activity)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if glob.config.debug:
            log('==== Asahi Discord bot started ====', Ansi.GREEN)

        await self.set_status.start()

    async def end_tasks(self) -> None:
        self.set_status.cancel()

    @commands.Cog.listener()
    async def on_command_error(self, _, error) -> None:
        if isinstance(error, commands.errors.CommandNotFound):
            pass

def setup(bot) -> None:
    bot.add_cog(asahiBot(bot))
