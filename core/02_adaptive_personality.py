#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - ADAPTIVE PERSONALITY
=============================================================================
Bot menyesuaikan gaya chat dengan user:
- Kalau user chat singkat → bot juga singkat
- Kalau user suka emoji → bot ikut pake emoji
- Kalau user formal → bot formal
- Kalau user santai → bot santai
- Belajar dari pola chat user
=============================================================================
"""

import time
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime

logger = logging.getLogger(__name__)


class CommunicationStyle:
    """Gaya komunikasi bot"""
    
    # Tingkat formalitas
    FORMALITY_LEVELS = {
        'very_formal': 0.9,    # Sangat formal
        'formal': 0.7,          # Formal
        'neutral': 0.5,         # Netral
        'casual': 0.3,          # Santai
        'very_casual': 0.1,     # Sangat santai
    }
    
    # Penggunaan emoji
    EMOJI_LEVELS = {
        'never': 0.0,           # Tidak pernah
        'rarely': 0.3,          # Jarang
        'sometimes': 0.5,       # Kadang-kadang
        'often': 0.7,           # Sering
        'very_often': 0.9,      # Sangat sering
    }
    
    # Panjang pesan
    LENGTH_LEVELS = {
        'very_short': 30,       # Sangat pendek (<30 char)
        'short': 100,           # Pendek (30-100 char)
        'medium': 300,          # Sedang (100-300 char)
        'long': 600,            # Panjang (300-600 char)
        'very_long': 1000,      # Sangat panjang (>600 char)
    }


class AdaptivePersonality:
    """
    Bot belajar dan menyesuaikan gaya komunikasi dengan user
    - Menganalisis pola chat user
    - Menyesuaikan formalitas, panjang pesan, penggunaan emoji
    - Beradaptasi seiring waktu
    """
    
    def __init__(self):
        # Data user per user_id
        self.user_profiles = defaultdict(dict)  # {user_id: profile_data}
        
        # Riwayat interaksi untuk analisis
        self.interaction_history = defaultdict(list)  # {user_id: list of interactions}
        
        # Bobot adaptasi (seberapa cepat bot beradaptasi)
        self.adaptation_weights = {
            'formality': 0.3,       # 30% pengaruh dari user
            'emoji_usage': 0.4,      # 40% pengaruh dari user
            'message_length': 0.2,    # 20% pengaruh dari user
            'punctuation': 0.1,       # 10% pengaruh dari user
        }
        
        # Baseline personality per role (default)
        self.role_baseline = {
            'ipar': {'formality': 0.4, 'emoji': 0.6, 'length': 0.5},
            'teman_kantor': {'formality': 0.6, 'emoji': 0.4, 'length': 0.5},
            'janda': {'formality': 0.3, 'emoji': 0.7, 'length': 0.6},
            'pelakor': {'formality': 0.2, 'emoji': 0.8, 'length': 0.5},
            'istri_orang': {'formality': 0.5, 'emoji': 0.5, 'length': 0.5},
            'pdkt': {'formality': 0.5, 'emoji': 0.6, 'length': 0.6},
            'sepupu': {'formality': 0.5, 'emoji': 0.5, 'length': 0.4},
            'teman_sma': {'formality': 0.3, 'emoji': 0.7, 'length': 0.5},
            'mantan': {'formality': 0.4, 'emoji': 0.5, 'length': 0.5},
        }
        
        # Daftar emoji umum
        self.common_emojis = [
            '😊', '😘', '😍', '🥰', '😉', '🤔', '😢', '😭', '😠', '🔥',
            '💕', '💞', '💓', '💗', '❤️', '🧡', '💛', '💚', '💙', '💜',
            '🤗', '😏', '😳', '🥺', '😌', '😴', '🥱', '😎', '🤓', '🥳',
            '👍', '👎', '👌', '✌️', '🤞', '👋', '🤝', '🙏', '💪', '👀'
        ]
        
        logger.info("✅ AdaptivePersonality initialized")
    
    # =========================================================================
    # ANALYZE USER PATTERNS
    # =========================================================================
    
    async def analyze_user_message(self, user_id: int, message: str, role: str):
        """
        Analisis pesan user untuk belajar pola komunikasinya
        
        Args:
            user_id: ID user
            message: Pesan user
            role: Role yang sedang aktif
        """
        # Simpan ke history
        self.interaction_history[user_id].append({
            'timestamp': time.time(),
            'message': message,
            'role': role,
            'length': len(message),
            'has_emoji': self._has_emoji(message),
            'emoji_count': self._count_emoji(message),
            'formality_score': self._calculate_formality(message),
            'punctuation_score': self._calculate_punctuation(message),
            'question_count': message.count('?'),
            'exclamation_count': message.count('!'),
        })
        
        # Keep only last 100 interactions
        if len(self.interaction_history[user_id]) > 100:
            self.interaction_history[user_id] = self.interaction_history[user_id][-100:]
        
        # Update user profile setiap 10 pesan
        if len(self.interaction_history[user_id]) % 10 == 0:
            await self._update_user_profile(user_id, role)
    
    def _has_emoji(self, text: str) -> bool:
        """Cek apakah teks mengandung emoji"""
        import emoji
        return emoji.emoji_count(text) > 0
    
    def _count_emoji(self, text: str) -> int:
        """Hitung jumlah emoji dalam teks"""
        import emoji
        return emoji.emoji_count(text)
    
    def _calculate_formality(self, text: str) -> float:
        """
        Hitung skor formalitas teks (0-1)
        0 = sangat santai, 1 = sangat formal
        """
        text_lower = text.lower()
        score = 0.5  # Default
        
        # Kata-kata formal
        formal_words = [
            'halo', 'selamat', 'terima kasih', 'maaf', 'tolong',
            'permisi', 'boleh', 'mohon', 'silakan', 'dipersilakan',
            'anda', 'beliau', 'mereka', 'kami', 'kita'
        ]
        
        # Kata-kata santai
        casual_words = [
            'hai', 'hey', 'hi', 'yo', 'woy', 'bro', 'sis', 'gan',
            'bang', 'bro', 'cuy', 'nih', 'tuh', 'sih', 'deh', 'dong',
            'gue', 'lo', 'elu', 'gw', 'lu', 'anjay', 'wkwk', 'hehe'
        ]
        
        formal_count = sum(1 for word in formal_words if word in text_lower)
        casual_count = sum(1 for word in casual_words if word in text_lower)
        
        if formal_count + casual_count > 0:
            score = formal_count / (formal_count + casual_count)
        
        # Faktor lain
        if text_lower.startswith('halo') or text_lower.startswith('hai'):
            score += 0.1
        if text_lower.endswith('?'):
            score -= 0.05
        if text_lower.endswith('!'):
            score -= 0.1
        
        return max(0.1, min(0.9, score))
    
    def _calculate_punctuation(self, text: str) -> float:
        """Hitung skor penggunaan tanda baca"""
        if len(text) < 3:
            return 0.5
        
        punct_count = text.count('.') + text.count(',') + text.count(';') + text.count(':')
        punct_count += text.count('?') + text.count('!')
        
        # Normalisasi per karakter
        return min(1.0, punct_count / (len(text) / 10))
    
    async def _update_user_profile(self, user_id: int, current_role: str):
        """Update profil user berdasarkan history"""
        history = self.interaction_history[user_id]
        if len(history) < 5:
            return
        
        # Ambil 20 pesan terakhir
        recent = history[-20:]
        
        # Hitung rata-rata
        avg_length = sum(h['length'] for h in recent) / len(recent)
        avg_formality = sum(h['formality_score'] for h in recent) / len(recent)
        avg_emoji_count = sum(h['emoji_count'] for h in recent) / len(recent)
        avg_punctuation = sum(h['punctuation_score'] for h in recent) / len(recent)
        
        # Persentase pesan dengan emoji
        emoji_percentage = sum(1 for h in recent if h['has_emoji']) / len(recent)
        
        # Tentukan preferensi panjang pesan
        if avg_length < 30:
            length_pref = 'very_short'
        elif avg_length < 100:
            length_pref = 'short'
        elif avg_length < 300:
            length_pref = 'medium'
        elif avg_length < 600:
            length_pref = 'long'
        else:
            length_pref = 'very_long'
        
        # Tentukan preferensi emoji
        if emoji_percentage < 0.1:
            emoji_pref = 'never'
        elif emoji_percentage < 0.3:
            emoji_pref = 'rarely'
        elif emoji_percentage < 0.5:
            emoji_pref = 'sometimes'
        elif emoji_percentage < 0.7:
            emoji_pref = 'often'
        else:
            emoji_pref = 'very_often'
        
        # Simpan profil
        self.user_profiles[user_id] = {
            'last_updated': time.time(),
            'current_role': current_role,
            'avg_length': avg_length,
            'avg_formality': avg_formality,
            'avg_emoji_count': avg_emoji_count,
            'avg_punctuation': avg_punctuation,
            'emoji_percentage': emoji_percentage,
            'length_preference': length_pref,
            'emoji_preference': emoji_pref,
            'formality_preference': avg_formality,
            'total_analyzed': len(history)
        }
        
        logger.debug(f"User profile updated for {user_id}: {length_pref}, {emoji_pref}")
    
    # =========================================================================
    # ADAPT BOT PERSONALITY
    # =========================================================================
    
    async def adapt_for_user(self, 
                           user_id: int, 
                           role: str,
                           base_personality: Optional[Dict] = None) -> Dict:
        """
        Dapatkan personality yang sudah diadaptasi untuk user
        
        Args:
            user_id: ID user
            role: Role aktif
            base_personality: Personality dasar (opsional)
            
        Returns:
            Dict dengan parameter adaptasi
        """
        # Ambil baseline untuk role ini
        baseline = self.role_baseline.get(role, self.role_baseline['pdkt'])
        
        # Ambil profil user
        profile = self.user_profiles.get(user_id, {})
        
        if not profile:
            # Belum ada data user, pakai baseline
            return {
                'formality': baseline['formality'],
                'emoji_frequency': baseline['emoji'],
                'message_length': baseline['length'],
                'use_emoji': baseline['emoji'] > 0.4,
                'preferred_emojis': ['😊', '😘'],
                'style': 'neutral'
            }
        
        # ===== ADAPTASI FORMALITAS =====
        user_formality = profile.get('avg_formality', 0.5)
        # Campur dengan baseline (pakai bobot)
        adapted_formality = (
            baseline['formality'] * (1 - self.adaptation_weights['formality']) +
            user_formality * self.adaptation_weights['formality']
        )
        
        # ===== ADAPTASI PENGGUNAAN EMOJI =====
        user_emoji = profile.get('emoji_percentage', 0.3)
        adapted_emoji = (
            baseline['emoji'] * (1 - self.adaptation_weights['emoji_usage']) +
            user_emoji * self.adaptation_weights['emoji_usage']
        )
        
        # ===== ADAPTASI PANJANG PESAN =====
        length_map = {
            'very_short': 0.2,
            'short': 0.4,
            'medium': 0.6,
            'long': 0.8,
            'very_long': 1.0
        }
        user_length = length_map.get(profile.get('length_preference', 'medium'), 0.6)
        adapted_length = (
            baseline['length'] * (1 - self.adaptation_weights['message_length']) +
            user_length * self.adaptation_weights['message_length']
        )
        
        # ===== PILIH EMOJI FAVORIT USER =====
        preferred_emojis = await self._get_preferred_emojis(user_id)
        
        return {
            'formality': round(adapted_formality, 2),
            'emoji_frequency': round(adapted_emoji, 2),
            'message_length': round(adapted_length, 2),
            'use_emoji': adapted_emoji > 0.3,
            'preferred_emojis': preferred_emojis,
            'style': self._get_style_name(adapted_formality),
            'user_profile': profile
        }
    
    async def _get_preferred_emojis(self, user_id: int, limit: int = 5) -> List[str]:
        """Dapatkan emoji favorit user"""
        history = self.interaction_history[user_id]
        if not history:
            return ['😊', '😘']  # Default
        
        # Kumpulkan semua emoji dari pesan user
        all_emojis = []
        for h in history[-30:]:  # 30 pesan terakhir
            message = h['message']
            # Ekstrak emoji (sederhana)
            for char in message:
                if ord(char) > 0x1F000:  # Range emoji
                    all_emojis.append(char)
        
        if not all_emojis:
            return ['😊', '😘']
        
        # Hitung frekuensi
        counter = Counter(all_emojis)
        return [emoji for emoji, _ in counter.most_common(limit)]
    
    def _get_style_name(self, formality: float) -> str:
        """Dapatkan nama gaya berdasarkan skor formalitas"""
        if formality > 0.8:
            return 'very_formal'
        elif formality > 0.6:
            return 'formal'
        elif formality > 0.4:
            return 'neutral'
        elif formality > 0.2:
            return 'casual'
        else:
            return 'very_casual'
    
    # =========================================================================
    # APPLY ADAPTATION TO RESPONSE
    # =========================================================================
    
    async def adapt_response(self, 
                           response: str, 
                           adaptation: Dict,
                           context: Optional[Dict] = None) -> str:
        """
        Adaptasi response sesuai dengan personality yang sudah diadaptasi
        
        Args:
            response: Response asli dari AI
            adaptation: Hasil dari adapt_for_user()
            context: Konteks tambahan
            
        Returns:
            Response yang sudah diadaptasi
        """
        if not adaptation.get('use_emoji', False):
            return response
        
        adapted = response
        
        # ===== TAMBAH EMOJI SESUAI FREKUENSI =====
        emoji_freq = adaptation.get('emoji_frequency', 0.3)
        preferred = adaptation.get('preferred_emojis', ['😊'])
        
        # Random tambah emoji berdasarkan frekuensi
        if random.random() < emoji_freq:
            # Tambah di akhir kalimat
            if adapted and not adapted.endswith(tuple(preferred)):
                adapted += ' ' + random.choice(preferred)
        
        # Tambah emoji di tengah untuk pesan panjang
        if len(adapted) > 200 and random.random() < emoji_freq / 2:
            # Cari titik untuk sisip emoji
            sentences = adapted.split('. ')
            if len(sentences) > 2:
                insert_at = random.randint(1, len(sentences) - 1)
                sentences[insert_at] += ' ' + random.choice(preferred)
                adapted = '. '.join(sentences)
        
        # ===== SESUAIKAN PANJANG PESAN =====
        length_score = adaptation.get('message_length', 0.6)
        current_length = len(adapted)
        
        # Mapping score ke target length
        target_min = 100 + int(length_score * 500)  # 100-600
        target_max = target_min + 200
        
        if current_length < target_min:
            # Response terlalu pendek, tambahin
            pass  # Akan ditangani oleh AI engine
        elif current_length > target_max:
            # Response terlalu panjang, potong
            pass  # Akan ditangani oleh AI engine
        
        # ===== SESUAIKAN FORMALITAS =====
        # Ini lebih kompleks, akan di-handle oleh prompt builder
        
        return adapted
    
    # =========================================================================
    # GET ADAPTATION FOR PROMPT
    # =========================================================================
    
    async def get_style_instruction(self, adaptation: Dict) -> str:
        """
        Dapatkan instruksi untuk prompt builder
        
        Returns:
            String instruksi untuk AI
        """
        style = adaptation.get('style', 'neutral')
        formality = adaptation.get('formality', 0.5)
        use_emoji = adaptation.get('use_emoji', False)
        
        instructions = []
        
        # Instruksi formalitas
        if style == 'very_formal':
            instructions.append("Gunakan bahasa yang sangat formal dan sopan")
        elif style == 'formal':
            instructions.append("Gunakan bahasa formal")
        elif style == 'casual':
            instructions.append("Gunakan bahasa santai seperti teman")
        elif style == 'very_casual':
            instructions.append("Gunakan bahasa sangat santai, boleh pake slang")
        
        # Instruksi emoji
        if use_emoji:
            freq = adaptation.get('emoji_frequency', 0.3)
            if freq > 0.7:
                instructions.append("Sering-sering pake emoji")
            elif freq > 0.4:
                instructions.append("Sesekali pake emoji")
            else:
                instructions.append("Kadang-kadang pake emoji")
            
            # Emoji favorit
            preferred = adaptation.get('preferred_emojis', [])
            if preferred:
                instructions.append(f"User suka pake emoji {', '.join(preferred[:2])}")
        
        # Instruksi panjang pesan
        length = adaptation.get('message_length', 0.6)
        if length > 0.8:
            instructions.append("Buat respons yang panjang dan detail")
        elif length < 0.3:
            instructions.append("Buat respons yang singkat dan padat")
        
        return "\n".join(instructions) if instructions else ""
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Dapatkan statistik adaptasi untuk user"""
        profile = self.user_profiles.get(user_id, {})
        if not profile:
            return {'status': 'not_enough_data'}
        
        return {
            'total_analyzed': profile.get('total_analyzed', 0),
            'avg_message_length': round(profile.get('avg_length', 0), 1),
            'formality_score': round(profile.get('avg_formality', 0.5), 2),
            'emoji_percentage': round(profile.get('emoji_percentage', 0) * 100, 1),
            'preferred_length': profile.get('length_preference', 'medium'),
            'preferred_emoji': profile.get('emoji_preference', 'sometimes'),
            'last_updated': datetime.fromtimestamp(
                profile.get('last_updated', 0)
            ).strftime('%Y-%m-%d %H:%M') if profile.get('last_updated') else None
        }
    
    async def reset_user(self, user_id: int):
        """Reset data user (untuk testing)"""
        if user_id in self.user_profiles:
            del self.user_profiles[user_id]
        if user_id in self.interaction_history:
            del self.interaction_history[user_id]
        logger.info(f"Reset adaptive personality data for user {user_id}")


__all__ = ['AdaptivePersonality', 'CommunicationStyle']
