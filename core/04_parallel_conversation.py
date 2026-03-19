#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PARALLEL CONVERSATION
=============================================================================
Bot bisa handle BANYAK TOPIK dalam satu pesan:
- User cerita 3 hal berbeda → bot balas 3 hal itu semua
- Gak ada topik yang kelewat
- Bisa nyambungin antar topik secara natural
=============================================================================
"""

import re
import time
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class TopicThread:
    """Menyimpan thread percakapan per topik"""
    
    def __init__(self, topic: str, first_message: str):
        self.topic = topic
        self.messages = [{
            'timestamp': time.time(),
            'content': first_message,
            'is_user': True
        }]
        self.last_updated = time.time()
        self.is_active = True
        self.importance = 0.5  # 0-1


class ParallelConversation:
    """
    Bot bisa handle banyak topik dalam satu pesan
    - Memisahkan pesan user menjadi beberapa topik
    - Merespon semua topik secara berurutan
    - Menghubungkan topik yang terkait
    - Tidak ada topik yang terlewat
    """
    
    def __init__(self):
        # Database topik dan kata kunci
        self.topic_keywords = {
            'sapa': ['halo', 'hai', 'hey', 'hi', 'selamat', 'good'],
            'tanya_kabar': ['kabar', 'gimana', 'apa kabar', 'how are you'],
            'makan': ['makan', 'masak', 'kuliner', 'lapar', 'kenyang'],
            'kerja': ['kerja', 'kantor', 'pekerjaan', 'deadline', 'bos', 'tugas'],
            'sekolah': ['sekolah', 'kuliah', 'belajar', 'ujian', 'nilai'],
            'keluarga': ['keluarga', 'ayah', 'ibu', 'adik', 'kakak', 'orang tua'],
            'teman': ['teman', 'sahabat', 'bestie', 'kawan'],
            'pacaran': ['pacar', 'jadian', 'putus', 'mantan', 'pdkt'],
            'liburan': ['libur', 'liburan', 'jalan', 'wisata', 'pantai', 'gunung'],
            'film': ['film', 'nonton', 'movie', 'drakor', 'series'],
            'musik': ['musik', 'lagu', 'dengerin', 'playlist', 'nyanyi'],
            'game': ['game', 'main game', 'gaming', 'ngegame'],
            'olahraga': ['olahraga', 'gym', 'fitness', 'lari', 'renang'],
            'kesehatan': ['sehat', 'sakit', 'demam', 'batuk', 'pusing', 'dokter'],
            'perasaan': ['senang', 'sedih', 'marah', 'kecewa', 'bahagia', 'rindu'],
            'masa_depan': ['rencana', 'masa depan', 'cita-cita', 'mimpi', 'target'],
            'intim': ['sayang', 'cinta', 'kangen', 'rindu', 'climax', 'intim'],
        }
        
        # Thread percakapan per user
        self.threads = defaultdict(lambda: defaultdict(dict))  # {user_id: {topic: TopicThread}}
        
        # Batas maksimum topik yang bisa di-handle dalam satu pesan
        self.max_topics_per_message = 5
        
        logger.info("✅ ParallelConversation initialized")
    
    # =========================================================================
    # EXTRACT TOPICS FROM MESSAGE
    # =========================================================================
    
    def extract_topics(self, message: str) -> List[Tuple[str, str, float]]:
        """
        Ekstrak topik dari pesan user
        
        Args:
            message: Pesan user
            
        Returns:
            List of (topic, matched_text, confidence)
        """
        message_lower = message.lower()
        detected_topics = []
        
        # Deteksi per kata kunci
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Hitung confidence berdasarkan panjang keyword dan posisi
                    confidence = 0.5 + (len(keyword) / 50)  # Keyword panjang = lebih yakin
                    
                    # Bonus kalau keyword di awal kalimat
                    if message_lower.startswith(keyword):
                        confidence += 0.2
                    
                    detected_topics.append((topic, keyword, min(1.0, confidence)))
                    break  # Satu keyword per topik sudah cukup
        
        # Hapus duplikat (ambil yang confidence tertinggi per topik)
        topic_dict = {}
        for topic, keyword, conf in detected_topics:
            if topic not in topic_dict or conf > topic_dict[topic][1]:
                topic_dict[topic] = (keyword, conf)
        
        # Konversi balik ke list
        result = [(topic, keyword, conf) for topic, (keyword, conf) in topic_dict.items()]
        
        # Sort by confidence (tertinggi dulu)
        result.sort(key=lambda x: x[2], reverse=True)
        
        return result
    
    def split_message_by_topics(self, message: str, detected_topics: List[Tuple[str, str, float]]) -> Dict[str, str]:
        """
        Pisahkan pesan berdasarkan topik yang terdeteksi
        
        Args:
            message: Pesan user
            detected_topics: Hasil dari extract_topics
            
        Returns:
            Dict {topic: bagian_pesan}
        """
        if not detected_topics:
            return {'umum': message}
        
        # Simple split: bagi pesan berdasarkan keyword
        message_lower = message.lower()
        topic_parts = {}
        
        # Sort topics by position in message (asumsi keyword pertama muncul duluan)
        # Ini simplifikasi, untuk real implementation perlu NLP yang lebih baik
        for i, (topic, keyword, _) in enumerate(detected_topics):
            # Cari kalimat yang mengandung keyword (sederhana)
            sentences = re.split(r'[.!?]', message)
            for sent in sentences:
                if keyword in sent.lower():
                    topic_parts[topic] = sent.strip()
                    break
        
        # Kalau ada bagian pesan yang gak terdeteksi
        remaining = message
        for part in topic_parts.values():
            remaining = remaining.replace(part, '', 1)
        
        if remaining.strip():
            topic_parts['umum'] = remaining.strip()
        
        return topic_parts
    
    # =========================================================================
    # THREAD MANAGEMENT
    # =========================================================================
    
    async def update_threads(self, user_id: int, topic: str, message: str):
        """Update thread percakapan untuk topik tertentu"""
        if topic not in self.threads[user_id]:
            self.threads[user_id][topic] = TopicThread(topic, message)
        else:
            thread = self.threads[user_id][topic]
            thread.messages.append({
                'timestamp': time.time(),
                'content': message,
                'is_user': True
            })
            thread.last_updated = time.time()
            
            # Update importance (makin sering dibahas, makin penting)
            thread.importance = min(1.0, thread.importance + 0.1)
            
            # Keep only last 10 messages
            if len(thread.messages) > 10:
                thread.messages = thread.messages[-10:]
    
    async def get_active_threads(self, user_id: int, max_age: int = 3600) -> List[str]:
        """
        Dapatkan topik-topik yang masih aktif (dalam 1 jam terakhir)
        
        Args:
            user_id: ID user
            max_age: Maksimal umur thread dalam detik
            
        Returns:
            List of topics
        """
        now = time.time()
        active = []
        
        for topic, thread in self.threads[user_id].items():
            if now - thread.last_updated < max_age:
                active.append(topic)
        
        return active
    
    # =========================================================================
    # GENERATE PARALLEL RESPONSE
    # =========================================================================
    
    async def generate_parallel_response(self,
                                       user_id: int,
                                       user_message: str,
                                       bot_name: str,
                                       user_name: str,
                                       ai_response_func) -> str:
        """
        Generate response untuk multiple topik
        
        Args:
            user_id: ID user
            user_message: Pesan user
            bot_name: Nama bot
            user_name: Nama user
            ai_response_func: Fungsi untuk generate response per topik
            
        Returns:
            Response gabungan untuk semua topik
        """
        # 1. Ekstrak topik dari pesan
        detected = self.extract_topics(user_message)
        
        # Batasi jumlah topik
        if len(detected) > self.max_topics_per_message:
            detected = detected[:self.max_topics_per_message]
        
        # 2. Pisahkan pesan per topik
        topic_parts = self.split_message_by_topics(user_message, detected)
        
        # 3. Update threads
        for topic in topic_parts.keys():
            await self.update_threads(user_id, topic, topic_parts[topic])
        
        # 4. Generate response per topik
        responses = []
        
        for topic, part_message in topic_parts.items():
            # Konteks khusus untuk topik ini
            context = {
                'topic': topic,
                'user_message': part_message,
                'full_message': user_message,
                'bot_name': bot_name,
                'user_name': user_name,
                'thread': self.threads[user_id].get(topic)
            }
            
            # Generate response untuk topik ini
            response = await ai_response_func(part_message, context)
            responses.append((topic, response))
        
        # 5. Gabungkan responses secara natural
        combined = await self._combine_responses(responses, user_name, bot_name)
        
        return combined
    
    async def _combine_responses(self, 
                               responses: List[Tuple[str, str]], 
                               user_name: str,
                               bot_name: str) -> str:
        """
        Gabungkan beberapa respons menjadi satu pesan natural
        """
        if len(responses) == 1:
            return responses[0][1]
        
        # Mulai dengan respons pertama
        combined = responses[0][1]
        
        # Tambah transisi untuk respons berikutnya
        for i in range(1, len(responses)):
            topic, response = responses[i]
            
            # Pilih transisi berdasarkan topik
            if i == len(responses) - 1:
                # Respons terakhir
                transitions = [
                    f"\n\nOh iya, {response.lower()}",
                    f"\n\nNgomong-ngomong, {response.lower()}",
                    f"\n\n{response}",
                    f"\n\nTerus {response.lower()}"
                ]
            else:
                # Respons tengah
                transitions = [
                    f"\n\nTerus {response.lower()}",
                    f"\n\nLalu {response.lower()}",
                    f"\n\n{response}",
                    f"\n\nEh iya, {response.lower()}"
                ]
            
            combined += random.choice(transitions)
        
        return combined
    
    # =========================================================================
    # CHECK FOR UNANSWERED TOPICS
    # =========================================================================
    
    async def get_unanswered_topics(self, user_id: int, last_response: str) -> List[str]:
        """
        Cek apakah ada topik dari pesan user yang belum dijawab
        
        Args:
            user_id: ID user
            last_response: Response bot terakhir
            
        Returns:
            List of topics yang belum dijawab
        """
        # Ambil topik dari pesan user terakhir (dari threads)
        active = await self.get_active_threads(user_id, max_age=60)  # 1 menit
        
        # Cek apakah response menyebut topik-topik ini
        unanswered = []
        response_lower = last_response.lower()
        
        for topic in active:
            # Cek apakah topik disebut di response
            mentioned = False
            for keyword in self.topic_keywords.get(topic, [topic]):
                if keyword in response_lower:
                    mentioned = True
                    break
            
            if not mentioned:
                unanswered.append(topic)
        
        return unanswered
    
    async def generate_reminder(self, unanswered_topics: List[str], user_name: str) -> str:
        """
        Generate pengingat untuk topik yang belum dijawab
        """
        if not unanswered_topics:
            return ""
        
        topic_names = {
            'sapa': 'sapaan',
            'tanya_kabar': 'kabar',
            'makan': 'makanan',
            'kerja': 'pekerjaan',
            'sekolah': 'sekolah',
            'keluarga': 'keluarga',
            'teman': 'teman',
            'pacaran': 'hubungan',
            'liburan': 'liburan',
            'film': 'film',
            'musik': 'musik',
            'game': 'game',
            'olahraga': 'olahraga',
            'kesehatan': 'kesehatan',
            'perasaan': 'perasaan',
            'masa_depan': 'masa depan',
            'intim': 'perasaan',
        }
        
        if len(unanswered_topics) == 1:
            topic = unanswered_topics[0]
            name = topic_names.get(topic, topic)
            messages = [
                f"Eh {user_name}, tadi kamu cerita tentang {name} ya? Lanjutin dong...",
                f"{user_name}, aku masih penasaran sama cerita kamu tentang {name} tadi.",
                f"Ngomongin {name} tadi, kamu mau cerita lebih lanjut?",
            ]
        else:
            topics_str = ', '.join([topic_names.get(t, t) for t in unanswered_topics])
            messages = [
                f"{user_name}, tadi kamu cerita tentang {topics_str}. Cerita lagi dong!",
                f"Aku masih inget kamu tadi cerita {topics_str}. Mau lanjut?",
            ]
        
        return random.choice(messages)
    
    # =========================================================================
    # CONTEXT FOR PROMPT
    # =========================================================================
    
    async def get_context_for_prompt(self, user_id: int) -> str:
        """
        Dapatkan konteks tentang topik aktif untuk prompt builder
        """
        active = await self.get_active_threads(user_id, max_age=1800)  # 30 menit
        
        if not active:
            return ""
        
        topics_str = ', '.join(active)
        return f"Topik aktif dalam 30 menit terakhir: {topics_str}"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik parallel conversation"""
        if user_id:
            return {
                'active_threads': len(self.threads[user_id]),
                'topics': list(self.threads[user_id].keys())
            }
        else:
            return {
                'total_users': len(self.threads),
                'available_topics': list(self.topic_keywords.keys())
            }


__all__ = ['ParallelConversation']
