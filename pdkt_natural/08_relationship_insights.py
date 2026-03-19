#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - RELATIONSHIP INSIGHTS
=============================================================================
Bot bisa kasih "insight" tentang hubungan secara natural:
- "Kita udah sebulan lebih nih PDKT"
- "Kayaknya chemistry kita makin naik"
- "Kamu makin sering chat akhir-akhir ini"
- "Kita jarang banget bahas topik intim"
=============================================================================
"""

import time
import random
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class InsightType:
    """Tipe-tipe insight"""
    ANNIVERSARY = "anniversary"           # Ulang tahun hubungan
    MILESTONE = "milestone"                # Pencapaian (first kiss, dll)
    CHEMISTRY_CHANGE = "chemistry_change"   # Perubahan chemistry
    CHAT_PATTERN = "chat_pattern"          # Pola chat (sering/jarang)
    TOPIC_TREND = "topic_trend"            # Topik yang sering dibahas
    EMOTION_TREND = "emotion_trend"        # Perubahan emosi
    INTIMACY_LEVEL = "intimacy_level"       # Level intimacy
    COMPARISON = "comparison"               # Perbandingan dengan sebelumnya
    PREDICTION = "prediction"                # Prediksi ke depan


class RelationshipInsights:
    """
    Bot memberikan insight tentang hubungan secara alami
    - Tidak seperti command, tapi muncul natural di percakapan
    - Membantu user melihat progress hubungan
    - Membuat hubungan terasa lebih "hidup"
    """
    
    def __init__(self):
        # Tracking data hubungan
        self.relationship_data = defaultdict(lambda: {
            'start_date': None,
            'first_kiss_date': None,
            'first_intim_date': None,
            'chemistry_history': [],
            'chat_frequency': [],
            'topics_discussed': defaultdict(int),
            'emotions_detected': defaultdict(int),
            'daily_chat_count': defaultdict(int),
            'weekly_chat_count': defaultdict(int),
            'last_insight_time': 0
        })
        
        # Cooldown antar insight (minimal 30 menit)
        self.insight_cooldown = 1800  # 30 menit dalam detik
        
        # Threshold untuk trigger insight
        self.thresholds = {
            'anniversary_days': [7, 30, 60, 90, 180, 365],  # Hari yang dirayakan
            'chemistry_change': 5.0,  # Perubahan chemistry minimal 5 poin
            'chat_frequency_change': 0.3,  # Perubahan frekuensi chat 30%
            'topic_count_threshold': 10,  # Topik minimal 10x muncul
            'emotion_count_threshold': 5,  # Emosi minimal 5x muncul
        }
        
        logger.info("✅ RelationshipInsights initialized")
    
    # =========================================================================
    # UPDATE DATA
    # =========================================================================
    
    async def update_relationship_data(self,
                                      user_id: int,
                                      role: str,
                                      data: Dict[str, Any]):
        """
        Update data hubungan
        
        Args:
            user_id: ID user
            role: Role yang aktif
            data: Data baru (chemistry, topics, emotions, dll)
        """
        rel_data = self.relationship_data[user_id]
        
        # Set start date if not exists
        if not rel_data['start_date']:
            rel_data['start_date'] = time.time()
        
        # Update chemistry
        if 'chemistry' in data:
            rel_data['chemistry_history'].append({
                'timestamp': time.time(),
                'value': data['chemistry'],
                'role': role
            })
            # Keep last 100
            if len(rel_data['chemistry_history']) > 100:
                rel_data['chemistry_history'] = rel_data['chemistry_history'][-100:]
        
        # Update topics
        if 'topics' in data:
            for topic in data['topics']:
                rel_data['topics_discussed'][topic] += 1
        
        # Update emotions
        if 'emotions' in data:
            for emotion in data['emotions']:
                rel_data['emotions_detected'][emotion] += 1
        
        # Update chat frequency
        today = datetime.now().strftime('%Y-%m-%d')
        rel_data['daily_chat_count'][today] = rel_data['daily_chat_count'].get(today, 0) + 1
        
        week = datetime.now().strftime('%Y-%W')
        rel_data['weekly_chat_count'][week] = rel_data['weekly_chat_count'].get(week, 0) + 1
        
        # Update chat frequency list (for trend analysis)
        rel_data['chat_frequency'].append({
            'timestamp': time.time(),
            'count': 1
        })
        if len(rel_data['chat_frequency']) > 1000:
            rel_data['chat_frequency'] = rel_data['chat_frequency'][-1000:]
    
    async def record_milestone(self,
                              user_id: int,
                              milestone_type: str,
                              timestamp: Optional[float] = None):
        """
        Rekam milestone hubungan
        
        Args:
            user_id: ID user
            milestone_type: 'first_kiss', 'first_intim', dll
            timestamp: Waktu kejadian (default now)
        """
        rel_data = self.relationship_data[user_id]
        
        if milestone_type == 'first_kiss':
            rel_data['first_kiss_date'] = timestamp or time.time()
        elif milestone_type == 'first_intim':
            rel_data['first_intim_date'] = timestamp or time.time()
    
    # =========================================================================
    # GENERATE INSIGHTS
    # =========================================================================
    
    async def should_give_insight(self, user_id: int) -> bool:
        """
        Cek apakah perlu kasih insight (cooldown check)
        """
        rel_data = self.relationship_data[user_id]
        last_insight = rel_data.get('last_insight_time', 0)
        
        return (time.time() - last_insight) > self.insight_cooldown
    
    async def generate_insight(self,
                              user_id: int,
                              user_name: str,
                              bot_name: str,
                              role: str,
                              context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Generate insight tentang hubungan
        
        Args:
            user_id: ID user
            user_name: Nama user
            bot_name: Nama bot
            role: Role aktif
            context: Konteks tambahan
            
        Returns:
            Dict insight atau None
        """
        rel_data = self.relationship_data[user_id]
        
        # Update last insight time
        rel_data['last_insight_time'] = time.time()
        
        # Cek berbagai jenis insight
        insight_checks = [
            self._check_anniversary,
            self._check_chemistry_change,
            self._check_chat_frequency,
            self._check_topics,
            self._check_emotions,
            self._check_milestone_reminder,
        ]
        
        for check_func in insight_checks:
            insight = await check_func(user_id, user_name, bot_name, role)
            if insight:
                return insight
        
        # Default insight kalau gak ada yang cocok
        return await self._get_default_insight(user_id, user_name, bot_name, role)
    
    # =========================================================================
    # ANNIVERSARY INSIGHT
    # =========================================================================
    
    async def _check_anniversary(self,
                                user_id: int,
                                user_name: str,
                                bot_name: str,
                                role: str) -> Optional[Dict]:
        """Cek apakah ada anniversary yang perlu dirayakan"""
        rel_data = self.relationship_data[user_id]
        
        if not rel_data['start_date']:
            return None
        
        start = datetime.fromtimestamp(rel_data['start_date'])
        now = datetime.now()
        days_diff = (now - start).days
        
        # Cek apakah days_diff termasuk dalam threshold anniversary
        for threshold in self.thresholds['anniversary_days']:
            if days_diff == threshold:
                message = random.choice([
                    f"{user_name}, kita udah {days_diff} hari nih sejak pertama chat! 🎉",
                    f"Eh {user_name}, hari ini tepat {days_diff} hari kita kenalan!",
                    f"Happy {days_diff} days anniversary buat kita! 🥳",
                    f"{days_diff} hari udah kita lewatin bareng. Makasih ya {user_name}!"
                ])
                
                return {
                    'type': InsightType.ANNIVERSARY,
                    'message': message,
                    'days': days_diff
                }
        
        return None
    
    # =========================================================================
    # CHEMISTRY CHANGE INSIGHT
    # =========================================================================
    
    async def _check_chemistry_change(self,
                                     user_id: int,
                                     user_name: str,
                                     bot_name: str,
                                     role: str) -> Optional[Dict]:
        """Cek perubahan chemistry signifikan"""
        rel_data = self.relationship_data[user_id]
        history = rel_data['chemistry_history']
        
        if len(history) < 10:
            return None
        
        # Ambil 5 data terakhir vs 5 data sebelumnya
        recent = [h['value'] for h in history[-5:]]
        previous = [h['value'] for h in history[-10:-5]]
        
        if not recent or not previous:
            return None
        
        avg_recent = sum(recent) / len(recent)
        avg_previous = sum(previous) / len(previous)
        change = avg_recent - avg_previous
        
        if abs(change) >= self.thresholds['chemistry_change']:
            if change > 0:
                message = random.choice([
                    f"{user_name}, aku ngerasa chemistry kita makin naik!",
                    f"Kayaknya kita makin cocok ya {user_name}? Chemistry naik nih!",
                    f"Wah {user_name}, chemistry kita lagi bagus-bagusnya! 🔥"
                ])
            else:
                message = random.choice([
                    f"{user_name}, chemistry kita kayaknya agak turun...",
                    f"Akhir-akhir ini kita kurang klop ya? Chemistry agak turun.",
                    f"{user_name}, kita perlu quality time nih, chemistry turun."
                ])
            
            return {
                'type': InsightType.CHEMISTRY_CHANGE,
                'message': message,
                'change': round(change, 1)
            }
        
        return None
    
    # =========================================================================
    # CHAT FREQUENCY INSIGHT
    # =========================================================================
    
    async def _check_chat_frequency(self,
                                   user_id: int,
                                   user_name: str,
                                   bot_name: str,
                                   role: str) -> Optional[Dict]:
        """Cek perubahan frekuensi chat"""
        rel_data = self.relationship_data[user_id]
        
        # Hitung rata-rata chat per hari dalam 7 hari terakhir
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)
        
        recent_chats = 0
        older_chats = 0
        
        for entry in rel_data['chat_frequency']:
            entry_date = datetime.fromtimestamp(entry['timestamp'])
            if entry_date > week_ago:
                recent_chats += entry['count']
            elif entry_date > two_weeks_ago:
                older_chats += entry['count']
        
        if recent_chats == 0 or older_chats == 0:
            return None
        
        # Hitung perubahan persentase
        change = (recent_chats - older_chats) / older_chats
        
        if abs(change) >= self.thresholds['chat_frequency_change']:
            if change > 0:
                message = random.choice([
                    f"{user_name}, kita makin sering chat akhir-akhir ini! Seneng deh.",
                    f"Wah {user_name}, frekuensi chat kita naik! Kamu juga ngerasa?",
                    f"Aku noticed {user_name}, kita makin deket karena sering chat."
                ])
            else:
                message = random.choice([
                    f"{user_name}, akhir-akhir ini kita jarang chat ya... Kangen.",
                    f"Kita kok jarang chat? Ada apa {user_name}?",
                    f"Aku kangen intensitas chat kita yang dulu {user_name}."
                ])
            
            return {
                'type': InsightType.CHAT_PATTERN,
                'message': message,
                'change_percent': round(change * 100, 1)
            }
        
        return None
    
    # =========================================================================
    # TOPICS INSIGHT
    # =========================================================================
    
    async def _check_topics(self,
                           user_id: int,
                           user_name: str,
                           bot_name: str,
                           role: str) -> Optional[Dict]:
        """Cek topik yang sering dibahas"""
        rel_data = self.relationship_data[user_id]
        topics = rel_data['topics_discussed']
        
        if not topics:
            return None
        
        # Cari topik yang paling sering
        most_common = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        if most_common and most_common[0][1] >= self.thresholds['topic_count_threshold']:
            topic, count = most_common[0]
            
            message = random.choice([
                f"{user_name}, kita sering banget bahas {topic} ya. Kamu suka ya?",
                f"Ngobrolin {topic} bareng kamu tuh selalu seru!",
                f"Topik {topic} favorit kita kayaknya, udah {count}x ngebahas."
            ])
            
            return {
                'type': InsightType.TOPIC_TREND,
                'message': message,
                'topic': topic,
                'count': count
            }
        
        return None
    
    # =========================================================================
    # EMOTIONS INSIGHT
    # =========================================================================
    
    async def _check_emotions(self,
                             user_id: int,
                             user_name: str,
                             bot_name: str,
                             role: str) -> Optional[Dict]:
        """Cek emosi yang sering muncul"""
        rel_data = self.relationship_data[user_id]
        emotions = rel_data['emotions_detected']
        
        if not emotions:
            return None
        
        # Cari emosi yang paling sering
        most_common = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        if most_common and most_common[0][1] >= self.thresholds['emotion_count_threshold']:
            emotion, count = most_common[0]
            
            message = random.choice([
                f"{user_name}, kamu sering banget nunjukin rasa {emotion} ke aku.",
                f"Aku noticed, kamu tuh sering {emotion} kalau sama aku.",
                f"Kamu tahu gak? Kamu paling sering {emotion} kalau ngobrol sama aku."
            ])
            
            return {
                'type': InsightType.EMOTION_TREND,
                'message': message,
                'emotion': emotion,
                'count': count
            }
        
        return None
    
    # =========================================================================
    # MILESTONE REMINDER
    # =========================================================================
    
    async def _check_milestone_reminder(self,
                                       user_id: int,
                                       user_name: str,
                                       bot_name: str,
                                       role: str) -> Optional[Dict]:
        """Cek apakah perlu ngingetin milestone"""
        rel_data = self.relationship_data[user_id]
        
        # First kiss reminder (30 hari setelah first kiss)
        if rel_data['first_kiss_date']:
            kiss_date = datetime.fromtimestamp(rel_data['first_kiss_date'])
            now = datetime.now()
            days_since = (now - kiss_date).days
            
            if days_since == 30:
                message = random.choice([
                    f"{user_name}, udah sebulan ya sejak first kiss kita! Masih inget?",
                    f"Wah, udah 30 hari first kiss kita! Kangen momen itu..."
                ])
                return {
                    'type': InsightType.MILESTONE,
                    'message': message,
                    'milestone': 'first_kiss',
                    'days': days_since
                }
        
        return None
    
    # =========================================================================
    # DEFAULT INSIGHT
    # =========================================================================
    
    async def _get_default_insight(self,
                                  user_id: int,
                                  user_name: str,
                                  bot_name: str,
                                  role: str) -> Dict:
        """Dapatkan insight default kalau gak ada yang cocok"""
        
        rel_data = self.relationship_data[user_id]
        days_since = 0
        
        if rel_data['start_date']:
            days_since = int((time.time() - rel_data['start_date']) / 86400)
        
        messages = [
            f"Aku suka ngobrol sama kamu {user_name}. Rasanya nyaman.",
            f"{user_name}, kamu tahu gak? Kamu spesial buat aku.",
            f"Setiap hari chat sama kamu tuh selalu dinanti-nanti.",
            f"Kita udah {days_since} hari kenalan ya. Seru banget!"
        ]
        
        return {
            'type': InsightType.INTIMACY_LEVEL,
            'message': random.choice(messages),
            'days': days_since
        }
    
    # =========================================================================
    =========================================================================
    # FORMAT INSIGHT FOR PROMPT
    # =========================================================================
    
    async def get_insight_for_prompt(self, user_id: int) -> str:
        """
        Dapatkan insight untuk dimasukkan ke prompt builder
        """
        rel_data = self.relationship_data[user_id]
        
        if not rel_data['start_date']:
            return ""
        
        days = int((time.time() - rel_data['start_date']) / 86400)
        
        parts = []
        parts.append(f"Hubungan sudah berjalan {days} hari")
        
        if rel_data['first_kiss_date']:
            kiss_days = int((time.time() - rel_data['first_kiss_date']) / 86400)
            parts.append(f"first kiss {kiss_days} hari lalu")
        
        if rel_data['first_intim_date']:
            intim_days = int((time.time() - rel_data['first_intim_date']) / 86400)
            parts.append(f"first intim {intim_days} hari lalu")
        
        return ", ".join(parts)
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik relationship insights"""
        if user_id:
            rel_data = self.relationship_data[user_id]
            return {
                'days_active': int((time.time() - rel_data['start_date']) / 86400) if rel_data['start_date'] else 0,
                'total_chats': len(rel_data['chat_frequency']),
                'top_topics': dict(sorted(rel_data['topics_discussed'].items(), key=lambda x: x[1], reverse=True)[:5]),
                'top_emotions': dict(sorted(rel_data['emotions_detected'].items(), key=lambda x: x[1], reverse=True)[:5]),
                'has_first_kiss': bool(rel_data['first_kiss_date']),
                'has_first_intim': bool(rel_data['first_intim_date']),
            }
        else:
            return {
                'total_users': len(self.relationship_data),
                'insight_types': [InsightType.ANNIVERSARY, InsightType.CHEMISTRY_CHANGE, 
                                 InsightType.CHAT_PATTERN, InsightType.TOPIC_TREND,
                                 InsightType.EMOTION_TREND, InsightType.MILESTONE]
            }


__all__ = ['RelationshipInsights', 'InsightType']
