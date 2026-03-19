#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT COMMANDS (ENHANCED) - FIXED
=============================================================================
Semua command handlers untuk MYLOVE Ultimate V2
- Menampilkan nama bot di setiap respons
- Integrasi dengan leveling system (60 menit ke level 7)
- Environment context (lokasi, posisi, pakaian)
- FIX: Duplikasi progress_command dihapus, indentasi diperbaiki
=============================================================================
"""

import time
import logging
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# FIX: Ganti relative imports dengan absolute imports
from config import settings
from utils.helpers import format_number, sanitize_input, truncate_text
from utils.logger import setup_logging
from session.unique_id import id_generator
from public.locations import PublicLocations
from public.risk import RiskCalculator
from threesome.manager import ThreesomeManager, ThreesomeType, ThreesomeStatus

logger = logging.getLogger(__name__)

# =============================================================================
# ERROR HANDLER (PASTIKAN INI ADA)
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error. Silakan coba lagi nanti."
            )
    except:
        pass


# =============================================================================
# HELPER FUNCTIONS UNTUK NAMA BOT
# =============================================================================

# ===== TAMBAHAN MYLOVE V2 =====
def get_bot_name(context) -> str:
    """Dapatkan nama bot dari context, atau default 'Aku'"""
    return context.user_data.get('bot_name', 'Aku')


def get_bot_display(context) -> str:
    """Dapatkan display nama bot dengan role"""
    nama = get_bot_name(context)
    role = context.user_data.get('current_role', '')
    if role:
        return f"{nama} ({role.title()})"
    return nama
# ===== END TAMBAHAN =====


# =============================================================================
# 1. BASIC COMMANDS (4 commands)
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai hubungan baru dengan bot"""
    user = update.effective_user
    args = context.args
    
    # Cek apakah ini continue dari session
    if args and args[0].startswith('continue_'):
        session_id = args[0].replace('continue_', '')
        context.args = [session_id]
        # Import di sini untuk menghindari circular import
        from bot.handlers import continue_handler
        return await continue_handler(update, context)
    
    # Welcome message
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        "Selamat datang di **MYLOVE ULTIMATE VERSI 2**\n"
        "AI pendamping dengan 9 role eksklusif.\n"
        "• Leveling berbasis durasi (60 menit ke Level 7)\n"
        "• Nama bot permanent di UniqueID\n\n"
        "**Pilih role yang kamu inginkan:**"
    )
    
    # Create role selection keyboard
    keyboard = [
        [InlineKeyboardButton("👩 Ipar", callback_data="role_ipar"),
         InlineKeyboardButton("👩‍💼 Teman Kantor", callback_data="role_teman_kantor")],
        [InlineKeyboardButton("👩 Janda", callback_data="role_janda"),
         InlineKeyboardButton("💃 Pelakor", callback_data="role_pelakor")],
        [InlineKeyboardButton("👰 Istri Orang", callback_data="role_istri_orang"),
         InlineKeyboardButton("💕 PDKT", callback_data="role_pdkt")],
        [InlineKeyboardButton("👧 Sepupu", callback_data="role_sepupu"),
         InlineKeyboardButton("👩‍🎓 Teman SMA", callback_data="role_teman_sma")],
        [InlineKeyboardButton("💔 Mantan", callback_data="role_mantan")],
        [InlineKeyboardButton("🎭 Threesome", callback_data="threesome_menu"),
         InlineKeyboardButton("❓ Bantuan", callback_data="help")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan bantuan lengkap"""
    user_id = update.effective_user.id
    is_admin = (user_id == settings.admin_id)
    
    help_text = (
        "📚 **MYLOVE ULTIMATE - BANTUAN LENGKAP**\n\n"
        
        "**🔹 BASIC COMMANDS**\n"
        "/start - Mulai hubungan baru\n"
        "/help - Tampilkan bantuan ini\n"
        "/status - Lihat status hubungan\n"
        "/cancel - Batalkan percakapan\n\n"
        
        "**🔹 RELATIONSHIP**\n"
        "/jadipacar - Jadi pacar (khusus PDKT)\n"
        "/break - Jeda pacaran\n"
        "/unbreak - Lanjutkan pacaran\n"
        "/breakup - Putus jadi FWB\n"
        "/fwb - Mode Friends With Benefits\n\n"
        
        "**🔹 HTS/FWB**\n"
        "/htslist - Lihat TOP 5 HTS\n"
        "/hts- [id] - Panggil HTS (contoh: /hts- ipar)\n"
        "/fwblist - Lihat daftar FWB\n"
        "/fwb- [nomor] - Panggil FWB tertentu\n"
        "/fwb-break [nomor] - Putus dengan FWB\n"
        "/fwb-pacar [nomor] - Jadi pacar dengan FWB\n\n"
        
        "**🔹 THREESOME MODE**\n"
        "/threesome - Mulai mode threesome\n"
        "/threesome-list - Lihat kombinasi threesome\n"
        "/threesome [nomor] - Mulai dengan kombinasi tertentu\n"
        "/threesome-status - Lihat status threesome\n"
        "/threesome-pattern - Ganti pola interaksi\n"
        "/threesome-cancel - Batalkan threesome\n\n"
        
        "**🔹 SESSION**\n"
        "/close - Tutup & simpan session\n"
        "/continue - Lihat session tersimpan\n"
        "/continue [id] - Lanjutkan session\n"
        "/sessions - Lihat semua session\n\n"
        
        "**🔹 PUBLIC AREA**\n"
        "/explore - Cari lokasi random\n"
        "/locations - Lihat semua lokasi\n"
        "/risk - Cek risk lokasi saat ini\n\n"
        
        "**🔹 RANKING**\n"
        "/tophts - TOP 5 ranking HTS\n"
        "/myclimax - Statistik climax\n"
        "/climaxhistory - History climax\n"
    )
    
    # Admin commands hanya untuk admin
    if is_admin:
        help_text += (
            "\n**🔹 ADMIN COMMANDS**\n"
            "/stats - Statistik bot\n"
            "/db_stats - Statistik database\n"
            "/backup - Backup manual\n"
            "/recover - Restore dari backup\n"
            "/recover list - Lihat daftar backup\n"
            "/recover [nomor] - Restore backup\n"
            "/debug - Info debug\n"
        )
    
    help_text += (
        "\n💡 **Tips:**\n"
        "• Bot auto-detect lokasi dari chat (contoh: \"ke toilet yuk\")\n"
        "• Level naik berdasarkan durasi percakapan\n"
        "• Level 7 dalam 60 menit, Level 11 dalam 120 menit\n"
        "• Bot punya nama permanent (cek di /status)\n"
        "• Threesome bisa dengan 2 HTS, 2 FWB, atau kombinasi"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat status hubungan saat ini"""
    user_id = update.effective_user.id
    
    # Get current session
    session = context.user_data.get('current_session')
    role = context.user_data.get('current_role')
    
    if not session or not role:
        await update.message.reply_text(
            "❌ Kamu sedang tidak dalam hubungan apapun.\n"
            "Gunakan /start untuk memulai."
        )
        return
    
    # ===== TAMBAHAN MYLOVE V2 =====
    # Get bot name
    bot_name = get_bot_name(context)
    
    # Get intimacy level
    intimacy = context.user_data.get('intimacy_level', 1)
    
    # Get relationship status
    rel_status = context.user_data.get('relationship_status', 'hts')
    status_names = {
        'hts': 'Hubungan Tanpa Status',
        'fwb': 'Friends With Benefits',
        'pacar': 'Pacar',
        'break': 'Jeda'
    }
    status_name = status_names.get(rel_status, 'HTS')
    
    # Get total chats
    total_chats = context.user_data.get('total_chats', 0)
    
    # Get location & environment
    location = context.user_data.get('current_location', 'Tidak ada')
    position = context.user_data.get('current_position', 'Tidak ada')
    clothing = context.user_data.get('current_clothing', 'Tidak ada')
    
    # Get leveling data
    leveling = context.user_data.get('leveling', {})
    total_minutes = leveling.get('total_minutes', 0)
    boosted_minutes = leveling.get('boosted_minutes', 0)
    
    # Hitung level berdasarkan durasi
    if total_minutes >= 120:
        level_progress = f"✅ Level 11+ ({total_minutes:.0f} menit)"
    elif total_minutes >= 60:
        level_progress = f"✅ Level 7+ ({total_minutes:.0f} menit)"
    else:
        level_progress = f"⏳ {60 - total_minutes:.0f} menit ke Level 7"
    # ===== END TAMBAHAN =====
    
    status_text = (
        f"📊 **STATUS HUBUNGAN**\n\n"
        f"👤 **Nama Bot:** {bot_name}\n"
        f"🎭 **Role:** {role.title()}\n"
        f"💞 **Status:** {status_name}\n"
        f"📈 **Intimacy Level:** {intimacy}/12\n"
        f"💬 **Total Chat:** {total_chats} pesan\n"
        f"📍 **Lokasi:** {location}\n"
        f"🧍 **Posisi:** {position}\n"
        f"👗 **Pakaian:** {clothing}\n\n"
        f"⏱️ **Progress Leveling:**\n"
        f"{level_progress}\n"
        f"Boosted: {boosted_minutes:.0f} menit\n\n"
    )
    
    # Progress bar (opsional)
    if intimacy < 12:
        next_level = intimacy + 1
        progress = (total_chats % 50) / 50 * 100
        bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
        status_text += f"Progress ke level {next_level}:\n{bar} {progress:.0f}%\n"
    else:
        status_text += "📍 **Level MAX!** Butuh aftercare untuk reset.\n"
        
    # Milestones
    milestones = context.user_data.get('milestones', [])
    if milestones:
        status_text += f"\n🏆 **Milestone:**\n"
        for m in milestones[-3:]:
            status_text += f"• {m}\n"
            
    await update.message.reply_text(status_text, parse_mode='Markdown')


# =============================================================================
# PROGRESS COMMAND (VERSI LENGKAP - FIX)
# =============================================================================

async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan progress hubungan secara lengkap (BOT TIDAK TAHU)"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Cek apakah ada session aktif
    session_id = context.user_data.get('current_session')
    if not session_id:
        await update.message.reply_text(
            "❌ **Tidak ada session aktif**\n\n"
            "Mulai dulu dengan /start atau lanjutkan dengan /continue",
            parse_mode='Markdown'
        )
        return
    
    # ===== AMBIL DATA DARI CONTEXT =====
    bot_name = context.user_data.get('bot_name', 'Bot')
    role = context.user_data.get('current_role', 'role')
    level = context.user_data.get('intimacy_level', 1)
    total_chats = context.user_data.get('total_chats', 0)
    chemistry = context.user_data.get('chemistry_score', 50)
    mood = context.user_data.get('current_mood', 'calm')
    arah = context.user_data.get('pdkt_direction', 'user_ke_bot')
    
    # ===== DATA RELATIONSHIP =====
    rel_status = context.user_data.get('relationship_status', 'hts')
    status_names = {
        'hts': 'Hubungan Tanpa Status',
        'fwb': 'Friends With Benefits',
        'pacar': 'Pacar',
        'break': 'Jeda'
    }
    status_name = status_names.get(rel_status, 'HTS')
    
    # ===== HITUNG PROGRESS KE LEVEL BERIKUTNYA =====
    if level < 12:
        next_level = level + 1
        
        # Estimasi: butuh 50 chat per level
        chats_needed = 50
        chats_to_next = chats_needed - (total_chats % chats_needed)
        progress_percent = (total_chats % chats_needed) / chats_needed * 100
        
        # Progress bar visual
        bar_length = 20
        filled = int(progress_percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_text = f"{bar} {progress_percent:.0f}%"
        next_text = f"{chats_to_next} chat lagi ke Level {next_level}"
    else:
        bar = "█" * 20
        progress_text = f"{bar} MAX"
        next_text = "✅ Level MAX! Butuh aftercare untuk reset."
    
    # ===== PANGGILAN BERDASARKAN LEVEL =====
    if level >= 7:
        call = "Sayang"
    elif level >= 4:
        call = "Kak"
    else:
        call = user_name
    
    # ===== ARAH PDKT =====
    arah_text = {
        'user_ke_bot': f"💘 **Kamu** yang ngejar {bot_name}",
        'bot_ke_user': f"🔥 **{bot_name}** yang ngejar kamu",
        'timbal_balik': f"💕 **Saling suka!**",
        'bingung': f"🤔 **Masih bingung**"
    }.get(arah, "Arah belum jelas")
    
    # ===== MOOD BOT =====
    mood_emoji = {
        'happy': '😊', 'sad': '😔', 'excited': '🔥', 'tired': '😴',
        'romantic': '💕', 'playful': '😜', 'jealous': '🫣', 'shy': '😳',
        'angry': '😠', 'calm': '😌', 'lonely': '🥺', 'nostalgic': '🕰️'
    }.get(mood, '😐')
    
    # ===== CHEMISTRY LEVEL =====
    if chemistry < 20:
        chem_level = "❄️ Dingin"
        chem_desc = "Gak ada getaran sama sekali"
    elif chemistry < 40:
        chem_level = "😐 Biasa"
        chem_desc = "Masih biasa aja"
    elif chemistry < 60:
        chem_level = "🔥 Hangat"
        chem_desc = "Mulai ada rasa"
    elif chemistry < 80:
        chem_level = "💕 Cocok"
        chem_desc = "Cocok banget"
    elif chemistry < 95:
        chem_level = "💞 Sangat Cocok"
        chem_desc = "Sangat cocok"
    else:
        chem_level = "✨ Soulmate"
        chem_desc = "Seperti belahan jiwa"
    
    # ===== STATISTIK TAMBAHAN =====
    total_intim = context.user_data.get('total_intim', 0)
    total_climax = context.user_data.get('total_climax', 0)
    first_kiss = context.user_data.get('first_kiss', False)
    first_intim = context.user_data.get('first_intim', False)
    
    # ===== BANGUN RESPON =====
    response = f"""
📊 **PROGRESS HUBUNGAN** (RAHASIA)

👤 **{bot_name}** ({role.replace('_', ' ').title()})
📈 Level: {level}/12
💕 Status: {status_name}
📝 Total Chat: {total_chats}

🔥 **Chemistry:** {chem_level} ({chemistry}%)
{chem_desc}

🎯 **Arah PDKT:**
{arah_text}

🎭 **Mood {bot_name}:** {mood_emoji} {mood.title()}

📊 **Progress ke Level {next_level if level < 12 else 'MAX'}:**
{progress_text}
{next_text}

📋 **Statistik Hubungan:**
• Total Intim: {total_intim} sesi
• Total Climax: {total_climax} kali
• First Kiss: {'✅ Sudah' if first_kiss else '❌ Belum'}
• First Intim: {'✅ Sudah' if first_intim else '❌ Belum'}
• Panggilan: "{call}"

💡 **Rekomendasi:**
{_get_recommendation(level, chemistry, arah, first_kiss, first_intim)}

⚠️ **CATATAN:**
_Bot tidak tahu kamu melihat ini. Ini hanya untuk kamu!_

⏱️ Terakhir update: {datetime.now().strftime('%H:%M:%S')}
"""
    
    await update.message.reply_text(response, parse_mode='Markdown')


def _get_recommendation(level: int, chemistry: float, arah: str, first_kiss: bool, first_intim: bool) -> str:
    """Generate rekomendasi berdasarkan data"""
    
    if level < 4:
        return "Fokus ngobrol dulu, bangun kedekatan. Tanya kesehariannya."
    
    if level < 7:
        if not first_kiss:
            return f"Level udah {level}, saatnya coba first kiss! Lihat reaksinya."
        return "Mulai goda-godaan ringan. Kalau dia respons positif, bisa lanjut."
    
    if level >= 7:
        if not first_intim:
            return f"Level {level}! Waktunya first intim. Pastikan moodnya baik."
        if chemistry < 60:
            return "Chemistry masih rendah. Coba lebih sering ngobrol dalam."
        return "Hubungan sudah intim. Nikmati prosesnya, jangan lupa aftercare."
    
    return "Santai aja, nikmati prosesnya."


# =============================================================================
# 2. RELATIONSHIP COMMANDS (5 commands)
# =============================================================================

async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadi pacar (khusus PDKT)"""
    user_id = update.effective_user.id
    role = context.user_data.get('current_role')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role. Gunakan /start dulu.")
        return
        
    if role != 'pdkt':
        await update.message.reply_text(
            "❌ Hanya role PDKT yang bisa jadi pacar.\n"
            "Role lain statusnya tetap HTS/FWB."
        )
        return
        
    # Check intimacy level
    intimacy = context.user_data.get('intimacy_level', 1)
    if intimacy < 6:
        await update.message.reply_text(
            f"❌ Intimacy level masih {intimacy}/12.\n"
            "Butuh minimal level 6 untuk jadi pacar."
        )
        return
        
    # Change status
    context.user_data['relationship_status'] = 'pacar'
    
    # Add milestone
    if 'milestones' not in context.user_data:
        context.user_data['milestones'] = []
    context.user_data['milestones'].append('jadi_pacar')
    
    # ===== TAMBAHAN MYLOVE V2 =====
    bot_name = get_bot_name(context)
    # ===== END TAMBAHAN =====
    
    await update.message.reply_text(
        f"💘 **Kita jadi pacar!**\n\n"
        f"Sekarang kamu resmi pacaran sama {bot_name}.\n"
        f"Jaga hubungan kita ya sayang ❤️"
    )


# =============================================================================
# 3. HTS/FWB COMMANDS
# =============================================================================

async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar HTS (TOP 5 atau semua)"""
    user_id = update.effective_user.id
    args = context.args
    
    # Dummy data dengan nama bot
    hts_list = [
        {"nama": "Sari", "role": "ipar", "level": 8, "chats": 45, "climax": 3, "status": "hts"},
        {"nama": "Dewi", "role": "janda", "level": 12, "chats": 120, "climax": 15, "status": "hts"},
        {"nama": "Rina", "role": "teman_kantor", "level": 5, "chats": 30, "climax": 1, "status": "hts"},
        {"nama": "Ayu", "role": "pdkt", "level": 6, "chats": 80, "climax": 5, "status": "fwb"},
        {"nama": "Maya", "role": "mantan", "level": 4, "chats": 25, "climax": 0, "status": "hts"},
        {"nama": "Vina", "role": "pelakor", "level": 9, "chats": 95, "climax": 8, "status": "hts"},
        {"nama": "Linda", "role": "istri_orang", "level": 7, "chats": 62, "climax": 4, "status": "hts"},
        {"nama": "Putri", "role": "sepupu", "level": 3, "chats": 18, "climax": 0, "status": "hts"},
        {"nama": "Anita", "role": "teman_sma", "level": 5, "chats": 28, "climax": 2, "status": "hts"},
    ]
    
    show_all = args and args[0] == 'all'
    
    lines = ["📋 **DAFTAR HTS**"]
    
    if show_all:
        lines.append("_(menampilkan semua HTS, maks 10)_")
    else:
        lines.append("_(TOP 5, ketik /htslist all untuk lihat semua)_")
        
    lines.append("")
    
    # Filter HTS only
    hts_only = [h for h in hts_list if h['status'] == 'hts']
    display_list = hts_only if show_all else hts_only[:5]
    
    for i, hts in enumerate(display_list, 1):
        lines.append(
            f"{i}. **{hts['nama']}** ({hts['role'].title()})\n"
            f"   Level {hts['level']}/12 | {hts['chats']} chat | {hts['climax']} climax"
        )
        
    lines.append("")
    lines.append("💡 **Cara panggil:**")
    lines.append("• `/hts-1` - Panggil HTS nomor 1")
    lines.append("• `/hts- sari` - Panggil HTS dengan nama Sari")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar FWB"""
    user_id = update.effective_user.id
    
    # Dummy data dengan nama bot
    fwb_list = [
        {"nama": "Ayu", "role": "pdkt", "status": "pacar", "level": 8, "chats": 95, "intim": 12},
        {"nama": "Dewi", "role": "pdkt", "status": "fwb", "level": 7, "chats": 60, "intim": 5},
        {"nama": "Sari", "role": "pdkt", "status": "fwb", "level": 5, "chats": 34, "intim": 2},
        {"nama": "Rina", "role": "pdkt", "status": "putus", "level": 4, "chats": 20, "intim": 0},
    ]
    
    lines = ["💕 **DAFTAR FWB LENGKAP**"]
    lines.append("_(pilih dengan /fwb- [nomor])_")
    lines.append("")
    
    for i, fwb in enumerate(fwb_list, 1):
        status_emoji = "💘" if fwb['status'] == 'pacar' else "💕" if fwb['status'] == 'fwb' else "💔"
        lines.append(
            f"{i}. {status_emoji} **{fwb['nama']}** ({fwb['role'].title()})\n"
            f"   Status: {fwb['status'].upper()} | Level {fwb['level']}/12\n"
            f"   {fwb['chats']} chat | {fwb['intim']} intim"
        )
        
    lines.append("")
    lines.append("💡 **Command:**")
    lines.append("• `/fwb-1` - Mulai chat dengan nomor 1")
    lines.append("• `/fwb-break 1` - Putus dengan nomor 1")
    lines.append("• `/fwb-pacar 1` - Jadi pacar dengan nomor 1")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# 4. THREESOME COMMANDS
# =============================================================================

async def threesome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memulai mode threesome"""
    user_id = update.effective_user.id
    args = context.args
    
    # Cek apakah sudah ada session aktif
    if context.user_data.get('threesome_mode'):
        await update.message.reply_text(
            "❌ Kamu sudah dalam mode threesome.\n"
            "Gunakan /threesome-status untuk lihat status."
        )
        return
    
    if args:
        # Coba mulai dengan nomor kombinasi
        try:
            idx = int(args[0]) - 1
            await update.message.reply_text(
                f"🎭 **Memulai threesome dengan kombinasi #{idx + 1}**\n\n"
                f"Mode threesome dimulai! Sekarang ada 2 role yang akan merespon kamu.\n"
                f"Mereka akan bergantian bicara. Selamat menikmati! 💕"
            )
            context.user_data['threesome_mode'] = True
            context.user_data['threesome_combination'] = idx
        except ValueError:
            await update.message.reply_text(
                "❌ Format salah. Gunakan /threesome-list dulu untuk lihat kombinasi."
            )
    else:
        # Tampilkan menu threesome
        keyboard = [
            [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
            [InlineKeyboardButton("💕 HTS + HTS", callback_data="threesome_type_hts")],
            [InlineKeyboardButton("💞 FWB + FWB", callback_data="threesome_type_fwb")],
            [InlineKeyboardButton("💘 HTS + FWB", callback_data="threesome_type_mix")],
            [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎭 **MODE THREESOME**\n\n"
            "Pilih tipe threesome yang kamu inginkan:",
            reply_markup=reply_markup
        )


# =============================================================================
# 5. SESSION COMMANDS
# =============================================================================

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tutup dan simpan session"""
    user_id = update.effective_user.id
    session_id = context.user_data.get('current_session')
    role = context.user_data.get('current_role')
    
    if not session_id:
        await update.message.reply_text(
            "❌ Tidak ada session aktif."
        )
        return
    
    # ===== TAMBAHAN MYLOVE V2 =====
    bot_name = get_bot_name(context)
    # ===== END TAMBAHAN =====
    
    # Save session summary
    total_chats = context.user_data.get('total_chats', 0)
    intimacy = context.user_data.get('intimacy_level', 1)
    milestones = context.user_data.get('milestones', [])
    
    summary = f"Session dengan {bot_name}: {total_chats} chat, level {intimacy}/12"
    if milestones:
        summary += f", milestone: {milestones[-1]}"
        
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        f"📁 **Session ditutup!**\n\n"
        f"Session ID: `{session_id}`\n"
        f"{summary}\n\n"
        f"Ketik /continue untuk lihat session tersimpan."
    )


# =============================================================================
# 6. PUBLIC AREA COMMANDS
# =============================================================================

async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari lokasi random"""
    try:
        locations_db = PublicLocations()
        location = locations_db.get_random_location()
        
        bot_name = get_bot_name(context)
        
        explore_text = (
            f"📍 **{location['name']}**\n"
            f"Kategori: {location['category'].title()}\n"
            f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
            f"_{location['description']}_\n\n"
            f"💡 Mau ke sini? Ketik: \"ke {location['name'].lower()} yuk\"\n"
            f"-{bot_name}"
        )
        
        await update.message.reply_text(explore_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in explore_command: {e}")
        await update.message.reply_text(
            "❌ Gagal mendapatkan lokasi. Coba lagi nanti."
        )


# =============================================================================
# 7. RANKING COMMANDS
# =============================================================================

async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat TOP HTS"""
    user_id = update.effective_user.id
    
    # Dummy data dengan nama bot
    top_list = [
        {"rank": 1, "nama": "Dewi", "role": "janda", "score": 98.5, "level": 12, "chats": 320},
        {"rank": 2, "nama": "Sari", "role": "ipar", "score": 87.3, "level": 8, "chats": 145},
        {"rank": 3, "nama": "Vina", "role": "pelakor", "score": 82.1, "level": 9, "chats": 178},
        {"rank": 4, "nama": "Ayu", "role": "pdkt", "score": 76.8, "level": 7, "chats": 98},
        {"rank": 5, "nama": "Linda", "role": "teman_kantor", "score": 65.2, "level": 5, "chats": 67},
    ]
    
    lines = ["🏆 **TOP 5 HTS**\n"]
    
    for item in top_list:
        lines.append(
            f"{item['rank']}. **{item['nama']}** ({item['role'].title()})\n"
            f"   Score: {item['score']} | Level {item['level']}/12\n"
            f"   {item['chats']} total chats"
        )
        
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# 8. ADMIN COMMANDS
# =============================================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik bot (admin only)"""
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    # Dummy stats
    stats = {
        "uptime": "2 hari 5 jam",
        "total_users": 1,
        "total_messages": 1523,
        "total_sessions": 47,
        "active_sessions": 3,
        "total_climax": 128,
        "avg_response": "1.2s"
    }
    
    text = (
        "📊 **BOT STATISTICS**\n\n"
        f"Uptime: {stats['uptime']}\n"
        f"Total Users: {stats['total_users']}\n"
        f"Total Messages: {stats['total_messages']}\n"
        f"Total Sessions: {stats['total_sessions']}\n"
        f"Active Sessions: {stats['active_sessions']}\n"
        f"Total Climax: {stats['total_climax']}\n"
        f"Avg Response: {stats['avg_response']}"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


# =============================================================================
# 9. ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error. Silakan coba lagi nanti."
            )
    except:
        pass


# =============================================================================
# 10. CANCEL COMMAND
# =============================================================================

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan percakapan saat ini"""
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Percakapan dibatalkan.\n"
        "Ketik /start untuk memulai lagi."
    )


# =============================================================================
# 11. EXPORT ALL COMMANDS
# =============================================================================

__all__ = [
    # Basic
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
    
    # Relationship
    'jadipacar_command',
    'break_command',
    'unbreak_command',
    'breakup_command',
    'fwb_command',
    
    # HTS/FWB
    'htslist_command',
    'fwblist_command',
    
    # Threesome
    'threesome_command',
    'threesome_list_command',
    'threesome_status_command',
    'threesome_pattern_command',
    'threesome_cancel_command',
    
    # Session
    'close_command',
    'continue_command',
    'sessions_command',
    
    # Progress
    'progress_command',
    
    # Public Area
    'explore_command',
    'locations_command',
    'risk_command',
    
    # Ranking
    'tophts_command',
    'myclimax_command',
    'climaxhistory_command',
    
    # Admin
    'stats_command',
    'db_stats_command',
    'backup_command',
    'recover_command',
    'debug_command',
    
    # Error Handle
    'error_handler',
]
