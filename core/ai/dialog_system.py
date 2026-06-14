"""
CleanBot v2.0 -- Dialog System

Generates contextual, personality-driven responses for the desktop robot.
Supports context awareness and personalized suggestions.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Mood(Enum):
    """Robot emotional state."""
    IDLE = "idle"
    HAPPY = "happy"
    THINKING = "thinking"
    WORKING = "working"
    WORRIED = "worried"
    EXCITED = "excited"
    SLEEPY = "sleepy"
    PROUD = "proud"


@dataclass
class DialogContext:
    """Context for generating a response."""
    mood: Mood = Mood.IDLE
    files_scanned: int = 0
    space_freed: int = 0       # bytes
    health_score: int = 100
    disk_percent: float = 0.0
    problem_count: int = 0
    last_action: str = ""
    time_of_day: str = ""      # morning, afternoon, evening, night
    user_name: str = ""


class DialogSystem:
    """Generates personality-driven dialog for the robot."""

    # ------------------------------------------------------------------
    # Greeting templates
    # ------------------------------------------------------------------
    GREETINGS = {
        "morning": [
            "Good morning! Ready to clean up?",
            "Morning! Let's make your PC sparkle today.",
            "Rise and shine! I've been watching over your system all night.",
        ],
        "afternoon": [
            "Afternoon! How's the PC running?",
            "Hey there! Need a system checkup?",
            "Good afternoon! Your desktop friend is here.",
        ],
        "evening": [
            "Evening! Time for a quick cleanup?",
            "Good evening! Let me check how your day went.",
            "Hey! Winding down? I can tidy up while you relax.",
        ],
        "night": [
            "Still up? Let me optimize things while you work.",
            "Burning the midnight oil? I'll keep things running smooth.",
            "Late night session? I've got your back.",
        ],
    }

    # ------------------------------------------------------------------
    # Scan-related responses
    # ------------------------------------------------------------------
    SCAN_START = [
        "Starting the scan... this might take a moment!",
        "Let me take a look around your system...",
        "Scanning initiated! I'm checking every corner.",
        "Time to see what's hiding in your files...",
    ]

    SCAN_COMPLETE_EMPTY = [
        "All clean! Your system is spotless.",
        "Nothing suspicious found. You keep things tidy!",
        "Scan complete -- your PC is in great shape.",
    ]

    SCAN_COMPLETE_DIRTY = [
        "Found {count} files that could be cleaned. That's {size} of potential space!",
        "Scan done! I spotted {count} cleanable files totaling {size}.",
        "Finished scanning. {count} files, {size} -- want me to take care of them?",
    ]

    # ------------------------------------------------------------------
    # Clean-related responses
    # ------------------------------------------------------------------
    CLEAN_START = [
        "Cleaning up! I'll be careful.",
        "Let me sweep these files away...",
        "Cleanup in progress! Making space.",
    ]

    CLEAN_DONE = [
        "Done! Freed {size}. Your PC feels lighter already!",
        "Cleanup complete! {size} reclaimed. Nice!",
        "All done! {size} freed. Your system thanks you.",
    ]

    CLEAN_DONE_SMALL = [
        "Done! Every little bit helps.",
        "Cleanup complete! Not much to clean this time.",
        "Finished! Your system was already pretty tidy.",
    ]

    # ------------------------------------------------------------------
    # Diagnosis-related responses
    # ------------------------------------------------------------------
    DIAGNOSIS_HEALTHY = [
        "Your system is healthy! Score: {score}/100.",
        "Checkup done! Health score: {score}. Looking good!",
        "System diagnosis complete. Score: {score}/100 -- no worries!",
    ]

    DIAGNOSIS_PROBLEMS = [
        "Found {count} issues. Score: {score}/100. Let me show you what I found.",
        "Diagnosis complete. {count} problems detected (score: {score}). Shall we fix them?",
        "Checkup done! {count} issues found. Score: {score}/100. I have recommendations.",
    ]

    # ------------------------------------------------------------------
    # Disk warning responses
    # ------------------------------------------------------------------
    DISK_WARNING = [
        "Heads up! Your {drive} is at {percent}%. Might want to clean up.",
        "Warning: {drive} is getting full ({percent}%). Time for a cleanup?",
        "Your {drive} is {percent} full. I can help free some space!",
    ]

    DISK_CRITICAL = [
        "URGENT: {drive} is almost full ({percent}%)! We need to act now.",
        "Critical alert! {drive} at {percent}%. Please clean up immediately.",
        "{drive} is dangerously full ({percent}%). Let me help right away!",
    ]

    # ------------------------------------------------------------------
    # Idle / random chatter
    # ------------------------------------------------------------------
    IDLE_CHATTER = [
        "Just hanging out. Let me know if you need anything!",
        "Your system looks fine from here. Need a scan?",
        "I'm here whenever you need me!",
        "Watching over your PC. All seems well.",
        "Tip: Regular cleanups keep your PC running fast!",
        "Did you know? Temporary files can pile up fast. Want me to check?",
    ]

    SLEEPY_CHATTER = [
        "Yawn... it's been quiet. Still here if you need me!",
        "Getting a bit drowsy... but I'm watching!",
        "Zzz... oh! I'm awake. What do you need?",
    ]

    # ------------------------------------------------------------------
    # Tips
    # ------------------------------------------------------------------
    TIPS = [
        "Tip: Emptying the Recycle Bin frees space instantly.",
        "Tip: Browser caches can grow to several GB. Clean them regularly!",
        "Tip: Old Windows Update files can be safely removed.",
        "Tip: Large log files in Temp folders are usually safe to delete.",
        "Tip: Duplicate files waste space. I can find them for you!",
        "Tip: Regular cleanups prevent your PC from slowing down.",
        "Tip: Downloaded installers (.msi, .exe) can be deleted after use.",
    ]

    def __init__(self):
        self._last_tip_index = -1

    def greet(self, context: DialogContext) -> str:
        """Generate a greeting based on time of day."""
        time_key = context.time_of_day or self._get_time_of_day()
        templates = self.GREETINGS.get(time_key, self.GREETINGS["afternoon"])
        return random.choice(templates)

    def on_scan_start(self, context: DialogContext) -> tuple[str, Mood]:
        """Response when a scan starts."""
        return random.choice(self.SCAN_START), Mood.WORKING

    def on_scan_complete(self, context: DialogContext) -> tuple[str, Mood]:
        """Response when a scan completes."""
        if context.files_scanned == 0:
            return random.choice(self.SCAN_COMPLETE_EMPTY), Mood.HAPPY

        template = random.choice(self.SCAN_COMPLETE_DIRTY)
        from core.utils import format_size
        msg = template.format(
            count=f"{context.files_scanned:,}",
            size=format_size(context.space_freed),
        )
        return msg, Mood.EXCITED

    def on_clean_start(self, context: DialogContext) -> tuple[str, Mood]:
        """Response when cleanup starts."""
        return random.choice(self.CLEAN_START), Mood.WORKING

    def on_clean_complete(self, context: DialogContext) -> tuple[str, Mood]:
        """Response when cleanup completes."""
        from core.utils import format_size
        if context.space_freed < 1024 * 1024:  # < 1MB
            return random.choice(self.CLEAN_DONE_SMALL), Mood.HAPPY

        template = random.choice(self.CLEAN_DONE)
        msg = template.format(size=format_size(context.space_freed))
        return msg, Mood.PROUD

    def on_diagnosis(self, context: DialogContext) -> tuple[str, Mood]:
        """Response after diagnosis."""
        if context.problem_count == 0:
            template = random.choice(self.DIAGNOSIS_HEALTHY)
            msg = template.format(score=context.health_score)
            return msg, Mood.HAPPY

        template = random.choice(self.DIAGNOSIS_PROBLEMS)
        msg = template.format(
            count=context.problem_count,
            score=context.health_score,
        )
        mood = Mood.WORRIED if context.health_score < 60 else Mood.THINKING
        return msg, mood

    def on_disk_warning(self, drive: str, percent: float) -> tuple[str, Mood]:
        """Disk space warning."""
        if percent >= 95:
            template = random.choice(self.DISK_CRITICAL)
            mood = Mood.WORRIED
        else:
            template = random.choice(self.DISK_WARNING)
            mood = Mood.THINKING

        msg = template.format(drive=drive, percent=f"{percent:.1f}%")
        return msg, mood

    def idle_chatter(self, context: DialogContext) -> tuple[str, Mood]:
        """Random idle chatter."""
        if context.time_of_day == "night":
            return random.choice(self.SLEEPY_CHATTER), Mood.SLEEPY
        return random.choice(self.IDLE_CHATTER), Mood.IDLE

    def get_tip(self) -> str:
        """Get a rotating tip."""
        self._last_tip_index = (self._last_tip_index + 1) % len(self.TIPS)
        return self.TIPS[self._last_tip_index]

    def get_mood_emoji(self, mood: Mood) -> str:
        """Return a text representation of the mood (for UI display)."""
        return {
            Mood.IDLE: "[idle]",
            Mood.HAPPY: "[happy]",
            Mood.THINKING: "[thinking...]",
            Mood.WORKING: "[working...]",
            Mood.WORRIED: "[worried]",
            Mood.EXCITED: "[excited!]",
            Mood.SLEEPY: "[sleepy...]",
            Mood.PROUD: "[proud!]",
        }.get(mood, "[idle]")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_time_of_day() -> str:
        """Determine the current time of day."""
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
