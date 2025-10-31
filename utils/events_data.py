# utils/events_data.py

# You can freely add/edit events here or load this from a JSON/DB later.
EVENTS_CATALOG = {
    "patrol": {
        "title": "Patrol Operation",
        "date_hint": "Today, 20:00 (server time)",      # free text; you can replace later
        "location": "Main Discord VC + In-Game",
        "description": (
            "Standard patrol to ensure readiness and discipline. "
            "Attendance will be recorded."
        ),
        "link": "https://discord.com",
        "color": 0x2ecc71,  # green
        "ping_role_id": 1376831480931815424 # set a role ID if you want to ping (e.g., 123456789012345678)
    },
    "combat_training": {
        "title": "Combat Training",
        "date_hint": "Tomorrow, 19:30",
        "location": "Training Grounds",
        "description": (
            "Live-fire exercises and formation drills. Come prepared."
        ),
        "link": "https://discord.com",
        "color": 0xe74c3c,  # red
        "ping_role_id": None
    },
    "game_night": {
        "title": "Community Game Night",
        "date_hint": "Saturday, 21:00",
        "location": "Community VC",
        "description": (
            "Relaxed session with mini-games, giveaways, and fun!"
        ),
        "link": "https://discord.com",
        "color": 0xf1c40f,  # yellow
        "ping_role_id": None
    },
    # Add more event templates below
    # "custom_key": {...}
}
