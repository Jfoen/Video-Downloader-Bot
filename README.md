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

<img src="https://github.com/user-attachments/assets/bc7645b0-f3c2-401a-b655-2d00aae000d4" width="400" />

In group chats, the bot can show who initiated a video download, which makes it easier to track requests and manage shared usage.
