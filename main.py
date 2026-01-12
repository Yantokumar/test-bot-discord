import discord
from discord.ext import commands
import json
import random
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_data():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    
    with open('users.json', 'r') as f:
        return json.load(f)

def save_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

def check_user(user_id, data):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "uang": 100, 
            "inventori": [],
            "terakhir_daily": "2000-01-01 00:00:00"
        }
    return data

@bot.event
async def on_ready():
    print(f'✅ Bot Online sebagai {bot.user}')

@bot.command()
async def saldo(ctx):
    data = load_data()
    data = check_user(ctx.author.id, data)
    uang = data[str(ctx.author.id)]["uang"]
    await ctx.send(f"💰 Saldo **{ctx.author.name}**: {uang} koin")

@bot.command()
async def daily(ctx):
    data = load_data()
    data = check_user(ctx.author.id, data)
    
    user_data = data[str(ctx.author.id)]
    terakhir = datetime.strptime(user_data["terakhir_daily"], "%Y-%m-%d %H:%M:%S")
    
    if datetime.now() - terakhir > timedelta(hours=24):
        hadiah = 200
        user_data["uang"] += hadiah
        user_data["terakhir_daily"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        await ctx.send(f"🎁 Kamu mengambil hadiah harian sebesar **{hadiah} koin**!")
    else:
        sisa = terakhir + timedelta(hours=24) - datetime.now()
        jam = int(sisa.total_seconds() // 3600)
        menit = int((sisa.total_seconds() % 3600) // 60)
        await ctx.send(f"⏳ Kamu sudah ambil koin hari ini. Tunggu {jam} jam {menit} menit lagi.")

@bot.command()
async def toko(ctx):
    embed = discord.Embed(title="🏪 Toko Keren", color=discord.Color.blue())
    embed.add_field(name="🍎 Apel", value="Harga: 50 koin\n`!beli apel`", inline=False)
    embed.add_field(name="⚔️ Pedang", value="Harga: 500 koin\n`!beli pedang`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def beli(ctx, barang: str):
    data = load_data()
    data = check_user(ctx.author.id, data)
    
    harga_toko = {"apel": 50, "pedang": 500}
    barang = barang.lower()

    if barang in harga_toko:
        biaya = harga_toko[barang]
        if data[str(ctx.author.id)]["uang"] >= biaya:
            data[str(ctx.author.id)]["uang"] -= biaya
            data[str(ctx.author.id)]["inventori"].append(barang)
            save_data(data)
            await ctx.send(f"✅ Berhasil membeli **{barang}**! Sisa saldo: {data[str(ctx.author.id)]['uang']}")
        else:
            await ctx.send("❌ Uang kamu tidak cukup!")
    else:
        await ctx.send("❌ Barang tidak ada di toko.")

@bot.command()
async def tebak(ctx, angka: int):
    data = load_data()
    data = check_user(ctx.author.id, data)
    
    jawaban = random.randint(1, 100)
    if angka == jawaban:
        hadiah = 150
        data[str(ctx.author.id)]["uang"] += hadiah
        save_data(data)
        await ctx.send(f"🎉 BENAR! Angkanya {jawaban}. Kamu dapat {hadiah} koin!")
    else:
        await ctx.send(f"😜 SALAH! Angkanya tadi {jawaban}. Coba lagi!")

@tebak.error
async def tebak_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kamu lupa memasukkan angka! Contoh: `!tebak 3`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Masukkan angka yang valid (1 sampai 5), bukan teks atau simbol!")

game_data = {
    "buah": {
        "mangga": "Kulitnya hijau atau kuning, dagingnya manis, ada biji besar di tengah.",
        "pisang": "Bentuknya panjang, warna kuning, makanan kesukaan monyet.",
        "semangka": "Besar, kulit hijau belang, isinya merah dan banyak air."
    },
    "hewan": {
        "gajah": "Punya belalai panjang dan telinga yang sangat lebar.",
        "jerapah": "Lehernya sangat panjang, suka makan daun di pohon tinggi.",
        "kucing": "Suka mengeong dan dipelihara manusia."
    },
    "sayur": {
        "wortel": "Warna oranye, konon bagus untuk kesehatan mata.",
        "bayam": "Sayuran hijau, favorit tokoh kartun Popeye.",
        "tomat": "Warna merah, bisa dianggap buah tapi sering di sayur, bentuknya bulat."
    }
}

@bot.command()
async def tebak_kata(ctx, kategori: str):
    kategori = kategori.lower()
    
    if kategori not in game_data:
        await ctx.send("❌ Kategori tidak ada! Pilih: `buah`, `hewan`, atau `sayur`.")
        return

    kata, kisi_kisi = random.choice(list(game_data[kategori].items()))
    
    await ctx.send(f"🎮 **Tebak {kategori.capitalize()}!**\n💡 Petunjuk: *{kisi_kisi}*")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        
        if msg.content.lower() == kata:
            data = load_data()
            data = check_user(ctx.author.id, data)
            hadiah = 250
            data[str(ctx.author.id)]["uang"] += hadiah
            save_data(data)
            await ctx.send(f"🎉 Selamat {ctx.author.name}! Jawabannya adalah **{kata}**. Kamu dapat **{hadiah} koin**!")
        else:
            await ctx.send(f"❌ Salah! Jawabannya tadi adalah **{kata}**.")
            
    except TimeoutError:
        await ctx.send(f"⏰ Waktu habis! Jawabannya adalah **{kata}**.")

@bot.command()
async def inventory(ctx):
    data = load_data()
    data = check_user(ctx.author.id, data)
    items = data[str(ctx.author.id)]["inventori"]
    
    if not items:
        await ctx.send(f"🎒 **{ctx.author.name}**, tas kamu masih kosong.")
    else:
        daftar_barang = ", ".join(items)
        await ctx.send(f"🎒 **Inventory {ctx.author.name}**:\n{daftar_barang}")

bot.run('Token_Bot_Discord_Anda_Di_Sini')