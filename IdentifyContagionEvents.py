import CSVPreprocessor
import os
import csv
import re
import json

LOG_FOLDER = "chat_logs"
EVENT_FOLDER = "contagion_events"
# Allowable elapsed time from last matching message
SPAM_THRESHOLD = 15
# Seconds after inital msg that user is still considered a leader
LEADER_DURATION = 5
# Fewest number of followers for a valid contagion event
MIN_FOLLOWERS = 10

class IdentifyContagionEvents:
    def __init__(self):
        self.log_files = [os.path.join(LOG_FOLDER, file) for file in os.listdir(LOG_FOLDER) if file.endswith('.csv')]
        self.current_log_index = 0
        self.current_log_name = ""
        
    def delete_processed_file(self):
        """Deletes all files prefixed with 'processed' in the given folder."""
        try:
            for file_name in os.listdir(LOG_FOLDER):
                if file_name.startswith("processed"):
                    file_path = os.path.join(LOG_FOLDER, file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
            print("Processed files deletion complete.")
        except Exception as e:
            print(f"Error deleting processed files: {e}")

    def load_next_log(self):
        """Loads the next chat log."""
        if self.current_log_index >= len(self.log_files):
            print("No more logs to load.")
            return None

        log_file = self.log_files[self.current_log_index]

        log_dir = os.path.dirname(log_file)
        log_filename = os.path.basename(log_file)

        new_filename = f"processed_{log_filename}"

        new_log_file = os.path.join(log_dir, new_filename)

        try:
            CSVPreprocessor.processCSV(log_file, new_log_file)
            with open(new_log_file, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)

                chat_log = []
                for row in reader:
                    chat_log.append((int(row[0]), row[1], row[3], False))

            self.delete_processed_file()

            self.current_log_index += 1
            base, _ = os.path.splitext(log_filename)
            self.current_log_name = base
            return chat_log

        except FileNotFoundError:
            print(f"File {log_file} not found, program ended.")
            self.delete_processed_file()
            return None


    def get_contagion_event(self, chat_log):
        """Converts 'social contagion' into discrete events with a common message and time."""
        contagion_events = []
        for i, (_, _, message, processed) in enumerate(chat_log):        
            if not processed:
                contagion_info = self.detect_contagion(chat_log, i)
                if contagion_info:
                    contagion_start, leaders, followers, message = contagion_info
                    contagion_events.append({
                        "start_time": contagion_start,
                        "message": message,
                        "leaders": leaders,
                        "followers": followers,
                    })
        return contagion_events

    def detect_contagion(self, chat_log, start_index):
        """If the given message initiates contagion, builds a contagion event."""
        chat_log[start_index] = (*chat_log[start_index][:3], True) # set initial message as processed
        event_start_time, init_user, init_msg = chat_log[start_index][:3]

        # Sets
        leaders = set()
        followers = set()

        # Tracking variable
        last_msg_time = event_start_time

        init_message_component = self.get_contagion_component(init_msg)
        
        if init_message_component == None:
            return None

        leaders.add(init_user)

        for i in range(start_index + 1, len(chat_log)):
            current_time, current_user, current_msg, current_processed = chat_log[i][:4]

            if not current_processed:
                # Check if current message matches original message
                match = self.match_message(current_msg, init_message_component, init_msg)
                if match:
                    chat_log[i] = (*chat_log[i][:3], True) # set matching message as processed
                    elapsed_time = current_time - event_start_time
                    last_msg_time = current_time

                    # Add leader
                    if elapsed_time <= LEADER_DURATION:
                        leaders.add(current_user)

                    # Add follower
                    else:
                        followers.add(current_user)

            # Conclude event if spam threshold is exceeded
            if current_time - last_msg_time > SPAM_THRESHOLD:
                break

        # Event must meet a follower minimum
        if len(followers) >= MIN_FOLLOWERS:
            return event_start_time, list(leaders), list(followers), init_msg

        return None

    def get_contagion_component(self, current_msg):
        """Reduces a string to a single word or pattern"""
        message_component = current_msg.lower().strip()
       
        while len(message_component.split()) > 1:
            match = re.match(r'^(.+?)(?: \1)*$', message_component)
   
            if match:
                pattern = match.group(1).strip()
                return pattern

            message_component= message_component.rsplit(' ', 1)[0]

        if message_component == '':
            return None
        
        return message_component

    def match_message(self, current_msg, init_message_component, init_msg):
        """Determines if messages are sufficiently similar to be contagion."""
        # Check exact match
        if init_msg == current_msg:
            return True

        current_msg = current_msg.lower()
        
        # Determine if message contains the component
        pattern = r'\b' + re.escape(init_message_component) + r'\b'
        if re.findall(pattern, current_msg):
            #print(f"'{current_msg}' matches '{init_msg}'")
            return True

        # Determines if both messages begin with '?'
        pattern = r'^\?+'
        if re.findall(pattern, init_msg):
            if re.findall(pattern, current_msg):
                return True

        # Convert to words without losing punctuation
        original_words = init_msg.split()
        incoming_words = current_msg.split()
        if len(incoming_words) == 0:
            return False

        if len(original_words) == 1:
            if original_words[0] == incoming_words[0] and len(incoming_words) <= 5:
                return True

        elif len(original_words) > 1:
            if original_words[0] == original_words[1]:
                if original_words[0] == incoming_words[0]:
                    return True

        return False

    def export_contagion_events(self, contagion_events):
        """Displays contagion events as a chart/graph with leaders and followers."""
        if not contagion_events:
            print("No contagion events found.")
            return
        print(f"Created {len(contagion_events)} contagion events")
        with open(f'{EVENT_FOLDER}/{self.current_log_name}.json', 'w') as file:
            json.dump(contagion_events, file)

# Run
contagion_detector = IdentifyContagionEvents()

while True:
    chat_log = contagion_detector.load_next_log()
    if not chat_log:
        break
    contagion_events = contagion_detector.get_contagion_event(chat_log)
    contagion_detector.export_contagion_events(contagion_events)
