"""
CleanBot v3.0 -- Advanced Dialog System

Enhanced dialog system with:
- Optimization suggestions
- System health feedback
- Personalized recommendations
- Context-aware responses
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict


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
    CONCERNED = "concerned"
    OPTIMISTIC = "optimistic"


@dataclass
class AdvancedDialogContext:
    """Advanced context for generating responses."""
    mood: Mood = Mood.IDLE
    files_scanned: int = 0
    space_freed: int = 0
    health_score: int = 100
    disk_percent: float = 0.0
    memory_percent: float = 0.0
    cpu_percent: float = 0.0
    problem_count: int = 0
    startup_items: int = 0
    services_running: int = 0
    last_action: str = ""
    time_of_day: str = ""
    user_name: str = ""
    optimization_score: int = 0


class AdvancedDialogSystem:
    """Advanced dialog system with optimization feedback."""

    # Optimization feedback templates
    OPTIMIZATION_START = [
        "Starting system optimization... this will make your PC faster!",
        "Let me optimize your system for better performance...",
        "Optimization initiated! I'll make your PC run smoother.",
        "Time to tune up your system... this will be worth it!",
    ]

    OPTIMIZATION_COMPLETE = [
        "Optimization complete! Your PC should feel {improvement} now.",
        "Done! I've optimized your system. {improvement} improvement detected.",
        "All optimized! Your PC is now running {improvement} than before.",
        "Optimization finished! {improvement} performance boost achieved.",
    ]

    OPTIMIZATION_PARTIAL = [
        "Partial optimization complete. {remaining} items still need attention.",
        "I've optimized what I could. {remaining} items require your decision.",
        "Some optimizations applied. {remaining} items need manual review.",
    ]

    # Startup optimization feedback
    STARTUP_OPTIMIZED = [
        "Disabled {count} startup items. Your PC will boot {speed} now!",
        "Startup optimized! {count} items disabled. Boot time reduced by {speed}.",
        "Done! {count} startup items disabled. Expect {speed} faster boot.",
    ]

    # Service optimization feedback
    SERVICE_OPTIMIZED = [
        "Optimized {count} services. Memory usage reduced by {memory}.",
        "Service optimization complete! {count} services adjusted, {memory} freed.",
        "Done! {count} services optimized, freeing up {memory} of resources.",
    ]

    # Memory optimization feedback
    MEMORY_OPTIMIZED = [
        "Memory optimized! Freed {memory} of RAM.",
        "Memory cleanup complete! {memory} of RAM now available.",
        "Done! {memory} of memory reclaimed. Your PC feels lighter!",
    ]

    # Registry cleaning feedback
    REGISTRY_CLEANED = [
        "Cleaned {count} registry entries. System should be more stable.",
        "Registry cleanup complete! {count} invalid entries removed.",
        "Done! {count} registry issues fixed. System stability improved.",
    ]

    # Health check feedback
    HEALTH_EXCELLENT = [
        "Your system is in excellent health! Score: {score}/100.",
        "System health: {score}/100. Everything is running perfectly!",
        "Excellent! Health score: {score}/100. Your PC is in top shape.",
    ]

    HEALTH_GOOD = [
        "System health is good. Score: {score}/100.",
        "Health score: {score}/100. Minor improvements possible.",
        "Good condition! Score: {score}/100. A few tweaks could help.",
    ]

    HEALTH_FAIR = [
        "System health is fair. Score: {score}/100. Some attention needed.",
        "Health score: {score}/100. I recommend running optimizations.",
        "Fair condition. Score: {score}/100. Let me help improve it.",
    ]

    HEALTH_POOR = [
        "System health needs attention. Score: {score}/100.",
        "Health score: {score}/100. Your PC needs some care.",
        "Poor condition detected. Score: {score}/100. Let's fix this together.",
    ]

    # Performance tips
    PERFORMANCE_TIPS = [
        "Tip: Disable startup programs you don't use daily.",
        "Tip: Regular memory cleanup keeps your PC responsive.",
        "Tip: A clean registry means fewer system errors.",
        "Tip: Disable unnecessary services to free up resources.",
        "Tip: Monitor disk space to prevent performance degradation.",
        "Tip: Regular optimization prevents gradual slowdown.",
        "Tip: Keep only essential programs running at startup.",
        "Tip: Clean temporary files weekly for best performance.",
    ]

    # Warning messages
    WARNING_HIGH_MEMORY = [
        "Warning: Memory usage is at {percent}%. Consider closing some programs.",
        "High memory usage detected ({percent}%). Some programs may be slow.",
        "Memory is {percent}% full. I recommend optimizing now.",
    ]

    WARNING_HIGH_DISK = [
        "Warning: Disk {drive} is {percent}% full. Time to clean up!",
        "Disk space warning: {drive} at {percent}%. Cleanup recommended.",
        "Your {drive} drive is {percent}% full. Let me help free space.",
    ]

    WARNING_SLOW_BOOT = [
        "Your PC takes {time} to boot. I can help speed it up!",
        "Boot time is {time}. Startup optimization could help.",
        "Slow boot detected ({time}). Want me to optimize startup?",
    ]

    def __init__(self):
        self._last_tip_index = -1
        self._conversation_history: List[Dict] = []

    def on_optimization_start(self, context: AdvancedDialogContext) -> tuple[str, Mood]:
        """Response when optimization starts."""
        return random.choice(self.OPTIMIZATION_START), Mood.WORKING

    def on_optimization_complete(self, context: AdvancedDialogContext, improvement: str) -> tuple[str, Mood]:
        """Response when optimization completes."""
        template = random.choice(self.OPTIMIZATION_COMPLETE)
        msg = template.format(improvement=improvement)
        return msg, Mood.PROUD

    def on_optimization_partial(self, context: AdvancedDialogContext, remaining: int) -> tuple[str, Mood]:
        """Response when partial optimization completes."""
        template = random.choice(self.OPTIMIZATION_PARTIAL)
        msg = template.format(remaining=remaining)
        return msg, Mood.CONCERNED

    def on_startup_optimized(self, count: int, speed: str) -> tuple[str, Mood]:
        """Response when startup is optimized."""
        template = random.choice(self.STARTUP_OPTIMIZED)
        msg = template.format(count=count, speed=speed)
        return msg, Mood.EXCITED

    def on_service_optimized(self, count: int, memory: str) -> tuple[str, Mood]:
        """Response when services are optimized."""
        template = random.choice(self.SERVICE_OPTIMIZED)
        msg = template.format(count=count, memory=memory)
        return msg, Mood.HAPPY

    def on_memory_optimized(self, memory: str) -> tuple[str, Mood]:
        """Response when memory is optimized."""
        template = random.choice(self.MEMORY_OPTIMIZED)
        msg = template.format(memory=memory)
        return msg, Mood.HAPPY

    def on_registry_cleaned(self, count: int) -> tuple[str, Mood]:
        """Response when registry is cleaned."""
        template = random.choice(self.REGISTRY_CLEANED)
        msg = template.format(count=count)
        return msg, Mood.HAPPY

    def on_health_check(self, context: AdvancedDialogContext) -> tuple[str, Mood]:
        """Response after health check."""
        score = context.health_score

        if score >= 90:
            template = random.choice(self.HEALTH_EXCELLENT)
            mood = Mood.HAPPY
        elif score >= 70:
            template = random.choice(self.HEALTH_GOOD)
            mood = Mood.OPTIMISTIC
        elif score >= 50:
            template = random.choice(self.HEALTH_FAIR)
            mood = Mood.CONCERNED
        else:
            template = random.choice(self.HEALTH_POOR)
            mood = Mood.WORRIED

        msg = template.format(score=score)
        return msg, mood

    def on_memory_warning(self, percent: float) -> tuple[str, Mood]:
        """Memory usage warning."""
        template = random.choice(self.WARNING_HIGH_MEMORY)
        msg = template.format(percent=f"{percent:.1f}")
        return msg, Mood.WORRIED

    def on_disk_warning(self, drive: str, percent: float) -> tuple[str, Mood]:
        """Disk space warning."""
        template = random.choice(self.WARNING_HIGH_DISK)
        msg = template.format(drive=drive, percent=f"{percent:.1f}")
        return msg, Mood.WORRIED

    def on_slow_boot_warning(self, boot_time: str) -> tuple[str, Mood]:
        """Slow boot warning."""
        template = random.choice(self.WARNING_SLOW_BOOT)
        msg = template.format(time=boot_time)
        return msg, Mood.CONCERNED

    def get_performance_tip(self) -> str:
        """Get a rotating performance tip."""
        self._last_tip_index = (self._last_tip_index + 1) % len(self.PERFORMANCE_TIPS)
        return self.PERFORMANCE_TIPS[self._last_tip_index]

    def get_optimization_summary(self, context: AdvancedDialogContext) -> str:
        """Get optimization summary."""
        lines = []

        if context.startup_items > 0:
            lines.append(f"• Startup: {context.startup_items} items optimized")

        if context.services_running > 0:
            lines.append(f"• Services: {context.services_running} services adjusted")

        if context.memory_percent > 0:
            lines.append(f"• Memory: {context.memory_percent:.1f}% usage")

        if context.disk_percent > 0:
            lines.append(f"• Disk: {context.disk_percent:.1f}% usage")

        if context.space_freed > 0:
            from core.utils import format_size
            lines.append(f"• Space freed: {format_size(context.space_freed)}")

        if not lines:
            return "No optimizations performed yet."

        return "Optimization Summary:\n" + "\n".join(lines)

    def get_health_report(self, context: AdvancedDialogContext) -> str:
        """Get detailed health report."""
        score = context.health_score

        if score >= 90:
            status = "Excellent"
            recommendation = "Keep up the good work!"
        elif score >= 70:
            status = "Good"
            recommendation = "Consider minor optimizations."
        elif score >= 50:
            status = "Fair"
            recommendation = "Optimization recommended."
        else:
            status = "Needs Attention"
            recommendation = "Immediate optimization suggested."

        return f"""
System Health Report
====================
Health Score: {score}/100
Status: {status}

Current Metrics:
• CPU Usage: {context.cpu_percent:.1f}%
• Memory Usage: {context.memory_percent:.1f}%
• Disk Usage: {context.disk_percent:.1f}%
• Problems Found: {context.problem_count}

Recommendation: {recommendation}
"""
