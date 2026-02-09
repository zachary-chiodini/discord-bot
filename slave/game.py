from __future__ import annotations
from io import BytesIO
from random import randint, random
from typing import List, Optional, Union

from discord import (AllowedMentions, ButtonStyle, Color, Embed, File, Interaction, Guild, Member,
    Role, TextChannel, User, Webhook)
from discord.errors import NotFound
from discord.ui import button, Button, View
from emoji import replace_emoji
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from setup import Setup
from stats import Stats


class Game:

    Gamer = Union[Member, Webhook, User]

    def __init__(self, guild: Guild):
        self.npcs = {BabySlime.alias: BabySlime, GoldNeko.alias: GoldNeko,
            Skyevolutrex.alias: Skyevolutrex, MommySlime.alias: MommySlime}
        self.roles = {}
        self.setup = Setup(guild, self.roles)
        self.stats = Stats()

    async def add_heart(self, gamer: Gamer) -> None:
        player = self.stats.get_player(gamer.id)
        if player.health == 10:
            return None
        if player.health == 0:
            new_role = self.roles['❤️']
            image = 'heart1'
            title, note = 'Animation', 'just animated!'
        elif 0 < player.health < 10:
            new_role = self.roles['❤️' * (player.health + 1)]
            image = f"heart{player.health + 1}"
            if player.health + 1 == 10:
                title, note = 'Achieved Maximum Potency', 'achieved maximum potency!'
            else:
                title, note = 'Got a Heart!', f"got +1 {self.roles['❤️'].mention}!"
        elif player.health == -1:
            new_role = self.roles['💀']
            image = 'skull'
            title, note = 'Transmutation', 'is liminal.'
        else:
            new_role = self.roles['👻' * abs(player.health + 1)]
            image = f"ghost{abs(player.health + 1)}"
            title, note = 'Rematerialization', 'is rematerializing!'
        if isinstance(gamer, Member):
            name = gamer.mention
            author = gamer.display_name
            avatar = gamer.display_avatar
            gamer = await gamer.guild.fetch_member(gamer.id)  # Refresh
            for cur_role in gamer.roles:
                if cur_role.name in self.setup.lives:
                    break
            await self.swap_roles(gamer, new_role, cur_role)
        else:
            name = f"**{gamer.name}**"
            author = gamer.name
            avatar = gamer.avatar
        self.stats.increase_health(gamer.id, 1)
        file = File(f"imgs/{image}.png", filename=f"{image}.png")
        embed = Embed(title=title, description=f"{name} {note}\n**Vigor**: {new_role.mention}", color=new_role.color)
        embed.set_image(url=f"attachment://{image}.png")
        embed.set_author(name=author, icon_url=avatar.url)
        await self.setup.guild.system_channel.send(embed=embed, file=file)
        return None

    async def clear_score(self, gamer: Gamer) -> None:
        self.stats.clear_score(gamer.id)
        await self.level_up(gamer)
        return None

    async def decrease_posts(self, gamer: Gamer) -> None:
        await self.increase_posts(gamer, -1)
        return None

    async def decrease_reacts(self, gamer: Gamer) -> None:
        await self.increase_reacts(gamer, -1)
        return None

    async def decrease_score(self, gamer: Gamer, points: int) -> None:
        await self.increase_score(gamer, -points)
        return None

    async def delete(self, gamer: Gamer) -> None:
        self.stats.delete(gamer.id)
        return None

    def get_level_role(self, level: int) -> Role:
        return self.roles['Level'][level]

    async def increase_posts(self, gamer: Gamer, points: int = 1) -> None:
        self.stats.increase_posts(gamer.id, points)
        await self.level_up(gamer)
        return None

    async def increase_reacts(self, gamer: Gamer, points: int = 1) -> None:
        self.stats.increase_reacts(gamer.id, points)
        await self.level_up(gamer)
        return None

    async def increase_score(self, gamer: Gamer, points: int) -> None:
        self.stats.increase_score(gamer.id, points)
        await self.level_up(gamer)
        return None

    async def level_up(self, gamer: Gamer) -> int:
        player = self.stats.get_player(gamer.id)
        curr_lvl = player.level
        next_lvl = self.stats.level_up(gamer.id)
        if next_lvl != curr_lvl:
            if next_lvl > curr_lvl:
                title = 'New Level Unlocked'
                prefix = 'Up'
                if next_lvl > len(self.roles['Level']) - 1:
                    # Can't create 100+ roles in a row.
                    ref_role = self.roles['Level'][-1]
                    for i in range(len(self.roles['Level']), next_lvl + 1):
                        new_role = await self.setup.role(str(i), f"#{Color.random().value:06X}",
                            alias='Level', ref_role=ref_role)
                        ref_role = new_role
            else:
                title = 'Level Lost'
                prefix = 'Down'
            new_role = self.get_level_role(next_lvl)
            old_role = self.get_level_role(curr_lvl)
            if isinstance(gamer, Member):
                author = gamer.display_name
                avatar = gamer.display_avatar
                await self.swap_roles(gamer, new_role, old_role)
            else:
                author = gamer.name
                avatar = gamer.avatar
            self.stats.level_up(gamer.id)
            image = str((next_lvl % 7) + 1)
            file = File(f"imgs/{image}.png", filename=f"{image}.png")
            note = f"{prefix}graded From Level {old_role.mention} to Level {new_role.mention}" 
            embed = Embed(title=title, description=note, color=new_role.color)
            embed.set_image(url=f"attachment://{image}.png")
            embed.set_author(name=author, icon_url=avatar.url)
            await self.setup.guild.system_channel.send(embed=embed, file=file)
            for _ in range(self.stats.level_hearts(gamer.id)):
                await self.add_heart(gamer)
        return None

    async def load_npcs(self) -> None:
        for webhook in await self.setup.guild.webhooks():
            if webhook.name in self.npcs:
                self.npcs[webhook.name] = self.npcs[webhook.name](self, webhook)
        return None

    async def remove_heart(self, gamer: Gamer, channel: Optional[TextChannel] = None, killer: str = '') -> None:
        player = self.stats.get_player(gamer.id)
        if player.health == -3:
            if isinstance(gamer, Member):
                await gamer.kick(reason='Dead')
                return None
        if player.health == 1:
            new_role = self.roles['💀']
            image = 'skull'
            title, note = 'Critical', 'is critical!'
        elif 1 < player.health <= 10:
            new_role = self.roles['❤️' * (player.health - 1)]
            image = f"heart{player.health - 1}"
            title, note = 'Ouch', f"lost -1 {self.roles['❤️'].mention}!"
        elif isinstance(gamer, Webhook):
            # NPCs do not turn into ghosts.
            npc = self.npcs.get(gamer.name)
            await npc.die(killer)
            return None
        elif player.health == 0:
            new_role = self.roles['👻']
            image = 'ghost1'
            title, note = f"🪦Dead {gamer.display_name}💐", 'has died!'
            embed = Embed(title=title,
                description=f"Killed by {killer}  {3 * self.roles['💀'].mention}",
                color=Color.dark_red())
            avatar_bytes = await gamer.display_avatar.replace(format='png', size=512).read()
            with Image.open(BytesIO(avatar_bytes)).convert('RGBA') as avatar_img:
                avatar_img = ImageOps.grayscale(avatar_img.convert("RGB")).convert("RGB")
                avatar_img = avatar_img.filter(ImageFilter.GaussianBlur(2))
                avatar_img = ImageEnhance.Contrast(avatar_img).enhance(2)
                avatar_img = ImageEnhance.Brightness(avatar_img).enhance(0.80)
                out = BytesIO()
                avatar_img.save(out, format='PNG')
                out.seek(0)
            embed.set_image(url="attachment://grave.png")
            await channel.send(embed=embed, file=File(out, filename='grave.png'))
        else:
            new_role = self.roles['👻' * abs(player.health - 1)]
            image = f"ghost{abs(player.health - 1)}"
            title, note = 'Transmogrification', 'is transmogrifying!'
        if isinstance(gamer, Member):
            gamer = await gamer.guild.fetch_member(gamer.id)  # Refresh
            name = gamer.mention
            author = gamer.display_name
            avatar = gamer.display_avatar
            for cur_role in gamer.roles:
                if cur_role in self.setup.lives:
                    break
            await self.swap_roles(gamer, new_role, cur_role)
        else:
            name = f"**{gamer.name}**"
            author = gamer.name
            avatar = gamer.avatar
        self.stats.increase_health(gamer.id, -1)
        file = File(f"imgs/{image}.png", filename=f"{image}.png")
        embed = Embed(title=title, description=f"{name} {note}\n**Vigor**: {new_role.mention}", color=new_role.color)
        embed.set_image(url=f"attachment://{image}.png")
        embed.set_author(name=author, icon_url=avatar.url)
        await self.setup.guild.system_channel.send(embed=embed, file=file)
        return None

    async def spawn(self, channel: TextChannel, npc: type[NPC]) -> None:
        with open(f"imgs/{npc.avatar}.png", 'rb') as f:
            avatar_bytes = f.read()
        webhook = await channel.create_webhook(name=npc.alias, avatar=avatar_bytes)
        self.stats.create_player(webhook.id)
        new_npc = npc(self, webhook)
        self.npcs[webhook.name] = new_npc
        await new_npc.send_passive_dialogue()
        return None

    async def swap_roles(self, member: Member, add_role: Role, rem_role: Union[None, Role]) -> None:
        # API calls are rate limited: Removing/adding roles should be a single call.
        new_roles = member.roles.copy()
        new_roles.append(add_role)
        if rem_role and rem_role in new_roles:
            new_roles.remove(rem_role)
        await member.edit(roles=new_roles)
        return None


class Interface(View):

    def __init__(self, npc: NPC, game: Game):
        super().__init__(timeout=None)
        self.gamer = game
        self.npc = npc
        self.toggled = False

    @button(label='⚔️', style=ButtonStyle.danger)
    async def attack_button(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        defender = replace_emoji(self.npc.alias, ' ').strip().title()
        offender = replace_emoji(interaction.user.display_name, ' ').strip().title()
        streak, tot_attack, tot_counter = 0, 0, 0
        # Collect previous round, if applicable
        for embed in interaction.message.embeds:
            if offender in embed.title:
                for field in embed.fields:
                    if field.name == '🧝‍♂️Total':
                        tot_attack += int(field.value)
                    elif field.name.startswith('X'):
                        streak += int(field.name[1:-1])
                    elif tot_attack and streak:
                        break
            elif defender in embed.title:
                for field in embed.fields:
                    if field.name == '☠️Total':
                        tot_counter += int(field.value)
                        break
        # Offender attacks and defender counter attacks
        player = self.gamer.stats.get_player(interaction.user.id)
        attack = player.attack()
        counter = self.npc.attack()
        attack_points = self.npc.defend(attack)
        counter_points = player.defend(counter)
        points_off = attack_points - counter_points
        points_def = counter_points - attack_points
        if (player.score == 0) and (points_def > 0):
            counter_points, points_def = 0, 0
            await self.gamer.remove_heart(interaction.user, interaction.channel, self.npc.webhook.name)
        elif points_def > player.score:
            points_def = player.score
        if (self.npc.player.score == 0) and (points_off > 0):
            attack_points, points_off = 0, 0
            await self.gamer.remove_heart(self.npc.webhook, killer=interaction.user.display_name)
        elif points_off > self.npc.player.score:
            points_off = self.npc.player.score
        tot_attack += attack_points
        tot_counter += counter_points
        embed1 = Embed(title=f"Level {player.level} {offender}",
            color=interaction.user.top_role.color)
        embed1.add_field(name='🧝‍♂️Attack', value=attack)
        embed1.add_field(name='🧝‍♂️Damage', value=attack_points)
        embed1.add_field(name='🧝‍♂️Total', value=tot_attack)
        embed1.add_field(name=f"X{streak + 1}!", value='')
        embed2 = Embed(title=f"Level {self.npc.player.level} {defender}",
            color=self.gamer.get_level_role(self.npc.player.level).color)
        embed2.add_field(name='☠️Counter', value=counter)
        embed2.add_field(name='☠️Damage', value=counter_points)
        embed2.add_field(name='☠️Total', value=tot_counter)
        await self.gamer.increase_score(interaction.user, points_off)
        await self.gamer.increase_score(self.npc.webhook, points_def)
        try:
            await self.npc.webhook.edit_message(interaction.message.id, embeds=[embed1, embed2], view=self)
        except NotFound:
            # NPC was killed.
            await self.gamer.increase_score(interaction.user, self.npc.points)
            message = await interaction.channel.fetch_message(interaction.message.id)
            await message.delete()
        return None

    @button(label='🫳', style=ButtonStyle.primary)
    async def pet_button(self, interaction: Interaction, button: Button) -> None:
        await self.npc.send_passive_dialogue()
        return None

    @button(label='🔍', style=ButtonStyle.gray)
    async def index_button(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        if self.toggled:
            button.label = '🔍'
            attach = {'attachments': [], 'embeds': []}
            self.toggled = False
        else:
            button.label = '🔺'
            items = []
            if self.npc.coins:
                items.append(self.gamer.roles['🪙' * self.npc.coins].mention)
            items.extend([self.gamer.roles[item].mention for item in self.npc.items])
            player = self.gamer.stats.get_player(self.npc.webhook.id)
            power_int = player.level // 10
            power_str = ''
            for _ in range(power_int // 3):
                power_str += self.gamer.roles['🎖️🎖️🎖️'].mention
            if power_int % 3:
                power_str += self.gamer.roles['🎖️' * (power_int % 3)].mention
            level = self.gamer.roles['Level'][player.level]
            vigor = self.gamer.roles[player.get_health_str()]
            embed = Embed(
                title=f"Level {player.level} {replace_emoji(self.npc.alias, '')}",
                description=self.npc.index,
                color=level.color)
            embed.add_field(name='Level', value=level.mention)
            embed.add_field(name='Vigor', value=vigor.mention)
            embed.add_field(name='Power', value=power_str)
            embed.add_field(name='Kills', value='0')
            embed.add_field(name='Posts', value=player.posts)
            embed.add_field(name='Score', value=player.score)
            embed.add_field(name='Loot', value=', '.join(items), inline=False)
            file = File(f"imgs/{self.npc.thumbnail}.png",
                filename=f"{self.npc.thumbnail}.png")
            embed.set_image(url=f"attachment://{self.npc.thumbnail}.png")
            attach = {'attachments': [file], 'embeds': [embed]}
            self.toggled = True
        await self.npc.webhook.edit_message(interaction.message.id, **attach, view=self)
        return None


class NPC:

    alias: str
    armor = 0
    avatar: str
    coins: int
    deathnail: str
    index: str
    items: List[str]
    passive_dialogue: List[str]
    points: int
    thumbnail: str

    def __init__(self, game: Game, webhook: Webhook):
        self.interface = Interface(self, game)
        self.player = game.stats.get_player(webhook.id)
        self.webhook = webhook

    def attack(self) -> int:
        return int(self.player.score * random()**0.5)

    def defend(self, damage: int) -> int:
        return damage - int(damage * random()**1.5)

    async def die(self, killer: str) -> None:
        channel = self.webhook.channel
        self.interface.gamer.delete(self.webhook)
        del self.interface.gamer.npcs[self.webhook.name]
        await self.webhook.delete()
        embed = Embed(title=f"🪦Dead {replace_emoji(self.alias, '')}💐",
            description=f"Killed by {killer} {3 * self.interface.gamer.roles['💀'].mention}",
            color=Color.dark_red())
        embed.set_image(url=f"attachment://{self.deathnail}.png")
        file = File(f"imgs/{self.deathnail}.png", filename=f"{self.deathnail}.png")
        await channel.send(embed=embed, file=file)
        return None

    async def send_passive_dialogue(self) -> None:
        async for message in self.webhook.channel.history(limit=1):
            if message.webhook_id == self.webhook.id:
                await self.webhook.edit_message(message.id, attachments=[], embed=None, view=None)
        await self.webhook.send(self.passive_dialogue[randint(0, len(self.passive_dialogue) - 1)],
            view=self.interface, allowed_mentions=AllowedMentions(roles=True))
        return None


class BabySlime(NPC):

    alias = '🍼Baby Slime'
    avatar = 'babyslime'
    coins = 0
    deathnail = 'babyslimedead'
    index = "It's just a little baby."
    items = ['☣️']
    passive_dialogue = ['Waah!', 'Boohoo!', 'Sniffle', 'Barf!', 'Bleah!', 'Hiccup!', 'Argh!', 'Mommy!', 'Help!', 'Meow']
    points = 100
    thumbnail = 'babyslime'


class GoldNeko(NPC):

    alias = '🐈Gold Neko'
    armor = 1000
    avatar = 'goldneko'
    coins = 5
    deathnail = 'goldnekodead'
    index = "A radiant gold neko"
    items = ['🐈', '🔪', '🍅']
    passive_dialogue = ['Meow.', 'Mrow.', 'Nya!', 'Mrrp!', 'Yeowr.', 'Raow!',
        'You can paint yourself and others different colors with /paint ☝🐱',
        'You can see a members stats with /show stats ☝🐱']
    points = 10000
    thumbnail = 'goldneko'


class MommySlime(NPC):

    alias = '🦠Mommy Slime'
    avatar = 'mommyslime'
    coins = 0
    deathnail = 'mommyslimedead'
    index = 'A slimey and smelly amorphous creature with a single gaping orifice.'
    items = ['☣️', '☢️', '🍅']
    passive_dialogue = ['Squish!', 'Splosh!', 'Plop!', 'Slurp', 'Sploosh!', 'Schlork!', 'Slush', 'Gurgle', 'Glug', 'Blurp!', 'Blub']
    points = 500
    thumbnail = 'mommyslime'


class Skyevolutrex(NPC):

    alias = '🐾Wild Skyevolutrex'
    avatar = 'wildskyevolutrex'
    coins = 5
    deathnail = 'wildskyevolutrexdead'
    index = "A creature that resembles a dog with wings, an orange hooked beak with teeth-like serrations and blue fur-like protofeathers. It's a nocturnal, small-pack hexapod with hollow bones that inhabits the caves of high-altitude forest cliffs in The Other World."
    items = ['🪬']
    passive_dialogue = ['EEK!', 'RAW!', 'BWARK!', 'SQAWK!', 'CAW!', 'SKREE!', "There's a city beyond the market 🦊🐦‍⬛"]
    points = 5000
    thumbnail = 'wildskyevolutrex'

    def __init__(self, game: Game, webhook: Webhook):
        super().__init__(game, webhook)
        self.passive_dialogue.append(f"Use {game.roles['🪬'].mention} to enter the Church.")
