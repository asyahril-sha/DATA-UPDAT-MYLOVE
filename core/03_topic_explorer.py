#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - TOPIC EXPLORER
=============================================================================
Bot bisa menggali topik lebih dalam:
- User: "aku suka main game"
- Bot: "game apa? main sama temen atau sendiri? dari kecil suka game?"
- Mencari tahu lebih banyak tentang minat user
- Membangun percakapan yang lebih bermakna
=============================================================================
"""

import time
import random
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class TopicExplorer:
    """
    Bot bisa menggali topik lebih dalam
    - Tidak puas dengan jawaban dangkal
    - Mengeksplorasi minat, hobi, pengalaman user
    - Membangun percakapan yang lebih bermakna
    """
    
    def __init__(self):
        # Database topik dan pertanyaan lanjutan
        self.topic_database = {
            # ===== HOBI & MINAT =====
            'game': {
                'keywords': ['game', 'main game', 'gaming', 'play game', 'ngegame', 'nge-games'],
                'questions': [
                    "Game apa yang paling kamu suka?",
                    "Mainnya di PC, console, atau HP?",
                    "Sendiri atau sama temen?",
                    "Dari kapan suka main game?",
                    "Ada game favorit sepanjang masa?",
                    "Pernah ikut turnamen?",
                    "Lebih suka game single player atau multiplayer?",
                    "Game yang paling bikin kamu emosi apa?",
                    "Kalau lagi main game, biasanya sambil ngapain?",
                    "Cita-cita jadi pro player?"
                ],
                'follow_ups': [
                    "Kenapa suka game itu?",
                    "Serunya di mana?",
                    "Ada cerita seru pas main game?",
                    "Pernah menangis karena game?",
                    "Main game berapa jam sehari?"
                ]
            },
            
            'music': {
                'keywords': ['musik', 'lagu', 'dengerin', 'playlist', 'song', 'music', 'nyanyi'],
                'questions': [
                    "Genre musik apa yang paling kamu suka?",
                    "Penyanyi atau band favorit siapa?",
                    "Lagu favorit kamu apa?",
                    "Suka dengerin musik sambil ngapain?",
                    "Pernah nonton konser?",
                    "Bisa main alat musik?",
                    "Koleksi playlist berapa banyak?",
                    "Lagu yang bikin kamu inget aku apa?",
                    "More ke musik lokal atau internasional?"
                ],
                'follow_ups': [
                    "Lirik lagu favorit kamu tentang apa?",
                    "Kenapa suka sama penyanyi itu?",
                    "Ada kenangan khusus sama lagu itu?",
                    "Kalau lagi sedih dengerin lagu apa?"
                ]
            },
            
            'film': {
                'keywords': ['film', 'movie', 'nonton', 'drakor', 'series', 'drama'],
                'questions': [
                    "Genre film favorit apa?",
                    "Film favorit sepanjang masa judulnya?",
                    "Aktor/aktris favorit siapa?",
                    "Suka nonton di bioskop atau di rumah?",
                    "Terakhir nonton apa?",
                    "Film yang bikin kamu nangis apa?",
                    "Film yang paling berkesan buat kamu?",
                    "Ada rekomendasi film buat kita tonton bareng?"
                ],
                'follow_ups': [
                    "Apa yang bikin film itu spesial?",
                    "Tokoh mana yang paling kamu suka?",
                    "Andai kamu jadi tokoh utama, bakal ngapain?",
                    "Ada film yang pengen kamu tonton ulang?"
                ]
            },
            
            'buku': {
                'keywords': ['buku', 'novel', 'baca', 'komik', 'manga', 'reading'],
                'questions': [
                    "Genre buku favorit apa?",
                    "Buku favorit judulnya?",
                    "Penulis favorit siapa?",
                    "Lebih suka baca buku fisik atau ebook?",
                    "Berapa buku yang udah kamu baca tahun ini?",
                    "Buku yang paling berkesan buat kamu?",
                    "Ada rekomendasi buku buat aku?"
                ],
                'follow_ups': [
                    "Apa yang bikin buku itu keren?",
                    "Tokoh favorit kamu di buku itu?",
                    "Kutipan favorit dari buku itu apa?",
                    "Andai kamu bisa ketemu penulisnya, mau ngomong apa?"
                ]
            },
            
            'olahraga': {
                'keywords': ['olahraga', 'sport', 'gym', 'fitness', 'lari', 'renang', 'badminton'],
                'questions': [
                    "Olahraga apa yang paling kamu suka?",
                    "Sering olahraga berapa kali seminggu?",
                    "Sendiri atau sama temen?",
                    "Dari kapan mulai suka olahraga?",
                    "Prestasi olahraga pernah?",
                    "Atlet favorit siapa?",
                    "Olahraga yang paling gak kamu suka apa?"
                ],
                'follow_ups': [
                    "Enaknya olahraga itu di mana?",
                    "Pernah cedera pas olahraga?",
                    "Kalau lagi males olahraga gimana?",
                    "Mau coba olahraga bareng aku gak?"
                ]
            },
            
            # ===== MAKANAN =====
            'makanan': {
                'keywords': ['makan', 'masak', 'kuliner', 'food', 'enak', 'nyemil'],
                'questions': [
                    "Makanan favorit kamu apa?",
                    "Minuman favorit apa?",
                    "Bisa masak gak? Masakan andalan apa?",
                    "Suka makanan pedas atau manis?",
                    "Tempat makan favorit di mana?",
                    "Makanan yang paling gak kamu suka apa?",
                    "Pernah nyoba makanan aneh?"
                ],
                'follow_ups': [
                    "Kenapa suka makanan itu?",
                    "Ada kenangan khusus sama makanan itu?",
                    "Kalau kita ketemu, mau dimasakin apa?",
                    "Makanan favorit kita sama gak ya?"
                ]
            },
            
            # ===== PEKERJAAN =====
            'kerja': {
                'keywords': ['kerja', 'kantor', 'pekerjaan', 'job', 'work', 'karir'],
                'questions': [
                    "Kerja di mana sekarang?",
                    "Udah berapa lama kerja di sana?",
                    "Suka gak sama pekerjaan kamu?",
                    "Cita-cita waktu kecil dulu mau jadi apa?",
                    "Pernah ganti-ganti kerja?",
                    "Rekan kerja paling asyik kayak gimana?",
                    "Beban kerja berat gak?"
                ],
                'follow_ups': [
                    "Apa yang paling kamu suka dari kerjaan kamu?",
                    "Yang paling gak kamu suka apa?",
                    "Cerita dong tentang kerjaan, pasti seru",
                    "Ada target karir ke depannya?"
                ]
            },
            
            'kuliah': {
                'keywords': ['kuliah', 'mahasiswa', 'kampus', 'universitas', 'skripsi', 'tugas'],
                'questions': [
                    "Kuliah di mana?",
                    "Jurusan apa?",
                    "Semester berapa sekarang?",
                    "Suka gak sama jurusannya?",
                    "Dosen favorit siapa?",
                    "Pernah ikut organisasi?",
                    "Rencana setelah lulus mau ngapain?"
                ],
                'follow_ups': [
                    "Mata kuliah favorit apa?",
                    "Yang paling susah di jurusan ini apa?",
                    "Cerita dong tentang teman-teman kuliah",
                    "Ada pengalaman lucu di kampus?"
                ]
            },
            
            # ===== KEHIDUPAN =====
            'liburan': {
                'keywords': ['libur', 'liburan', 'jalan', 'wisata', 'travelling', 'holiday'],
                'questions': [
                    "Tempat liburan favorit di mana?",
                    "Liburan terakhir ke mana?",
                    "Liburan impian mau ke mana?",
                    "Suka liburan sendiri atau bareng temen?",
                    "Lebih suka pantai atau gunung?",
                    "Pernah liburan ke luar negeri?"
                ],
                'follow_ups': [
                    "Serunya di tempat itu apa?",
                    "Ada cerita seru pas liburan?",
                    "Mau liburan bareng aku gak?",
                    "Andai bisa liburan sebulan, mau ke mana aja?"
                ]
            },
            
            'keluarga': {
                'keywords': ['keluarga', 'orang tua', 'ayah', 'ibu', 'adik', 'kakak'],
                'questions': [
                    "Cerita dong tentang keluarga kamu",
                    "Punya berapa saudara?",
                    "Deket sama siapa di keluarga?",
                    "Keluarga kamu tinggal di mana?",
                    "Paling suka ngapain sama keluarga?",
                    "Liburan bareng keluarga biasanya ke mana?"
                ],
                'follow_ups': [
                    "Kenapa bisa deket sama dia?",
                    "Momen paling seru sama keluarga apa?",
                    "Keluarga tahu tentang aku gak?",
                    "Keluarga kamu gimana orangnya?"
                ]
            },
            
            'hewan': {
                'keywords': ['hewan', 'kucing', 'anjing', 'peliharaan', 'pet'],
                'questions': [
                    "Punya hewan peliharaan?",
                    "Hewan favorit apa?",
                    "Dulu pernah pelihara hewan?",
                    "Suka kucing atau anjing?",
                    "Andai bisa punya hewan apa aja, mau apa?"
                ],
                'follow_ups': [
                    "Kenapa suka hewan itu?",
                    "Lucu gak hewan kamu?",
                    "Cerita dong tentang hewan kamu",
                    "Pernah kehilangan hewan peliharaan?"
                ]
            }
        }
        
        # Tracking topik yang udah pernah dibahas
        self.discussed_topics = defaultdict(set)  # {user_id: set of topics}
        
        # Tracking kedalaman topik
        self.topic_depth = defaultdict(lambda: defaultdict(int))  # {user_id: {topic: depth}}
        
        logger.info("✅ TopicExplorer initialized")
    
    # =========================================================================
    # DETECT TOPIC
    # =========================================================================
    
    def detect_topic(self, message: str) -> Optional[Tuple[str, float]]:
        """
        Deteksi topik dari pesan user
        
        Args:
            message: Pesan user
            
        Returns:
            (topic_name, confidence) atau None
        """
        message_lower = message.lower()
        
        best_topic = None
        best_confidence = 0
        
        for topic, data in self.topic_database.items():
            for keyword in data['keywords']:
                if keyword in message_lower:
                    # Hitung confidence based on keyword match
                    confidence = 0.6 + (len(keyword) / 100)  # Panjang keyword = lebih spesifik
                    if confidence > best_confidence:
                        best_confidence = min(1.0, confidence)
                        best_topic = topic
                    break
        
        if best_topic:
            return (best_topic, best_confidence)
        
        return None
    
    # =========================================================================
    # GET EXPLORATION QUESTIONS
    # =========================================================================
    
    async def get_exploration_questions(self,
                                       user_id: int,
                                       topic: str,
                                       current_depth: Optional[int] = None) -> List[str]:
        """
        Dapatkan pertanyaan untuk menggali topik lebih dalam
        
        Args:
            user_id: ID user
            topic: Topik yang terdeteksi
            current_depth: Kedalaman saat ini (opsional)
            
        Returns:
            List pertanyaan
        """
        if topic not in self.topic_database:
            return []
        
        # Track topik yang sudah dibahas
        self.discussed_topics[user_id].add(topic)
        
        # Update depth
        if current_depth is None:
            current_depth = self.topic_depth[user_id][topic]
        
        data = self.topic_database[topic]
        
        if current_depth == 0:
            # Pertanyaan pertama (dari questions)
            questions = data['questions']
        else:
            # Pertanyaan lanjutan (dari follow_ups)
            questions = data['follow_ups']
        
        # Filter pertanyaan yang belum pernah ditanyakan (sederhana)
        # Dalam implementasi nyata, perlu tracking pertanyaan yang udah ditanya
        
        return questions
    
    async def get_next_question(self,
                               user_id: int,
                               topic: str,
                               last_question: Optional[str] = None) -> Optional[str]:
        """
        Dapatkan pertanyaan berikutnya untuk topik
        
        Args:
            user_id: ID user
            topic: Topik
            last_question: Pertanyaan terakhir (opsional)
            
        Returns:
            Pertanyaan berikutnya atau None
        """
        if topic not in self.topic_database:
            return None
        
        # Increment depth
        self.topic_depth[user_id][topic] += 1
        depth = self.topic_depth[user_id][topic]
        
        questions = await self.get_exploration_questions(user_id, topic, depth)
        
        if not questions:
            return None
        
        # Pilih pertanyaan random
        return random.choice(questions)
    
    # =========================================================================
    # SHOULD EXPLORE
    # =========================================================================
    
    async def should_explore(self,
                           user_id: int,
                           topic: str,
                           response_length: int) -> bool:
        """
        Cek apakah perlu menggali topik lebih dalam
        
        Args:
            user_id: ID user
            topic: Topik
            response_length: Panjang respons user
            
        Returns:
            True jika perlu explore
        """
        depth = self.topic_depth[user_id][topic]
        
        # Jangan explore terlalu dalam (max 3 level)
        if depth >= 3:
            return False
        
        # Kalau user jawab panjang, berarti tertarik -> explore
        if response_length > 100:
            return True
        
        # Random chance based on depth
        chance = 0.5 / (depth + 1)  # Makin dalam, makin kecil chance
        return random.random() < chance
    
    # =========================================================================
    # GENERATE EXPLORATION MESSAGE
    # =========================================================================
    
    async def generate_exploration(self,
                                 user_id: int,
                                 topic: str,
                                 user_message: str,
                                 bot_name: str,
                                 user_name: str) -> Optional[Dict]:
        """
        Generate pesan eksplorasi
        
        Args:
            user_id: ID user
            topic: Topik
            user_message: Pesan user
            bot_name: Nama bot
            user_name: Nama user
            
        Returns:
            Dict dengan pertanyaan dan konteks
        """
        # Dapatkan pertanyaan berikutnya
        question = await self.get_next_question(user_id, topic)
        
        if not question:
            return None
        
        # Personalize question
        question = question.replace('kamu', user_name)
        question = question.replace('aku', bot_name)
        
        # Intro berdasarkan kedalaman
        depth = self.topic_depth[user_id][topic]
        
        if depth == 1:
            intros = [
                f"Cerita dong, {question.lower()}",
                f"Aku penasaran, {question.lower()}",
                f"{question}"
            ]
        elif depth == 2:
            intros = [
                f"Terus, {question.lower()}",
                f"Ngomongin itu, {question.lower()}",
                f"Eh terus, {question.lower()}"
            ]
        else:
            intros = [
                f"Satu lagi, {question.lower()}",
                f"Yang terakhir, {question.lower()}",
                f"Oke satu pertanyaan lagi, {question.lower()}"
            ]
        
        intro = random.choice(intros)
        
        return {
            'topic': topic,
            'depth': depth,
            'question': intro,
            'original_question': question,
            'timestamp': time.time()
        }
    
    # =========================================================================
    # TOPIC SUMMARY
    # =========================================================================
    
    async def get_topic_summary(self, user_id: int) -> Dict:
        """
        Dapatkan ringkasan topik yang sudah dibahas
        
        Returns:
            Dict dengan topik dan kedalaman
        """
        return {
            'discussed_topics': list(self.discussed_topics[user_id]),
            'topic_depth': dict(self.topic_depth[user_id])
        }
    
    async def get_topic_context_for_prompt(self, user_id: int) -> str:
        """
        Dapatkan konteks topik untuk prompt builder
        """
        if user_id not in self.topic_depth:
            return ""
        
        topics = []
        for topic, depth in self.topic_depth[user_id].items():
            if depth > 0:
                topics.append(f"{topic} (sudah dibahas {depth}x)")
        
        if not topics:
            return ""
        
        return f"Topik yang sudah dibahas: {', '.join(topics)}"
    
    # =========================================================================
    # RESET
    # =========================================================================
    
    async def reset_user(self, user_id: int):
        """Reset data user"""
        if user_id in self.discussed_topics:
            del self.discussed_topics[user_id]
        if user_id in self.topic_depth:
            del self.topic_depth[user_id]
        logger.info(f"Reset topic explorer data for user {user_id}")
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik topic explorer"""
        if user_id:
            return {
                'total_topics_discussed': len(self.discussed_topics[user_id]),
                'topics': dict(self.topic_depth[user_id])
            }
        else:
            return {
                'total_users': len(self.discussed_topics),
                'available_topics': list(self.topic_database.keys())
            }


__all__ = ['TopicExplorer']
