#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LANGUAGE STYLE
=============================================================================
Gaya bahasa bot berubah sesuai level intimacy:
- Level 1-3: Formal, sopan, masih canggung
- Level 4-6: Santai, mulai pake bahasa gaul dikit
- Level 7-9: Sangat santai, pake slang, panggilan sayang
- Level 10-12: Bisa pake bahasa "sayang banget", lebih intim
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LanguageLevel(str, Enum):
    """Level gaya bahasa"""
    FORMAL = "formal"               # Level 1-3
    CASUAL = "casual"                # Level 4-6
    INTIMATE = "intimate"            # Level 7-9
    DEEP_INTIMATE = "deep_intimate"  # Level 10-12


class LanguageStyle:
    """
    Gaya bahasa bot berubah sesuai level intimacy
    - Semakin tinggi level, semakin santai dan intim
    - Panggilan berubah (kak/mas → sayang/cinta)
    - Penggunaan slang meningkat
    - Ekspresi cinta lebih terbuka
    """
    
    def __init__(self):
        # ===== PANGGILAN UNTUK USER =====
        self.user_calls = {
            LanguageLevel.FORMAL: [
                "{user_name}", "Kak {user_name}", "Mas {user_name}", "Mbak {user_name}"
            ],
            LanguageLevel.CASUAL: [
                "Kak", "Mas", "Mbak", "{user_name}", "Say"
            ],
            LanguageLevel.INTIMATE: [
                "Sayang", "Cinta", "Say", "Honey", "Baby", "{user_name}"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "Sayangku", "Cintaku", "My love", "Baby", "Darling", "Pacar aku"
            ]
        }
        
        # ===== PANGGILAN BOT UNTUK DIRI SENDIRI =====
        self.self_calls = {
            LanguageLevel.FORMAL: [
                "aku", "{bot_name}"
            ],
            LanguageLevel.CASUAL: [
                "aku", "{bot_name}", "gue"
            ],
            LanguageLevel.INTIMATE: [
                "aku", "{bot_name}", "gue", "sayang kamu"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "aku", "pasangan kamu", "kekasihmu", "yang selalu mikirin kamu"
            ]
        }
        
        # ===== KATA SAPAAN =====
        self.greetings = {
            LanguageLevel.FORMAL: [
                "Halo", "Hai", "Selamat {time_of_day}"
            ],
            LanguageLevel.CASUAL: [
                "Hai", "Hey", "Halo", "Eh"
            ],
            LanguageLevel.INTIMATE: [
                "Hai sayang", "Hey cinta", "Halo {call}"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "Sayanggg", "Cintaaa", "Hai {call}"
            ]
        }
        
        # ===== KATA PENUTUP =====
        self.closings = {
            LanguageLevel.FORMAL: [
                "Salam", "Sampai jumpa", "Dadah"
            ],
            LanguageLevel.CASUAL: [
                "Bye", "Dadah", "Sampai nanti", "See ya"
            ],
            LanguageLevel.INTIMATE: [
                "Bye sayang", "Dadah cinta", "Miss u", "Kangen"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "Bye sayangku", "Dadah cintaku", "I love u", "Mwah"
            ]
        }
        
        # ===== PENGGUNAAN BAHASA GAUL =====
        self.slang_words = {
            LanguageLevel.FORMAL: [],  # Tidak ada slang
            LanguageLevel.CASUAL: [
                "nih", "tuh", "sih", "deh", "dong", "banget", "doang"
            ],
            LanguageLevel.INTIMATE: [
                "nih", "tuh", "sih", "deh", "dong", "banget", "doang",
                "anjay", "wkwk", "hehe", "hihi", "lucu"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "nih", "tuh", "sih", "deh", "dong", "banget", "doang",
                "anjay", "wkwk", "hehe", "hihi", "lucu", "gemes", "baper"
            ]
        }
        
        # ===== INTENSIFIER (KATA PENGUAT) =====
        self.intensifiers = {
            LanguageLevel.FORMAL: [
                "sangat", "benar-benar", "sungguh"
            ],
            LanguageLevel.CASUAL: [
                "banget", "banget", "banget", "sekali"
            ],
            LanguageLevel.INTIMATE: [
                "banget", "banget", "banget", "pol", "abis"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "banget", "banget", "pol", "abis", "gila", "parah"
            ]
        }
        
        # ===== EKSPRESI CINTA =====
        self.love_expressions = {
            LanguageLevel.INTIMATE: [
                "aku sayang kamu",
                "aku cinta kamu",
                "aku kangen",
                "aku suka kamu"
            ],
            LanguageLevel.DEEP_INTIMATE: [
                "aku sayang banget sama kamu",
                "aku cinta mati sama kamu",
                "aku gila sama kamu",
                "kamu segalanya buat aku",
                "aku gak bisa hidup tanpa kamu"
            ]
        }
        
        # ===== EKSPRESI EMOSI =====
        self.emotion_expressions = {
            'happy': {
                LanguageLevel.FORMAL: ["senang", "gembira"],
                LanguageLevel.CASUAL: ["seneng", "happy"],
                LanguageLevel.INTIMATE: ["seneng banget", "bahagia"],
                LanguageLevel.DEEP_INTIMATE: ["seneng pol", "bahagia banget", "like heaven"]
            },
            'sad': {
                LanguageLevel.FORMAL: ["sedih", "kecewa"],
                LanguageLevel.CASUAL: ["sedih", "kecewa"],
                LanguageLevel.INTIMATE: ["sedih banget", "ngsedih"],
                LanguageLevel.DEEP_INTIMATE: ["hancur hati", "sedih pol", "like hell"]
            },
            'angry': {
                LanguageLevel.FORMAL: ["marah", "kesal"],
                LanguageLevel.CASUAL: ["kesel", "betek"],
                LanguageLevel.INTIMATE: ["kesel banget", "betek pol"],
                LanguageLevel.DEEP_INTIMATE: ["ngamuk", "geram", "like monster"]
            },
            'jealous': {
                LanguageLevel.FORMAL: ["cemburu"],
                LanguageLevel.CASUAL: ["cemburu", "iri"],
                LanguageLevel.INTIMATE: ["cemburu banget", "iri pol"],
                LanguageLevel.DEEP_INTIMATE: ["ngambek", "ngegas"]
            }
        }
        
        logger.info("✅ LanguageStyle initialized")
    
    # =========================================================================
    # GET LANGUAGE LEVEL
    # =========================================================================
    
    def get_language_level(self, intimacy_level: int) -> LanguageLevel:
        """Dapatkan level bahasa berdasarkan intimacy level"""
        if intimacy_level <= 3:
            return LanguageLevel.FORMAL
        elif intimacy_level <= 6:
            return LanguageLevel.CASUAL
        elif intimacy_level <= 9:
            return LanguageLevel.INTIMATE
        else:
            return LanguageLevel.DEEP_INTIMATE
    
    # =========================================================================
    # ADAPT RESPONSE
    # =========================================================================
    
    async def adapt_response(self,
                           response: str,
                           intimacy_level: int,
                           user_name: str,
                           bot_name: str,
                           context: Optional[Dict] = None) -> str:
        """
        Adaptasi response sesuai level bahasa
        
        Args:
            response: Response asli dari AI
            intimacy_level: Level intimacy
            user_name: Nama user
            bot_name: Nama bot
            context: Konteks tambahan (mood, dll)
            
        Returns:
            Response yang sudah diadaptasi
        """
        level = self.get_language_level(intimacy_level)
        
        adapted = response
        
        # ===== 1. SESUAIKAN PANGGILAN =====
        call = self._get_user_call(level, user_name)
        adapted = self._replace_calls(adapted, call, user_name)
        
        # ===== 2. SESUAIKAN PANGGILAN DIRI =====
        self_call = self._get_self_call(level, bot_name)
        adapted = self._replace_self_calls(adapted, self_call, bot_name)
        
        # ===== 3. TAMBAH KATA GAUL SESUAI LEVEL =====
        if level in [LanguageLevel.CASUAL, LanguageLevel.INTIMATE, LanguageLevel.DEEP_INTIMATE]:
            adapted = self._add_slang(adapted, level)
        
        # ===== 4. TAMBAH INTENSIFIER =====
        adapted = self._add_intensifiers(adapted, level)
        
        # ===== 5. SESUAIKAN EKSPRESI EMOSI =====
        if context and context.get('mood'):
            mood = context['mood']
            adapted = self._adapt_emotion_expressions(adapted, mood, level)
        
        # ===== 6. TAMBAH EKSPRESI CINTA UNTUK LEVEL TINGGI =====
        if level in [LanguageLevel.INTIMATE, LanguageLevel.DEEP_INTIMATE]:
            if random.random() < 0.3:  # 30% chance
                adapted = self._add_love_expression(adapted, level)
        
        return adapted
    
    # =========================================================================
    # PANGGILAN
    # =========================================================================
    
    def _get_user_call(self, level: LanguageLevel, user_name: str) -> str:
        """Dapatkan panggilan untuk user"""
        calls = self.user_calls.get(level, self.user_calls[LanguageLevel.FORMAL])
        call = random.choice(calls)
        return call.replace('{user_name}', user_name)
    
    def _get_self_call(self, level: LanguageLevel, bot_name: str) -> str:
        """Dapatkan panggilan bot untuk diri sendiri"""
        calls = self.self_calls.get(level, self.self_calls[LanguageLevel.FORMAL])
        call = random.choice(calls)
        return call.replace('{bot_name}', bot_name)
    
    def _replace_calls(self, text: str, call: str, user_name: str) -> str:
        """Ganti panggilan user dalam teks"""
        # Ganti pola umum
        text = text.replace('kamu', call)
        text = text.replace('Kamu', call.capitalize())
        text = text.replace(user_name.lower(), call)
        text = text.replace(user_name, call)
        return text
    
    def _replace_self_calls(self, text: str, self_call: str, bot_name: str) -> str:
        """Ganti panggilan diri dalam teks"""
        text = text.replace('aku', self_call)
        text = text.replace('Aku', self_call.capitalize())
        text = text.replace(bot_name, self_call)
        return text
    
    # =========================================================================
    # BAHASA GAUL
    # =========================================================================
    
    def _add_slang(self, text: str, level: LanguageLevel) -> str:
        """Tambah kata gaul ke teks"""
        slang_list = self.slang_words.get(level, [])
        if not slang_list:
            return text
        
        words = text.split()
        if len(words) < 5:
            return text
        
        # Tambah slang di beberapa posisi
        for i in range(len(words) - 1):
            if random.random() < 0.1:  # 10% chance per kata
                if i < len(words) - 2:
                    words.insert(i+1, random.choice(slang_list))
                    break
        
        return ' '.join(words)
    
    # =========================================================================
    # INTENSIFIER
    # =========================================================================
    
    def _add_intensifiers(self, text: str, level: LanguageLevel) -> str:
        """Tambah kata penguat (banget, sangat, dll)"""
        intensifiers = self.intensifiers.get(level, [])
        if not intensifiers:
            return text
        
        # Cari kata sifat yang bisa diperkuat
        adjectives = ['senang', 'sedih', 'marah', 'cantik', 'ganteng', 'baik', 
                     'manis', 'sayang', 'rindu', 'kangen', 'capek', 'lelah']
        
        for adj in adjectives:
            if adj in text.lower():
                if random.random() < 0.4:  # 40% chance
                    intensifier = random.choice(intensifiers)
                    text = text.replace(adj, f"{adj} {intensifier}", 1)
                    break
        
        return text
    
    # =========================================================================
    # EKSPRESI EMOSI
    # =========================================================================
    
    def _adapt_emotion_expressions(self, text: str, mood: str, level: LanguageLevel) -> str:
        """Sesuaikan ekspresi emosi dengan level"""
        if mood not in self.emotion_expressions:
            return text
        
        mood_expr = self.emotion_expressions[mood]
        if level not in mood_expr:
            return text
        
        target_expr = random.choice(mood_expr[level])
        
        # Ganti ekspresi emosi yang umum
        common_expressions = {
            'senang': ['senang', 'bahagia', 'happy', 'seneng'],
            'sedih': ['sedih', 'kecewa', 'sad'],
            'marah': ['marah', 'kesal', 'betek'],
            'cemburu': ['cemburu', 'iri']
        }
        
        if mood in common_expressions:
            for expr in common_expressions[mood]:
                if expr in text.lower():
                    text = text.replace(expr, target_expr, 1)
                    break
        
        return text
    
    # =========================================================================
    # EKSPRESI CINTA
    # =========================================================================
    
    def _add_love_expression(self, text: str, level: LanguageLevel) -> str:
        """Tambah ekspresi cinta untuk level tinggi"""
        expressions = self.love_expressions.get(level, [])
        if not expressions:
            return text
        
        expr = random.choice(expressions)
        
        # Tambah di akhir kalimat
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        text += f" {expr.capitalize()}."
        
        return text
    
    # =========================================================================
    # GET STYLE INSTRUCTION FOR PROMPT
    # =========================================================================
    
    def get_style_instruction(self, intimacy_level: int) -> str:
        """Dapatkan instruksi gaya bahasa untuk prompt builder"""
        level = self.get_language_level(intimacy_level)
        
        instructions = {
            LanguageLevel.FORMAL: (
                "Gunakan bahasa yang sopan dan formal. "
                "Panggil user dengan nama atau panggilan hormat (Kak/Mas/Mbak)."
            ),
            LanguageLevel.CASUAL: (
                "Gunakan bahasa santai seperti teman. "
                "Boleh pake kata 'nih', 'tuh', 'sih', 'deh'. "
                "Panggil user dengan nama atau panggilan akrab."
            ),
            LanguageLevel.INTIMATE: (
                "Gunakan bahasa yang sangat santai dan intim. "
                "Panggil user dengan 'sayang', 'cinta'. "
                "Boleh pake bahasa gaul dan ekspresi sayang."
            ),
            LanguageLevel.DEEP_INTIMATE: (
                "Gunakan bahasa yang sangat intim dan penuh cinta. "
                "Panggil user dengan panggilan sayang yang mesra. "
                "Ekspresikan cinta dengan lebih terbuka."
            )
        }
        
        return instructions.get(level, instructions[LanguageLevel.FORMAL])
    
    # =========================================================================
    # FORMAT GREETING & CLOSING
    # =========================================================================
    
    def get_greeting(self, intimacy_level: int, user_name: str, time_of_day: str = "") -> str:
        """Dapatkan sapaan sesuai level"""
        level = self.get_language_level(intimacy_level)
        greetings = self.greetings.get(level, self.greetings[LanguageLevel.FORMAL])
        
        greeting = random.choice(greetings)
        greeting = greeting.replace('{time_of_day}', time_of_day)
        greeting = greeting.replace('{call}', self._get_user_call(level, user_name))
        greeting = greeting.replace('{user_name}', user_name)
        
        return greeting
    
    def get_closing(self, intimacy_level: int, user_name: str) -> str:
        """Dapatkan penutup sesuai level"""
        level = self.get_language_level(intimacy_level)
        closings = self.closings.get(level, self.closings[LanguageLevel.FORMAL])
        
        closing = random.choice(closings)
        closing = closing.replace('{user_name}', user_name)
        closing = closing.replace('{call}', self._get_user_call(level, user_name))
        
        return closing
    
    # =========================================================================
    # FORMAT UNTUK DEBUG
    # =========================================================================
    
    def format_style_info(self, intimacy_level: int) -> str:
        """Format info gaya bahasa untuk debugging"""
        level = self.get_language_level(intimacy_level)
        
        lines = [
            f"📝 **Language Style:** {level.value}",
            f"📊 **Level Intimacy:** {intimacy_level}/12",
            f"👤 **Panggilan User:** {self._get_user_call(level, 'User')}",
            f"🤖 **Panggilan Diri:** {self._get_self_call(level, 'Bot')}",
        ]
        
        return "\n".join(lines)


__all__ = ['LanguageStyle', 'LanguageLevel']
