"""
Rank and Path System for Ignis Bot.

Defines all progression paths, ranks, and requirements.
This is the source of truth for all rank progression logic.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RankRequirement:
    """Single rank requirement"""
    current_rank: str
    next_rank: str
    exp_required: int
    rank_limit: int  # Visual progress bar limit for this rank
    is_handpicked: bool = False
    additional_requirement: Optional[str] = None  # e.g., "Trial of Obsidian", "2 weeks service"


@dataclass
class Path:
    """Progression path with ranks"""
    name: str
    display_name: str
    ranks: List[RankRequirement]


# ============================================
# PRE-INDUCTION PATH
# Sacred Path of Initiation
# ============================================
PRE_INDUCTION_PATH = Path(
    name="pre_induction",
    display_name="Pre-Induction Path",
    ranks=[
        RankRequirement("Civitas Aspirant", "Emberbound Initiate", 15, rank_limit=20),
        RankRequirement("Emberbound Initiate", "Obsidian Trialborn", 20, rank_limit=35, additional_requirement="Trial of Obsidian"),
        RankRequirement("Obsidian Trialborn", "Crucible Neophyte", 30, rank_limit=50, additional_requirement="Gene-seed implantation"),
        RankRequirement("Crucible Neophyte", "Emberbrand Proving", 40, rank_limit=70, additional_requirement="Field trial success"),
        RankRequirement("Emberbrand Proving", "Inductii", 55, rank_limit=100, additional_requirement="Declared fit for Legionary Path"),
    ]
)

# ============================================
# LEGIONARY PATH
# Sacred Path of the Legion Warrior
# ============================================
LEGIONARY_PATH = Path(
    name="legionary",
    display_name="Legionary Path",
    ranks=[
        RankRequirement("Inductii", "Ashborn Legionary", 70, rank_limit=120, additional_requirement="Basic Training"),
        RankRequirement("Ashborn Legionary", "Flamehardened Veteran", 130, rank_limit=150, additional_requirement="2 weeks service"),
        RankRequirement("Flamehardened Veteran", "Cindershield Sergeant", 130, rank_limit=200, is_handpicked=True),  # Minimum 130, handpicked
        RankRequirement("Cindershield Sergeant", "Emberblade Veteran Sergeant", 200, rank_limit=250, is_handpicked=True),
        RankRequirement("Emberblade Veteran Sergeant", "2nd Lieutenant (Furnace Warden)", 250, rank_limit=300, is_handpicked=True),
        RankRequirement("2nd Lieutenant (Furnace Warden)", "1st Lieutenant (Pyre Watcher)", 300, rank_limit=400, is_handpicked=True),
        RankRequirement("1st Lieutenant (Pyre Watcher)", "Flameborne Captain", 400, rank_limit=600, is_handpicked=False),  # Final rank by points (NOT handpicked)
    ]
)

# ============================================
# ALL PATHS
# ============================================
ALL_PATHS: Dict[str, Path] = {
    "pre_induction": PRE_INDUCTION_PATH,
    "legionary": LEGIONARY_PATH,
}

# Default path for new users
DEFAULT_PATH = "pre_induction"


def get_rank_progress(
    exp: int,
    current_rank: str,
    path_name: str
) -> Tuple[str, int, int, Optional[str], bool]:
    """
    Calculate progress towards next rank.
    
    Args:
        exp: Current EXP points
        current_rank: Current rank name
        path_name: Path identifier
    
    Returns:
        Tuple of:
        - next_rank: Next rank name (or "Max Rank" if at max)
        - exp_in_current: EXP in current rank range (towards next)
        - exp_needed: EXP needed for next rank (from current)
        - additional_req: Additional requirement text (if any)
        - is_handpicked: Whether next rank is handpicked
    """
    if path_name not in ALL_PATHS:
        path_name = DEFAULT_PATH
    
    path = ALL_PATHS[path_name]
    
    # Find current rank in path
    current_idx = -1
    for i, req in enumerate(path.ranks):
        if req.current_rank == current_rank or req.next_rank == current_rank:
            # Found match - use the requirement that leads to this rank
            if req.next_rank == current_rank:
                current_idx = i
            elif req.current_rank == current_rank:
                current_idx = i
            break
    
    # If rank not found, find highest rank user qualifies for based on EXP
    if current_idx == -1:
        # Find highest rank user qualifies for
        for i in range(len(path.ranks) - 1, -1, -1):
            req = path.ranks[i]
            if exp >= req.exp_required:
                current_idx = i
                break
        
        # If still not found, user is below first rank
        if current_idx == -1:
            if path.ranks:
                first_rank = path.ranks[0]
                return (
                    first_rank.next_rank,
                    exp,
                    first_rank.exp_required,
                    first_rank.additional_requirement,
                    first_rank.is_handpicked
                )
    
    # Find next rank
    if current_idx >= len(path.ranks) - 1:
        # At max rank
        return ("Max Rank", 0, 0, None, False)
    
    next_req = path.ranks[current_idx + 1]
    current_req = path.ranks[current_idx]
    
    # Calculate EXP: how much user has towards next rank
    # exp_in_current = how much EXP user has beyond current rank threshold
    # exp_needed = how much EXP needed from current threshold to next threshold
    current_threshold = current_req.exp_required
    next_threshold = next_req.exp_required
    
    exp_in_current = max(0, exp - current_threshold)
    exp_needed = next_threshold - current_threshold
    
    # Clamp exp_in_current to not exceed exp_needed (for display)
    exp_in_current = min(exp_in_current, exp_needed)
    
    return (
        next_req.next_rank,
        exp_in_current,
        exp_needed,
        next_req.additional_requirement,
        next_req.is_handpicked
    )


def get_rank_from_exp(exp: int, path_name: str) -> str:
    """
    Get rank name based on EXP and path.
    Sacred protocol: Flameborne Captain is the final rank by points.
    Handpicked ranks require manual promotion and are not auto-assigned.
    
    Args:
        exp: Current EXP
        path_name: Path identifier
    
    Returns:
        Rank name (never exceeds Flameborne Captain by points alone)
    """
    if path_name not in ALL_PATHS:
        path_name = DEFAULT_PATH
    
    path = ALL_PATHS[path_name]
    
    # Find highest rank user qualifies for (excluding handpicked ranks)
    # Only ranks that can be achieved by points alone
    for req in reversed(path.ranks):
        if exp >= req.exp_required and not req.is_handpicked:
            return req.next_rank
    
    # Check if user qualifies for Flameborne Captain (final rank by points)
    # This is the last rank that can be achieved through points alone
    final_rank_req = path.ranks[-1] if path.ranks else None
    if final_rank_req and exp >= final_rank_req.exp_required and not final_rank_req.is_handpicked:
        return final_rank_req.next_rank  # "Flameborne Captain"
    
    # Below all ranks, return starting rank
    if path.ranks:
        return path.ranks[0].current_rank
    
    return "Civitas Aspirant"


def get_path_display_name(path_name: str) -> str:
    """Get display name for path"""
    if path_name in ALL_PATHS:
        return ALL_PATHS[path_name].display_name
    return "Unknown Path"


def progress_bar(current: int, total: int, width: int = 12) -> str:
    """
    Generate ASCII progress bar with Warhammer terminal aesthetic.
    Sacred protocol: Bar fills completely when current >= total, but displays actual points.
    
    Args:
        current: Current value (can exceed total - shows actual points)
        total: Total/Limit value (cap for visual bar)
        width: Bar width in characters (default: 12 for uniform embed)
    
    Returns:
        Progress bar string with terminal-style brackets
    
    Examples:
        progress_bar(10, 20, 12) -> "│██████░░░░░░│" (50% filled)
        progress_bar(20, 20, 12) -> "│████████████│" (100% filled)
        progress_bar(30, 20, 12) -> "│████████████│" (full, exceeds limit)
        progress_bar(0, 20, 12)   -> "│░░░░░░░░░░░░│" (0% filled)
    """
    # Handle edge cases
    if total <= 0:
        # Invalid total, show full bar
        return f"│{'█' * width}│"
    
    if current < 0:
        # Negative current, show empty bar
        return f"│{'░' * width}│"
    
    # Calculate fill percentage (cap at 100% for visual)
    if current >= total:
        # Bar is full, but we show actual points separately
        filled = width
        empty = 0
    else:
        # Normal progression: calculate percentage and convert to bar width
        percentage = current / total
        filled = int(percentage * width)
        
        # Ensure filled is within bounds
        filled = max(0, min(filled, width))
        
        # For very small percentages, show at least 1 block if current > 0
        if current > 0 and filled == 0 and percentage > 0:
            filled = 1
        
        empty = width - filled
    
    # Warhammer terminal style: │ for borders, █ for filled, ░ for empty
    return f"│{'█' * filled}{'░' * empty}│"


def get_rank_limit(rank: str, path_name: str) -> int:
    """
    Get visual progress bar limit for a rank.
    
    This returns the rank_limit for the rank, which is used as the visual cap
    for the progress bar. The bar will fill completely when points reach this limit,
    but users can continue accumulating points beyond it.
    
    Args:
        rank: Rank name
        path_name: Path identifier
    
    Returns:
        Rank limit (visual bar limit)
    
    Examples:
        get_rank_limit("Civitas Aspirant", "pre_induction") -> 20
        get_rank_limit("Flamehardened Veteran", "legionary") -> 150
    """
    if path_name not in ALL_PATHS:
        path_name = DEFAULT_PATH
    
    path = ALL_PATHS[path_name]
    
    # Find rank in path - check both current_rank and next_rank
    # Priority: check next_rank first (user is at this rank)
    for req in reversed(path.ranks):  # Check from highest to lowest
        if req.next_rank == rank:
            return req.rank_limit
        if req.current_rank == rank:
            return req.rank_limit
    
    # If rank not found, try to find based on starting rank
    if path.ranks and path.ranks[0].current_rank == rank:
        return path.ranks[0].rank_limit
    
    # Default limit if not found (shouldn't happen in normal operation)
    return 20


