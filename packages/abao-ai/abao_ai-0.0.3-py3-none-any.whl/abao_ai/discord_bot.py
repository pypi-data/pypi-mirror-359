from discord import Client, Intents


class Discord(Client):
    def __init__(self) -> None:
        intents = Intents().all()
        Client.__init__(self, intents=intents)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")
        for intent in self.intents:
            print(intent)

    async def on_message(self, message):
        if message.author.bot:
            return
        username = message.author.name

        async with message.channel.typing():
            await message.reply(username)
