import discord
from discord.ui import View, Button

class EscapeRoomView(View):
    def __init__(self, user_id, progress, error):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.progress = progress
        self.error = error
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.message:
            self.message = interaction.message
            self.message.author = interaction.user
        return True

    async def update_progress_channels(self, guild):
        category = discord.utils.get(guild.categories, name="0001")
        if category:
            for ch in category.channels:
                if ch.name.startswith("process-"):
                    await ch.edit(name=f"process-{self.progress}")
                if ch.name.startswith("error-"):
                    await ch.edit(name=f"error-{self.error}")

    @discord.ui.button(label="大廳", style=discord.ButtonStyle.secondary)
    async def enter_hall(self, button: Button, interaction: discord.Interaction):
        if self.progress == 1:
            await interaction.response.send_message("你進入了大廳，裡面有著一個未被點著的火爐，拿取卡片11。")
            self.progress = 2
        elif self.progress > 1:
            await interaction.response.send_message("你再次回到大廳，此時火爐已經熄滅。")
        else:
            await interaction.response.send_message("大廳有一座沒在燃燒的壁盧。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="藏書室", style=discord.ButtonStyle.primary)
    async def enter_library(self, button: Button, interaction: discord.Interaction):
        if self.progress == 0:
            await interaction.response.send_message("你進入了藏書室，拿取卡片B。")
            self.progress = 1
        else:
            await interaction.response.send_message("這裡是藏書室，裡面藏著各種書籍。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="廁所", style=discord.ButtonStyle.secondary)
    async def enter_toilet(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("這是普通的廁所。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="討論室", style=discord.ButtonStyle.secondary)
    async def enter_discussion_room(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("裡面除了桌子什麼也沒有。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="餐廳", style=discord.ButtonStyle.secondary)
    async def enter_restaurant(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("現在好像過了晚餐時間，裡面只有幾隻老鼠再嬉戲。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="影印室", style=discord.ButtonStyle.secondary)
    async def enter_copy_room(self, button: Button, interaction: discord.Interaction):
        if self.progress == 2:
            await interaction.response.send_message("你進入了影印室，拿取卡片B。")
            self.progress = 3
        else:
            await interaction.response.send_message("門好像鎖住了打不開。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="天文館", style=discord.ButtonStyle.secondary)
    async def enter_astronomy(self, button: Button, interaction: discord.Interaction):
        if self.progress == 3:
            await interaction.response.send_message("你進入了天文館，試玩部分結束。")
        else:
            await interaction.response.send_message("天文館一片寂靜，沒有任何異樣。")
        await self.update_progress_channels(interaction.guild)

    @discord.ui.button(label="警衛室", style=discord.ButtonStyle.secondary)
    async def enter_security(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("警衛正在睡覺，你最好不要去打擾。")
        await self.update_progress_channels(interaction.guild)
