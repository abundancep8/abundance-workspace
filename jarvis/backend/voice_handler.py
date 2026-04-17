"""
Voice Handler - TTS + Audio-Reactive Orb Visualization
Manages voice input/output and real-time neural orb deformation.
"""
import base64
import asyncio
from typing import Dict, Optional, Tuple
import logging
import math

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

logger = logging.getLogger(__name__)

class VoiceHandler:
    """
    Manages voice I/O and audio-reactive visualization.
    """
    
    def __init__(self):
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Natural speaking rate
                self.engine.setProperty('volume', 0.9)
            except Exception as e:
                logger.warning(f"pyttsx3 initialization failed: {e}")
        
        self.orb_state = {
            "position": [0, 0, 0],
            "scale": 1.0,
            "rotation": [0, 0, 0],
            "color": "#0099FF",
            "intensity": 0.5,
            "neural_firing": []
        }
    
    async def transcribe(self, audio_data: str) -> str:
        """
        Transcribe audio input.
        In production: integrate with Whisper API or local model.
        """
        # For MVP: return placeholder
        # In production, decode audio_data (base64) and transcribe
        logger.info("🎙️ Processing audio input...")
        
        # Simulated transcription - in prod use Whisper API
        return "[transcribed audio would go here]"
    
    async def synthesize(self, text: str) -> Optional[str]:
        """
        Convert text to speech.
        Returns: base64-encoded audio file or None if unavailable.
        """
        if not text:
            return None
        
        if self.engine is None:
            logger.warning("TTS engine not available - skipping audio synthesis")
            return None
        
        try:
            # Generate audio file
            output_file = "/tmp/jarvis_response.wav"
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            
            # Read and encode
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
                audio_b64 = base64.b64encode(audio_bytes).decode()
            
            logger.info(f"✅ TTS: Generated {len(audio_bytes)} bytes")
            return audio_b64
        
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return None
    
    def calculate_orb_state(self, intensity: float, text: str = "") -> Dict:
        """
        Calculate real-time orb state based on:
        - Audio intensity
        - Text content (sentiment, complexity)
        - Neural activity patterns
        """
        # Normalize intensity (0-1)
        intensity = max(0, min(1, intensity))
        
        # Scale orb based on intensity
        scale = 1.0 + (intensity * 0.5)
        
        # Rotation based on intensity
        rotation_speed = intensity * 360
        
        # Color shift based on intensity
        if intensity < 0.33:
            color = "#0099FF"  # Blue (calm)
        elif intensity < 0.66:
            color = "#00FF99"  # Green (engaged)
        else:
            color = "#FF0099"  # Pink/red (active)
        
        # Neural firing pattern based on text complexity
        neural_firing = self._generate_neural_pattern(text, intensity)
        
        # Update orb state
        self.orb_state = {
            "position": [0, 0, 0],
            "scale": scale,
            "rotation": [rotation_speed, rotation_speed * 0.7, rotation_speed * 0.5],
            "color": color,
            "intensity": round(intensity, 2),
            "neural_firing": neural_firing,
            "pulse": self._calculate_pulse(intensity)
        }
        
        return self.orb_state
    
    def _generate_neural_pattern(self, text: str = "", intensity: float = 0.5) -> list:
        """
        Generate visual neural firing pattern.
        Based on text processing + intensity.
        """
        pattern = []
        
        # Text complexity drives neuron count
        word_count = len(text.split()) if text else 0
        neuron_count = min(20, 5 + word_count // 10)
        
        # Generate random firing positions weighted by intensity
        import random
        for i in range(neuron_count):
            if random.random() < intensity:
                pattern.append({
                    "x": random.uniform(-1, 1),
                    "y": random.uniform(-1, 1),
                    "z": random.uniform(-1, 1),
                    "brightness": random.uniform(intensity * 0.5, 1.0),
                    "duration": random.uniform(0.1, 0.5)
                })
        
        return pattern
    
    def _calculate_pulse(self, intensity: float) -> Dict:
        """Calculate orb pulse animation parameters."""
        return {
            "frequency": 2 + (intensity * 4),  # Hz
            "amplitude": 0.2 + (intensity * 0.3),  # Scale oscillation
            "wave_type": "sine"
        }
    
    def get_current_state(self) -> Dict:
        """Get current orb visualization state."""
        return self.orb_state.copy()
    
    def reset_state(self):
        """Reset orb to idle state."""
        self.orb_state = {
            "position": [0, 0, 0],
            "scale": 1.0,
            "rotation": [0, 0, 0],
            "color": "#0099FF",
            "intensity": 0.3,
            "neural_firing": [],
            "pulse": {"frequency": 2, "amplitude": 0.1, "wave_type": "sine"}
        }

# Audio-reactive visualization helpers
class OrbVisualizer:
    """
    Helper for WebGL orb animations.
    Generates visualization parameters for Three.js frontend.
    """
    
    @staticmethod
    def generate_vertex_deformation(intensity: float, time: float) -> Tuple[list, list]:
        """
        Generate vertex displacement data for orb deformation.
        
        Returns: (vertices, colors) for Three.js
        """
        vertices = []
        colors = []
        
        # Base icosphere vertices
        segments = 8
        
        for i in range(segments):
            theta = (i / segments) * math.pi * 2
            for j in range(segments):
                phi = (j / segments) * math.pi
                
                # Base sphere coords
                x = math.sin(phi) * math.cos(theta)
                y = math.cos(phi)
                z = math.sin(phi) * math.sin(theta)
                
                # Deformation based on intensity and time
                deformation = intensity * math.sin(time + (i + j)) * 0.3
                scale = 1.0 + deformation
                
                vertices.extend([x * scale, y * scale, z * scale])
                
                # Color based on position + intensity
                r = 0.0 + (intensity * 0.5)
                g = 0.6 + (intensity * 0.3)
                b = 1.0 - (intensity * 0.2)
                colors.extend([r, g, b])
        
        return vertices, colors
    
    @staticmethod
    def generate_particle_effect(intensity: float, count: int = 50) -> list:
        """
        Generate particle positions for neural firing visualization.
        """
        import random
        particles = []
        
        for _ in range(count):
            if random.random() < intensity:
                particles.append({
                    "x": random.uniform(-2, 2),
                    "y": random.uniform(-2, 2),
                    "z": random.uniform(-2, 2),
                    "vx": random.uniform(-1, 1) * intensity,
                    "vy": random.uniform(-1, 1) * intensity,
                    "vz": random.uniform(-1, 1) * intensity,
                    "life": random.uniform(0.5, 1.5),
                    "color": [
                        random.uniform(0.3, 1.0),
                        random.uniform(0.6, 1.0),
                        random.uniform(0.8, 1.0)
                    ]
                })
        
        return particles
