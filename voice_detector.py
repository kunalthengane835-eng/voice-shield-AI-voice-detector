"""
Advanced AI Voice Detector Module
Detects AI-generated voices and scam patterns in audio files using multiple detection algorithms
"""
import os
import numpy as np
import librosa
from scipy import stats, signal
import json
import warnings
warnings.filterwarnings('ignore')


class VoiceDetector:
    def __init__(self, sample_rate=22050, n_fft=2048, hop_length=512):
        """
        Initialize the voice detector with parameters
        
        Args:
            sample_rate: Target sample rate for audio processing
            n_fft: FFT window size
            hop_length: Number of samples between frames
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.ai_detection_threshold = 0.6
    
    def detect_ai_voice(self, audio_path):
        """
        Detect if voice is AI-generated and identify scam patterns
        
        Args:
            audio_path: Path to the audio file
        
        Returns:
            dict: Analysis results with detection scores and patterns
        """
        try:
            # Load audio file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Extract audio features
            features = self._extract_features(audio_path)
            
            # Analyze for AI generation
            ai_detection = self._analyze_ai_indicators(features)
            
            # Detect scam patterns (transcription would be needed for full analysis)
            scam_patterns = self._detect_scam_patterns(features)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(ai_detection, scam_patterns)
            
            # Determine if AI-generated (using threshold)
            is_ai_generated = confidence > self.ai_detection_threshold
            
            return {
                'is_ai_generated': is_ai_generated,
                'confidence': float(confidence),
                'scam_patterns': scam_patterns,
                'details': {
                    'spectral_features': ai_detection,
                    'audio_duration': features.get('duration', 0),
                    'sample_rate': features.get('sample_rate', 0)
                }
            }
        
        except Exception as e:
            # Return default values on error
            return {
                'is_ai_generated': False,
                'confidence': 0.5,
                'scam_patterns': [],
                'details': {'error': str(e)}
            }
    
    def _extract_features(self, audio_path):
        """
        Extract comprehensive audio features for analysis
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            dict: Extracted audio features
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate, duration=None)
            
            # Basic audio properties
            duration = len(y) / sr
            
            # Spectral features
            stft = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            power = magnitude ** 2
            
            # Spectral centroid (brightness/timbre)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Spectral rolloff (high-frequency content)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Spectral bandwidth (timbre width)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Zero crossing rate (noisiness/periodicity)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCC (Mel-frequency cepstral coefficients) - voice characteristics
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Chroma features (pitch class)
            chroma = librosa.feature.chroma_stft(S=power, sr=sr)
            
            # Spectral contrast (harmonic vs noise)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            
            # Tempo and rhythm (if applicable)
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            except:
                tempo = 0
            
            # Harmonic and percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_ratio = np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y_harmonic)) + np.mean(np.abs(y_percussive)) + 1e-10)
            
            # Pitch tracking (fundamental frequency)
            try:
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            except:
                pitch_mean = 0
            
            # RMS energy (loudness)
            rms = librosa.feature.rms(y=y)[0]
            
            return {
                'duration': float(duration),
                'sample_rate': int(sr),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'zcr_mean': float(np.mean(zcr)),
                'zcr_std': float(np.std(zcr)),
                'mfcc_mean': [float(x) for x in np.mean(mfccs, axis=1)],
                'mfcc_std': [float(x) for x in np.std(mfccs, axis=1)],
                'chroma_mean': [float(x) for x in np.mean(chroma, axis=1)],
                'spectral_contrast_mean': [float(x) for x in np.mean(spectral_contrast, axis=1)],
                'audio_energy': float(np.mean(power)),
                'audio_energy_std': float(np.std(power)),
                'rms_mean': float(np.mean(rms)),
                'rms_std': float(np.std(rms)),
                'tempo': float(tempo),
                'harmonic_ratio': float(harmonic_ratio),
                'pitch_mean': float(pitch_mean)
            }
        
        except Exception as e:
            raise Exception(f"Feature extraction failed: {str(e)}")
    
    def _analyze_ai_indicators(self, features):
        """
        Advanced analysis for AI generation indicators using multiple algorithms
        
        Args:
            features: Dictionary of audio features
        
        Returns:
            dict: AI detection indicators and scores
        """
        ai_scores = {
            'spectral_regularity': 0.0,
            'temporal_regularity': 0.0,
            'naturalness': 0.0,
            'harmonic_stability': 0.0,
            'formant_consistency': 0.0,
            'prosody_analysis': 0.0,
            'overall_ai_score': 0.0
        }
        
        try:
            # 1. Spectral Regularity Analysis
            # AI-generated voices often have more regular spectral patterns
            spectral_centroid_std = features.get('spectral_centroid_std', 0)
            if spectral_centroid_std < 500:  # Threshold for regularity
                ai_scores['spectral_regularity'] = min(1.0, (500 - spectral_centroid_std) / 500)
            
            # 2. Temporal Regularity Analysis
            # AI voices may have less variation in zero crossing rate
            zcr_std = features.get('zcr_std', 0)
            if zcr_std < 0.01:
                ai_scores['temporal_regularity'] = min(1.0, (0.01 - zcr_std) / 0.01)
            
            # 3. Naturalness Analysis (MFCC consistency)
            # Human voices have more variation in MFCC coefficients
            mfcc_std = features.get('mfcc_std', [])
            if mfcc_std:
                avg_mfcc_std = np.mean(mfcc_std)
                if avg_mfcc_std < 2.0:  # Lower variation might indicate AI
                    ai_scores['naturalness'] = min(1.0, (2.0 - avg_mfcc_std) / 2.0)
            
            # 4. Harmonic Stability Analysis
            # AI voices may have more stable harmonics
            spectral_contrast = features.get('spectral_contrast_mean', [])
            if spectral_contrast:
                contrast_variance = np.var(spectral_contrast)
                if contrast_variance < 10:  # Low variance indicates stability (possible AI)
                    ai_scores['harmonic_stability'] = min(1.0, (10 - contrast_variance) / 10)
            
            # 5. Formant Consistency (using spectral centroid)
            # Human voices have more formant variation
            spectral_centroid_mean = features.get('spectral_centroid_mean', 0)
            spectral_centroid_std = features.get('spectral_centroid_std', 0)
            if spectral_centroid_mean > 0:
                coefficient_of_variation = spectral_centroid_std / spectral_centroid_mean
                if coefficient_of_variation < 0.1:  # Low CV indicates consistency (possible AI)
                    ai_scores['formant_consistency'] = min(1.0, (0.1 - coefficient_of_variation) / 0.1)
            
            # 6. Prosody Analysis (using energy variation)
            # Human speech has more natural energy variations
            audio_energy_std = features.get('audio_energy_std', 0)
            audio_energy = features.get('audio_energy', 0)
            if audio_energy > 0:
                energy_cv = audio_energy_std / audio_energy
                if energy_cv < 0.3:  # Low energy variation might indicate AI
                    ai_scores['prosody_analysis'] = min(1.0, (0.3 - energy_cv) / 0.3)
            
            # Calculate overall AI score (weighted average of all indicators)
            ai_scores['overall_ai_score'] = (
                ai_scores['spectral_regularity'] * 0.25 +
                ai_scores['temporal_regularity'] * 0.20 +
                ai_scores['naturalness'] * 0.20 +
                ai_scores['harmonic_stability'] * 0.15 +
                ai_scores['formant_consistency'] * 0.10 +
                ai_scores['prosody_analysis'] * 0.10
            )
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
        
        return ai_scores
    
    def _detect_scam_patterns(self, features):
        """
        Detect potential scam patterns in audio
        Note: Full scam detection would require transcription and NLP
        
        Args:
            features: Dictionary of audio features
        
        Returns:
            list: Detected scam patterns
        """
        patterns = []
        
        try:
            # Detect high energy/urgency (potential urgency tactics)
            audio_energy = features.get('audio_energy', 0)
            if audio_energy > 0.1:  # Threshold for high energy
                patterns.append({
                    'type': 'high_energy',
                    'description': 'High audio energy detected (possible urgency tactics)',
                    'confidence': min(1.0, audio_energy * 10)
                })
            
            # Detect rapid speech (potential pressure tactics)
            # This is a simplified check; full analysis would require speech rate calculation
            duration = features.get('duration', 0)
            if duration > 0 and duration < 30:  # Very short calls might be suspicious
                patterns.append({
                    'type': 'short_duration',
                    'description': 'Very short call duration',
                    'confidence': 0.3
                })
            
            # Note: Real scam pattern detection would require:
            # 1. Speech-to-text transcription
            # 2. NLP analysis for keywords like "urgent", "immediately", "verify", etc.
            # 3. Sentiment analysis
            # 4. Conversation flow analysis
            
        except Exception as e:
            print(f"Error in scam pattern detection: {str(e)}")
        
        return patterns
    
    def _calculate_confidence(self, ai_detection, scam_patterns):
        """
        Calculate overall confidence score for AI detection
        
        Args:
            ai_detection: Dictionary of AI detection scores
            scam_patterns: List of detected scam patterns
        
        Returns:
            float: Confidence score between 0 and 1
        """
        base_confidence = ai_detection.get('overall_ai_score', 0.5)
        
        # Adjust confidence based on scam patterns
        pattern_bonus = len(scam_patterns) * 0.1
        confidence = min(1.0, base_confidence + pattern_bonus)
        
        return confidence
