Telegram Video Downloader Bot

My code for Telegram bot for downloading videos from various platforms.  
The bot also provides video transcription and explanations (in Russian).

- 📥 Download videos from different sources
- 📝 Generate video transcriptions
- 💡 Provide explanations and summaries of video content (in Russian)
- 👥 Support group chats
- 📊 Collect basic usage statistics with SQLite


The bot uses an SQLite database to store basic usage statistics, such as:

- Which video platforms are used the most
- How many videos each user has downloaded through the bot

Only the user's Telegram ID is stored — no personal information is collected.

<img width="400" alt="изображение" src="https://github.com/user-attachments/assets/bdfcb8b5-59c9-4b34-9fb4-945e542e55a5" />

In group chats, the bot can show who initiated a video download, which makes it easier to track requests and manage shared usage.

Bot example: @Youtube_video_summarybot
