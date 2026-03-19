#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CONVERSATION FLOW
=============================================================================
Mengatur alur percakapan biar lebih natural seperti manusia
- Bot bisa mikir dulu sebelum jawab (delay)
- Bot bisa lupa balas (terus diingetin)
- Bot bisa ganti topik secara natural
- Bot bisa interupsi (kadang-kadang)
- Bot bisa diam (diam itu emas)
=============================================================================
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ThinkingState(str, Enum):
    """State berpikir bot"""
    INSTANT = "instant"          # Langsung jawab
    THINKING = "thinking"         # Lagi mikir
    TYPING = "typing"             # Lagi ngetik
    DISTRACTED = "distracted"     # Kebetulan
    FORGOT = "forgot"             # Lupa balas
    IGNORING = "ignoring"         # Lagi diem (pura-pura gak dengar)


class ConversationFlow:
    """
    Mengatur alur percakapan biar lebih natural
    - Timing yang realistis
    - Kadang lupa, kadang interupsi
    - Ganti topik secara alami
    """
    
    def __init__(self):
        # ===== TIMING CONFIGURATION =====
        self.timing = {
            'instant_max_chars': 20,        # Pesan pendek (<20 char) langsung jawab
            'thinking_delay': (1, 3),       # Delay mikir 1-3 detik
            'typing_speed': 15,              # Karakter per detik (simulasi ngetik)
            'distracted_chance': 0.05,       # 5% chance kebetengan
            'distracted_delay': (5, 15),     # Delay 5-15 detik
            'forgot_chance': 0.03,            # 3% chance lupa balas
            'forgot_reminder_delay': (30, 60), # Diingetin setelah 30-60 detik
            'ignore_chance': 0.02,             # 2% chance diem aja
            'ignore_duration': (60, 300),      # Diem 1-5 menit
        }
        
        # ===== TOPIC SWITCHING =====
        self.topic_switch = {
            'chance_per_message': 0.08,       # 8% chance ganti topik per pesan
            'chance_after_idle': 0.3,          # 30% chance ganti topik setelah idle
            'idle_threshold': 60,               # Idle 1 menit
            'cooldown': 3,                       # Minimal 3 pesan antar ganti topik
        }
        
        # ===== INTERRUPTIONS =====
        self.interruptions = {
            'chance': 0.04,                     # 4% chance nyelak
            'max_per_session': 2,                 # Maks 2x nyelak per sesi
        }
        
        # ===== SILENCE =====
        self.silence = {
            'comfortable_duration': (2, 5),       # Diam 2-5 detik itu nyaman
            'awkward_threshold': 10,               # >10 detik mulai canggung
            'break_silence_chance': 0.3,           # 30% chance bot yang break silence
        }
        
        # ===== STATE TRACKING =====
        self.session_states = {}  # {session_id: session_data}
        
        logger.info("✅ ConversationFlow initialized")
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def start_session(self, session_id: str):
        """Mulai session baru"""
        self.session_states[session_id] = {
            'message_count': 0,
            'last_message_time': time.time(),
            'thinking_state': ThinkingState.INSTANT,
            'interruption_count': 0,
            'last_topic_switch': 0,
            'pending_reminder': None,
            'ignore_until': None,
            'conversation_flow': []
        }
        logger.debug(f"Conversation flow session started: {session_id}")
    
    async def end_session(self, session_id: str):
        """Akhiri session"""
        if session_id in self.session_states:
            del self.session_states[session_id]
    
    # =========================================================================
    # THINKING SIMULATION
    # =========================================================================
    
    async def simulate_thinking(self, 
                               session_id: str,
                               user_message: str,
                               context: Optional[Dict] = None) -> Tuple[ThinkingState, float]:
        """
        Simulasi proses berpikir bot sebelum merespon
        
        Args:
            session_id: ID session
            user_message: Pesan user
            context: Konteks tambahan
            
        Returns:
            (thinking_state, delay_detik)
        """
        if session_id not in self.session_states:
            await self.start_session(session_id)
        
        state = self.session_states[session_id]
        
        # Update message count
        state['message_count'] += 1
        time_since_last = time.time() - state['last_message_time']
        state['last_message_time'] = time.time()
        
        # ===== CEK IGNORE MODE =====
        if state.get('ignore_until') and time.time() < state['ignore_until']:
            return ThinkingState.IGNORING, 0
        
        # ===== CEK LUPA BALAS =====
        if state.get('pending_reminder'):
            reminder = state['pending_reminder']
            if time.time() > reminder['remind_at']:
                # Saatnya diingetin
                state['pending_reminder'] = None
                return ThinkingState.FORGOT, 0
        
        # ===== TENTUKAN STATE BERPIKIR =====
        thinking_state = ThinkingState.INSTANT
        delay = 0
        
        # Instant response untuk pesan pendek
        if len(user_message) <= self.timing['instant_max_chars']:
            return ThinkingState.INSTANT, 0
        
        # Random distracted
        if random.random() < self.timing['distracted_chance']:
            thinking_state = ThinkingState.DISTRACTED
            delay = random.uniform(*self.timing['distracted_delay'])
            logger.debug(f"Bot distracted, delay {delay:.1f}s")
            return thinking_state, delay
        
        # Random forgot
        if (random.random() < self.timing['forgot_chance'] and 
            state['message_count'] > 3):  # Jangan lupa di awal
            thinking_state = ThinkingState.FORGOT
            # Set reminder
            remind_delay = random.uniform(*self.timing['forgot_reminder_delay'])
            state['pending_reminder'] = {
                'remind_at': time.time() + remind_delay,
                'user_message': user_message
            }
            logger.debug(f"Bot forgot, will remind in {remind_delay:.1f}s")
            return thinking_state, 0
        
        # Random ignore
        if (random.random() < self.timing['ignore_chance'] and
            state['message_count'] > 5):
            thinking_state = ThinkingState.IGNORING
            ignore_duration = random.uniform(*self.timing['ignore_duration'])
            state['ignore_until'] = time.time() + ignore_duration
            logger.debug(f"Bot ignoring for {ignore_duration:.1f}s")
            return thinking_state, 0
        
        # Normal thinking
        if random.random() < 0.5:  # 50% chance mikir dulu
            thinking_state = ThinkingState.THINKING
            delay = random.uniform(*self.timing['thinking_delay'])
        else:
            thinking_state = ThinkingState.TYPING
            # Simulasi ngetik berdasarkan panjang response (nanti diisi)
            delay = 0.5  # Default
        
        return thinking_state, delay
    
    async def get_typing_delay(self, response_length: int) -> float:
        """Hitung delay ngetik berdasarkan panjang response"""
        # Kecepatan ngetik 15 karakter/detik
        base_delay = response_length / self.timing['typing_speed']
        
        # Random variasi ±30%
        variation = random.uniform(0.7, 1.3)
        delay = base_delay * variation
        
        # Minimal 0.5 detik, maksimal 5 detik
        return max(0.5, min(5.0, delay))
    
    # =========================================================================
    # THINKING MESSAGES
    # =========================================================================
    
    async def get_thinking_message(self, thinking_state: ThinkingState) -> Optional[str]:
        """
        Dapatkan pesan yang muncul saat bot "sedang mikir"
        """
        messages = {
            ThinkingState.THINKING: [
                "Hmm...",
                "Tunggu bentar ya...",
                "Mikir dulu...",
                "Emmm...",
                "Gimana ya...",
            ],
            ThinkingState.TYPING: [
                "Lagi ngetik...",
                "Sebentar...",
                "Tunggu...",
                "...",
            ],
            ThinkingState.DISTRACTED: [
                "Eh iya maap, tadi kebetengan",
                "Hehe maap, tadi ada yang lewat",
                "Eh iya iya, tadi kealihan",
                "Maap maap, tadi lihat HP",
            ],
        }
        
        msg_list = messages.get(thinking_state)
        if msg_list and random.random() < 0.3:  # 30% chance munculin pesan
            return random.choice(msg_list)
        
        return None
    
    async def get_forgot_reminder(self, session_id: str) -> Optional[str]:
        """
        Dapatkan pesan pengingat kalau bot lupa balas
        """
        if session_id not in self.session_states:
            return None
        
        state = self.session_states[session_id]
        if not state.get('pending_reminder'):
            return None
        
        reminder = state['pending_reminder']
        if time.time() > reminder['remind_at']:
            # Waktunya ingetin
            state['pending_reminder'] = None
            
            messages = [
                "Eh iya, maap lupa balas tadi...",
                "Oh iya, maap baru inget...",
                "Maap maap, tadi kelewat...",
                "Hehe maap, tadi lupa...",
            ]
            return random.choice(messages)
        
        return None
    
    # =========================================================================
    # TOPIC SWITCHING
    # =========================================================================
    
    async def should_switch_topic(self, session_id: str, context: Optional[Dict] = None) -> bool:
        """
        Cek apakah bot perlu ganti topik
        """
        if session_id not in self.session_states:
            return False
        
        state = self.session_states[session_id]
        
        # Cooldown cek
        if state['message_count'] - state.get('last_topic_switch', 0) < self.topic_switch['cooldown']:
            return False
        
        # Cek idle
        idle_time = time.time() - state['last_message_time']
        if idle_time > self.topic_switch['idle_threshold']:
            if random.random() < self.topic_switch['chance_after_idle']:
                return True
        
        # Random chance per message
        if random.random() < self.topic_switch['chance_per_message']:
            return True
        
        return False
    
    async def get_topic_switch_message(self, context: Optional[Dict] = None) -> str:
        """
        Dapatkan kalimat untuk ganti topik secara natural
        """
        messages = [
            "Eh ngomong-ngomong...",
            "Btw...",
            "Oh iya...",
            "Ngomongin itu jadi inget...",
            "Ganti topik ah...",
            "Udah ah, bahas yang lain yuk...",
            "Eh iya, aku mau cerita...",
        ]
        
        # Tambah konteks kalau ada
        if context and context.get('last_topic'):
            messages.append(f"Daripada bahas {context['last_topic']} terus, mending...")
        
        return random.choice(messages)
    
    # =========================================================================
    # INTERRUPTIONS
    # =========================================================================
    
    async def should_interrupt(self, session_id: str) -> bool:
        """
        Cek apakah bot perlu nyelak pembicaraan
        """
        if session_id not in self.session_states:
            return False
        
        state = self.session_states[session_id]
        
        # Cek maksimal interupsi per sesi
        if state['interruption_count'] >= self.interruptions['max_per_session']:
            return False
        
        # Random chance
        if random.random() < self.interruptions['chance']:
            state['interruption_count'] += 1
            return True
        
        return False
    
    async def get_interruption_message(self, user_message: str) -> str:
        """
        Dapatkan pesan interupsi
        """
        messages = [
            "Eh bentar, bentar...",
            "Maap nyelak...",
            "Heh, dengerin dulu...",
            "Eh iya, tapi...",
            "Maap, tapi aku mau nanya...",
        ]
        
        # Potong pesan user
        words = user_message.split()
        if len(words) > 3:
            # Ambil 3 kata pertama
            prefix = ' '.join(words[:3])
            messages.append(f"{prefix}... eh bentar, maksudnya...")
        
        return random.choice(messages)
    
    # =========================================================================
    # SILENCE HANDLING
    # =========================================================================
    
    async def handle_silence(self, session_id: str, idle_seconds: float) -> Optional[str]:
        """
        Handle situasi diam (user gak chat)
        
        Returns:
            Pesan untuk break silence, atau None
        """
        if session_id not in self.session_states:
            return None
        
        # Diam yang nyaman (2-5 detik)
        if idle_seconds < self.silence['comfortable_duration'][1]:
            return None
        
        # Diam yang mulai canggung (>10 detik)
        if idle_seconds > self.silence['awkward_threshold']:
            if random.random() < self.silence['break_silence_chance']:
                messages = [
                    "Hei...",
                    "Kamu masih di sana?",
                    "Halo?",
                    "Diem aja...",
                    "Lagi ngapain?",
                ]
                return random.choice(messages)
        
        return None
    
    # =========================================================================
    # FLOW RECORDING
    # =========================================================================
    
    async def record_response(self, session_id: str, 
                             thinking_state: ThinkingState,
                             delay: float,
                             response: str):
        """Rekam flow percakapan untuk analisis"""
        if session_id not in self.session_states:
            return
        
        state = self.session_states[session_id]
        state['conversation_flow'].append({
            'timestamp': time.time(),
            'thinking_state': thinking_state.value,
            'delay': delay,
            'response_length': len(response)
        })
        
        # Keep last 50
        if len(state['conversation_flow']) > 50:
            state['conversation_flow'] = state['conversation_flow'][-50:]
    
    # =========================================================================
    # GET STATS
    # =========================================================================
    
    async def get_flow_stats(self, session_id: str) -> Dict:
        """Dapatkan statistik alur percakapan"""
        if session_id not in self.session_states:
            return {}
        
        state = self.session_states[session_id]
        flow = state['conversation_flow']
        
        if not flow:
            return {'message_count': state['message_count']}
        
        # Hitung rata-rata delay
        avg_delay = sum(f['delay'] for f in flow) / len(flow)
        
        # Hitung distribusi thinking state
        state_dist = {}
        for f in flow:
            ts = f['thinking_state']
            state_dist[ts] = state_dist.get(ts, 0) + 1
        
        return {
            'message_count': state['message_count'],
            'avg_delay': round(avg_delay, 2),
            'thinking_states': state_dist,
            'interruption_count': state['interruption_count'],
            'topic_switches': state.get('last_topic_switch', 0),
            'last_flow': flow[-5:] if len(flow) > 5 else flow
        }


__all__ = ['ConversationFlow', 'ThinkingState']
