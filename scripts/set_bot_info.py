"""Script to set Telegram bot commands, description, and short description."""

import asyncio
from telegram import Bot, BotCommand
from app.config import settings


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_TOKEN)

    # 1. Set bot commands for menu button
    commands = [
        BotCommand("start", "Start study session & guide"),
        BotCommand("portal", "Open web dashboard & flashcards"),
        BotCommand("weak", "View weak topics & accuracy"),
        BotCommand("practice", "Practice mistake questions"),
        BotCommand("help", "Instructions & photo tips"),
    ]
    await bot.set_my_commands(commands)
    print("Commands set successfully.")

    # 2. Set bot description (shown before pressing START)
    description = (
        "📚 Welcome to SnapStudy AI!\n\n"
        "Your AI-powered study companion powered by Gemma 4.\n\n"
        "📸 Snap a photo of notes, slides, or textbook pages\n"
        "📝 Get instant bullet summaries & key concepts\n"
        "❓ Practice with interactive 5-question quizzes\n"
        "🎯 Track weak topics & practice past mistakes\n"
        "💻 Web portal with 3D flashcards & classmate challenges\n\n"
        "👉 Click the 'START' button below to begin!"
    )
    await bot.set_my_description(description=description)
    print("Description set successfully.")

    # 3. Set short description (shown in bot profile/share link)
    short_description = "AI study partner: snap notes, get summaries, quizzes, weak topics & web dashboard."
    await bot.set_my_short_description(short_description=short_description)
    print("Short description set successfully.")

    me = await bot.get_me()
    print(f"Bot info updated for @{me.username} ({me.first_name})")


if __name__ == "__main__":
    asyncio.run(main())
