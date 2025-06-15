import os
import discord
from datetime import datetime
import pytz
from discord.ext import commands
from discord import option
from dotenv import load_dotenv

from views.escape_room_view import EscapeRoomView
from utils.channel_helper import create_group_channels, get_progress_and_error

load_dotenv()

import json

bot = commands.Bot(intents=discord.Intents.all())

tz = pytz.timezone('Asia/Taipei')

@bot.event
async def on_ready():
    print("✅ Bot is on and ready!")
    activity = discord.Activity(type=discord.ActivityType.playing, name="時光圖書館")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.slash_command(name="start", description="開始遊戲")
async def start(ctx):
    member_roles = [role.name for role in ctx.user.roles]
    group_id = next((r for r in member_roles if r in [f"000{i}" for i in range(1, 7)]), None)
    if not group_id:
        await ctx.respond("❌ 無效身份組，請確認你的角色。")
        return
    await create_group_channels(ctx, tz, group_id)
    await ctx.respond(f"✅ 組別 {group_id} 的遊戲已開始！")

@bot.slash_command(name="mechanism", description="機關(一個機關只能觸發一次)")
@option("id", description="請輸入觸發的機關號碼", required=True)
async def mechanism(ctx, id: str):
    await ctx.defer()
    member_roles = [role.name for role in ctx.user.roles]
    group_id = next((r for r in member_roles if r in [f"000{i}" for i in range(1, 7)]), None)
    if not group_id:
        await ctx.respond("❌ 無效身份組，請確認你的角色。")
        return

    category = discord.utils.get(ctx.guild.categories, name=group_id)
    if not category or not any(ch.name == "started" for ch in category.channels):
        await ctx.respond("❌ 請先使用 /start 建立遊戲頻道！")
        return

    if id != "31":
        await ctx.respond("無此機關。")
        return

    progress, error = get_progress_and_error(category)
    view = EscapeRoomView(ctx.user.id, progress, error)
    message = await ctx.respond("🗺️ 歡迎來到時光圖書館！請選擇你要進入的房間：", view=view)
    view.message = await message.original_response()

@bot.slash_command(name="password", description="輸入密碼")
@option("pw", description="請輸入密碼", required=True)
async def password(ctx, pw: str):
    await ctx.defer()
    member_roles = [role.name for role in ctx.user.roles]
    group_id = next((r for r in member_roles if r in [f"000{i}" for i in range(1, 7)]), None)
    if not group_id:
        await ctx.respond("❌ 無效身份組，請確認你的角色。")
        return

    category = discord.utils.get(ctx.guild.categories, name=group_id)
    if not category or not any(ch.name == "started" for ch in category.channels):
        await ctx.respond("❌ 請先使用 /start 建立遊戲頻道！")
        return

    progress, error = get_progress_and_error(category)

    correct_pw = {
        "1225": "卡牌35",
        "7326": "卡牌22",
    }

    if pw in correct_pw:
        embed = discord.Embed(title="密碼正確", description=f"請拿取{correct_pw[pw]}。", color=discord.Color.green())
        await ctx.respond(embed=embed)
    else:
        error += 1
        error_channel_name = f"error-{error}"
        if not discord.utils.get(category.channels, name=error_channel_name):
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            player_role = discord.utils.get(ctx.guild.roles, name=group_id)
            if player_role:
                overwrites[player_role] = discord.PermissionOverwrite(read_messages=True)
            await category.create_text_channel(name=error_channel_name, overwrites=overwrites)

        embed = discord.Embed(title="密碼錯誤", description="請再試一次...", color=discord.Color.red())
        await ctx.respond(embed=embed)

@bot.slash_command(name="hint", description="取得提示")
@option("id", description="請輸入提示卡牌編號", required=True)
async def hint(ctx, id: str):
    member_roles = [role.name for role in ctx.user.roles]
    group_id = next((r for r in member_roles if r in [f"000{i}" for i in range(1, 7)]), None)
    if not group_id:
        await ctx.respond("❌ 無效身份組，請確認你的角色。")
        return

    category = discord.utils.get(ctx.guild.categories, name=group_id)
    if not category or not any(ch.name == "started" for ch in category.channels):
        await ctx.respond("❌ 請先使用 /start 建立遊戲頻道！")
        return
    try:
        with open("hint.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        hints = [data[f"{id}-{i}"] for i in range(1, 4) if f"{id}-{i}" in data]

        if not hints:
            await ctx.respond("❌ 查無此卡牌提示。")
            return

        class HintView(discord.ui.View):
            def __init__(self, hints):
                super().__init__(timeout=None)
                self.hints = hints
                self.index = 0

            @discord.ui.button(label="下一個提示", style=discord.ButtonStyle.primary)
            async def next_hint(self, button, interaction):
                self.index += 1
                if self.index < len(self.hints):
                    await interaction.response.edit_message(content=f"💡 提示 {id}-{self.index}: {self.hints[self.index]}", view=self if self.index + 1 < len(self.hints) else None)
                else:
                    await interaction.response.edit_message(view=None)

        await ctx.respond(f"💡 提示 {id}-1: {hints[0]}", view=HintView(hints) if len(hints) > 1 else None)

    except Exception as e:
        await ctx.respond(f"❌ 發生錯誤：{str(e)}")

bot.run("MTM3ODg4MzI2ODM1ODk2NzQ0OA.GFggOy.27YPBLbfSDa11Xh_ybRgo-eoYPL0I1f89v2Vs4")
