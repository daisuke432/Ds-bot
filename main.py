import json
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Для Replit

# === Загрузка конфигурации ===
import os

TOKEN = os.environ["token"]
NEW_ROLE_ID = int(os.environ["new_role_id"])
MEMBER_ROLE_ID = int(os.environ["member_role_id"])
RULES_CHANNEL_ID = int(os.environ["rules_channel_id"])


# === Интенты ===
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Кнопка "Принять правила" ===
class AcceptRulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Принять правила", style=discord.ButtonStyle.success, custom_id="accept_rules")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        new_role = guild.get_role(NEW_ROLE_ID)
        member_role = guild.get_role(MEMBER_ROLE_ID)

        if member_role in member.roles:
            await interaction.response.send_message("✅ Ты уже принял правила!", ephemeral=True)
            return

        try:
            if new_role in member.roles:
                await member.remove_roles(new_role)
            await member.add_roles(member_role)
            await interaction.response.send_message("🎉 Спасибо! Ты получил доступ ко всем каналам.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня нет прав на изменение ролей.", ephemeral=True)

# === При запуске ===
@bot.event
async def on_ready():
    bot.add_view(AcceptRulesView())
    print(f"✅ Бот {bot.user} запущен.")

    guild = bot.guilds[0]
    new_role = guild.get_role(NEW_ROLE_ID)
    member_role = guild.get_role(MEMBER_ROLE_ID)

    updated = 0
    for member in guild.members:
        if member.bot:
            continue
        has_higher_role = any(role.position > member_role.position for role in member.roles)
        if new_role not in member.roles and member_role not in member.roles and not has_higher_role:
            await member.add_roles(new_role, reason="Роль выдана при запуске бота")
            updated += 1

    print(f"🌱 Добавлена роль 'New' {updated} участникам.")

# === При заходе нового участника ===
@bot.event
async def on_member_join(member):
    new_role = member.guild.get_role(NEW_ROLE_ID)
    if new_role:
        await member.add_roles(new_role, reason="Новый участник")
        try:
            await member.send("👋 Добро пожаловать! Ознакомься с правилами и нажми кнопку в канале #📜правила.")
        except:
            pass

# === Команда администратора: отправка правил с кнопкой ===
@bot.command()
@commands.has_permissions(administrator=True)
async def sendrules(ctx):
    embed = discord.Embed(
        title="📕 Правила сервера",
        description=(
            "Добро пожаловать на наш сервер! Пожалуйста, ознакомьтесь с правилами ниже и нажмите кнопку ✅ "
            "**Принять правила**, чтобы получить доступ ко всем каналам.\n\n"
            "1. Проявление расизма, сексизма, нацизма, а также оскорблений на религиозной почве запрещено.\n"
            "2. Запрещено кричать и раздавать громкие, раздражающие звуки в голосовых каналах.\n"
            "3. Запрещена реклама любого характера без согласования с администрацией.\n"
            "4. Запрещён флуд и оффтоп в тематических каналах.\n"
            "5. Контент 18+ только в канале 🔞 | nsfw\n\n"
            "*Правила могут изменяться. Спасибо за понимание!*"
        ),
        color=0xff4444
    )
    embed.set_footer(text="Нажмите кнопку ниже, чтобы подтвердить согласие.")
    await ctx.send(embed=embed, view=AcceptRulesView())

# === Запуск бота ===
keep_alive()  # Запускает веб-сервер Replit
bot.run(TOKEN)
