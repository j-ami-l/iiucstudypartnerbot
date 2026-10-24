"""Internationalization (i18n) strings for SnapStudy AI in English and Bangla."""

from typing import Dict, Any

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "welcome": (
            "👋 <b>Welcome to SnapStudy AI!</b>\n\n"
            "Send me a clear photo of your handwritten notes, textbook page, "
            "or lecture slide 📷\n\n"
            "Gemma 4 will analyze your notes, summarize key points, explain "
            "difficult terms, and generate a 5-question practice quiz!"
        ),
        "help": (
            "📖 <b>How to use SnapStudy AI:</b>\n\n"
            "1. Take a clear, well-lit photo of your study material.\n"
            "2. Send it here as a photo or image document.\n"
            "3. I will read your notes and generate a study summary and quiz.\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - Instructions"
        ),
        "reading_notes": "⏳ Reading your notes…",
        "photo_received": "✅ Got your photo ({width}x{height}, {size_kb:.1f} KB)",
        "send_photo_prompt": "Send me a photo of your notes 📷",
        "invalid_file": "Please send a valid image file of your notes (JPEG or PNG).",
        "error_generic": "Something went wrong while processing your photo. Please try again.",
    },
    "bn": {
        "welcome": (
            "👋 <b>SnapStudy AI-তে স্বাগতম!</b>\n\n"
            "আপনার হাতে লেখা নোট, বইয়ের পাতা বা লেকচার স্লাইডের একটি পরিষ্কার ছবি পাঠান 📷\n\n"
            "Gemma 4 আপনার নোট পড়ে সারসংক্ষেপ, মূল পয়েন্ট, কঠিন শব্দের ব্যাখ্যা এবং "
            "৫টি প্রশ্নের প্র্যাকটিস কুইজ তৈরি করে দেবে!"
        ),
        "help": (
            "📖 <b>SnapStudy AI যেভাবে ব্যবহার করবেন:</b>\n\n"
            "১. আপনার পড়ার নোটের একটি স্পষ্ট ছবি তুলুন।\n"
            "২. এখানে ছবি বা ইমেজ ফাইল হিসেবে পাঠান।\n"
            "৩. আমি নোট পড়ে সারসংক্ষেপ ও কুইজ তৈরি করব।\n\n"
            "কমান্ডসমূহ:\n"
            "/start - স্বাগতম বার্তা\n"
            "/help - নির্দেশাবলী"
        ),
        "reading_notes": "⏳ আপনার নোট পড়া হচ্ছে…",
        "photo_received": "✅ আপনার ছবি পেয়েছি ({width}x{height}, {size_kb:.1f} KB)",
        "send_photo_prompt": "আপনার পড়ার নোটের একটি ছবি পাঠান 📷",
        "invalid_file": "অনুগ্রহ করে আপনার পড়ার নোটের একটি বৈধ ছবি পাঠান (JPEG বা PNG)।",
        "error_generic": "ছবি প্রসেস করার সময় একটি সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।",
    },
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Retrieve localized string by key with fallback to English."""
    lang_code = "bn" if lang.lower() in ("bn", "bangla") else "en"
    template = STRINGS.get(lang_code, {}).get(
        key, STRINGS["en"].get(key, f"[{key}]")
    )
    if kwargs:
        return template.format(**kwargs)
    return template
