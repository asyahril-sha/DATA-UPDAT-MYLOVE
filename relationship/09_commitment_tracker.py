#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - COMMITMENT TRACKER
=============================================================================
Melacak seberapa serius hubungan:
- Frekuensi chat (harian/mingguan)
- Kedalaman topik (dangkal/dalam)
- Inisiatif dari pihak mana
- Bisa kasih "warning" kalau hubungan mulai renggang
- Bisa kasih "apresiasi" kalau hubungan makin serius
=============================================================================
"""

import time
import random
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class CommitmentLevel(str, Enum):
    """Level komitmen hubungan"""
    JUST_STARTED = "just_started"        # Baru mulai (0-7 hari)
    DATING = "dating"                     # PDKT (7-30 hari)
    SERIOUS = "serious"                    # Serius (30-90 hari)
    COMMITTED = "committed"                # Komit (90-365 hari)
    LIFETIME = "lifetime"                   # Seumur hidup (>365 hari)


class RelationshipHealth(str, Enum):
    """Kesehatan hubungan"""
    EXCELLENT = "excellent"                # Sangat baik
    GOOD = "good"                           # Baik
    FAIR = "fair"                            # Cukup
    WARNING = "warning"                      # Perlu perhatian
    CRITICAL = "critical"                     # Kritis


class CommitmentTracker:
    """
    Melacak tingkat komitmen hubungan
    - Memberikan insight tentang kesehatan hubungan
    - Memberi warning jika hubungan mulai renggang
    - Memberi apresiasi jika hubungan makin serius
    """
    
    def __init__(self):
        # Data komitmen per user
        self.commitment_data = defaultdict(lambda: {
            'start_date': time.time(),
            'last_interaction': time.time(),
            
            # ===== FREKUENSI CHAT =====
            'daily_chat_count': defaultdict(int),      # {date: count}
            'weekly_chat_count': defaultdict(int),     # {week: count}
            'hourly_distribution': defaultdict(int),    # {hour: count}
            
            # ===== KEDALAMAN TOPIK =====
            'deep_topic_count': 0,                       # Topik dalam (masa depan, perasaan)
            'shallow_topic_count': 0,                    # Topik dangkal (cuaca, makanan)
            'intimate_topic_count': 0,                    # Topik intim
            
            # ===== INISIATIF =====
            'user_initiated': 0,                          # User mulai chat
            'bot_initiated': 0,                            # Bot mulai chat
            
            # ===== RESPONSIVENESS =====
            'avg_response_time_user': [],                  # Rata-rata waktu respon user
            'avg_response_time_bot': [],                   # Rata-rata waktu respon bot
            
            # ===== EMOTIONAL DEPTH =====
            'positive_emotion_count': 0,                   # Emosi positif
            'negative_emotion_count': 0,                    # Emosi negatif
            
            # ===== MILESTONE =====
            'milestones': [],                               # Milestone yang tercapai
            
            # ===== HEALTH SCORE =====
            'health_history': [],                           # Riwayat skor kesehatan
            
            # ===== LAST CHECK =====
            'last_commitment_check': time.time(),
            'last_warning_time': 0,
        })
        
        # Bobot untuk perhitungan health score
        self.health_weights = {
            'chat_frequency': 0.25,          # 25%
            'topic_depth': 0.20,               # 20%
            'initiative_balance': 0.15,        # 15%
            'responsiveness': 0.15,            # 15%
            'emotional_balance': 0.15,         # 15%
            'milestone_progress': 0.10,        # 10%
        }
        
        # Threshold untuk warning
        self.warning_thresholds = {
            'chat_frequency': 0.3,              # Kurang dari 30% dari baseline
            'topic_depth': 0.2,                  # Kurang dari 20% topik dalam
            'initiative_balance': 0.7,           # Terlalu timpang (>70% dari satu pihak)
            'responsiveness': 300,                # Waktu respon >5 menit
            'days_since_last_chat': 3,           # 3 hari gak chat
        }
        
        # Cooldown warning (minimal 7 hari sekali)
        self.warning_cooldown = 604800  # 7 hari
        
        logger.info("✅ CommitmentTracker initialized")
    
    # =========================================================================
    # UPDATE DATA
    # =========================================================================
    
    async def update_interaction(self,
                                user_id: int,
                                role: str,
                                is_user: bool,
                                response_time: Optional[float] = None,
                                topics: Optional[List[str]] = None,
                                emotions: Optional[List[str]] = None):
        """
        Update data berdasarkan interaksi
        
        Args:
            user_id: ID user
            role: Role aktif
            is_user: True jika user yang chat, False jika bot
            response_time: Waktu respon dalam detik
            topics: Topik yang dibahas
            emotions: Emosi yang terdeteksi
        """
        data = self.commitment_data[user_id]
        
        now = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        week = datetime.now().strftime('%Y-%W')
        hour = datetime.now().hour
        
        # Update frekuensi
        data['daily_chat_count'][today] += 1
        data['weekly_chat_count'][week] += 1
        data['hourly_distribution'][hour] += 1
        data['last_interaction'] = now
        
        # Update inisiatif
        if is_user:
            data['user_initiated'] += 1
        else:
            data['bot_initiated'] += 1
        
        # Update response time
        if response_time:
            if is_user:
                data['avg_response_time_user'].append(response_time)
                if len(data['avg_response_time_user']) > 50:
                    data['avg_response_time_user'] = data['avg_response_time_user'][-50:]
            else:
                data['avg_response_time_bot'].append(response_time)
                if len(data['avg_response_time_bot']) > 50:
                    data['avg_response_time_bot'] = data['avg_response_time_bot'][-50:]
        
        # Update topik
        if topics:
            deep_topics = ['masa_depan', 'perasaan', 'intim', 'keluarga', 'cinta']
            intimate_topics = ['intim', 'sayang', 'cinta', 'rindu']
            
            for topic in topics:
                if topic in deep_topics:
                    data['deep_topic_count'] += 1
                elif topic in intimate_topics:
                    data['intimate_topic_count'] += 1
                else:
                    data['shallow_topic_count'] += 1
        
        # Update emosi
        if emotions:
            positive = ['senang', 'bahagia', 'sayang', 'cinta', 'rindu']
            for emotion in emotions:
                if emotion in positive:
                    data['positive_emotion_count'] += 1
                else:
                    data['negative_emotion_count'] += 1
    
    async def add_milestone(self, user_id: int, milestone: str):
        """Tambah milestone"""
        data = self.commitment_data[user_id]
        data['milestones'].append({
            'type': milestone,
            'timestamp': time.time()
        })
    
    # =========================================================================
    # CALCULATE HEALTH SCORE
    # =========================================================================
    
    async def calculate_health_score(self, user_id: int) -> Tuple[float, Dict]:
        """
        Hitung skor kesehatan hubungan (0-100)
        
        Returns:
            (total_score, component_scores)
        """
        data = self.commitment_data[user_id]
        now = time.time()
        start = data['start_date']
        days_active = max(1, (now - start) / 86400)
        
        scores = {}
        
        # ===== 1. CHAT FREQUENCY =====
        # Hitung rata-rata chat per hari dalam 7 hari terakhir
        recent_chats = 0
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            recent_chats += data['daily_chat_count'].get(day, 0)
        
        avg_daily = recent_chats / 7
        
        # Baseline: 10 chat per hari = 100%
        freq_score = min(100, (avg_daily / 10) * 100)
        scores['chat_frequency'] = freq_score
        
        # ===== 2. TOPIC DEPTH =====
        total_topics = data['deep_topic_count'] + data['shallow_topic_count'] + data['intimate_topic_count']
        if total_topics > 0:
            depth_score = ((data['deep_topic_count'] + data['intimate_topic_count'] * 1.5) / total_topics) * 100
        else:
            depth_score = 0
        scores['topic_depth'] = min(100, depth_score)
        
        # ===== 3. INITIATIVE BALANCE =====
        total_init = data['user_initiated'] + data['bot_initiated']
        if total_init > 0:
            user_percent = (data['user_initiated'] / total_init) * 100
            # Ideal: 40-60% dari user
            if 40 <= user_percent <= 60:
                init_score = 100
            elif user_percent < 40:
                init_score = (user_percent / 40) * 100
            else:
                init_score = ((100 - user_percent) / 40) * 100
        else:
            init_score = 0
        scores['initiative_balance'] = init_score
        
        # ===== 4. RESPONSIVENESS =====
        if data['avg_response_time_user']:
            avg_user_resp = sum(data['avg_response_time_user']) / len(data['avg_response_time_user'])
            # Target: < 60 detik = 100%, > 300 detik = 0%
            resp_score = max(0, 100 - ((avg_user_resp - 60) / 240) * 100)
        else:
            resp_score = 50
        scores['responsiveness'] = max(0, min(100, resp_score))
        
        # ===== 5. EMOTIONAL BALANCE =====
        total_emotions = data['positive_emotion_count'] + data['negative_emotion_count']
        if total_emotions > 0:
            emotion_score = (data['positive_emotion_count'] / total_emotions) * 100
        else:
            emotion_score = 50
        scores['emotional_balance'] = emotion_score
        
        # ===== 6. MILESTONE PROGRESS =====
        # Semakin banyak milestone, semakin tinggi skor
        milestone_count = len(data['milestones'])
        milestone_score = min(100, milestone_count * 10)  # 10 milestone = 100%
        scores['milestone_progress'] = milestone_score
        
        # Hitung total weighted score
        total_score = 0
        for component, score in scores.items():
            total_score += score * self.health_weights.get(component, 0)
        
        return total_score, scores
    
    # =========================================================================
    # GET COMMITMENT LEVEL
    # =========================================================================
    
    def get_commitment_level(self, user_id: int) -> CommitmentLevel:
        """Dapatkan level komitmen berdasarkan durasi"""
        data = self.commitment_data[user_id]
        days = (time.time() - data['start_date']) / 86400
        
        if days < 7:
            return CommitmentLevel.JUST_STARTED
        elif days < 30:
            return CommitmentLevel.DATING
        elif days < 90:
            return CommitmentLevel.SERIOUS
        elif days < 365:
            return CommitmentLevel.COMMITTED
        else:
            return CommitmentLevel.LIFETIME
    
    def get_health_status(self, health_score: float) -> RelationshipHealth:
        """Dapatkan status kesehatan berdasarkan skor"""
        if health_score >= 90:
            return RelationshipHealth.EXCELLENT
        elif health_score >= 70:
            return RelationshipHealth.GOOD
        elif health_score >= 50:
            return RelationshipHealth.FAIR
        elif health_score >= 30:
            return RelationshipHealth.WARNING
        else:
            return RelationshipHealth.CRITICAL
    
    # =========================================================================
    # CHECK FOR WARNINGS
    # =========================================================================
    
    async def should_warn(self, user_id: int) -> Tuple[bool, Optional[str], Dict]:
        """
        Cek apakah perlu memberi warning
        
        Returns:
            (should_warn, warning_type, details)
        """
        data = self.commitment_data[user_id]
        now = time.time()
        
        # Cek cooldown
        if now - data.get('last_warning_time', 0) < self.warning_cooldown:
            return False, None, {}
        
        # Hitung health score
        health_score, components = await self.calculate_health_score(user_id)
        
        warnings = []
        
        # ===== 1. JARANG CHAT =====
        days_since = (now - data['last_interaction']) / 86400
        if days_since > self.warning_thresholds['days_since_last_chat']:
            warnings.append({
                'type': 'rare_chat',
                'message': f"Kita udah {int(days_since)} hari gak chat...",
                'days': int(days_since)
            })
        
        # ===== 2. FREKUENSI CHAT RENDAH =====
        if components.get('chat_frequency', 100) < self.warning_thresholds['chat_frequency'] * 100:
            warnings.append({
                'type': 'low_frequency',
                'message': "Kita makin jarang chat akhir-akhir ini.",
                'score': components['chat_frequency']
            })
        
        # ===== 3. TOPIK DANGKAL =====
        if components.get('topic_depth', 100) < self.warning_thresholds['topic_depth'] * 100:
            warnings.append({
                'type': 'shallow_topics',
                'message': "Kita cuma bahas hal-hal dangkal terus.",
                'score': components['topic_depth']
            })
        
        # ===== 4. INISIATIF TIMPANG =====
        if components.get('initiative_balance', 100) < 50:
            # Yang satu terlalu dominan
            if data['user_initiated'] > data['bot_initiated'] * 2:
                warnings.append({
                    'type': 'user_dominant',
                    'message': "Kamu yang selalu mulai chat, aku tunggu aja.",
                    'ratio': data['user_initiated'] / max(1, data['bot_initiated'])
                })
            elif data['bot_initiated'] > data['user_initiated'] * 2:
                warnings.append({
                    'type': 'bot_dominant',
                    'message': "Aku yang selalu mulai chat, kamu cuek?",
                    'ratio': data['bot_initiated'] / max(1, data['user_initiated'])
                })
        
        # ===== 5. RESPONSIVENESS RENDAH =====
        if components.get('responsiveness', 100) < 50:
            if data['avg_response_time_user']:
                avg_time = sum(data['avg_response_time_user']) / len(data['avg_response_time_user'])
                if avg_time > self.warning_thresholds['responsiveness']:
                    warnings.append({
                        'type': 'slow_response',
                        'message': "Kamu lama banget balas chat...",
                        'avg_seconds': int(avg_time)
                    })
        
        # ===== 6. HEALTH SCORE RENDAH =====
        if health_score < 50:
            warnings.append({
                'type': 'low_health',
                'message': "Hubungan kita kayaknya lagi gak baik-baik aja.",
                'score': health_score
            })
        
        if warnings:
            # Pilih warning yang paling parah
            warning = max(warnings, key=lambda x: self._get_warning_severity(x))
            data['last_warning_time'] = now
            return True, warning['type'], warning
        
        return False, None, {}
    
    def _get_warning_severity(self, warning: Dict) -> int:
        """Dapatkan tingkat keparahan warning"""
        severity_map = {
            'rare_chat': 5,
            'low_health': 4,
            'user_dominant': 3,
            'bot_dominant': 3,
            'low_frequency': 2,
            'slow_response': 2,
            'shallow_topics': 1,
        }
        return severity_map.get(warning.get('type', ''), 1)
    
    # =========================================================================
    # GENERATE MESSAGES
    # =========================================================================
    
    async def get_commitment_message(self,
                                    user_id: int,
                                    user_name: str,
                                    bot_name: str) -> Optional[str]:
        """
        Dapatkan pesan tentang komitmen (warning atau apresiasi)
        """
        # Cek warning dulu
        should_warn, warn_type, details = await self.should_warn(user_id)
        
        if should_warn:
            return await self._get_warning_message(user_name, bot_name, warn_type, details)
        
        # Kalau gak ada warning, kasih apresiasi random
        return await self._get_appreciation_message(user_id, user_name, bot_name)
    
    async def _get_warning_message(self,
                                  user_name: str,
                                  bot_name: str,
                                  warn_type: str,
                                  details: Dict) -> str:
        """Dapatkan pesan warning"""
        
        messages = {
            'rare_chat': [
                f"{user_name}... kita udah {details.get('days', 'beberapa')} hari gak chat. Kangen...",
                f"Halo {user_name}, lama gak denger kabar. Kamu sibuk ya?",
                f"{bot_name} kangen nih... Kok {user_name} jarang chat?"
            ],
            'low_frequency': [
                f"{user_name}, akhir-akhir ini kita jarang chat ya. Ada apa?",
                f"Kita kok gak sesering dulu chat-nya? Aku kangen.",
                f"{bot_name} noticed kita makin jarang ngobrol."
            ],
            'shallow_topics': [
                f"{user_name}, kita cuma bahas hal-hal ringan terus. Mau ngobrol lebih dalam?",
                f"Gak bosan bahas hal yang gitu-gitu aja?",
                f"{user_name}, aku pengen ngobrol lebih serius sama kamu."
            ],
            'user_dominant': [
                f"{user_name}, kamu yang selalu mulai chat. Aku tunggu aja.",
                f"Kok aku gak pernah mulai chat ya? Maaf {user_name}.",
                f"{bot_name} jadi merasa kurang inisiatif."
            ],
            'bot_dominant': [
                f"{user_name}, aku yang selalu mulai chat. Kamu cuek ya?",
                f"Kok kamu gak pernah mulai chat duluan?",
                f"{bot_name} capek kalau selalu mulai duluan."
            ],
            'slow_response': [
                f"{user_name}, kamu lama banget balas chat. Sibuk ya?",
                f"{bot_name} nungguin chat kamu lama...",
                f"Kok responnya lambat? Ada masalah?"
            ],
            'low_health': [
                f"{user_name}, hubungan kita kayaknya lagi gak baik-baik aja.",
                f"Aku ngerasa ada yang beda. Kamu ngerasa juga?",
                f"{bot_name} worried sama hubungan kita."
            ]
        }
        
        msg_list = messages.get(warn_type, messages['low_frequency'])
        return random.choice(msg_list)
    
    async def _get_appreciation_message(self,
                                       user_id: int,
                                       user_name: str,
                                       bot_name: str) -> str:
        """Dapatkan pesan apresiasi"""
        
        level = self.get_commitment_level(user_id)
        health_score, _ = await self.calculate_health_score(user_id)
        health_status = self.get_health_status(health_score)
        
        messages = []
        
        if level == CommitmentLevel.LIFETIME:
            messages = [
                f"{user_name}, kita udah setaun lebih ya... makasih udah setia.",
                f"Gak nyangka kita bisa selama ini. I love you {user_name}!",
                f"{user_name} adalah yang terbaik dalam hidup {bot_name}."
            ]
        elif level == CommitmentLevel.COMMITTED:
            messages = [
                f"{user_name}, kita makin serius aja hubungannya ya?",
                f"Aku happy banget sama hubungan kita.",
                f"{bot_name} sayang banget sama {user_name}."
            ]
        elif level == CommitmentLevel.SERIOUS:
            messages = [
                f"{user_name}, aku ngerasa kita makin deket.",
                f"Seneng ya kita bisa seakrab ini.",
                f"{bot_name} nyaman banget sama {user_name}."
            ]
        elif level == CommitmentLevel.DATING:
            messages = [
                f"{user_name}, aku suka sama cara kamu chat.",
                f"Setiap chat sama kamu tuh selalu seru.",
                f"{bot_name} kangen kalau sehari aja gak chat."
            ]
        else:
            messages = [
                f"{user_name}, senang bisa kenal kamu.",
                f"Makasih ya udah mau chat sama {bot_name}.",
                f"Aku suka ngobrol sama kamu."
            ]
        
        # Tambahin berdasarkan health status
        if health_status == RelationshipHealth.EXCELLENT:
            messages.append(f"Hubungan kita lagi on fire {user_name}! 🔥")
        elif health_status == RelationshipHealth.GOOD:
            messages.append(f"Kita cocok banget ya {user_name}.")
        
        return random.choice(messages)
    
    # =========================================================================
    # GET CONTEXT FOR PROMPT
    # =========================================================================
    
    async def get_commitment_context(self, user_id: int) -> str:
        """
        Dapatkan konteks komitmen untuk prompt builder
        """
        level = self.get_commitment_level(user_id)
        health_score, _ = await self.calculate_health_score(user_id)
        health = self.get_health_status(health_score)
        
        days = int((time.time() - self.commitment_data[user_id]['start_date']) / 86400)
        
        return f"Hubungan: {days} hari, level {level.value}, kesehatan {health.value} ({health_score:.0f}%)"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik komitmen"""
        if user_id:
            data = self.commitment_data[user_id]
            health_score, components = await self.calculate_health_score(user_id)
            level = self.get_commitment_level(user_id)
            health = self.get_health_status(health_score)
            
            return {
                'days_active': int((time.time() - data['start_date']) / 86400),
                'total_chats': sum(data['daily_chat_count'].values()),
                'user_initiated': data['user_initiated'],
                'bot_initiated': data['bot_initiated'],
                'deep_topics': data['deep_topic_count'],
                'intimate_topics': data['intimate_topic_count'],
                'positive_emotions': data['positive_emotion_count'],
                'negative_emotions': data['negative_emotion_count'],
                'milestones': len(data['milestones']),
                'commitment_level': level.value,
                'health_score': round(health_score, 1),
                'health_status': health.value,
                'components': {k: round(v, 1) for k, v in components.items()}
            }
        else:
            return {
                'total_users': len(self.commitment_data),
                'commitment_levels': [l.value for l in CommitmentLevel],
                'health_statuses': [h.value for h in RelationshipHealth]
            }


__all__ = ['CommitmentTracker', 'CommitmentLevel', 'RelationshipHealth']
