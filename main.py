import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button
import re
from datetime import timedelta
import asyncio

# Cấu hình Intents Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None, reconnect=True)

bot_permissions = {}

# 🔒 ĐỘC QUYỀN 2 ADMIN TỐI CAO
ALLOWED_ADMIN_USERNAMES = ["alphathunderkethulinh", "bomayduwar"]

# CHỈ BẮT XÁC NHẬN CHO 2 ROLE CAO NHẤT
STRICT_VIP_ROLES = ["owner | admin 👑", "administrator"]

HIGHEST_ROLE_NAMES = ["owner | admin 👑", "administrator"]
HIGH_ROLE_NAMES = ["đấng tối cao", "alphathunder", "dev"]
MEDIUM_ROLE_NAMES = ["member", "aecw"]

WELCOME_CHANNEL_ID = 1562102970684940298
LEAVE_CHANNEL_ID = 1562103001274122453
ONLINE_NOTIFY_CHANNEL_ID = 1562102970684940298
WELCOME_GIF_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnh4Z3p5Z3Zydm1pZjBsYTh3d3Y0ZGNyZTF4Yzg3eG9yZXF2pDE0ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/L1R1tvI9svvpHujy26/giphy.gif"


# --- 📌 ĐỒNG BỘ LỆNH SLASH (/) VÀ THÔNG BÁO TỰ ĐỘNG ---
@bot.event
async def on_ready():
    print(f"🚀 [ONLINE 24/7] Bot {bot.user} đã kết nối thành công với Token mới!")
    await bot.change_presence(activity=discord.Game(name="👑 Anh Em Chat War | .help"))
    
    # Đồng bộ danh sách lệnh Slash (/) với Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Đã đồng bộ {len(synced)} lệnh Slash (/) thành công!")
    except Exception as e:
        print(f"⚠️ Lỗi đồng bộ lệnh Slash: {e}")

    # Chờ 2 giây gửi tin nhắn thông báo khi khởi động
    await asyncio.sleep(2)
    channel = bot.get_channel(ONLINE_NOTIFY_CHANNEL_ID)
    if channel:
        try:
            embed = discord.Embed(
                title="⚡ HỆ THỐNG BOT ĐÃ KÍCH HOẠT ⚡",
                description=(
                    f"# 🚀 Bot {bot.user.mention} đã hoạt động thành công!\n\n"
                    f"🟢 **Trạng thái:** Đã kết nối hệ thống\n"
                    f"👑 **Sẵn sàng:** Dùng `/bot` hoặc `/onlbot1` để đánh thức bot!"
                ),
                color=discord.Color.green()
            )
            await channel.send(content="@here 🟢 Bot đã hoạt động trở lại!", embed=embed)
        except Exception as e:
            print(f"Lỗi gửi thông báo online: {e}")


# --- 📌 LỆNH SLASH DẠNG (/) ĐÁNH THỨC BOT ---
@bot.tree.command(name="bot", description="Đánh thức Bot dậy")
async def slash_bot(interaction: discord.Interaction):
    await interaction.response.send_message(f"# 👑 Xin chào ông chủ {interaction.user.mention}!")

@bot.tree.command(name="onlbot1", description="Kích hoạt trạng thái Onl Bot")
async def slash_onlbot1(interaction: discord.Interaction):
    await interaction.response.send_message(f"# 👑 Xin chào ông chủ {interaction.user.mention}!")


# --- 📌 TỰ ĐỘNG BẮT TỪ KHÓA CHAT VÀ PHẢN HỒI KHI BỊ TAG ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip().lower()

    if content in ["hi", "hi cậu", "hi cawu", "hello"]:
        await message.channel.send(f"Hi cậu {message.author.mention}, chúc bạn một ngày tốt lành! ✨")
    elif content in ["?", "??", "???", "????"]:
        await message.channel.send(f"{message.author.mention} Mày sĩ à 😂 Muốn cần gì gõ `.help` nha!")
    elif content in ["uk", "ừk", "ukm", "ừ"]:
        await message.channel.send(f"{message.author.mention} Uk Thằng Cha Mày! 😼")

    if bot.user in message.mentions and not message.mention_everyone:
        user_roles = [r.name.lower().strip() for r in message.author.roles]

        if message.author == message.guild.owner or any(r in user_roles for r in HIGHEST_ROLE_NAMES):
            await message.channel.send(f"# 👑 Thưa ngài, ngài kêu tôi phục vụ gì ạ? {message.author.mention}")
        elif any(r in user_roles for r in HIGH_ROLE_NAMES):
            await message.channel.send(f"Kêu tôi à ông chủ! {message.author.mention} ✨")
        elif any(r in user_roles for r in MEDIUM_ROLE_NAMES):
            await message.channel.send(f"{message.author.mention} tag lmj? 🤨")
        else:
            await message.channel.send(f"{message.author.mention} Mày tag tao chi? 🙄")

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Phát hiện lỗi lệnh: {error}")


def check_exclusive_admin(ctx):
    return ctx.author.name.lower() in ALLOWED_ADMIN_USERNAMES


# --- 📌 THỰC THI CẤP ROLE HÀNG LOẠT ---
async def execute_add_role(channel, author, role, members):
    success_members = []
    failed_members = []

    for member in members:
        try:
            await member.add_roles(role, reason=f"Cấp bởi Admin {author}")
            success_members.append(member)
        except discord.Forbidden:
            failed_members.append(member)
        except Exception as e:
            print(f"Lỗi cấp role: {e}")

    if success_members:
        mentions_str = " ".join([m.mention for m in success_members[:15]])
        if len(success_members) > 15:
            mentions_str += f" và {len(success_members) - 15} người khác..."

        embed = discord.Embed(
            title="✨ THÔNG BÁO CẤP ROLE THÀNH CÔNG ✨",
            description=(
                f"# 👑 Ông chủ {author.mention} đã cấp role **{role.name}**!\n\n"
                f"📊 **Số lượng:** `{len(success_members)}` thành viên\n"
                f"👥 **Danh sách:** {mentions_str}\n\n"
                f"📢 @here Bảng tin cập nhật vai trò mới!"
            ),
            color=discord.Color.green()
        )
        if len(success_members) == 1 and success_members[0].display_avatar:
            embed.set_thumbnail(url=success_members[0].display_avatar.url)

        await channel.send(content=f"@here 🎉 Tin tức hot!", embed=embed)

    if failed_members:
        await channel.send(
            f"⚠️ **CẢNH BÁO:** Bot không đủ quyền cấp role **{role.name}**!\n"
            f"👉 *Hãy vào Cài đặt máy chủ -> Vai trò -> Kéo Role của Bot Đệ Alpha 3 lên TRÊN role {role.name}!*"
        )


# --- 📌 VIEW XÁC NHẬN ROLE VIP ---
class ConfirmRoleView(View):
    def __init__(self, author, role, target_members):
        super().__init__(timeout=60)
        self.author = author
        self.role = role
        self.target_members = target_members

    @discord.ui.button(label="✅ XÁC NHẬN CẤP ROLE VIP", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        await interaction.response.edit_message(content=f"⏳ Đang tiến hành cấp Role VIP **{self.role.name}**...", view=None)
        await execute_add_role(interaction.channel, self.author, self.role, self.target_members)

    @discord.ui.button(label="❌ HỦY BỎ", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        await interaction.response.edit_message(content="❌ Đã hủy thao tác cấp Role VIP!", view=None)


# --- 📌 MỤC CẤP ROLE THÔNG MINH ---
class SmartMemberSelectForAdd(Select):
    def __init__(self, role, author):
        self.role = role
        self.author = author

        if role.name.lower().strip() == "member":
            candidates = [
                m for m in role.guild.members 
                if not m.bot and len([r for r in m.roles if not r.is_default()]) == 0
            ]
        else:
            candidates = [m for m in role.guild.members if not m.bot and role not in m.roles]

        if not candidates:
            super().__init__(placeholder=f"✨ Tất cả thành viên đều đã có Role '{role.name}'!", disabled=True, options=[discord.SelectOption(label="None", value="none")])
            return

        options = [
            discord.SelectOption(
                label="🚀 BẤM CÁI RẸT (CẤP TẤT CẢ)", 
                value="ALL", 
                description=f"Cấp role {role.name} cho TOÀN BỘ {len(candidates)} người chưa có!", 
                emoji="⚡"
            )
        ]

        for m in candidates[:24]:
            options.append(
                discord.SelectOption(
                    label=m.display_name[:100], 
                    value=str(m.id), 
                    description=f"Chưa có role {role.name}"
                )
            )

        super().__init__(
            placeholder=f"👉 Chọn người chưa có Role '{role.name}' để cấp ({len(candidates)} người)...",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return

        if self.role.name.lower().strip() == "member":
            candidates = [
                m for m in self.role.guild.members 
                if not m.bot and len([r for r in self.role.guild.roles if not r.is_default()]) == 0
            ]
        else:
            candidates = [m for m in self.role.guild.members if not m.bot and self.role not in m.roles]

        selected_members = []

        if "ALL" in self.values:
            selected_members = candidates
        else:
            for m_id in self.values:
                m = interaction.guild.get_member(int(m_id))
                if m:
                    selected_members.append(m)

        if not selected_members:
            await interaction.response.send_message("❌ Không có thành viên nào được chọn!", ephemeral=True)
            return

        is_strict_vip = any(vip in self.role.name.lower().strip() for vip in STRICT_VIP_ROLES)

        if is_strict_vip:
            view_confirm = ConfirmRoleView(self.author, self.role, selected_members)
            await interaction.response.edit_message(
                content=f"# ⚠️ XÁC NHẬN CẤP ROLE VIP TỐI CAO!\nÔng chủ {self.author.mention} có chắc chắn muốn cấp Role VIP **{self.role.name}** cho `{len(selected_members)}` thành viên?",
                view=view_confirm
            )
        else:
            await interaction.response.edit_message(content=f"⏳ Đang cấp role **{self.role.name}**...", view=None)
            await execute_add_role(interaction.channel, self.author, self.role, selected_members)


# --- 📌 MỤC XÓA ROLE THÔNG MINH ---
class SmartMemberSelectForRemove(Select):
    def __init__(self, role, author):
        self.role = role
        self.author = author

        candidates = [m for m in role.guild.members if not m.bot and role in m.roles]

        if not candidates:
            super().__init__(placeholder="❌ Không có ai trong Server sở hữu Role này!", disabled=True, options=[discord.SelectOption(label="None", value="none")])
            return

        options = [
            discord.SelectOption(label="🔥 BẤM CÁI RẸT (XÓA HẾT TẤT CẢ)", value="ALL", description=f"Gỡ sạch role {role.name} của TOÀN BỘ {len(candidates)} người!", emoji="🗑️")
        ]

        for m in candidates[:24]:
            options.append(discord.SelectOption(label=m.display_name[:100], value=str(m.id), description=f"Đang sở hữu role {role.name}"))

        super().__init__(
            placeholder=f"🗑️ Chọn người đang có role '{role.name}' để xóa ({len(candidates)} người)...",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return

        candidates = [m for m in self.role.guild.members if not m.bot and self.role in m.roles]
        selected_members = []

        if "ALL" in self.values:
            selected_members = candidates
        else:
            for m_id in self.values:
                m = interaction.guild.get_member(int(m_id))
                if m:
                    selected_members.append(m)

        await interaction.response.defer()
        removed_members = []

        for m in selected_members:
            try:
                await m.remove_roles(self.role, reason=f"Xóa bởi Admin {self.author}")
                removed_members.append(m)
            except Exception:
                pass

        if removed_members:
            mentions_str = " ".join([m.mention for m in removed_members[:15]])
            embed = discord.Embed(
                title="🗑️ THÔNG BÁO XÓA ROLE 🐶",
                description=(
                    f"# 👑 Ông chủ {self.author.mention} đã xóa role **{self.role.name}**!\n\n"
                    f"📊 **Số lượng bị xóa:** `{len(removed_members)}` thằng ngu 🐶\n"
                    f"👥 **Danh sách:** {mentions_str}\n\n"
                    f"📢 @here Thông báo cập nhật danh sách!"
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(content=f"@here ⚠️ Cập nhật xóa Role!", embed=embed)


# --- 📌 BẢNG ROLE CHÍNH (.bangrole) ---
class MasterBangRoleSelect(Select):
    def __init__(self, mode, author):
        self.mode = mode
        self.author = author

        guild = author.guild
        roles = [r for r in guild.roles if not r.is_default() and not r.managed][:25]

        options = [
            discord.SelectOption(label=r.name[:100], value=str(r.id), description=f"Số người đang có: {len(r.members)}")
            for r in roles
        ]

        placeholder_text = "✨ Chọn Role định CẤP cho người dùng..." if mode == "ADD" else "🗑️ Chọn Role định XÓA khỏi người dùng..."
        super().__init__(placeholder=placeholder_text, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return

        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message("❌ Role không tồn tại!", ephemeral=True)
            return

        view_step2 = View(timeout=120)
        if self.mode == "ADD":
            view_step2.add_item(SmartMemberSelectForAdd(role, self.author))
            await interaction.response.edit_message(
                content=f"# 👑 BẢNG CẤP ROLE THÔNG MINH\nĐã chọn Role: **{role.name}**. Hãy chọn thành viên ở danh sách bên dưới:",
                view=view_step2
            )
        else:
            view_step2.add_item(SmartMemberSelectForRemove(role, self.author))
            await interaction.response.edit_message(
                content=f"# 🗑️ BẢNG XÓA ROLE THÔNG MINH\nĐã chọn Role: **{role.name}**. Hãy chọn thành viên cần gỡ role bên dưới:",
                view=view_step2
            )


class MasterBangRoleView(View):
    def __init__(self, author):
        super().__init__(timeout=120)
        self.author = author
        self.add_item(MasterBangRoleSelect(mode="ADD", author=author))

    @discord.ui.button(label="✨ CHẾ ĐỘ CẤP ROLE", style=discord.ButtonStyle.success, row=1)
    async def mode_add(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        self.clear_items()
        self.add_item(MasterBangRoleSelect(mode="ADD", author=self.author))
        self.add_item(button)
        await interaction.response.edit_message(content="# ✨ ĐÃ CHUYỂN SANG CHẾ ĐỘ CẤP ROLE THÔNG MINH", view=self)

    @discord.ui.button(label="🗑️ CHẾ ĐỘ XÓA ROLE", style=discord.ButtonStyle.danger, row=1)
    async def mode_remove(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        self.clear_items()
        self.add_item(MasterBangRoleSelect(mode="REMOVE", author=self.author))
        self.add_item(button)
        await interaction.response.edit_message(content="# 🗑️ ĐÃ CHUYỂN SANG CHẾ ĐỘ XÓA ROLE THÔNG MINH", view=self)


# --- 📌 LỆNH .bangrole ---
@bot.command(name="bangrole")
async def bangrole_cmd(ctx):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return

    embed = discord.Embed(
        title="👑 BẢNG QUẢN LÝ ROLE THÔNG MINH - ANH EM CHAT WAR 👑",
        description=(
            f"# 👑 Ông Chủ {ctx.author.mention} Muốn Quản Lý Role Kìa!\n\n"
            f"⚡ **Nút Bấm Cái Rẹt:** Cấp/Xóa cực nhanh cho TẤT CẢ mọi người cùng lúc.\n"
            f"🔒 **Xác Nhận Role VIP:** Chỉ 2 Role tối cao mới bắt xác nhận, role lỏ cấp thẳng trực tiếp!\n\n"
            f"👉 *Chọn chế độ CẤP ROLE hoặc XÓA ROLE bên dưới để bắt đầu:* "
        ),
        color=discord.Color.gold()
    )
    view = MasterBangRoleView(author=ctx.author)
    await ctx.send(embed=embed, view=view)


# --- 📌 BẢNG XẾP HẠNG ROLE .Roleall ---
@bot.command(name="Roleall")
async def role_all_command(ctx):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return

    embed = discord.Embed(title="📊 BẢNG XẾP HẠNG VÀ PHÂN CẤP ROLE", color=discord.Color.gold())
    for role in sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True):
        if not role.is_default() and not role.managed:
            members_with_role = [m.mention for m in role.members if not m.bot]
            if members_with_role:
                embed.add_field(
                    name=f"👑 **{role.name}** ({len(members_with_role)})",
                    value=", ".join(members_with_role[:15]) + ("..." if len(members_with_role) > 15 else ""),
                    inline=False
                )
    await ctx.send(embed=embed)


# --- 📌 LỆNH .Add VÀ .UnLever ---
@bot.command(name="Add")
async def add_permission(ctx, arg1: str = None, arg2: str = None, member: discord.Member = None):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return

    if arg1 and arg1.lower() == "bot":
        embed = discord.Embed(
            title="📖 HƯỚNG DẪN CẤP QUYỀN LEVEL (.Add)",
            description="# 👑 HỆ THỐNG PHÂN CẤP QUYỀN BOT",
            color=discord.Color.gold()
        )
        embed.add_field(name="⭐ **Level 1**", value="Sử dụng lệnh `.mute` và `.unmute`.", inline=False)
        embed.add_field(name="⭐⭐ **Level 2**", value="Sử dụng lệnh `.lock`, `.unlock`, `.mute`, `.unmute`.", inline=False)
        embed.add_field(name="⭐⭐⭐ **Level 3**", value="Sử dụng toàn bộ lệnh bao gồm cả `.Roleall`.", inline=False)
        embed.add_field(name="🤖 **.Xoamainauto**", value="Xóa hàng loạt các main nhiều trang.", inline=False)
        embed.add_field(name="❌ **.UnLever**", value="Gỡ bỏ sạch Level của thành viên.", inline=False)
        await ctx.send(embed=embed)
        return

    if not arg1 or not arg2:
        await ctx.send(f"Ông Chủ 👑 Muốn Cho Ai Ạ {ctx.author.mention}")
        return

    level_text = arg1.lower() + " " + arg2.lower() if arg2 else arg1.lower()
    target = member or (ctx.message.mentions[0] if ctx.message.mentions else None)

    if not target:
        await ctx.send(f"Ông Chủ 👑 Muốn Cho Ai Ạ {ctx.author.mention}")
        return

    if "1" in level_text:
        bot_permissions[target.id] = 1
        await ctx.send(f"✨ Bạn đã có quyền sở hữu 2 lệnh thuộc **Level 1** đó {target.mention}!")
    elif "2" in level_text:
        bot_permissions[target.id] = 2
        await ctx.send(f"✨ Bạn đã có quyền sở hữu các lệnh quản trị kênh **Level 2** {target.mention}!")
    elif "3" in level_text:
        bot_permissions[target.id] = 3
        await ctx.send(f"✨ Bạn đã có quyền cao cấp **Level 3** bao gồm xem danh sách Role {target.mention}!")
    else:
        await ctx.send("⚠️ Cú pháp sai! Gõ `.Add bot` để xem hướng dẫn chi tiết.")


@bot.command(name="UnLever")
async def unlever_permission(ctx, member: discord.Member = None):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return
    if not member:
        await ctx.send("💡 Cú pháp: `.UnLever @thành_viên`")
        return
    if member.id in bot_permissions:
        del bot_permissions[member.id]
    await ctx.send(f"# ❌ Người chơi {member.mention} đã bị ông chủ gỡ quyền Level!")


# --- 📌 LỆNH .Xoamainauto ---
class ChannelSelect(Select):
    def __init__(self, channels):
        options = [
            discord.SelectOption(
                label=f"#{channel.name}"[:100],
                value=str(channel.id),
                description=f"ID Kênh: {channel.id}",
                emoji="🗑️"
            )
            for channel in channels
        ]
        super().__init__(
            placeholder="📌 Tích chọn các main muốn xóa tự động...",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        deleted_names = []

        for channel_id in self.values:
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                channel_name = channel.name
                try:
                    await channel.delete(reason=f"Xóa tự động bởi Admin {interaction.user}")
                    deleted_names.append(f"#{channel_name}")
                except Exception as e:
                    print(f"Lỗi không thể xóa kênh {channel_id}: {e}")

        deleted_str = ", ".join(deleted_names) if deleted_names else "Không có"
        await interaction.followup.send(
            content=f"# 🤖 ĐÃ TỰ ĐỘNG DỌN SẠCH CÁC MAIN:\n**{deleted_str}**"
        )


class MultiPageDeleteView(View):
    def __init__(self, channels, author_id):
        super().__init__(timeout=120)
        self.channels = channels
        self.author_id = author_id
        self.current_page = 0
        self.per_page = 25
        self.update_components()

    def update_components(self):
        self.clear_items()
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_channels = self.channels[start:end]

        if page_channels:
            self.add_item(ChannelSelect(page_channels))

        if len(self.channels) > self.per_page:
            btn_prev = Button(label="⬅️ Trang trước", style=discord.ButtonStyle.secondary, disabled=(self.current_page == 0))
            btn_next = Button(label="Trang sau ➡️", style=discord.ButtonStyle.secondary, disabled=(end >= len(self.channels)))

            btn_prev.callback = self.prev_page_callback
            btn_next.callback = self.next_page_callback

            self.add_item(btn_prev)
            self.add_item(btn_next)

    async def prev_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        self.current_page -= 1
        self.update_components()
        await interaction.response.edit_message(view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Thằng cha mày có role đâu mà bấm?", ephemeral=True)
            return
        self.current_page += 1
        self.update_components()
        await interaction.response.edit_message(view=self)


@bot.command(name="Xoamainauto")
async def delete_main_auto_command(ctx):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return

    text_channels = [ch for ch in ctx.guild.text_channels]
    if not text_channels:
        await ctx.send("❌ Không tìm thấy main nào trong server!")
        return

    embed = discord.Embed(
        title="🤖 HỆ THỐNG XÓA MAIN TỰ ĐỘNG (.Xoamainauto)",
        description=f"# 🗑️ QUẢN LÝ DỌN MAIN HÀNG LOẠT\nTích chọn các kênh bạn muốn xóa bên dưới.\n\n📊 *Tổng số kênh text hiện tại:* `{len(text_channels)}` kênh",
        color=discord.Color.gold()
    )
    view = MultiPageDeleteView(text_channels, ctx.author.id)
    await ctx.send(embed=embed, view=view)


# --- 📌 LỆNH .help ---
@bot.command(name="help")
async def help_command(ctx):
    try:
        embed = discord.Embed(
            title="👑 HỆ THỐNG QUẢN LÝ ANH EM CHAT WAR 👑",
            description="# 🚀 DANH SÁCH LỆNH QUẢN TRỊ BOT ĐỆ ALPHA 3",
            color=discord.Color.purple()
        )
        embed.add_field(name="🔒 **.lock**", value="Khóa kênh chat hiện tại.", inline=True)
        embed.add_field(name="🔓 **.unlock**", value="Mở khóa kênh chat hiện tại.", inline=True)
        embed.add_field(name="🔇 **.mute @user <thời_gian>**", value="Cấm chat thành viên.", inline=False)
        embed.add_field(name="🔊 **.unmute @user**", value="Gỡ cấm chat thành viên.", inline=False)
        embed.add_field(name="👑 **.bangrole**", value="Quản lý Role thông minh (Cấp/Xóa/Xác nhận/Tag @here).", inline=False)
        embed.add_field(name="📊 **.Roleall**", value="Xem xếp hạng danh sách Role.", inline=False)
        embed.add_field(name="🤖 **.Xoamainauto**", value="Xóa hàng loạt các main nhiều trang.", inline=False)
        embed.add_field(name="⭐ **.Add bot**", value="Xem hướng dẫn & cấp Level quản lý.", inline=False)
        embed.add_field(name="❌ **.UnLever @user**", value="Gỡ sạch Level thành viên.", inline=False)
        embed.set_thumbnail(url=WELCOME_GIF_URL)
        embed.set_footer(text=f"Yêu cầu bởi: {ctx.author.name} • Anh Em Chat War Bot")
        await ctx.send(embed=embed)
    except Exception:
        text_help = (
            "# 👑 HỆ THỐNG QUẢN LÝ ANH EM CHAT WAR 👑\n\n"
            "🔒 `.lock` - Khóa kênh chat hiện tại.\n"
            "🔓 `.unlock` - Mở khóa kênh chat hiện tại.\n"
            "🔇 `.mute @user <thời_gian>` - Cấm chat thành viên.\n"
            "🔊 `.unmute @user` - Gỡ cấm chat thành viên.\n"
            "👑 `.bangrole` - Quản lý Cấp / Xóa Role thông minh.\n"
            "📊 `.Roleall` - Xem xếp hạng phân cấp Role.\n"
            "🤖 `.Xoamainauto` - Xóa hàng loạt main nhiều trang."
        )
        await ctx.send(text_help)


# --- 📌 CÁC LỆNH QUẢN TRỊ KÊNH AND MUTE ---
@bot.command(name="lock")
async def lock_channel(ctx):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        try:
            await ctx.message.add_reaction("🔒")
        except Exception:
            pass
        await ctx.send(embed=discord.Embed(title="🔒 ĐÃ KHÓA KÊNH CHAT", description=f"# 🔒 Kênh {ctx.channel.mention} đã bị khóa!", color=discord.Color.red()))
    except Exception as e:
        await ctx.send(f"❌ Không thể khóa kênh: {e}")


@bot.command(name="unlock")
async def unlock_channel(ctx):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        try:
            await ctx.message.add_reaction("🔓")
        except Exception:
            pass
        await ctx.send(embed=discord.Embed(title="🔓 ĐÃ MỞ KHÓA KÊNH CHAT", description=f"# 🔓 Kênh {ctx.channel.mention} đã mở khóa!", color=discord.Color.green()))
    except Exception as e:
        await ctx.send(f"❌ Không thể mở khóa kênh: {e}")


@bot.command(name="mute")
async def mute_user(ctx, member: discord.Member = None, time_str: str = None):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return
    if not member or not time_str:
        await ctx.send("💡 Cú pháp: `.mute @thành_viên <thời_gian>`")
        return
    time_regex = re.match(r"^(\d+)([spmhd])$", time_str.lower())
    if not time_regex:
        await ctx.send("⚠️ Định dạng thời gian sai! Dùng: `10s`, `10p`, `1h`.")
        return
    amount, unit = int(time_regex.group(1)), time_regex.group(2)
    delta = {"s": timedelta(seconds=amount), "p": timedelta(minutes=amount), "m": timedelta(minutes=amount), "h": timedelta(hours=amount), "d": timedelta(days=amount)}[unit]
    try:
        await member.timeout(delta, reason=f"Mute bởi {ctx.author}")
        try:
            await ctx.message.add_reaction("🔇")
        except Exception:
            pass
        await ctx.send(embed=discord.Embed(title="🔇 CẤM CHAT THÀNH VIÊN", description=f"# 🔇 Thành viên {member.mention} đã bị cấm chat.", color=discord.Color.dark_red()))
    except Exception as e:
        await ctx.send(f"❌ Không thể mute: {e}")


@bot.command(name="unmute")
async def unmute_user(ctx, member: discord.Member = None):
    if not check_exclusive_admin(ctx):
        await ctx.send(f"Thằng cha mày có role đâu mà ghi? {ctx.author.mention}")
        return
    if not member:
        await ctx.send("💡 Cú pháp: `.unmute @thành_viên`")
        return
    try:
        await member.timeout(None, reason=f"Unmute bởi {ctx.author}")
        try:
            await ctx.message.add_reaction("🔊")
        except Exception:
            pass
        await ctx.send(embed=discord.Embed(title="🔊 GỠ CẤM CHAT", description=f"# 🔊 Thành viên {member.mention} đã được gỡ cấm chat.", color=discord.Color.green()))
    except Exception:
        await ctx.send("❌ Không thể gỡ cấm chat cho người này!")


# --- 📌 THÔNG BÁO VÀO / RỜI SERVER ---
@bot.event
async def on_member_join(member):
    if len([r for r in member.roles if not r.is_default()]) == 0:
        role_member = discord.utils.find(lambda r: r.name.lower().strip() == "member", member.guild.roles)
        if role_member:
            try:
                await member.add_roles(role_member, reason="Tự động cấp role Member cho người mới.")
            except Exception:
                pass

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        try:
            embed = discord.Embed(
                title="👑 Welcome to Anh Em Chat War 👑",
                description=(
                    f"# 🎉 Xin Chào {member.mention} Đến Với Ank Emk Chat War 👑\n\n"
                    f"✨ **Chúc bạn có những giây phút giao lưu thật vui vẻ!**\n\n"
                    f"🛡️ **Trạng thái:** Đã tự động cấp Role **Member**\n"
                    f"📊 **Tổng thành viên:** `{member.guild.member_count}` người"
                ),
                color=discord.Color.from_rgb(155, 89, 182)
            )
            embed.set_image(url=WELCOME_GIF_URL)
            if member.display_avatar:
                embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(content=f"# 🎉 Xin Chào Đến Với Ank Emk Chat War 👑 {member.mention}", embed=embed)
        except Exception:
            await channel.send(f"# 🎉 Xin Chào {member.mention} Đến Với Ank Emk Chat War 👑")


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL_ID)
    if channel:
        try:
            embed = discord.Embed(
                title="⚔️ THÀNH VIÊN ĐÃ OUT SERVER ⚔️",
                description=(
                    f"# 💔 1 Người Đã Phản Bội Ank Emk Chat War ❤️\n\n"
                    f"🔥 **Thằng Lồn Ngu {member.mention} Đã Chạy Khỏi Sever 😂**\n\n"
                    f"📊 **Tổng thành viên còn lại:** `{member.guild.member_count}` người"
                ),
                color=discord.Color.dark_red()
            )
            if member.display_avatar:
                embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(content=f"# ⚠️ {member.mention} 1 Người Đã Phản Bội Ank Emk Chat War ❤️ Thằng Lồn Ngu Đã Chạy Khỏi Sever 😂", embed=embed)
        except Exception:
            await channel.send(f"# ⚠️ {member.mention} 1 Người Đã Phản Bội Ank Emk Chat War ❤️ Thằng Lồn Ngu Đã Chạy Khỏi Sever 😂")


# CHẠY BOT VỚI TOKEN MỚI
bot.run("MTU2MTk5MzYwNTk4NjM5NDIyMw.G9gKkB.TE-jHvL7rMn0I3GsHbKnxqCVloqfJSnaTQIg90")
