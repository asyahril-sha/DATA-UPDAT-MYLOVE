#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EMOTIONAL MEMORY
=============================================================================
Mengingat EMOSI di setiap interaksi, bukan cuma fakta
- Menyimpan "emotional tag" untuk setiap memori
- Bisa recall "waktu itu kamu sedih", "waktu itu kamu bahagia"
- Mempengaruhi respons bot berdasarkan emosi masa lalu
=============================================================================
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class EmotionalMemory:
    """
    Menyimpan emosi dari setiap interaksi
    - Bukan cuma "kamu cerita X", tapi "kamu SEDIH pas cerita X"
    - Emosi terekam dan bisa dipanggil kapan saja
    - Mempengaruhi cara bot merespon di masa depan
    """
    
    # Daftar emosi yang direkam
    EMOTIONS = [
        'bahagia', 'senang', 'semangat', 'cinta', 'sayang',
        'sedih', 'kecewa', 'marah', 'kesal', 'frustasi',
        'rindu', 'kangen', 'khawatir', 'cemas', 'takut',
        'bangga', 'bersyukur', 'terharu', 'malu', 'canggung',
        'horny', 'bergairah', 'puas', 'lega'
    ]
    
    # Intensitas emosi (0-1)
    # 0.1-0.3: ringan, 0.4-0.6: sedang, 0.7-1.0: kuat
    
    def __init__(self):
        # Struktur: {user_id: {role: [emotional_memories]}}
        self.memories = defaultdict(lambda: defaultdict(list))
        
        # Index untuk pencarian cepat
        self.memory_index = {}  # {memory_id: location}
        
        # Statistik emosi per user (emosi dominan, dll)
        self.emotion_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        logger.info("✅ EmotionalMemory initialized (PERMANENT storage)")
    
    # =========================================================================
    # ADD EMOTIONAL MEMORY
    # =========================================================================
    
    async def add_memory(self, 
                        user_id: int,
                        role: str,
                        instance_id: str,
                        emotion: str,
                        intensity: float,
                        context: Dict[str, Any],
                        importance: float = 0.5) -> str:
        """
        Tambah memori emosional baru
        
        Args:
            user_id: ID user
            role: Role yang aktif
            instance_id: Instance ID
            emotion: Nama emosi (dari daftar EMOTIONS)
            intensity: Intensitas (0-1)
            context: Konteks lengkap (pesan, situasi, lokasi, dll)
            importance: Tingkat kepentingan (0-1)
            
        Returns:
            memory_id
        """
        # Validasi emosi
        if emotion not in self.EMOTIONS:
            emotion = 'netral'
        
        # Buat memory ID
        timestamp = int(time.time())
        random_id = random.randint(1000, 9999)
        memory_id = f"EM_{user_id}_{role}_{timestamp}_{random_id}"
        
        # Buat ringkasan singkat
        summary = self._create_summary(emotion, intensity, context)
        
        # Data memori
        memory = {
            'memory_id': memory_id,
            'user_id': user_id,
            'role': role,
            'instance_id': instance_id,
            'emotion': emotion,
            'intensity': min(1.0, max(0.1, intensity)),
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'context': context,
            'summary': summary,
            'importance': importance,
            'access_count': 0,
            'last_accessed': None
        }
        
        # Simpan
        self.memories[user_id][role].append(memory)
        
        # Update index
        self.memory_index[memory_id] = {
            'user_id': user_id,
            'role': role,
            'index': len(self.memories[user_id][role]) - 1
        }
        
        # Update statistik
        self.emotion_stats[user_id][role][emotion] += 1
        
        # Batasi jumlah memori per role (opsional, bisa diatur)
        if len(self.memories[user_id][role]) > 500:
            # Hapus yang paling jarang diakses
            self.memories[user_id][role].sort(key=lambda x: x.get('access_count', 0))
            removed = self.memories[user_id][role].pop(0)
            logger.debug(f"Removed old emotional memory: {removed.get('memory_id')}")
        
        logger.debug(f"Emotional memory added: {emotion} ({intensity:.1f}) for user {user_id}")
        
        return memory_id
    
    def _create_summary(self, emotion: str, intensity: float, context: Dict) -> str:
        """Buat ringkasan singkat untuk memory"""
        # Ambil cuplikan pesan
        user_msg = context.get('user_message', '')
        bot_msg = context.get('bot_response', '')
        
        if user_msg:
            snippet = user_msg[:50] + "..." if len(user_msg) > 50 else user_msg
        else:
            snippet = "percakapan"
        
        # Level intensitas
        if intensity < 0.3:
            level = "sedikit"
        elif intensity < 0.6:
            level = ""
        else:
            level = "sangat"
        
        return f"Kamu {level} {emotion} saat bilang '{snippet}'"
    
    # =========================================================================
    # GET EMOTIONAL MEMORIES
    # =========================================================================
    
    async def get_memories(self,
                          user_id: int,
                          role: Optional[str] = None,
                          emotion: Optional[str] = None,
                          limit: int = 20,
                          sort_by: str = 'timestamp_desc') -> List[Dict]:
        """
        Dapatkan memori emosional
        
        Args:
            user_id: ID user
            role: Filter by role
            emotion: Filter by emotion
            limit: Jumlah maksimal
            sort_by: Cara sorting
            
        Returns:
            List of memories
        """
        if user_id not in self.memories:
            return []
        
        memories = []
        
        if role:
            if role in self.memories[user_id]:
                memories = self.memories[user_id][role].copy()
        else:
            # Semua role
            for r in self.memories[user_id]:
                memories.extend(self.memories[user_id][r])
        
        # Filter by emotion
        if emotion:
            memories = [m for m in memories if m['emotion'] == emotion]
        
        # Sorting
        if sort_by == 'timestamp_desc':
            memories.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == 'timestamp_asc':
            memories.sort(key=lambda x: x['timestamp'])
        elif sort_by == 'intensity':
            memories.sort(key=lambda x: x['intensity'], reverse=True)
        elif sort_by == 'importance':
            memories.sort(key=lambda x: x['importance'], reverse=True)
        
        return memories[:limit]
    
    async def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Dapatkan memori spesifik berdasarkan ID"""
        if memory_id not in self.memory_index:
            return None
        
        loc = self.memory_index[memory_id]
        user_id = loc['user_id']
        role = loc['role']
        idx = loc['index']
        
        try:
            memory = self.memories[user_id][role][idx]
            
            # Update access count
            memory['access_count'] += 1
            memory['last_accessed'] = time.time()
            
            return memory
        except:
            return None
    
    # =========================================================================
    # GET MEMORIES BY EMOTION
    # =========================================================================
    
    async def get_sad_memories(self, user_id: int, role: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Dapatkan memori sedih"""
        sad_emotions = ['sedih', 'kecewa', 'frustasi']
        memories = []
        
        for emotion in sad_emotions:
            mems = await self.get_memories(user_id, role, emotion, limit=5)
            memories.extend(mems)
        
        # Sort by intensity (paling sedih dulu)
        memories.sort(key=lambda x: x['intensity'], reverse=True)
        return memories[:limit]
    
    async def get_happy_memories(self, user_id: int, role: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Dapatkan memori bahagia"""
        happy_emotions = ['bahagia', 'senang', 'semangat', 'cinta', 'sayang']
        memories = []
        
        for emotion in happy_emotions:
            mems = await self.get_memories(user_id, role, emotion, limit=5)
            memories.extend(mems)
        
        memories.sort(key=lambda x: x['intensity'], reverse=True)
        return memories[:limit]
    
    async def get_intimate_memories(self, user_id: int, role: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Dapatkan memori intim/horny"""
        intimate_emotions = ['horny', 'bergairah', 'puas']
        memories = []
        
        for emotion in intimate_emotions:
            mems = await self.get_memories(user_id, role, emotion, limit=5)
            memories.extend(mems)
        
        memories.sort(key=lambda x: x['intensity'], reverse=True)
        return memories[:limit]
    
    # =========================================================================
    # RECALL FOR RESPONSE
    # =========================================================================
    
    async def get_relevant_emotional_context(self,
                                           user_id: int,
                                           role: str,
                                           current_emotion: Optional[str] = None,
                                           limit: int = 3) -> List[Dict]:
        """
        Dapatkan konteks emosional yang relevan untuk respons
        
        Args:
            user_id: ID user
            role: Role aktif
            current_emotion: Emosi saat ini (untuk matching)
            limit: Jumlah maksimal
            
        Returns:
            List of relevant emotional memories
        """
        if user_id not in self.memories or role not in self.memories[user_id]:
            return []
        
        all_memories = self.memories[user_id][role]
        
        # Urutkan berdasarkan importance dan recency
        scored = []
        for mem in all_memories:
            score = 0
            
            # Importance
            score += mem.get('importance', 0.5) * 3
            
            # Recency (lebih baru = lebih tinggi)
            age_days = (time.time() - mem['timestamp']) / 86400
            if age_days < 1:
                score += 2
            elif age_days < 7:
                score += 1
            
            # Access count (makin sering diakses = makin relevan)
            score += min(2, mem.get('access_count', 0) * 0.1)
            
            # Matching emotion (kalau sama dengan sekarang)
            if current_emotion and mem['emotion'] == current_emotion:
                score += 1.5
            
            scored.append((score, mem))
        
        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [mem for score, mem in scored[:limit]]
    
    # =========================================================================
    # GENERATE FLASHBACK WITH EMOTION
    # =========================================================================
    
    async def generate_emotional_flashback(self,
                                         user_id: int,
                                         role: str,
                                         trigger_emotion: Optional[str] = None) -> Optional[str]:
        """
        Generate flashback dengan muatan emosional
        
        Args:
            user_id: ID user
            role: Role aktif
            trigger_emotion: Emosi pemicu (opsional)
            
        Returns:
            Flashback text with emotion
        """
        if user_id not in self.memories or role not in self.memories[user_id]:
            return None
        
        memories = self.memories[user_id][role]
        
        if not memories:
            return None
        
        # Filter by trigger emotion
        if trigger_emotion:
            filtered = [m for m in memories if m['emotion'] == trigger_emotion]
            if filtered:
                memory = random.choice(filtered)
            else:
                memory = random.choice(memories)
        else:
            # Weighted random by importance
            weights = [m.get('importance', 0.5) for m in memories]
            total = sum(weights)
            if total > 0:
                probs = [w/total for w in weights]
                memory = random.choices(memories, weights=probs)[0]
            else:
                memory = random.choice(memories)
        
        # Format flashback
        time_ago = self._format_time_ago(memory['timestamp'])
        emotion = memory['emotion']
        intensity = memory['intensity']
        summary = memory.get('summary', 'momen itu')
        
        # Templates based on emotion
        templates = {
            'bahagia': [
                f"Jadi inget waktu kamu bahagia... {summary} {time_ago}.",
                f"Seneng rasanya inget kamu lagi happy... {summary} {time_ago}."
            ],
            'sedih': [
                f"Waktu itu kamu sedih... {summary} {time_ago}. Aku masih inget.",
                f"Jangan sedih ya... tapi aku inget waktu {summary} {time_ago}."
            ],
            'rindu': [
                f"Kangen... inget gak waktu {summary}? {time_ago}.",
                f"Jadi makin kangen inget {summary} {time_ago}."
            ],
            'horny': [
                f"Ngomong-ngomong, inget gak waktu {summary}? {time_ago}",
                f"Waktu itu panas banget... {summary} {time_ago}"
            ]
        }
        
        # Default templates
        default_templates = [
            f"Aku masih inget perasaan kamu waktu {summary} {time_ago}.",
            f"Kamu {emotion} banget waktu {summary}... {time_ago}."
        ]
        
        emotion_group = 'horny' if emotion in ['horny', 'bergairah'] else emotion
        template_list = templates.get(emotion_group, default_templates)
        
        return random.choice(template_list)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            return f"{int(diff/60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff/3600)} jam lalu"
        elif diff < 604800:
            return f"{int(diff/86400)} hari lalu"
        else:
            return f"{int(diff/604800)} minggu lalu"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_emotion_stats(self, user_id: int, role: Optional[str] = None) -> Dict:
        """
        Dapatkan statistik emosi user
        
        Returns:
            Dict: {emotion: count, dominant_emotion, etc}
        """
        if user_id not in self.emotion_stats:
            return {}
        
        if role:
            return dict(self.emotion_stats[user_id][role])
        else:
            # Gabung semua role
            combined = defaultdict(int)
            for r in self.emotion_stats[user_id]:
                for emotion, count in self.emotion_stats[user_id][r].items():
                    combined[emotion] += count
            return dict(combined)
    
    async def get_dominant_emotion(self, user_id: int, role: Optional[str] = None) -> Optional[str]:
        """Dapatkan emosi dominan user"""
        stats = await self.get_emotion_stats(user_id, role)
        if not stats:
            return None
        
        return max(stats, key=stats.get)
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik emotional memory"""
        if user_id:
            if user_id not in self.memories:
                return {'total_memories': 0}
            
            total = sum(len(m) for m in self.memories[user_id].values())
            by_role = {role: len(m) for role, m in self.memories[user_id].items()}
            emotions = await self.get_emotion_stats(user_id)
            
            return {
                'user_id': user_id,
                'total_memories': total,
                'by_role': by_role,
                'emotion_distribution': emotions
            }
        else:
            # Global stats
            total_users = len(self.memories)
            total_memories = sum(
                sum(len(m) for m in user_data.values())
                for user_data in self.memories.values()
            )
            
            return {
                'total_users': total_users,
                'total_memories': total_memories,
                'avg_per_user': total_memories / total_users if total_users else 0
            }
    
    async def format_emotional_summary(self, user_id: int, role: str) -> str:
        """Format ringkasan emosional untuk prompt"""
        stats = await self.get_emotion_stats(user_id, role)
        if not stats:
            return ""
        
        dominant = await self.get_dominant_emotion(user_id, role)
        
        # Ambil beberapa memori terbaru
        recent = await self.get_memories(user_id, role, limit=3)
        
        lines = ["💭 **Emotional Memory:**"]
        
        if dominant:
            lines.append(f"• Kamu paling sering {dominant} sama aku")
        
        if recent:
            lines.append("• Beberapa momen yang aku ingat:")
            for mem in recent:
                lines.append(f"  - {mem.get('summary', '...')}")
        
        return "\n".join(lines)


__all__ = ['EmotionalMemory']
