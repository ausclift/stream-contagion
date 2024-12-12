# Stream Contagion

## Social Contagion in Livestream Chats

This project seeks to quantify social contagion within Twitch chat logs.

## Use

1. Install necessary modules: vaderSentiment, homebrew + openai-whisper

2. Download each stream as an MP3 file (we used 4K Video Downloader) and place in 'audio_logs'

3. Download the associated chat log using 'www.twitchchatdownloader.com' and place in 'chat_logs'

4. Run 'IdentifyContagionEvents.py' to generate contagion events

5. Run 'main.py' to execute sentiment analysis on the contagion events

**Audio files and chat logs MUST have the same file name, a.k.a 'XYZ.mp3' and 'XYZ.csv'**
Event JSON files SHOULD be generated with the same name as well

## Analysis

LeaderFollwerAnalysis.py and SentimentScatter.py DO NOT WORK as intended. Most data analysis was performed using Excel spreadsheets on the output of sentiment results.