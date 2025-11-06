"""
Event Presets - Salamanders-themed event configurations.
"""

# Salamanders-flavored presets. Adjust times/links/role IDs freely.
EVENT_PRESETS = {
    "patrol": {
        "title": "++ PATROL ++",
        "description": "",  # Empty by default, can be added via modal
        "when": "Now",  # Not used in display
        "location": "Averium Invicta",  # Not used in display
        "link": "https://www.roblox.com/games/99813489644549/Averium-Invicta-The-Grave-World",
        "color": 0x2ECC71,  # Salamanders green
        "ping_role_id": 1435800430516113511,  # Patrol role
        "image_url": "https://i.pinimg.com/originals/1d/a0/54/1da054566318e2d46117c8b3e3961877.png",
    },
    "combat_training": {
        "title": "⚔️ Combat Training",
        "description": (
            "Intensive combat drills to hone your skills and unit coordination. "
            "Bring your best; the forge masters are watching."
        ),
        "when": "TBD",
        "location": "Training Grounds",
        "link": None,
        "color": 0x27AE60,
        "ping_role_id": None,
        "image_url": "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294",
    },
    "basic_training": {
        "title": "🛠️ Basic Training",
        "description": (
            "Foundational training for new recruits and veterans revisiting fundamentals. "
            "Perfect for initiates and those seeking to strengthen their core skills."
        ),
        "when": "TBD",
        "location": "Training Grounds",
        "link": None,
        "color": 0x1ABC9C,
        "ping_role_id": None,
        "image_url": "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294",
    },
    "internal_raid": {
        "title": "⚔️ Internal Practice Raid",
        "description": (
            "Closed-door raid for squad coordination and target calling. "
            "Sharpen your strike in the heat of controlled battle."
        ),
        "when": "TBD",
        "location": "Operations Channel",
        "link": None,
        "color": 0xE74C3C,  # red row
        "ping_role_id": None,
        "image_url": "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294",
    },
    "practice_raid": {
        "title": "⚔️ Practice Raid",
        "description": (
            "Open practice raid. New brothers welcome—learn by the flame, "
            "advance by the anvil. Together we stand; divided we fall."
        ),
        "when": "TBD",
        "location": "Operations Channel",
        "link": None,
        "color": 0xC0392B,
        "ping_role_id": None,
        "image_url": "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294",
    },
    "rally": {
        "title": "🔥 Rally",
        "description": (
            "Rapid assembly and briefing. Be present, be ready—Vulkan's sons do not falter. "
            "The call to arms has been sounded; answer with honor."
        ),
        "when": "TBD",
        "location": "Briefing Hall",
        "link": None,
        "color": 0xA93226,
        "ping_role_id": None,
        "image_url": "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294",
    },
}
