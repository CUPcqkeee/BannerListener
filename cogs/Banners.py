import io
from io import BytesIO

import disnake
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont
import asyncio
from datetime import datetime, timedelta, timezone
import random


class BannerUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 998684071829966989
        self.channel_id = 1051114841412210710
        self.base_image_path = "./resources/banner.png"
        self.font_path = "arial.ttf"
        self.update_interval = 60
        self.update_member_interval = 2 * 60 * 60
        self.last_banner_message = None
        self.last_member_update = None
        self.message_counts = {}
        self.voice_time = {}

        self.bot.loop.create_task(self.update_banner_loop())
        self.bot.loop.create_task(self.update_member_loop())

    async def update_banner_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.update_banner()
            await asyncio.sleep(self.update_interval)

    async def update_member_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.last_member_update is None or datetime.utcnow() - self.last_member_update > timedelta(
                    seconds=self.update_member_interval):
                await self.update_most_active_member()
                self.last_member_update = datetime.utcnow()
            await asyncio.sleep(self.update_interval)

    async def update_banner(self):
        guild = self.bot.get_guild(self.guild_id)
        # channel = guild.get_channel(self.channel_id)
        if not guild:
            return

        total_members = guild.member_count

        most_active_member = self.most_active_member if hasattr(self, 'most_active_member') else None

        base_image = Image.open(self.base_image_path)
        white_color = "#FFFFFF"
        draw = ImageDraw.Draw(base_image)
        font = ImageFont.truetype(self.font_path, 70)
        font_activity_player = ImageFont.truetype(self.font_path, 80)
        font_activity_player_not_find = ImageFont.truetype(self.font_path, 50)

        draw.text((1130, 610), f"{total_members}", fill=white_color, font=font)
        if most_active_member:
            try:
                avatar_bytes = await most_active_member.display_avatar.read()
                avatar_image = Image.open(BytesIO(avatar_bytes)).convert("RGBA")

                avatar_image = avatar_image.resize((280, 280), Image.ADAPTIVE)

                # # # # #

                mask = Image.new("L", (280, 280), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, 280, 280), fill=255)

                # # # # #

                rounded_avatar = Image.new("RGBA", (280, 280), (255, 255, 255, 0))
                rounded_avatar.paste(avatar_image, (0, 0), mask)

                # # # # #

                base_image.paste(rounded_avatar, (292, 702), rounded_avatar)

                # # # # #
                draw_text = ImageDraw.Draw(base_image)

                username = most_active_member.display_name[:15] + '...' if len(
                    most_active_member.display_name) > 15 else most_active_member.display_name
                draw_text.text((650, 800), username, fill=white_color, font=font_activity_player)
            except BaseException as event:
                print(event)

                draw_text = ImageDraw.Draw(base_image)

                username = most_active_member.display_name[:15] + '...' if len(
                    most_active_member.display_name) > 15 else most_active_member.display_name
                draw_text.text((650, 800), username, fill=white_color, font=font_activity_player)
        else:
            draw.text((650, 800), "Нет активного пользователя", fill=white_color, font=font_activity_player_not_find)

        # print("TEST")
        # ----------------- ГС КАНАЛЫ -----------------
        voice_channels = sum(len(channel.members) for channel in guild.voice_channels)

        draw.text((1525, 730), f"{voice_channels}", fill=white_color, font=font)
        # ---------------------------------------------------

        banner_path = "./resources/banner_with_info.png"
        base_image.save(banner_path, format="PNG")
        with open(banner_path, "rb") as foto:
            banner = foto.read()

        try:
            await guild.edit(banner=banner)
            print(banner)
        except BaseException as event:
            print(f"Не удалось обновить баннер: {event}")

    async def update_most_active_member(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return

        current_time = datetime.now(timezone(timedelta(hours=+3)))

        for member in guild.members:
            if member.voice and member.voice.channel:
                if member not in self.voice_time:
                    self.voice_time[member] = current_time
            elif member in self.voice_time:
                del self.voice_time[member]

        def get_most_active_by_voice_time():
            active_members = {}

            active_time_threshold = timedelta(minutes=1)

            for member, start_time in self.voice_time.items():
                time_in_voice = current_time - start_time

                if time_in_voice >= active_time_threshold:
                    active_members[member] = time_in_voice

            if active_members:
                most_active_member = max(active_members, key=active_members.get)
            else:
                most_active_member = None

            return most_active_member

        most_active_member = get_most_active_by_voice_time()
        #print(most_active_member)
        self.most_active_member = most_active_member


def setup(bot):
    bot.add_cog(BannerUpdater(bot))
