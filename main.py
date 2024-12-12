import os
import csv
import json
from GetTranscription import get_transcription
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

input_folder = "contagion_events"
output_folder = "sentiment_results"

# Initialize Vader
analyzer = SentimentIntensityAnalyzer()

def vader_sentiment_analysis(text):
    """Perform sentiment analysis and return the score."""
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']

def process_events(input_folder, output_folder):
    # Open CSV file for writing
    output_csv = os.path.join(output_folder, "sentiment_results.csv")

    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["event_message", "streamer_sentiment", "event_size"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header row to CSV file
            writer.writeheader()
            
            for file_name in os.listdir(input_folder):
                if file_name.endswith(".json"):
                    input_file = os.path.join(input_folder, file_name)
                    
                    try:
                        with open(input_file, 'r') as f:
                            events = json.load(f)
                        
                        for event in events:
                            # Extract event details

                            start_time = event["start_time"]
                            message = event["message"]
                            leaders = event["leaders"]
                            followers = event["followers"]
                            mp3_name = os.path.splitext(file_name)[0] + '.mp3'
                            path = os.path.join("audio_logs", mp3_name)

                            # Get transcription
                            transcription = get_transcription(path, start_time)
                            # Perform sentiment analysis
                            sentiment = vader_sentiment_analysis(transcription or message)
                            # Calculate event size
                            event_size = len(leaders) + len(followers)

                            # Write row to CSV file
                            writer.writerow({
                                "event_message": message,
                                "streamer_sentiment": sentiment,
                                "event_size": event_size 
                            })

                            print(f"Written event from {file_name}")

                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"Error reading file {input_file}: {e}")
                    
    except Exception as e:
        print(f"Error processing events: {e}")

# Run
process_events(input_folder, output_folder)
print("Processing complete")
