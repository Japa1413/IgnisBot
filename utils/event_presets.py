# utils/event_presets.py

# Salamanders-flavored presets. Adjust times/links/role IDs freely.
EVENT_PRESETS = {
    "rite_of_flame": {
        "title": "Rite of Flame",
        "description": (
            "Initiatory rite to temper spirit and steel. "
            "Stand firm in the fire and prove your resolve."
        ),
        "when": "Today, 20:00 (server time)",
        "location": "Forge-Temple VC + In-Game",
        "link": None,
        "color": 0x2ECC71,  # Salamanders green
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",  # replace with your art/banner
    },
    "forge_drill": {
        "title": "Forge Drill",
        "description": (
            "Formation practice and live drills to refine discipline. "
            "Bring your best; the forge masters are watching."
        ),
        "when": "Tomorrow, 19:30",
        "location": "Drill Yard",
        "link": None,
        "color": 0x27AE60,
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    "promethean_training": {
        "title": "Promethean Training",
        "description": (
            "Foundational maneuvers, unit cohesion, and Promethean creed. "
            "Perfect for initiates and veterans revisiting fundamentals."
        ),
        "when": "Saturday, 18:00",
        "location": "Nocturne Quadrangle",
        "link": None,
        "color": 0x1ABC9C,
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    "internal_raid": {
        "title": "Internal Practice Raid",
        "description": (
            "Closed-door raid for squad coordination and target calling. "
            "Sharpen your strike in the heat of controlled battle."
        ),
        "when": "Friday, 21:00",
        "location": "Operations Channel",
        "link": None,
        "color": 0xE74C3C,  # red row
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    "practice_raid": {
        "title": "Practice Raid",
        "description": (
            "Open practice raid. New brothers welcome—learn by the flame, "
            "advance by the anvil."
        ),
        "when": "Sunday, 20:00",
        "location": "Operations Channel",
        "link": None,
        "color": 0xC0392B,
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    "forge_muster": {
        "title": "Forge Muster",
        "description": (
            "Rapid assembly and briefing. Be present, be ready—Vulkan’s sons do not falter."
        ),
        "when": "Soon™",
        "location": "Briefing Hall",
        "link": None,
        "color": 0xA93226,
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    "hearthfire_night": {
        "title": "Hearthfire Night",
        "description": (
            "Community game night—stories, laughter, and friendly challenges. "
            "Lay down the hammer and rest by the fire."
        ),
        "when": "Saturday, 21:00",
        "location": "Hearthfire VC",
        "link": None,
        "color": 0x95A5A6,  # grey row
        "ping_role_id": None,
        "image_url": "https://i.imgur.com/4QxE7bI.png",
    },
    # "custom" will be handled in the UI and can call your util with user-provided fields later.
}