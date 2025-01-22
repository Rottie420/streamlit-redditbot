import praw
import random
import time
import json
import streamlit as st
from datetime import datetime
from config import CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD
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

    # Navigation Menu using Radio Buttons in Horizontal Layout
    menu = st.radio(
        "Select an Action:",
        ["🏠 Home", "✉️ Inbox", "📝 r/usernames"],
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
            except Exception as e:
                container.error(f"{self.time_now()} Failed to send message to {username}: {e}")  # Changed to container.write

        def target_subreddit(self):
            subreddits = ['vet', 'AskVet', 'VetTech', 'ApoioVet', 'AskVetAnimals', 'Petsuppliesplus']

            return random.choice(subreddits)

        def random_messages(self, username):
            message = [(
               f"Hi {username},\n\n"
                "I noticed you're a fellow pet lover, so I wanted to share something "
                "I’ve been working on that might interest you: an NFC Pet Tag. "
                "It’s designed to help reunite lost pets with their owners by securely "
                "storing details like:\n\n"
                "    - Your contact details\n"
                "    - Your pet’s medical history\n"
                "    - Their last known location\n\n"
                "Here’s a quick [demo](https://connecta.store/demo) to show you how it works." 
                "Feel free to ask me any "
                "questions or share your thoughts—I’d genuinely love to hear what you think.\n\n"
                "If it sounds like something you’d find helpful, you can check it out [here](https://connecta.store)."
            ),
            (
                f"Hey {username},\n\n"
                "As a fellow pet lover, I wanted to share something cool I’ve been working on—"
                "an NFC Pet Tag! It’s a handy little tag designed to help reunite lost pets "
                "with their owners by storing important details like:\n\n"
                "    - Your contact details\n"
                "    - Your pet’s medical history\n"
                "    - Their last known location\n\n"
                "Here’s a [demo](https://connecta.store/demo) to show you how it works. "
                "I’d love to hear your thoughts or answer any questions you have.\n\n"
                "If you think it’d be useful, you can check it out [here](https://connecta.store)!"
            ),
            (
                f"Hello {username},\n\n"
                "I hope this message finds you well. As a pet owner, you might find this "
                "useful: an NFC Pet Tag that I’ve been working on. It’s designed to help reunite "
                "lost pets with their owners by securely storing information such as:\n\n"
                "    - Your contact details\n"
                "    - Your pet’s medical history\n"
                "    - Their last known location\n\n"
                "You can view a quick [demo](https://connecta.store/demo) to learn more. "
                "If you have any questions or feedback, I’d be delighted to hear from you.\n\n"
                "Feel free to check it out [here](https://connecta.store) if you’re interested."
            )]

            return random.choice(message)

        def time_now(self):
            return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        def random_subjects(self):
            subject = [
                        "A Smart Way to Keep Your Pet Safe: NFC Pet Tag",
                        "For Pet Lovers: Meet the NFC Tag That Protects Your Furry Friend",
                        "Lost Pet? Here’s How This Tag Can Help You Reunite Quickly!"
                    ]
            
            return random.choice(subject)

        def scan_and_send_messages(self):
            for _ in range(100000):
                try:
                    subreddit = self.target_subreddit()
                    container.info(f"{self.time_now()} Scanning subreddit: {subreddit}")  # Changed to container.write
                    for submission in reddit.subreddit(subreddit).new(limit=10):
                        for comment in submission.comments:
                            if isinstance(comment, praw.models.Comment) and comment.author:
                                username = comment.author.name
                                if username not in self.usernames_list:
                                    self.usernames_list.append(username)
                                    
                                    self.send_reddit_message(username, self.random_subjects(), self.random_messages(username))
                                    self.save_usernames()
                                    time.sleep(33)
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

    def load_usernames():
        scanner = RedditUserScanner(file_path)
        st.write(scanner.usernames_list)

    # Routing based on menu selection
    if menu == "✉️ Inbox":
        st.write("Unread Mail")
        log_unread_messages()

    elif menu == "📝 r/usernames":
        st.write("Username List")
        load_usernames()

    else:
        if st.sidebar.button("Start Bot"):
            scanner = RedditUserScanner(file_path)
            scanner.scan_and_send_messages()

if __name__ == "__main__":
    main()
