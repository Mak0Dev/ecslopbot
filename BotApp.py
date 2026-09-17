# python -m pip install discord requests
# also this bot made like in 2025 and based on rophix bot
# https://github.com/Mak0Dev/ecslopbot

import discord
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv

import logging
import os
import requests
import random
import json

from datetime import datetime, timezone

BOT_NAME = "ecslop" # name it like ur ecslop revival
BASE_URL = "https://YourURL" # put ur url here
DATA_FILE = "gambling_data.json"
DAILY_CLAIM = 100


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("discord")


load_dotenv()

TOKEN = os.getenv("TOKEN")


API_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def get_today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

# i guess it's broken lmao
def load_gambling_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, dict):
                return data

    except Exception as e:
        logger.error(
            "Failed to load gambling data: %s",
            e
        )

    return {}


def save_gambling_data():
    try:
        temp_file = DATA_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                gambling_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(
            temp_file,
            DATA_FILE
        )

    except Exception as e:
        logger.error(
            "Failed to save gambling data: %s",
            e
        )


gambling_data = load_gambling_data()


def get_gambling_user(discord_user_id: int):
    user_id = str(discord_user_id)
    today = get_today()

    if user_id not in gambling_data:
        gambling_data[user_id] = {
            "balance": 0,
            "wins": 0,
            "losses": 0,
            "total_won": 0,
            "total_lost": 0,
            "today_won": 0,
            "today_lost": 0,
            "last_claim": None,
            "stats_day": today
        }

        save_gambling_data()

    user = gambling_data[user_id]

    defaults = {
        "balance": 0,
        "wins": 0,
        "losses": 0,
        "total_won": 0,
        "total_lost": 0,
        "today_won": 0,
        "today_lost": 0,
        "last_claim": None,
        "stats_day": today
    }

    changed = False

    for key, value in defaults.items():
        if key not in user:
            user[key] = value
            changed = True

    if user.get("stats_day") != today:
        user["today_won"] = 0
        user["today_lost"] = 0
        user["stats_day"] = today
        changed = True

    if changed:
        save_gambling_data()

    return user


class profilelink(View):

    def __init__(self, user_id: int):
        super().__init__(timeout=None)

        self.add_item(
            Button(
                label="🔗 Profile",
                style=discord.ButtonStyle.link,
                url=f"{BASE_URL}/users/{user_id}/profile"
            )
        )


class GlobalClient(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            intents=intents
        )

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

        try:
            synced = await self.tree.sync()

            logger.info(
                "Synced %s slash commands",
                len(synced)
            )

        except Exception as e:

            logger.error(
                "Failed to sync commands: %s",
                e
            )

    async def on_ready(self):

        logger.info(
            "%s Started ✅",
            self.user
        )

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name=BOT_NAME
            )
        )


client = GlobalClient()


def get_user_by_username(username: str):

    url = (
        f"{BASE_URL}"
        f"/apisite/api/users/get-by-username"
        f"?username={requests.utils.quote(username)}"
    )

    try:

        response = requests.get(
            url,
            headers=API_HEADERS,
            allow_redirects=False,
            timeout=10
        )

        logger.info(
            "Username API: %s %s",
            response.status_code,
            url
        )

        if response.status_code != 200:

            logger.error(
                "Username lookup failed: %s %s",
                response.status_code,
                response.text[:500]
            )

            return None

        data = response.json()

        user_id = data.get("Id")

        if user_id is None:
            user_id = data.get("id")

        if user_id is None:
            return None

        return {
            "id": int(user_id),
            "username": (
                data.get("Username")
                or data.get("username")
                or username
            )
        }

    except Exception as e:

        logger.error(
            "Username lookup exception: %s",
            e
        )

        return None

def get_user_info(user_id: int):

    url = (
        f"{BASE_URL}"
        f"/apisite/users/v1/users/{user_id}"
    )

    try:

        response = requests.get(
            url,
            headers=API_HEADERS,
            allow_redirects=False,
            timeout=10
        )

        logger.info(
            "User info API: %s %s",
            response.status_code,
            url
        )

        if response.status_code != 200:

            logger.error(
                "User info failed: %s %s",
                response.status_code,
                response.text[:500]
            )

            return None

        return response.json()

    except Exception as e:

        logger.error(
            "User info exception: %s",
            e
        )

        return None

def get_avatar(user_id: int):

    url = (
        f"{BASE_URL}"
        f"/apisite/thumbnails/v1/users/avatar"
        f"?userIds={user_id}"
        f"&size=420x420"
        f"&format=png"
    )

    try:

        response = requests.get(
            url,
            headers=API_HEADERS,
            allow_redirects=False,
            timeout=10
        )

        logger.info(
            "Avatar API: %s %s",
            response.status_code,
            url
        )

        if response.status_code != 200:
            return None

        data = response.json()

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        image = items[0].get(
            "imageUrl"
        )

        if not image:
            return None

        if image.startswith("/"):
            image = BASE_URL + image

        return image

    except Exception as e:

        logger.error(
            "Avatar lookup failed: %s",
            e
        )

        return None


def get_user_rap(user_id: int):

    base_url = (
        f"{BASE_URL}"
        f"/apisite/inventory/v1/users/{user_id}/assets/collectibles"
    )

    total_rap = 0
    cursor = None
    page = 0

    while True:

        page += 1

        params = {
            "limit": 100
        }

        if cursor:
            params["cursor"] = cursor

        try:

            response = requests.get(
                base_url,
                headers=API_HEADERS,
                params=params,
                allow_redirects=False,
                timeout=10
            )

            logger.info(
                "RAP API page %s: %s %s",
                page,
                response.status_code,
                response.url
            )

            if response.status_code != 200:

                logger.error(
                    "RAP lookup failed: %s %s",
                    response.status_code,
                    response.text[:500]
                )

                break

            data = response.json()

            items = data.get(
                "data",
                []
            )

            for item in items:

                recent_average_price = item.get(
                    "recentAveragePrice",
                    0
                )

                try:

                    total_rap += int(
                        recent_average_price or 0
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    logger.warning(
                        "Invalid recentAveragePrice: %s",
                        recent_average_price
                    )

            next_cursor = data.get(
                "nextPageCursor"
            )

            logger.info(
                "RAP page %s: items=%s total_rap=%s next_cursor=%s",
                page,
                len(items),
                total_rap,
                bool(next_cursor)
            )

            if not next_cursor:
                break

            cursor = next_cursor

        except Exception as e:

            logger.error(
                "RAP lookup exception: %s",
                e
            )

            break

    return total_rap


def format_created_date(created):

    if not created:
        return "Unknown"

    try:

        dt = datetime.fromisoformat(
            created.replace(
                "Z",
                "+00:00"
            )
        )

        return dt.strftime(
            "%d %B %Y, %H:%M UTC"
        )

    except Exception:

        return str(created)


@client.tree.command(
    name="sup",
    description="say sup to app"
)
async def sup(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "Sup"
    )

    logger.info(
        "command sup used"
    )


@client.tree.command(
    name="site",
    description="site"
)
async def site(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="Link:",
        description=f"[{BOT_NAME}]({BASE_URL}/)",
        color=discord.Color.orange()
    )

    embed.set_thumbnail(
        url=(
            "https://images-ext-1.discordapp.net/"
            "external/8QsbS3bjhZEeW-F93j-Pb6t2jecI8d-piEkXAtBVPi4/"
            "%3Fsize%3D1024/"
            "https/cdn.discordapp.com/"
            "avatars/1416906209667321908/"
            "bff55986a4ae2125aba483a68eb78bba.png"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )



@client.tree.command(
    name="info",
    description="the bot info"
)
async def info(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="Info:",
        description=(
            "Bot Version: 1.4\n"
            f"Site: [{BOT_NAME}]({BASE_URL}/)"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(
        url=(
            "https://images-ext-1.discordapp.net/"
            "external/8QsbS3bjhZEeW-F93j-Pb6t2jecI8d-piEkXAtBVPi4/"
            "%3Fsize%3D1024/"
            "https/cdn.discordapp.com/"
            "avatars/1416906209667321908/"
            "bff55986a4ae2125aba483a68eb78bba.png"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# /DROP-ITEM
# ============================================================

@client.tree.command(
    name="drop-item",
    description="id, name, price, limited"
)
@app_commands.describe(
    id="id",
    name="name",
    price="price",
    stock="how much in stock"
)
async def relese(
    interaction: discord.Interaction,
    id: int,
    name: str,
    price: str,
    stock: str
):

    url = (
        f"{BASE_URL}"
        f"/apisite/thumbnails/v1/assets"
        f"?assetIds={id}"
        f"&format=png"
        f"&size=420x420"
    )

    try:

        response = requests.get(
            url,
            headers=API_HEADERS,
            allow_redirects=False,
            timeout=10
        )

        if response.status_code != 200:

            await interaction.response.send_message(
                f"⚠️ Failed to fetch item "
                f"(status {response.status_code}).",
                ephemeral=True
            )

            return

        data = response.json()

        items = data.get(
            "data",
            []
        )

        if not items:

            await interaction.response.send_message(
                "⚠️ No thumbnail data returned.",
                ephemeral=True
            )

            return

        image = items[0].get(
            "imageUrl"
        )

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Error while fetching item: `{e}`",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title="Drop Item:",
        color=discord.Color.orange()
    )

    if image:

        if image.startswith("/"):
            image = BASE_URL + image

        embed.set_thumbnail(
            url=image
        )

    embed.add_field(
        name="🔗 Link:",
        value=f"[{name}]({BASE_URL}/catalog/{id}/item)",
        inline=False
    )

    embed.add_field(
        name="💵 Price:",
        value=price,
        inline=False
    )

    embed.add_field(
        name="📊 Stock:",
        value=stock,
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


@client.tree.command(
    name="profile",
    description="Get a Karblox profile by username"
)
@app_commands.describe(
    username="Karblox username"
)
async def profile(
    interaction: discord.Interaction,
    username: str
):

    user = get_user_by_username(
        username
    )

    if not user:

        await interaction.response.send_message(
            f"❌ User `{username}` was not found.",
            ephemeral=True
        )

        return

    user_id = user["id"]

    user_data = get_user_info(
        user_id
    )

    if not user_data:

        await interaction.response.send_message(
            "❌ Failed to load user information.",
            ephemeral=True
        )

        return

    avatar = get_avatar(
        user_id
    )

    rap = get_user_rap(
        user_id
    )

    name = (
        user_data.get("name")
        or user["username"]
        or username
    )

    display_name = (
        user_data.get("displayName")
        or name
    )

    description = (
        user_data.get("description")
        or "No description."
    )

    created = user_data.get(
        "created"
    )

    is_banned = user_data.get(
        "isBanned",
        False
    )

    is_verified = user_data.get(
        "isVerified",
        False
    )

    post_count = user_data.get(
        "postCount",
        0
    )

    embed = discord.Embed(
        title=name,
        description=description,
        color=discord.Color.orange()
    )

    if avatar:

        embed.set_thumbnail(
            url=avatar
        )

    embed.add_field(
        name="Display Name",
        value=str(display_name),
        inline=True
    )

    embed.add_field(
        name="User ID",
        value=str(user_id),
        inline=True
    )

    embed.add_field(
        name="💰 RAP",
        value=f"**{rap:,} Robux**",
        inline=True
    )

    embed.add_field(
        name="Banned",
        value=(
            "True"
            if is_banned
            else "False"
        ),
        inline=True
    )

    embed.add_field(
        name="Verified",
        value=(
            "True"
            if is_verified
            else "False"
        ),
        inline=True
    )

    embed.add_field(
        name="Created",
        value=format_created_date(
            created
        ),
        inline=True
    )

    embed.add_field(
        name="Posts",
        value=str(post_count),
        inline=True
    )

    view = profilelink(
        user_id=user_id
    )

    await interaction.response.send_message(
        embed=embed,
        view=view
    )


@client.tree.command(
    name="avatar",
    description="Show a user's avatar by username"
)
@app_commands.describe(
    username="Karblox username"
)
async def avatar(
    interaction: discord.Interaction,
    username: str
):

    user = get_user_by_username(
        username
    )

    if not user:

        await interaction.response.send_message(
            f"❌ User `{username}` was not found.",
            ephemeral=True
        )

        return

    user_id = user["id"]

    image = get_avatar(
        user_id
    )

    if not image:

        await interaction.response.send_message(
            "❌ Failed to get avatar.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title=f"{user['username']}'s Avatar",
        color=discord.Color.orange()
    )

    embed.set_image(
        url=image
    )

    view = profilelink(
        user_id=user_id
    )

    await interaction.response.send_message(
        embed=embed,
        view=view
    )


@client.tree.command(
    name="item-idea",
    description="link on item, name, price, limited"
)
@app_commands.describe(
    link="id",
    name="name",
    price="price",
    stock="how much in stock"
)
async def itemidea(
    interaction: discord.Interaction,
    link: str,
    name: str,
    price: str,
    stock: str
):

    embed = discord.Embed(
        title="Item Idea:",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="🔗 Link:",
        value=f"[{name}]({link})",
        inline=False
    )

    embed.add_field(
        name="💵 Price:",
        value=price,
        inline=False
    )

    embed.add_field(
        name="📊 Stock:",
        value=stock,
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


@client.tree.command(
    name="claim",
    description="Claim your daily coins"
)
async def claim(
    interaction: discord.Interaction
):

    user = get_gambling_user(
        interaction.user.id
    )

    today = get_today()

    last_claim = user.get(
        "last_claim"
    )

    if last_claim == today:

        await interaction.response.send_message(
            "❌ You already claimed your daily "
            "coins today.\n"
            f"Come back tomorrow for **{DAILY_CLAIM} coins**.",
            ephemeral=True
        )

        return

    user["balance"] += DAILY_CLAIM
    user["last_claim"] = today

    save_gambling_data()

    embed = discord.Embed(
        title="🎁 Daily Reward",
        description=(
            f"You received **{DAILY_CLAIM} coins**!"
        ),
        color=discord.Color.orange()
    )

    embed.add_field(
        name="💰 Balance",
        value=f"{user['balance']} coins",
        inline=False
    )

    embed.set_footer(
        text="You can claim again tomorrow."
    )

    await interaction.response.send_message(
        embed=embed
    )


@client.tree.command(
    name="stats",
    description="Show your gambling statistics"
)
async def stats(
    interaction: discord.Interaction
):

    user = get_gambling_user(
        interaction.user.id
    )

    embed = discord.Embed(
        title=f"🎰 {interaction.user.display_name}'s Stats",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="💰 Balance",
        value=f"**{user['balance']} coins**",
        inline=False
    )

    embed.add_field(
        name="🏆 Wins",
        value=str(user["wins"]),
        inline=True
    )

    embed.add_field(
        name="💀 Losses",
        value=str(user["losses"]),
        inline=True
    )

    embed.add_field(
        name="💵 Total Won",
        value=f"{user['total_won']} coins",
        inline=True
    )

    embed.add_field(
        name="📉 Total Lost",
        value=f"{user['total_lost']} coins",
        inline=True
    )

    embed.add_field(
        name="📅 Won Today",
        value=f"{user['today_won']} coins",
        inline=True
    )

    embed.add_field(
        name="📅 Lost Today",
        value=f"{user['today_lost']} coins",
        inline=True
    )

    total_games = (
        user["wins"]
        + user["losses"]
    )

    if total_games > 0:

        win_rate = (
            user["wins"]
            / total_games
            * 100
        )

        win_rate_text = f"{win_rate:.1f}%"

    else:

        win_rate_text = "0%"

    embed.add_field(
        name="📊 Win Rate",
        value=win_rate_text,
        inline=False
    )

    embed.set_footer(
        text="Gambling statistics"
    )

    await interaction.response.send_message(
        embed=embed
    )


@client.tree.command(
    name="playingame",
    description="just gambling"
)
@app_commands.describe(
    id2="profile id",
    id="profile id",
    value="how much"
)
async def playingame(
    interaction: discord.Interaction,
    id: int,
    id2: int,
    value: int
):

    image1 = get_avatar(
        id
    )

    image2 = get_avatar(
        id2
    )

    if not image1:

        await interaction.response.send_message(
            f"❌ Avatar not found for ID {id}.",
            ephemeral=True
        )

        return

    if not image2:

        await interaction.response.send_message(
            f"❌ Avatar not found for ID {id2}.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title="",
        color=discord.Color.orange()
    )

    result = random.randint(
        1,
        2
    )

    if result == 2:

        embed.set_thumbnail(
            url=image1
        )

        embed.add_field(
            name=f"ID: {id} won:",
            value=f"{value} robux",
            inline=False
        )

        view = profilelink(
            user_id=id
        )

    else:

        embed.set_thumbnail(
            url=image2
        )

        embed.add_field(
            name=f"ID: {id2} won:",
            value=f"{value} robux",
            inline=False
        )

        view = profilelink(
            user_id=id2
        )

    await interaction.response.send_message(
        embed=embed,
        view=view
    )



@client.tree.command(
    name="gambling",
    description="Gamble your coins"
)
@app_commands.describe(
    robux="How many coins you want to bet"
)
async def gambling(
    interaction: discord.Interaction,
    robux: int
):

    if robux <= 0:

        await interaction.response.send_message(
            "❌ Your bet must be greater than 0.",
            ephemeral=True
        )

        return

    user = get_gambling_user(
        interaction.user.id
    )

    if user["balance"] < robux:

        await interaction.response.send_message(
            "❌ You don't have enough coins.\n"
            f"💰 Your balance: **{user['balance']}**\n"
            f"🎰 Your bet: **{robux}**",
            ephemeral=True
        )

        return

    result = random.randint(
        1,
        2
    )

    if result == 2:

        winnings = robux * 2

        user["balance"] += robux
        user["wins"] += 1
        user["total_won"] += winnings
        user["today_won"] += winnings

        save_gambling_data()

        embed = discord.Embed(
            title="🎰 You Won!",
            description=(
                f"You bet **{robux} coins**\n"
                f"You won **{winnings} coins**!"
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="💰 Balance",
            value=f"{user['balance']} coins",
            inline=False
        )

    else:

        user["balance"] -= robux
        user["losses"] += 1
        user["total_lost"] += robux
        user["today_lost"] += robux

        save_gambling_data()

        embed = discord.Embed(
            title="💀 You Lost!",
            description=(
                f"You lost **{robux} coins**."
            ),
            color=discord.Color.red()
        )

        embed.add_field(
            name="💰 Balance",
            value=f"{user['balance']} coins",
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN2 is not set in environment variables."
    )


client.run(
    TOKEN
)