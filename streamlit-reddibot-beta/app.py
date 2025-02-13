import praw
import random
import time
import json
import streamlit as st
from datetime import datetime
from config import CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD
from PromptHandler import PromptHandler


# Set up Streamlit app
def main():
    st.set_page_config(page_title="Reddit Dashboard", layout="wide")
    st.title("PRAW-8 spammer v1")

    # Sidebar for input fields
    st.sidebar.header("USER CREDENTIALS")
    REDDIT_CLIENT_ID = st.sidebar.text_input("Reddit Client ID", CLIENT_ID)
    REDDIT_CLIENT_SECRET = st.sidebar.text_input("Reddit Client Secret", CLIENT_SECRET, type="password")
    REDDIT_USER_AGENT = st.sidebar.text_input("User Agent", USER_AGENT)
    REDDIT_USERNAME = st.sidebar.text_input("Reddit Username", USERNAME)
    REDDIT_PASSWORD = st.sidebar.text_input("Reddit Password", PASSWORD, type="password")
    file_path = st.sidebar.text_input("File Path for Usernames", "users.json")
    file_path_subs = st.sidebar.text_input("File Path for Subbreddits", "subbredits-dogs.json")

    # Navigation Menu using Radio Buttons in Horizontal Layout
    menu = st.radio(
        "Select an Action:",
        ["▶️ Run", "✉️ Inbox", "💬 Response", "📝 r/usernames"],
        horizontal=True,
    )
    st.experimental_set_query_params(menu=menu)

    # Main layout
    container = st.container()  # Using container for both col1 and col2

    # Initialize Reddit API client
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
    )

    # Define the RedditUserScanner class
    class RedditUserScanner:
        def __init__(self, file_path):
            self.file_path = file_path
            self.file_path_subs = file_path_subs
            self.usernames_list = self.load_usernames()

        def load_usernames(self):
            try:
                with open(self.file_path, 'r') as file:
                    usernames = json.load(file)
                    return usernames
            except FileNotFoundError:
                return []

        def save_usernames(self):
            with open(self.file_path, 'w') as file:
                json.dump(self.usernames_list, file)

        def send_reddit_message(self, username, subject, message_body):
            try:
                reddit.redditor(username).message(subject, message_body)
                container.success(f"{self.time_now()} Message sent to {username}")  # Changed to container.write
                self.usernames_list.append(username)
                self.save_usernames()
            except Exception as e:
                if 'RATELIMIT' in str(e):
                    # Parsing the rate limit message and extracting the duration
                    container.error(f"{self.time_now()} An error occurred: {e}")  # Changed to container.write
                    time.sleep(70)
                else:
                    container.error(f"{self.time_now()} Failed to send message to {username}: {e}")  # Changed to container.write

        def target_subreddit(self):
            with open(self.file_path_subs, 'r') as file:
                    subreddits = json.load(file)
                    self._target_subreddit = random.choice(subreddits)

        def random_messages(self, username):
            subreddit = self._target_subreddit
            message = [
                        (
                            f"Hey u/{username},\n\n"
                            f"I noticed you're active in r/{subreddit}, and I thought you might find this interesting.\n"
                            f"I've been working on Pet accessories, and I think it could be super helpful for people in our community.\n\n"
                            f"Let me know if you'd like to know more! Happy to chat 😊"
                        ),
                        (
                            f"Hey u/{username},\n\n"
                            f"I saw you’re active in r/{subreddit}, and thought you might be interested in something I’ve been working on.\n" 
                            f"It’s a Pet accessories, and I think it could really help to all pet owners.\n\n"
                            f"If you’re curious, feel free to reach out! I’d love to chat more about it."
                        ),
                        (
                            f"Hey u/{username},\n\n"
                            f"I noticed you’re active in r/{subreddit}, and I think you might find this Pet accessories useful.\n"
                            f"I’ve been working on something that could help with Pet owners,\n"
                            f"and thought it could be a good fit for folks in this community.\n\n"
                            f"If you're interested or want to chat, feel free to reach out! Happy to share more details."
                        )
                    ]

            return random.choice(message)

        def time_now(self):
            return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        def random_subjects(self):
            subreddit = self._target_subreddit
            subject = [
                        "I apologize if I’m reaching out unexpectedly.",
                        "I hope I’m not overstepping by messaging you.",
                        "I appreciate your time and hope this message is okay.",
                        "I apologize if this message is an intrusion.",
                        "I hope this DM is alright, I just wanted to share something"
                    ]
            
            return random.choice(subject)

        def scan_and_send_messages(self):
            try:
                self.target_subreddit()
                subreddit = self._target_subreddit
                container.info(f"{self.time_now()} Scanning subreddit: {subreddit}")  # Changed to container.write
                for submission in reddit.subreddit(subreddit).new(limit=5):
                    for comment in submission.comments:
                        if isinstance(comment, praw.models.Comment) and comment.author:
                            username = comment.author.name
                            if username not in self.usernames_list:
                                self.send_reddit_message(username, self.random_subjects(), self.random_messages(username))
                                time.sleep(18)

            except Exception as e:           
                container.error(f"{self.time_now()} An error occurred: {e}")  # Changed to container.write

    def log_unread_messages():
        try:
            unread_messages = reddit.inbox.unread(limit=None)
            if unread_messages:
                for msg in unread_messages:
                    st.write(f"**Author:** {msg.author.name if msg.author else 'Unknown'}")
                    st.write(f"**Subject:** {msg.subject}")
                    st.write(f"**Body:** {msg.body}")
                    st.write("---")
            else:
                st.write("No unread messages.")
        except Exception as e:
            st.error(f"Error fetching messages: {e}")

    def log_unread_messages_to_json():
        try:
            _prompt = PromptHandler()
            unread_messages = reddit.inbox.unread(limit=None)
            output = []
            _timenow = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            if unread_messages:    
                for msg in unread_messages:
                    if msg.author is not None:  
                        prompt = _prompt.handle_prompt(msg.author.name, msg.body)
                        try :
                            msg.reply(prompt)
                            message_data = {
                                "author": msg.author.name if msg.author else 'Unknown',
                                "subject": msg.subject,
                                "body": msg.body,
                                "response" : prompt
                            }

                            output.append(message_data)

                            # Mark the message as read
                            msg.mark_read()
                        except Exception as e:
                            if 'RATELIMIT' in str(e):
                                    st.error(f"Respond failed: {e}")
                                    time.sleep(70)
                                    continue

            else:
                output.append({"message": "No unread messages."})

            # Read existing data from the JSON file
            try:
                with open('unread_messages.json', 'r') as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                existing_data = []

            # Append new data to the existing data
            existing_data.extend(output)

            # Save the updated result back to the JSON file
            with open('unread_messages.json', 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

            # Return the result to be displayed with st.write
            return existing_data

        except Exception as e:
            st.error(f"Error fetching messages: {e}")
            return []


    def load_usernames():
        scanner = RedditUserScanner(file_path)
        st.write(scanner.usernames_list)

    # Routing based on menu selection
    if menu == "✉️ Inbox":
        st.write("Unread Mail")
        log_unread_messages()

    if menu == "💬 Response":
        st.write(log_unread_messages_to_json())
        
    elif menu == "📝 r/usernames":
        st.write("Username List")
        load_usernames()

    else:
        if st.sidebar.button("▶️ Run Bot"):
            scanner = RedditUserScanner(file_path)
            
            for _ in range(100000):
                scanner.scan_and_send_messages()
                log_unread_messages_to_json()

if __name__ == "__main__":
    main()