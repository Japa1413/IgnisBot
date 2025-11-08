"""
Event Presets - Salamanders-themed event configurations.
"""

# Salamanders-flavored presets. Adjust times/links/role IDs freely.
EVENT_PRESETS = {
    "patrol": {
        "title": "++ Patrol ++",
        "description": "",  # Empty by default, can be added via modal
        "when": "Now",  # Not used in display
        "location": "Averium Invicta",  # Not used in display
        "link": "https://www.roblox.com/games/99813489644549/Averium-Invicta-The-Grave-World",
        "color": 0x2ECC71,  # Salamanders green
        "ping_role_id": 1435800430516113511,  # Patrol role
        "image_url": "https://i.pinimg.com/originals/1d/a0/54/1da054566318e2d46117c8b3e3961877.png",
    },
    "combat_training": {
        "title": "++ Combat Training ++",
        "description": (
            "Intensive combat drills to hone your skills and unit coordination. "
            "Bring your best; the forge masters are watching."
        ),
        "when": "TBD",
        "location": "Training Grounds",
        "link": None,
        "color": 0x27AE60,
        "ping_role_id": None,
        "image_url": "https://i.pinimg.com/originals/27/bd/29/27bd295557639429171cfcb9c322b1cd.jpg",
    },
    "basic_training": {
        "title": "++ Basic Training ++",
        "description": (
            "Foundational training for new recruits and veterans revisiting fundamentals. "
            "Perfect for initiates and those seeking to strengthen their core skills."
        ),
        "when": "TBD",
        "location": "Training Grounds",
        "link": None,
        "color": 0x1ABC9C,
        "ping_role_id": None,
        "image_url": "https://artwork.40k.gallery/wp-content/uploads/2024/08/Salamander-Chaplain-768x981.jpg.webp",
    },
    "internal_raid": {
        "title": "++ Internal Practice Raid ++",
        "description": (
            "Closed-door raid for squad coordination and target calling. "
            "Sharpen your strike in the heat of controlled battle."
        ),
        "when": "TBD",
        "location": "Operations Channel",
        "link": None,
        "color": 0xE74C3C,  # red row
        "ping_role_id": None,
        "image_url": "https://doquizzes.com/wp-content/uploads/2024/10/space-marine-legion-quiz-1728639643.jpg",
    },
    "practice_raid": {
        "title": "++ Practice Raid ++",
        "description": (
            "Open practice raid. New brothers welcome—learn by the flame, "
            "advance by the anvil. Together we stand; divided we fall."
        ),
        "when": "TBD",
        "location": "Operations Channel",
        "link": None,
        "color": 0xC0392B,
        "ping_role_id": None,
        "image_url": "https://i.pinimg.com/474x/9d/90/45/9d90458cfa8b3413d4df97ecc4995a54.jpg",
    },
    "rally": {
        "title": "++ Rally ++",
        "description": (
            "Rapid assembly and briefing. Be present, be ready—Vulkan's sons do not falter. "
            "The call to arms has been sounded; answer with honor."
        ),
        "when": "TBD",
        "location": "Briefing Hall",
        "link": None,
        "color": 0xA93226,
        "ping_role_id": None,
        "image_url": "https://artwork.40k.gallery/wp-content/uploads/2023/12/Salamanders-768x464.jpg.webp",
    },
    "gamenight": {
        "title": "++ Gamenight ++",
        "description": "",
        "when": "TBD",
        "location": "TBD",
        "link": None,
        "color": 0x95A5A6,
        "ping_role_id": None,
        "image_url": "https://i.pinimg.com/originals/97/10/32/9710328fc2d70322bab4d6d05da6e9ba.jpg",
    },
}
