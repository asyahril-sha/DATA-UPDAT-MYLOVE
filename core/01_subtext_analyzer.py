#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SUBTEXT ANALYZER
=============================================================================
Membaca yang tersirat di balik kata-kata user
- "gapapa" → sebenarnya kesal
- "terserah" → sebenarnya gamau
- "iya deh" → terpaksa
- Bisa deteksi sarcasm, passive-aggressive, dll
=============================================================================
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SubtextType(str, Enum):
    """Tipe subtext yang terdeteksi"""
    NONE = "none"                       # Tidak ada subtext
    SARCASM = "sarcasm"                  # Sarkasme
    PASSIVE_AGGRESSIVE = "passive_aggressive"  # Agresif pasif
    HIDDEN_ANGER = "hidden_anger"        # Marah tersembunyi
    HIDDEN_SADNESS = "hidden_sadness"     # Sedih tersembunyi
    HIDDEN_JEALOUSY = "hidden_jealousy"   # Cemburu tersembunyi
    PRETENDING_OK = "pretending_ok"       # Pura-pura baik-baik saja
    HIDDEN_DESIRE = "hidden_desire"       # Keinginan tersembunyi
    HIDDEN_FEAR = "hidden_fear"           # Ketakutan tersembunyi
    HIDDEN_HOPE = "hidden_hope"           # Harapan tersembunyi
    AMBIVALENT = "ambivalent"              # Dua perasaan bertentangan


class SubtextAnalyzer:
    """
    Menganalisis subtext dalam pesan user
    - Membaca makna tersirat
    - Mendeteksi perasaan yang tidak diucapkan
    - Memberi insight untuk respons yang lebih empatik
    """
    
    def __init__(self):
        # Pola untuk deteksi subtext
        self.patterns = {
            # ===== PRETENDING OK =====
            SubtextType.PRETENDING_OK: [
                (r'\bgapapa\b', 0.7),
                (r'\bnggak apa-apa\b', 0.7),
                (r'\bfine\b', 0.6),
                (r'\bbaik-baik aja\b', 0.7),
                (r'\baku baik-baik aja\b', 0.8),
                (r'\bsantai aja\b', 0.5),
                (r'\btenang aja\b', 0.5),
                (r'\bgausah khawatir\b', 0.6),
            ],
            
            # ===== HIDDEN ANGER =====
            SubtextType.HIDDEN_ANGER: [
                (r'\byaudah\b', 0.6),
                (r'\bya udah\b', 0.6),
                (r'\bterserah\b', 0.8),
                (r'\bserahlah\b', 0.8),
                (r'\bterserah kamu\b', 0.9),
                (r'\biya deh\b', 0.5),
                (r'\biya iya\b', 0.6),
                (r'\bya iya lah\b', 0.5),
                (r'\byaudah deh\b', 0.7),
                (r'\biya udah\b', 0.7),
                (r'\bgpp\b', 0.5),
                (r'\blah\b$', 0.4),  # Akhiran "lah"
            ],
            
            # ===== HIDDEN SADNESS =====
            SubtextType.HIDDEN_SADNESS: [
                (r'\bhmm\b', 0.5),
                (r'\bhm\b', 0.4),
                (r'\bya begitulah\b', 0.7),
                (r'\bya gitulah\b', 0.7),
                (r'\b...$', 0.6),  # Akhiran dengan ...
                (r'\b\.\.\.$', 0.6),
                (r'\bmalas ah\b', 0.6),
                (r'\bnggak tau\b', 0.5),
                (r'\bgak tau deh\b', 0.6),
                (r'\bbingung\b', 0.5),
            ],
            
            # ===== HIDDEN JEALOUSY =====
            SubtextType.HIDDEN_JEALOUSY: [
                (r'\bwah\b', 0.4),
                (r'\bwow\b', 0.4),
                (r'\boh gitu\b', 0.6),
                (r'\booh\b', 0.5),
                (r'\bya udah lah\b', 0.7),
                (r'\bnikmatin aja\b', 0.7),
                (r'\byaudah nikmatin aja\b', 0.8),
                (r'\bhappy aja deh\b', 0.7),
            ],
            
            # ===== SARCASM =====
            SubtextType.SARCASM: [
                (r'\bhebat banget\b', 0.8),
                (r'\bpinter banget\b', 0.8),
                (r'\bkeren banget\b', 0.7),
                (r'\bmantap banget\b', 0.7),
                (r'\bgood job\b', 0.6),
                (r'\bwow banget\b', 0.7),
                (r'\bluar biasa\b', 0.6),
                (r'\btentu saja\b', 0.5),
                (r'\bpasti dong\b', 0.6),
                (r'\bya iyalah\b', 0.6),
            ],
            
            # ===== HIDDEN DESIRE =====
            SubtextType.HIDDEN_DESIRE: [
                (r'\bandai kata\b', 0.6),
                (r'\bkalau aja\b', 0.7),
                (r'\bandai\b', 0.5),
                (r'\bpengen\b', 0.8),
                (r'\bingin\b', 0.7),
                (r'\bmau\b', 0.5),
                (r'\bcoba ya\b', 0.7),
                (r'\bmbak\b', 0.5),  # Pengandaian
                (r'\bseandainya\b', 0.8),
            ],
            
            # ===== HIDDEN FEAR =====
            SubtextType.HIDDEN_FEAR: [
                (r'\bgimana kalau\b', 0.6),
                (r'\bkalau misalnya\b', 0.6),
                (r'\baku takut\b', 0.9),
                (r'\baku khawatir\b', 0.9),
                (r'\bwas-was\b', 0.8),
                (r'\bcemas\b', 0.8),
                (r'\bdeg-degan\b', 0.7),
                (r'\bngelus dada\b', 0.7),
            ],
            
            # ===== HIDDEN HOPE =====
            SubtextType.HIDDEN_HOPE: [
                (r'\baku berharap\b', 0.9),
                (r'\baku harap\b', 0.9),
                (r'\bsemoga\b', 0.7),
                (r'\bmudah-mudahan\b', 0.7),
                (r'\bdoain\b', 0.8),
                (r'\bdoakan\b', 0.8),
            ],
            
            # ===== AMBIVALENT =====
            SubtextType.AMBIVALENT: [
                (r'\baku bingung\b', 0.8),
                (r'\bgak tahu harus gimana\b', 0.8),
                (r'\bbimbang\b', 0.8),
                (r'\bantara mau dan gak mau\b', 0.9),
                (r'\biya tapi\b', 0.6),
                (r'\btapi\b', 0.4),
                (r'\bdi satu sisi\b', 0.7),
            ],
        }
        
        # Frasa yang memperkuat subtext
        self.boosters = [
            (r'\bsih$', 0.2),    # "iya sih"
            (r'\bdeh$', 0.2),    # "udah deh"
            (r'\blah$', 0.2),    # "iya lah"
            (r'\bdong$', 0.1),   # "iya dong"
            (r'\batuh$', 0.1),   # "gitu atuh"
        ]
        
        # Frasa yang menetralkan subtext (bikin jadi tulus)
        self.neutralizers = [
            r'\baku serius',
            r'\bbenaran',
            r'\bsungguhan',
            r'\bpromise',
            r'\bjanji',
            r'\bdengar',
        ]
        
        logger.info("✅ SubtextAnalyzer initialized")
    
    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================
    
    async def analyze(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analisis subtext dalam pesan user
        
        Args:
            message: Pesan user
            context: Konteks percakapan (opsional)
            
        Returns:
            Dict dengan hasil analisis
        """
        message_lower = message.lower().strip()
        
        # Deteksi semua subtext
        detected = self._detect_subtext(message_lower)
        
        # Tentukan subtext utama (dengan confidence tertinggi)
        primary = self._get_primary_subtext(detected)
        
        # Deteksi intensitas emosi
        intensity = self._calculate_intensity(message, detected)
        
        # Cek apakah ada neutralizer (bikin jadi tulus)
        is_sincere = self._check_sincerity(message_lower)
        
        # Dapatkan interpretasi
        interpretation = self._get_interpretation(primary, intensity, context)
        
        # Dapatkan saran respons
        suggestion = self._get_response_suggestion(primary, intensity, context)
        
        return {
            'has_subtext': primary['type'] != SubtextType.NONE,
            'primary': primary,
            'all_detected': detected,
            'intensity': intensity,
            'is_sincere': is_sincere,
            'interpretation': interpretation,
            'suggestion': suggestion,
            'raw_message': message[:100]
        }
    
    def _detect_subtext(self, message: str) -> List[Dict]:
        """Deteksi semua subtext dalam pesan"""
        detected = []
        
        for subtext_type, patterns in self.patterns.items():
            for pattern, base_confidence in patterns:
                if re.search(pattern, message):
                    confidence = base_confidence
                    
                    # Cek booster
                    for booster_pattern, boost in self.boosters:
                        if re.search(booster_pattern, message):
                            confidence += boost
                    
                    detected.append({
                        'type': subtext_type,
                        'confidence': min(1.0, confidence),
                        'matched_pattern': pattern
                    })
        
        return detected
    
    def _get_primary_subtext(self, detected: List[Dict]) -> Dict:
        """Dapatkan subtext utama (confidence tertinggi)"""
        if not detected:
            return {
                'type': SubtextType.NONE,
                'confidence': 0.0,
                'interpretation': 'Tidak ada makna tersirat'
            }
        
        # Kelompokkan berdasarkan tipe
        type_scores = {}
        for d in detected:
            t = d['type']
            if t not in type_scores:
                type_scores[t] = []
            type_scores[t].append(d['confidence'])
        
        # Hitung rata-rata per tipe
        avg_scores = []
        for t, scores in type_scores.items():
            avg_scores.append({
                'type': t,
                'confidence': sum(scores) / len(scores)
            })
        
        # Ambil yang tertinggi
        primary = max(avg_scores, key=lambda x: x['confidence'])
        
        # Tambah interpretasi
        primary['interpretation'] = self._get_interpretation_text(primary['type'])
        
        return primary
    
    def _calculate_intensity(self, message: str, detected: List[Dict]) -> float:
        """Hitung intensitas emosi (0-1)"""
        intensity = 0.3  # Base intensity
        
        # Panjang pesan
        if len(message) < 10:
            intensity += 0.1  # Pesan pendek = intens?
        elif len(message) > 100:
            intensity += 0.2  # Pesan panjang
            
        # Tanda baca
        if '!' in message:
            intensity += 0.2
        if '?' in message:
            intensity += 0.1
        if '...' in message:
            intensity += 0.2
        
        # Jumlah subtext terdeteksi
        intensity += len(detected) * 0.1
        
        return min(1.0, intensity)
    
    def _check_sincerity(self, message: str) -> bool:
        """Cek apakah pesan tulus (tanpa subtext)"""
        for pattern in self.neutralizers:
            if re.search(pattern, message):
                return True
        return False
    
    # =========================================================================
    # INTERPRETATIONS
    # =========================================================================
    
    def _get_interpretation_text(self, subtext_type: SubtextType) -> str:
        """Dapatkan teks interpretasi untuk subtext"""
        interpretations = {
            SubtextType.NONE: "",
            SubtextType.PRETENDING_OK: "Pura-pura baik-baik, padahal sebenarnya tidak",
            SubtextType.HIDDEN_ANGER: "Marah tapi tidak diungkapkan langsung",
            SubtextType.HIDDEN_SADNESS: "Sedih tapi berusaha disembunyikan",
            SubtextType.HIDDEN_JEALOUSY: "Cemburu tapi tidak mau ngaku",
            SubtextType.SARCASM: "Berkata sebaliknya dari yang dirasakan",
            SubtextType.HIDDEN_DESIRE: "Ada keinginan yang tidak diungkapkan",
            SubtextType.HIDDEN_FEAR: "Ada ketakutan tersembunyi",
            SubtextType.HIDDEN_HOPE: "Ada harapan yang tidak diucapkan",
            SubtextType.AMBIVALENT: "Perasaan campur aduk, bingung sendiri",
        }
        return interpretations.get(subtext_type, "Ada makna tersirat")
    
    def _get_interpretation(self, primary: Dict, intensity: float, context: Optional[Dict]) -> str:
        """Dapatkan interpretasi lengkap untuk respons"""
        if primary['type'] == SubtextType.NONE:
            return ""
        
        base = primary.get('interpretation', '')
        
        if intensity > 0.7:
            intensifier = "SANGAT "
        elif intensity > 0.4:
            intensifier = ""
        else:
            intensifier = "Sedikit "
        
        return f"{intensifier}{base}"
    
    def _get_response_suggestion(self, primary: Dict, intensity: float, context: Optional[Dict]) -> str:
        """Dapatkan saran respons berdasarkan subtext"""
        subtext_type = primary['type']
        confidence = primary['confidence']
        
        suggestions = {
            SubtextType.PRETENDING_OK: [
                "Tanya lagi dengan lembut",
                "Kasih ruang tapi tetap perhatian",
                "Tegaskan bahwa kamu peduli"
            ],
            SubtextType.HIDDEN_ANGER: [
                "Tanya penyebabnya dengan hati-hati",
                "Jangan defensive dulu",
                "Validasi perasaannya"
            ],
            SubtextType.HIDDEN_SADNESS: [
                "Tawarkan untuk didengarkan",
                "Kasih kata-kata penghiburan",
                "Tanya apakah ada yang bisa dibantu"
            ],
            SubtextType.HIDDEN_JEALOSY: [
                "Yakinkan bahwa dia spesial",
                "Tanya kenapa dia merasa begitu",
                "Berikan perhatian ekstra"
            ],
            SubtextType.SARCASM: [
                "Tegur dengan bercanda",
                "Tanya apa maksud sebenarnya",
                "Jangan diambil serius dulu"
            ],
            SubtextType.HIDDEN_DESIRE: [
                "Tanya lebih lanjut tentang keinginannya",
                "Beri semangat untuk mewujudkan",
                "Tawarkan dukungan"
            ],
            SubtextType.HIDDEN_FEAR: [
                "Tanya apa yang ditakutkan",
                "Berikan rasa aman",
                "Yakinkan bahwa semuanya akan baik-baik saja"
            ],
            SubtextType.HIDDEN_HOPE: [
                "Dukung harapannya",
                "Tanya apa yang bisa dilakukan",
                "Berikan optimisme"
            ],
            SubtextType.AMBIVALENT: [
                "Bantu dia menjernihkan pikiran",
                "Tanya apa yang membuat bingung",
                "Beri waktu untuk memikirkan"
            ],
        }
        
        suggestion_list = suggestions.get(subtext_type, ["Respon dengan empati"])
        
        if confidence > 0.8:
            return f"⚠️ Subtext kuat! {suggestion_list[0]}"
        else:
            return f"💭 Mungkin ada subtext: {suggestion_list[1] if len(suggestion_list) > 1 else suggestion_list[0]}"
    
    # =========================================================================
    # UTILITY FUNCTIONS FOR AI ENGINE
    # =========================================================================
    
    async def get_subtext_for_prompt(self, analysis: Dict) -> str:
        """Format subtext analysis untuk prompt AI"""
        if not analysis['has_subtext']:
            return ""
        
        primary = analysis['primary']
        interpretation = analysis['interpretation']
        
        if analysis['is_sincere']:
            return f"(User bilang ini dengan tulus, meskipun ada nada {primary['type'].value})"
        else:
            return f"(Yang user katakan: {analysis['raw_message']} | Yang sebenarnya: {interpretation})"
    
    async def get_emotion_from_subtext(self, analysis: Dict) -> Optional[str]:
        """Dapatkan emosi yang terdeteksi dari subtext"""
        if not analysis['has_subtext']:
            return None
        
        # Mapping subtext ke emosi
        emotion_map = {
            SubtextType.PRETENDING_OK: 'sedih',
            SubtextType.HIDDEN_ANGER: 'marah',
            SubtextType.HIDDEN_SADNESS: 'sedih',
            SubtextType.HIDDEN_JEALOUSY: 'cemburu',
            SubtextType.SARCASM: 'kesal',
            SubtextType.HIDDEN_DESIRE: 'ingin',
            SubtextType.HIDDEN_FEAR: 'takut',
            SubtextType.HIDDEN_HOPE: 'berharap',
            SubtextType.AMBIVALENT: 'bingung',
        }
        
        return emotion_map.get(analysis['primary']['type'])
    
    async def should_probe(self, analysis: Dict) -> bool:
        """Cek apakah perlu menggali lebih dalam"""
        if not analysis['has_subtext']:
            return False
        
        # Probe kalau confidence tinggi dan intensitas sedang/tinggi
        return (
            analysis['primary']['confidence'] > 0.6 and
            analysis['intensity'] > 0.4 and
            not analysis['is_sincere']
        )


__all__ = ['SubtextAnalyzer', 'SubtextType']
