import disnake
from disnake.ext import commands
import re
import discord
import disnake.utils
import asyncio
import os
from asyncio import sleep
import keep_alive

bot = commands.Bot(command_prefix="!",
                   help_command=None,
                   intents=disnake.Intents.all(),
                   test_guilds=[717425551635120219])
CENSORED_WORDS = ['fook']

#logs chanel

# events

# подключения бота
@bot.event
async def on_ready():
  print(f"Bot {bot.user} is ready to work!")
  


# выдача роли
@bot.event
async def on_member_join(member: disnake.Member):  
    # Создаем embed-сообщение
    embed = disnake.Embed(title='Добро пожаловать!', description='Привет, {}! Добро пожаловать на наш сервер "FAM"!'.format(member.mention), color=0x0000FF)
# Добавляем фото
    embed.set_image(url='https://media.tenor.com/iVCiM9W7cvYAAAAC/welcome.gif')
# Добавляем текст
    embed.add_field(name="Выберете роль", value="Для получения роли перейдите в канал 'roles' и выберете подходящую для вас роль")

    # Отправляем личное сообщение участнику
    await member.send(embed=embed)
    role_id = 1092837151911186482 # замените на ID роли, которую нужно выдать
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)
        print(f"{member.name}#{member.discriminator} was given the role {role.name}")

        channel_id = 1092883614196318210 # замените на ID канала, в который нужно отправить сообщение
        channel = bot.get_channel(channel_id)
        if channel:
            embed = disnake.Embed(
                title="New Member",
                description=f"{member.mention} joined the server!",
                color=0xffa500
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
            print(f"Sent a welcome message in {channel.name}")
        else:
            print(f"Channel with ID {channel_id} was not found")
    else:
        print(f"Role with ID {role_id} was not found in the server")

guild_id = 1075198933862727702

#авто выдача роли
ID_POST = 1092840819662274662  # Your Post ID
USER_ROLES_LIST = ()
MAX_ROLES = 2

ROLES_LIST = {  # Your roles ID and emoji
  "👹": 1092850919705677876,  # Dota
  "🎯": 1092853640760397906,  # Cs
  "🌍": 1092854076569563257,  # Gta
  "🫂": 1092854192974086294,  # Talk
}


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == ID_POST:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = discord.utils.get(message.guild.members, id=payload.user_id)
        emoji = str(payload.emoji)

        try:
            role = discord.utils.get(message.guild.roles, id=ROLES_LIST[emoji])

            if len([i for i in user.roles if i.id not in USER_ROLES_LIST]) <= MAX_ROLES:
                # Удаляем старую роль, если она есть
                old_role = discord.utils.get(message.guild.roles, id=1092837151911186482)
                if old_role in user.roles:
                    await user.remove_roles(old_role)

                await user.add_roles(role)

                # Отправляем сообщение о выборе роли в другой канал
                notification_channel = bot.get_channel(1092883614196318210)
                await notification_channel.send(f"{user.mention} выбрал роль {role.name}")
            else:
                await message.remove_reaction(payload.emoji, user)
                await user.send(f"{user.mention} вы попытались получить слишком много ролей на сервере 'FAM' максимум ролей {MAX_ROLES}")
        except Exception as _ex:
            print(repr(_ex))


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == ID_POST:
        guild = await bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        emoji = str(payload.emoji)

        try:
            role = discord.utils.get(guild.roles, id=ROLES_LIST[emoji])

            if role in member.roles:
                await member.remove_roles(role)

                # Отправляем сообщение об удалении роли в другой канал
                notification_channel = bot.get_channel(1092883614196318210)
                await notification_channel.send(f"{member.mention} больше не имеет роль {role.name}")
        except Exception as _ex:
            print(repr(_ex))

     

#бан слоц

#errors
@bot.event
async def on_command_error(ctx, error):
  print(error)

  if isinstance(error, commands.MissingPermissions):
    await ctx.send(
      f"{ctx.author}, у вас недостаточно прав для выполнения даной команды!")
  elif isinstance(error, commands.UserInputError):
    await ctx.send(embed=disnake.Embed(
      description=
      f"Правильное использивоние команды: `{ctx.prefix}{ctx.command.name}` ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}"
    ))


#commands
#command kick
@bot.slash_command(usage="kick <@user> <reason=None>")
@commands.has_permissions(kick_members=True, administrator=True)  #роль для кика
async def kick(ctx, member: disnake.Member, *, reason="Нарушения правил"):
  notification_channel = ctx.guild.get_channel(1092883614196318210)
  await ctx.send(
    f"Администратор {ctx.author.mention} исключил пользевателя {member.mention}", ephemeral=True)
  await notification_channel.send(f"Администратор {ctx.author.mention} исключил пользевателя {member.mention}")
  await member.kick(reason=reason)
  await ctx.message.delete()


#command ban
@bot.slash_command(name="ban")
@commands.has_permissions(ban_members=True, administrator=True)  #роль для бана
async def ban(ctx, member: disnake.Member, *, reason="Нарушения правил"):
  notification_channel = ctx.guild.get_channel(1092883614196318210)
  await ctx.send(
    f"Администратор {ctx.author.mention} забанил пользователя {member.mention}",
    ephemeral=True)
  await notification_channel.send(
    f"Администратор {ctx.author.mention} забанил пользователя {member.mention}"
  )
  await member.ban(reason=reason)
  await ctx.message.delete()


#command clear (message_clear)
@bot.slash_command()
@commands.has_permissions(administrator=True)
async def clear(ctx):
  notification_channel = ctx.guild.get_channel(1092883614196318210)
  await ctx.send(f"Вы очистили чат {ctx.channel.name}",ephemeral=True)
  await ctx.channel.purge()
  await notification_channel.send(f"{ctx.author.mention} очистил чат {ctx.channel.name}")
  
  
#mute command
@bot.slash_command(name='mute')
@commands.has_permissions(administrator=True)
async def mute(ctx, member: disnake.Member, duration: int, *, reason: str):
  notification_channel = ctx.guild.get_channel(1092883614196318210)
  # Получаем роль для мута
  mute_role = disnake.utils.get(ctx.guild.roles, name='Muted')

  # Проверяем, что роль для мута существует
  if not mute_role:
    # Если роль не найдена, создаем новую роль
    mute_role = await ctx.guild.create_role(name='Muted')

    # Ограничиваем права участников с ролью "Muted"
    for channel in ctx.guild.channels:
      await channel.set_permissions(mute_role, send_messages=False)

  # Выдаем роль для мута
  await member.add_roles(mute_role, reason=reason)

  # Мьютим участника во всех голосовых каналах
  for channel in ctx.guild.voice_channels:
    for member_in_channel in channel.members:
      if member_in_channel == member:
        await member.edit(mute=True, reason=reason)
        break

  # Отправляем уведомление
  await ctx.send(
    f'{member.mention} был замучен Администратором {ctx.author.mention} на {duration} минут(ы) по причине "{reason}"',
    ephemeral=True)
  await notification_channel.send(
    f'{member.mention} был замучен Администратором {ctx.author.mention} на {duration} минут(ы) по причине "{reason}"'
  )

  # Ждем указанное время
  await asyncio.sleep(duration * 60)
  # Снимаем роль для мута
  await member.remove_roles(mute_role, reason="Истекло время мута")
  # Снимаем мьют участника во всех голосовых каналах
  for channel in ctx.guild.voice_channels:
    for member_in_channel in channel.members:
      if member_in_channel == member:
        await member.edit(mute=False, reason="Закончился мут")
        break

  # Отправляем уведомление
  await notification_channel.send(f'{member.mention} был размучен ')

#unmute command
@bot.slash_command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: disnake.Member):
  notification_channel = ctx.guild.get_channel(1092883614196318210)
  role = disnake.utils.get(ctx.guild.roles, name="Muted")
  for channel in ctx.guild.voice_channels:
    for member_in_channel in channel.members:
      if member_in_channel == member:
        await member.edit(mute=False, reason="Закончился мут")
        break
  if role in member.roles:
    await member.remove_roles(role)
    await notification_channel.send(
      f"{member.mention} был размучен пользоватилем {ctx.author.mention}")

  else:
    await ctx.send(
      f"{ctx.author.mention} размутил пользователя {member.mention}", ephemeral=True)
    await notification_channel.send(
      f"{ctx.author.mention} размутил пользователя {member.mention}")

#kino(отправляет ссылку на кино )
@bot.slash_command()
@commands.has_role('kinoman')
async def kino(ctx, url: str):
  if ctx.channel.id != 1080273230713065533:
    return await ctx.response.send_message(
      "Эту команду можно использовать только в определенном канале.",
      ephemeral=True,
      delete_after=5)

  if not re.match(r'^(http|https)://', url):
    return await ctx.response.send_message(
      "Вы ввели неверную ссылку.\n Example : https://google.com/",
      ephemeral=True,
      delete_after=5)

  embed = disnake.Embed(title="Приятного просмотра", url=url, color=0xff0000)
  embed.set_image(
    url=
    'https://i.pinimg.com/originals/77/dc/7d/77dc7d33347e3fec1359b39c901bbfe9.gif'
  )

  await ctx.response.send_message(embed=embed)
  print(f"{ctx.author.name} вставил ссылку на кино")
#invite to game
@bot.slash_command(name='invite', description='Invite a user to play a game')
async def invite(ctx: disnake.ApplicationCommandInteraction, user: disnake.User, game: str):
    # Отправить сообщение с приглашением
    await user.send(f"{ctx.author.mention} приглашает вас сыграть вместе в игру {game}! перейдите в нужный канал и начните игру. Удачи!")
    # Отправить сообщение подтверждения в канал, где была вызвана команда
    await ctx.send(f"Приглашение отправлено пользователю {user.mention}!", ephemeral=True)



keep_alive.keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))