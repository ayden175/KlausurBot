import discord
import asyncio
import time
import pickle
from functools import partial
from random import shuffle
import traceback


class Bot(discord.Client):
    async def on_ready(self):
        self.admin = discord.utils.get(self.get_all_members(), name='Ayden', discriminator='7318')
        self.known_guilds = []
        self.settings = ['known_guilds', 'settings_bot', 'settings_general', 'settings_rooms']
        self.settings_bot = {'default': 'bot'}
        self.settings_general = {'default': 'general'}
        self.settings_rooms = {'default': 'voice-'}
        self.settings_size = {'default': 3}
        self.bot_channel = {}
        self.tutor = {}
        self.tutor_role = {}
        self.general_channel = {}
        self.general = {}
        self.rooms = {}
        self.started_at = {}
        self.min = {}
        self.timer = {}
        self.tutor_username = ["Sothis#0628", "Mr.Skooma#5139", "ShrewdLuke#1230", "_Yui#4615", "LeandiBandi#6116", "Eliah#7118", "Mihaela Popescu#0681", "YellowCadet#9880", "Niklas#6999", "Rachel#2774", "Agandaur#4678", "Wete#0945"]

        for file in self.settings:
            try:
                with open('settings/'+ file + '.pkl', 'rb') as f:
                    setattr(self, file, pickle.load(f))
            except FileNotFoundError:
                pass

        print("------------- Initializations -------------")
        for guild in self.guilds:
            await self.initialize(guild, startup=True)

        self.help = (" - `!ping`: Schickt eine Benachrichtigung, wenn du eine Frage hast\n"
                     " - `!rem`: Gibt zurück wie lange die Klausur noch geht\n"
                     " - `!help`: Gibt diese Nachricht aus")

        self.help_full = (" - `!init`: Aktualisisert die Einstellungen für den Server\n"
                          " - `!create arg`: Passt die Servereinstellungen an, sodass es mindestens `arg` viele Räume gibt\n"
                          " - `!ping`: Schickt eine Benachrichtigung, wenn jemand eine Frage hat\n"
                          " - `!room`: Teilt alle teilnehmenden Studierenden auf die Räume auf\n"
                          " - `!start`: Startet den Klausurtimer für 90 Minuten\n"
                          " - `!cancel`: Bricht den Klausurtimer ab\n"
                          " - `!rem`: Gibt zurück wie lange der aktuelle Timer noch läuft\n"
                          " - `!ann`: Ruft alle in den allgemeinen Channel zurück\n"
                          " - `!help`: Gibt diese Nachricht aus")

        self.save_settings()

        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def save_settings(self):
        for file in self.settings:
            with open('settings/'+ file + '.pkl', 'wb+') as f:
                pickle.dump(getattr(self, file), f, pickle.HIGHEST_PROTOCOL)

    async def initialize(self, guild, message=None, startup=False):
        new = False
        if guild.id not in self.known_guilds:
            new = True
            self.known_guilds.append(guild.id)
            if not startup:
                self.save_settings()

        bot     = self.settings_bot[guild.id]     if guild.id in self.settings_bot     else self.settings_bot['default']
        general = self.settings_general[guild.id] if guild.id in self.settings_general else self.settings_general['default']
        rooms   = self.settings_rooms[guild.id]   if guild.id in self.settings_rooms   else self.settings_rooms['default']

        self.tutor[guild.id] = []
        self.tutor_role[guild.id] = discord.utils.get(guild.roles,name="Tutor*in")
        for member in guild.members:
            if self.tutor_role[guild.id] in member.roles:
                self.tutor[guild.id].append(member)


        self.bot_channel[guild.id] = discord.utils.get(guild.text_channels, name=bot)
        self.general_channel[guild.id] = discord.utils.get(guild.text_channels, name=general)
        self.general[guild.id]     = discord.utils.get(guild.voice_channels, name=general)
        self.rooms[guild.id]       = []
        i = 1
        while True:
            room = discord.utils.get(guild.voice_channels, name=f'{rooms}{i}')
            if room is not None:
                self.rooms[guild.id].append(room)
                i += 1
            else:
                break
        rooms_found = len(self.rooms) > 0
        self.started_at[guild.id]  = None
        self.min[guild.id] = None

        text =  f'Beep boop, ich habe folgende Einstellungen für "{guild.name}" übernommen:\n'
        text += f'Tutor*innen: {", ".join(m.display_name for m in self.tutor[guild.id])}\n'
        text += f'Bot Channel: {self.bot_channel[guild.id]}\n'
        text += f'General Channel: {self.general_channel[guild.id]}\n'
        text += f'General Voice Channel: {self.general[guild.id]}\n'
        text += f"Voice Channel: {', '.join(r.name for r in self.rooms[guild.id])}\n"

        print()
        print(text)
        print()
        if not message is None:
            await message.reply(text, mention_author=False)
        elif new:
            await guild.owner.send(text)

    async def on_guild_join(self, guild):
        await self.initialize(guild)

    async def on_member_join(self, member):
        if str(member) in self.tutor_username:
            await member.add_roles(self.tutor_role[member.guild.id])
            self.tutor[member.guild.id].append(member)
            await self.admin.send(f'Tutor {member} has joined {member.guild}.')
            print(f'Tutor {member} has joined {member.guild}.')
        else:
            await self.admin.send(f'Student {member} has joined {member.guild}.')
            print(f'Student {member} has joined {member.guild}.')

    async def on_message(self, message):
        cmd_orig = message.content.split()
        cmd = message.content.lower().split()
        if message.author == self.user or len(cmd) == 0 or not cmd[0].startswith('!') or message.guild is None:
            return

        guild = message.guild.id

        issued_command_by = f"{message.author.display_name}: {message.content}"
        print(issued_command_by)

        try:
            if cmd[0].startswith('!create'):
                if (not self.tutor_role[guild] in message.author.roles) and (not message.author == self.admin):
                    await message.reply(f'Beep boop, du hast keine Berechtigung dafür!', mention_author=False)
                    return

                try:
                    amount = int(cmd[1])
                except:
                    await message.reply('Beep boop, ich hatte Probleme beim parsen der Zeit! Bitte benutze nur natürliche Zahlen!', mention_author=False)
                    return

                # set notification to mention only
                await message.guild.edit(default_notifications=discord.NotificationLevel.only_mentions)

                # create admin role
                role = discord.utils.get(message.guild.roles, name="Tutor*in")
                if role is None:
                    permissions = discord.Permissions(8)
                    await message.guild.create_role(name="Tutor*in", permissions=permissions, colour=discord.Colour.purple(), hoist=True)
                    role = discord.utils.get(message.guild.roles, name="Tutor*in")
                    print(role)
                    await message.author.add_roles(role)

                # create admin role
                role = discord.utils.get(message.guild.roles, name="Bot")
                if role is None:
                    await message.guild.create_role(name="Bot", colour=discord.Colour.green(), hoist=True)
                    role = discord.utils.get(message.guild.roles, name="Bot")
                    bot_user = discord.utils.get(message.guild.members, name='KlausurBot')
                    await bot_user.add_roles(role)

                # create bot channel
                channel_bot = discord.utils.get(message.guild.text_channels, name="bot")
                if channel_bot is None:
                    overwrites = {
                        message.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                        role: discord.PermissionOverwrite(view_channel=True),
                        message.guild.me: discord.PermissionOverwrite(view_channel=True)
                    }
                    await message.guild.create_text_channel("bot", position=0, overwrites=overwrites)

                # make
                category = discord.utils.get(message.guild.categories, name="Allgemein")
                if category is None:
                    await message.guild.create_category("Allgemein")
                    category = discord.utils.get(message.guild.categories, name="Allgemein")
                    general_text = discord.utils.get(message.guild.text_channels, name="general")
                    general_voice = discord.utils.get(message.guild.voice_channels, name="General")
                    await general_text.edit(category=category)
                    await general_voice.edit(name="general")
                    await general_voice.edit(category=category)
                    await discord.utils.get(message.guild.categories, name="Text Channels").delete()
                    await discord.utils.get(message.guild.categories, name="Voice Channels").delete()

                # create the voice channels
                for i in range(1, amount+1):
                    category = discord.utils.get(message.guild.categories, name=f"Raum {i}")
                    if category is None:
                        await message.guild.create_category(f"Raum {i}")
                        category = discord.utils.get(message.guild.categories, name=f"Raum {i}")
                        await category.create_text_channel(f"text-{i}")
                        await category.create_voice_channel(f"voice-{i}", user_limit=1)

                await self.initialize(message.guild, message=message)
                await message.reply(f'Server wurde fertig eingerichtet!', mention_author=False)

            elif cmd[0].startswith('!init'):
                if not self.tutor_role[guild] in message.author.roles:
                    await message.reply(f'Beep boop, du hast keine Berechtigung dafür!', mention_author=False)
                    return
                await self.initialize(message.guild, message)


            elif cmd[0].startswith('!hallo'):
                await message.reply(f'Hallo {message.author.display_name}!', mention_author=False)


            elif cmd[0].startswith('!ping'):
                try:
                    category = message.author.voice.channel.category
                    room = f' in {category if category is not None else message.author.voice.channel}'
                except AttributeError:
                    room = ''
                await self.bot_channel[guild].send(f'{self.tutor_role[guild].mention}: {message.author.display_name} hat eine Frage{room}!')
                await message.reply('Beep boop, ich habe eine Benachrichtigung geschickt!', mention_author=False)


            elif cmd[0].startswith('!start'):
                if not self.tutor_role[guild] in message.author.roles:
                    await message.reply(f'Beep boop, du kannst keine Timer stellen! Falls du wissen willst wie lange der aktuelle Timer noch läuft, benutz `!rem`', mention_author=False)
                    return

                if not self.started_at[guild] == None:
                    await message.reply(f'Beep boop, der Klausurtimer läuft schon! Mit `!cancel` kannst du ihn abbrechen', mention_author=False)
                    return

                self.started_at[guild] = time.time()
                self.timer[guild] = []
                self.timer[guild].append(Timer(45*60, partial(self.announce, message.guild, "@everyone Die Hälfte der Zeit ist um, ihr habt noch 45 Minuten!")))
                self.timer[guild].append(Timer(80*60, partial(self.announce, message.guild, "@everyone Die Zeit ist fast um, ihr habt noch 10 Minuten!")))
                self.timer[guild].append(Timer(90*60, partial(self.announce, message.guild, "@everyone Die Zeit für die Klausur ist um!")))
                await message.reply(f'Beep boop, ich habe einen Klausurtimer für 90 Minuten gestellt! Ich werde zwischendurch Benachrichtigungen zur Zeit schicken', mention_author=False)



            elif cmd[0].startswith('!rem'):
                if self.started_at[guild] == None:
                    await message.reply('Beep boop, es ist kein Timer gestellt!', mention_author=False)
                    return

                remaining_min = int((self.started_at[guild] + 90*60 - time.time()) / 60)
                if remaining_min == 0:
                    time_text = "weniger als eine Minute"
                elif remaining_min == 1:
                    time_text = "eine Minute"
                else:
                    time_text = f"{remaining_min} Minuten"
                await message.reply(f'Beep boop, die Klausur geht noch {time_text}!', mention_author=False)

            elif cmd[0].startswith('!cancel'):
                if not self.tutor_role[guild] in message.author.roles:
                    await message.reply(f'Beep boop, du kannst keine Timer abbrechen!', mention_author=False)
                    return

                if self.started_at[guild] == None:
                    await message.reply('Beep boop, es ist kein Timer gestellt!', mention_author=False)
                    return

                self.started_at[guild] = None
                for timer in self.timer[guild]:
                    timer.cancel()
                await message.reply(f'Beep boop, ich habe den Klausur-Timer abgebrochen!', mention_author=False)


            elif cmd[0].startswith('!ann'):
                if not self.tutor_role[guild] in message.author.roles:
                    await message.reply(f'Beep boop, du kannst keine Benachrichtigung schicken lassen!', mention_author=False)
                    return

                await self.announce(message.guild, text="@everyone Kommt bitte alle zurück in den allgemeinen Channel!", timer=False)

            elif cmd[0].startswith('!room'):
                if not self.tutor_role[guild] in message.author.roles:
                    await message.reply(f'Beep boop, du kannst keine Leute aufteilen lassen!', mention_author=False)
                    return

                members = self.general[guild].members
                if len(members) <= 0:
                    await message.reply(f'Beep boop, ich habe niemanden zum Aufteilen gefunden!', mention_author=False)
                    print('WARN: No members to assign found!')
                    return

                print(f'Assigning {len(members) - 1} people to rooms')

                # add people to the rooms
                i = 0
                for member in members:
                    if not self.tutor_role[guild] in member.roles:
                        while len(self.rooms[guild][i].members) > 0:
                            i += 1
                        try:
                            await member.move_to(self.rooms[guild][i])
                            print(f'Moved {member.display_name} to room {i+1}')
                        except discord.errors.HTTPException:
                            print(f'Error while assigning {member.display_name} to room {i+1}, skipping')
                        i += 1
                    else:
                        print(f'Skipped {member.display_name}')

                await message.reply('Beep boop, alle Teilnehmer wurden auf die Räume aufgeteilt!', mention_author=False)
                print('Done')


            elif cmd[0].startswith('!help'):
                help = self.help if not self.tutor_role[guild] in message.author.roles else self.help_full
                await message.reply(f'Beep boop, hier sind alle Befehle die ich zur Zeit kann:\n{help}', mention_author=False)

            elif cmd[0].startswith('!error'):
                raise Exception

            elif cmd[0].startswith('!'):
                help = self.help if not self.tutor_role[guild] in message.author.roles else self.help_full
                await message.reply(f'Beep boop, den Befehl kenne ich nicht, hier sind alle Befehle die ich zur Zeit kann:\n{help}', mention_author=False)

        except Exception:
            await message.reply(f'Beep boop, es ist leider ein Fehler aufgetreten :sob: Es wurde eine Benachrichtigung geschickt und der Fehler wird so bald wie möglich behoben!', mention_author=False)
            excep_traceback = traceback.format_exc()
            except_message = (f"Der Command war: {issued_command_by}\n"
                              f"Hier ist der Stracktrace:\n{excep_traceback}")
            if not self.admin is None:
                exception_text = f"Es ist ein Fehler bei dem Klausurserver von {', '.join(m.display_name for m in self.tutor[guild])} aufgetreten!\n" + except_message
                print(exception_text)
                await self.admin.send(exception_text)
            else:
                await self.tutor[guild][0].send("Es ist ein Fehler aufgetreten! Bitte leite diese Informationen weiter, damit der Fehler behoben werden kann.\n" + except_message)


    async def announce(self, guild, text, timer=True):
        if timer:
            self.started_at[guild.id] = None
        await self.general_channel[guild.id].send(text)


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        if self._timeout > 0:
            await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    activity = discord.Activity(type=discord.ActivityType.listening, name="!ping")
    client = Bot(activity=activity, intents=intents)
    try:
        with open('token', 'r') as f:
            token = f.read()
    except FileNotFoundError:
        print("Token nicht gefunden! Bitte füge eine Datei 'token' mit dem Discord Bot Token hinzu.")
    client.run(token)
