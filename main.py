
import discord
from discord.ext import commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

verify_channel_id = None

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    global verify_channel_id
    verify_channel_id = channel.id
    await ctx.send(f"✅ تم تحديد قناة التحقق: {channel.mention}")

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تحقق ✅", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_callback(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="موثق")
        unverified_role = discord.utils.get(guild.roles, name="غير موثق")

        if verified_role in member.roles:
            await interaction.response.send_message("✅ أنت بالفعل موثق!", ephemeral=True)
            return

        if unverified_role in member.roles:
            await member.remove_roles(unverified_role)
        if verified_role:
            await member.add_roles(verified_role)

        await interaction.response.send_message("✅ تم التحقق بنجاح!", ephemeral=True)

    @discord.ui.button(label="إنشاء الرتب 🛠️", style=discord.ButtonStyle.primary, custom_id="setup_roles")
    async def setup_roles(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر فقط للإدمن!", ephemeral=True)
            return

        guild = interaction.guild

        if not discord.utils.get(guild.roles, name="غير موثق"):
            await guild.create_role(name="غير موثق")

        if not discord.utils.get(guild.roles, name="موثق"):
            await guild.create_role(name="موثق")

        await interaction.response.send_message("✅ تم إنشاء الرتب بنجاح!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def add_verify(ctx):
    if verify_channel_id is None:
        await ctx.send("❌ لازم تستخدم !setup لتحديد قناة التحقق أولاً.")
        return

    channel = bot.get_channel(verify_channel_id)
    if channel:
        embed = discord.Embed(
            title="مرحبا بك في السيرفر!",
            description="اضغط الزر أدناه للحصول على صلاحيات الدخول.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed, view=VerifyView())
        await ctx.send("✅ تم إرسال رسالة التحقق بنجاح.")
    else:
        await ctx.send("❌ لم يتم العثور على القناة.")

bot.run(os.getenv("DISCORD_TOKEN"))
