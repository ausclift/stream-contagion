import os
import csv
import re
from collections import deque

LOG_FOLDER = "chat_logs"
# Allowable elapsed time from last matching message
SPAM_THRESHOLD = 20
# Seconds after inital msg that user is still considered a leader
LEADER_DURATION = 5
# Fewest number of followers for a valid contagion event
MIN_FOLLOWERS = 20

class FindContagion:
    def __init__(self):
        self.log_files = [os.path.join(LOG_FOLDER, file) for file in os.listdir(LOG_FOLDER) if file.endswith('.csv')]
        #self.log_files.sort()  # not needed?
        self.current_log_index = 0
        self.recent_messages = deque()

    def load_next_log(self):
        """Loads the next chat log file from the log folder."""
        if self.current_log_index >= len(self.log_files):
            print("No more logs to load.")
            return None
        
        log_file = self.log_files[self.current_log_index]
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # skip header
                chat_log = [(int(row[0]), row[1], row[3], False) for row in reader]
            self.current_log_index += 1
            return chat_log
        except FileNotFoundError:
            print(f"File {log_file} not found.")
            return None

    def get_contagion_event(self, chat_log):
        """Identifies instances of social contagion in a chat log."""
        contagion_events = []
        for i, (timestamp, user_name, message, processed) in enumerate(chat_log):        
            if not processed:
                contagion_info = self.detect_contagion(chat_log, i)
                if contagion_info:
                    contagion_start, leaders, followers, message = contagion_info
                    message = message.strip()
                    contagion_events.append({
                        "start_time": contagion_start,
                        "message": message,
                        "leaders": leaders,
                        "followers": followers,
                    })
        
        return contagion_events

    def detect_contagion(self, chat_log, start_index):
        """Detects if a new message initiates spam and marks related messages as processed."""
        chat_log[start_index] = (*chat_log[start_index][:3], True) # set processed
        event_start_time, init_user, init_msg = chat_log[start_index][:3]

        init_message_component = self.get_contagion_component(init_msg)
        
        leaders = set()
        followers = set()

        last_msg_time = event_start_time
        
        leaders.add(init_user)
        for i in range(start_index + 1, len(chat_log)):
            current_time, current_user, current_msg, current_processed = chat_log[i][:4]

            current_message_component = self.get_contagion_component(current_msg)
            
            # Check if current message matches original message
            if not current_processed and self.match_message(current_message_component, init_message_component):
                chat_log[i] = (*chat_log[i][:3], True) # set processed
                elapsed_time = current_time - event_start_time
                last_msg_time = current_time

                # Add leader
                if elapsed_time <= LEADER_DURATION:
                    leaders.add(current_user)
                    
                # Add follower
                else:
                    followers.add(current_user)
                
            # Conclude event if spam threshold is exceeded
            elif current_time - last_msg_time > SPAM_THRESHOLD:
                break
        
        # Event must meet a follower minimum
        if len(followers) >= MIN_FOLLOWERS:
            return event_start_time, list(leaders), list(followers), init_message_component
        
        return None

    def get_contagion_component(self, current_msg):
        message_component = current_msg.lower().strip()
        
        match = re.match(r'^(.+?)(?: \1)*$', message_component)
    
        if match:
            pattern = match.group(1).strip()
        
            parts = message_component.split(pattern)
        
            # If splitting leaves only an empty or partial last segment, return candidate
            if all(part.strip() == "" for part in parts[:-1]):
                #print(f"Converted '{current_msg}' to '{pattern}'")
                return pattern
            
        return message_component

    def match_message(self, current_msg, init_msg):
        """Determines if messages are sufficiently similar to be contagion."""
        if init_msg == current_msg:
            return True # Check exact match

        # need to match "???" with "?" and "???????" and "???? om wow"
        # also "..." or unicode emojis (heart, etc.)


        # Convert to words without losing punctuation
        original_words = init_msg.split()
        incoming_words = current_msg.split()
        if len(incoming_words) == 0:
            return False

        if len(original_words) == 1:
            if original_words[0] == incoming_words[0] and len(incoming_words) <= 5:
                return True # Matche "Flushed" with "Flushed uhh hello?" or "OMG" with "omg omg omg"


        elif len(original_words) > 1:
            if original_words[0] == original_words[1]:
                if original_words[0] == incoming_words[0]:
                    return True # Matche "vedalwave vedalwave <3 <3" with "vedalwave bye"
            
        return False

    def display_contagion(self, contagion_events):
        """Displays contagion events as a chart/graph with leaders and followers."""
        if not contagion_events:
            print("No contagion events found.")
            return
        
        # Print event data
        for event in contagion_events:
            print(f"Contagion Event - Start Time: {event['start_time']}, Message: '{event['message']}'")
            print(f"  Leaders: {', '.join(event['leaders'])}")
            print(f"  Followers: {', '.join(event['followers'])}")
            print("-" * 40)

# Run
contagion_detector = FindContagion()

while True:
    chat_log = contagion_detector.load_next_log()
    if not chat_log:
        break
    contagion_events = contagion_detector.get_contagion_event(chat_log)
    contagion_detector.display_contagion(contagion_events)
