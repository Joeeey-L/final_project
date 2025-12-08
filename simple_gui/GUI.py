#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
import tkinter as tk
from tkinter import ttk
from chat_utils import *
import json
from chatbot import ChatBot
from snake_game import SnakeGame
from sentiment_tools import analyze_sentiment
from typing import List
from nlp_tools import extract_keywords_yake, summarize_with_sumy
import re
import time


# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.chatbot = ChatBot(api_key="sk-59aea2a31153449891fb6cd2596993d0") #add chatbot
        self.chatbot_mode = False
        self.sentiment_mode = False
        self.chat_history = []

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width = False, 
                             height = False)
        self.login.configure(width = 400,
                             height = 300)
        # create a Label
        self.pls = Label(self.login, 
                       text = "Please login to continue",
                       justify = CENTER, 
                       font = "Helvetica 14 bold")
          
        self.pls.place(relheight = 0.15,
                       relx = 0.2, 
                       rely = 0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text = "Name: ",
                               font = "Helvetica 12")
          
        self.labelName.place(relheight = 0.2,
                             relx = 0.1, 
                             rely = 0.2)
          
        # create a entry box for 
        # tyoing the message
        self.entryName = Entry(self.login, 
                             font = "Helvetica 14")
          
        self.entryName.place(relwidth = 0.4, 
                             relheight = 0.12,
                             relx = 0.35,
                             rely = 0.2)
          
        # set the focus of the curser
        self.entryName.focus()
          
        # create a Continue Button 
        # along with action
        self.go = Button(self.login,
                         text = "CONTINUE", 
                         font = "Helvetica 14 bold", 
                         command = lambda: self.goAhead(self.entryName.get()))
          
        self.go.place(relx = 0.4,
                      rely = 0.55)
        self.Window.mainloop()
  
    def goAhead(self, name):
        if len(name) > 0:
            msg = json.dumps({"action":"login", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state = NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")   
                self.textCons.insert(END, menu +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)
                # while True:
                #     self.proc()
        # the thread to receive messages
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()
  
    # The main layout of the chat
    def layout(self,name):
        
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 470,
                              height = 550,
                              bg = "#17202A")
        self.labelHead = Label(self.Window,
                             bg = "#17202A", 
                              fg = "#EAECEE",
                              text = self.name ,
                               font = "Helvetica 13 bold",
                               pady = 5)
          
        self.labelHead.place(relwidth = 1)
        self.line = Label(self.Window,
                          width = 450,
                          bg = "#ABB2B9")
          
        self.line.place(relwidth = 1,
                        rely = 0.07,
                        relheight = 0.012)
          
        self.textCons = Text(self.Window,
                             width = 20, 
                             height = 2,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = "Helvetica 14", 
                             padx = 5,
                             pady = 5)
          
        self.textCons.place(relheight = 0.745,
                            relwidth = 1, 
                            rely = 0.08)
          
        self.labelBottom = Label(self.Window,
                                 bg = "#ABB2B9",
                                 height = 80)
          
        self.labelBottom.place(relwidth = 1,
                               rely = 0.825)
          
        self.entryMsg = Entry(self.labelBottom,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = "Helvetica 13")
          
        #smaller width to leave a place for emoji button
        self.entryMsg.place(relwidth = 0.64,
                            relheight = 0.06,
                            rely = 0.008,
                            relx = 0.011)
          
        self.entryMsg.focus()
        
        # new emoji button
        self.buttonEmoji = Button(self.labelBottom,
                                  text = "😀",
                                  font = "Helvetica 12 bold",
                                  width = 5,
                                  bg = "#ABB2B9",
                                  command = self.open_emoji_window)
        
        self.buttonEmoji.place(relx = 0.66,
                               rely = 0.008,
                               relheight = 0.06,
                               relwidth = 0.09)
        
        # in the layout method
        self.buttonBot = Button(self.Window, 
                text="Bot: OFF",  # 初始状态为关闭
                font="Helvetica 10 bold",
                bg="#445566",
                fg="white",
                command=self.toggle_chatbot)

        # put this button at the top-right corner
        self.buttonBot.place(relx=0.82, rely=0.018, 
                     relheight=0.045, relwidth=0.15)
        
        #add a game button
        self.snakeButton = Button(self.Window,
                         text="Play Snake",
                         font="Helvetica 9 bold",
                         bg="#556677",
                         fg="white",
                         command=self.open_snake_game)
        self.snakeButton.place(relx=0.02, rely=0.018, relheight=0.045, relwidth=0.15)

        self.is_requesting_leaderboard = False
        self.leaderboard_data = []

        self.rankButton = Button(
            self.Window,
            text="Ranking",
            font="Helvetica 9 bold",
            bg="#556677",
            fg="white",
            command=self.open_leaderboard_window
        )
        self.rankButton.place(relx=0.18, rely=0.018, relheight=0.045, relwidth=0.12)

          
        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 10 bold", 
                                width = 20,
                                bg = "#ABB2B9",
                                command = lambda : self.sendButton(self.entryMsg.get()))
          
        self.buttonMsg.place(relx = 0.77,
                             rely = 0.008,
                             relheight = 0.06, 
                             relwidth = 0.22)
        
        self.personalityButton = Button(self.Window, 
                        text="Personality",
                        font="Helvetica 10 bold",
                        bg="#556677",
                        fg="white",
                        command=self.open_personality_window)
        self.personalityButton.place(relx=0.65, rely=0.018, 
                     relheight=0.045, relwidth=0.15)
        
        self.buttonSentiment = Button(self.Window,
                         text="😐 OFF",
                         font="Helvetica 9 bold",
                         bg="#664477",
                         fg="white",
                         command=self.toggle_sentiment)
        self.buttonSentiment.place(relx=0.32, rely=0.018, 
                                   relheight=0.045, relwidth=0.1)
          
        self.textCons.config(cursor = "arrow")
          
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
          
        # place the scroll bar 
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
          
        scrollbar.config(command = self.textCons.yview)
          
        self.textCons.config(state = DISABLED)
  
    # function to basically start the thread for sending messages
    # New Feature: Emotion Analysis function
    def toggle_sentiment(self):
        self.sentiment_mode = not self.sentiment_mode
        self.textCons.config(state=NORMAL)
        if self.sentiment_mode:
            self.textCons.insert(END, "【Sentiment Analysis: ON - Analyzing others' messages】\n\n")
            self.buttonSentiment.config(bg="#8B4789", text="😊 ON")
        else:
            self.textCons.insert(END, "【Sentiment Analysis: OFF】\n\n")
            self.buttonSentiment.config(bg="#664477", text="😐 OFF")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    
    
    def check_bot_mention(self, msg):
        """
        Check if the message mentions a bot
        Supports formats such as @bot, @chatbot, @Bot, @ChatBot, etc.
       
        """
        pattern = r'@(bot|chatbot)'
        return re.search(pattern, msg.lower()) is not None  
    def remove_bot_mention(self, msg):
        """
        Remove the @bot tag from the message 
        to obtain the actual content to be processed.
    
        """
        pattern = r'@(bot|chatbot)\s*'
        return re.sub(pattern, '', msg, flags=re.IGNORECASE).strip()    

    def sendButton(self, msg):
        if len(msg) == 0:
            return

        
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "You: " + msg + "\n")
        # ------------ Add own message to chat history ------------
        # Filter commands, such as /summary /keywords
        if not msg.startswith("/"):
            clean_msg = re.sub(r"\[[^\]]+\]$", "", msg).strip()
            if clean_msg:
                self.chat_history.append(clean_msg)
        # ---------------------------------------------------------

        self.textCons.config(state=DISABLED)
        self.textCons.see(END)   
        self.entryMsg.delete(0, END)

        # ---------- NLP Commands ----------
        if msg.strip() == "/keywords":
            # Original Keywords
            result = extract_keywords_yake(self.chat_history, top_k=10)

            # Junk keywords to filter out
            ban_list = {
                "Request", "requested", "Connect", "connected", "connecting",
                "chat", "you", "are", "with", "from", "to", "the"
            }

            # Filter out junk words (match lowercase)
            cleaned = [w for w in result if w.lower() not in ban_list]

            # If delete too many, at least keep the first few.
            cleaned = cleaned[:5] if len(cleaned) > 0 else result[:5]

            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【Keywords】 {', '.join(cleaned)}\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            return

        if msg.strip() == "/summary":
            result = summarize_with_sumy(self.chat_history, sentences_count=3)
            summary_text = "\n".join(result)
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【Summary】\n{summary_text}\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            return
# ----------------------------------


        if self.check_bot_mention(msg):
            self.my_msg = msg
            actual_msg = self.remove_bot_mention(msg)
            
            # Get bot response
            bot_reply = self.chatbot.get_response(actual_msg)
            
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, "🤖 Bot: " + bot_reply + "\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
            # Broadcast the bot's reply to everyone
            # Construct specially formatted messages so other clients can display bot replies.
            def send_bot_reply():
                import time
                time.sleep(0.1)  # A brief delay ensures the original message is processed first.
                broadcast_msg = f"🤖 Bot: {bot_reply}"
                # Send bot replies through the normal process
                temp_msg = self.my_msg
                self.my_msg = broadcast_msg
                # Waiting to send
                time.sleep(0.05)
                self.my_msg = temp_msg if temp_msg != msg else ""
            
            bot_thread = threading.Thread(target=send_bot_reply)
            bot_thread.daemon = True
            bot_thread.start()
            return
         
        if self.chatbot_mode:
            bot_reply = self.chatbot.get_response(msg)
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, "Bot: " + bot_reply + "\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            return
        self.my_msg = msg     
    
    #open game method    
    def open_snake_game(self):
        SnakeGame(self.Window, self.on_player_score)

    def on_player_score(self, score):
        """
        Send the player's game score to the server
        """
        try:
            print(f"Player {self.name} scored: {score}")
            
            # Construct game score messages
            score_msg = json.dumps({
                "action": "game_score",
                "score": score,
                "player": self.name  # Add Player Name
            })
            
            # Send to server
            self.send(score_msg)
            
            # Display local prompts in the chat window
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【Game】You scored {score} points in Snake Game!\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
        except Exception as e:
            print(f"Error sending score to server: {e}")
            # If sending fails, display a local message at least.
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【Game】You scored {score} points! (Not saved to server)\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
        self.send(score_msg) 

    def request_leaderboard(self):
        self.client.send("GET_SNAKE_LEADERBOARD")
        data = self.client.receive()

        # transform in Python object
        import json
        leaderboard = json.loads(data)

        return leaderboard   

   
    def open_leaderboard_window(self):
        """
        Open the leaderboard window directly using locally stored data.
        """
        try:
            # If data is available locally, display it directly.
            if hasattr(self, 'leaderboard_data') and self.leaderboard_data:
                self.show_leaderboard(self.leaderboard_data)
            else:
                # If no data is available, display an empty leaderboard and request data.
                self.show_leaderboard([])
                # Simultaneously request the latest data
                leaderboard_msg = json.dumps({"action": "get_leaderboard"})
                self.send(leaderboard_msg)
            
            # Display the prompt regardless of whether data is available.
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, "【Ranking】Opening leaderboard...\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
        except Exception as e:
            print(f"Error opening leaderboard: {e}")
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【Error】Failed to open leaderboard: {str(e)}\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
    
    def show_leaderboard(self, leaderboard_data):
        """Display the Leaderboard Window"""
        leaderboard_win = Toplevel(self.Window)
        leaderboard_win.title("Snake Game Leaderboard 🐍")
        leaderboard_win.geometry("400x500")
        leaderboard_win.configure(bg="#17202A")
        leaderboard_win.resizable(False, False)
        
        # titles
        title_label = Label(
            leaderboard_win,
            text="🐍 Snake Game Ranking 🐍",
            font=("Helvetica", 18, "bold"),
            bg="#17202A",
            fg="#4CAF50"
        )
        title_label.pack(pady=15)
        
        # Create a framework for displaying leaderboards
        frame = Frame(leaderboard_win, bg="#2C3E50")
        frame.pack(pady=10, padx=20, fill=BOTH, expand=True)
        
        # headers
        header_frame = Frame(frame, bg="#34495E")
        header_frame.pack(fill=X)
        
        headers = ["Rank", "Player", "Score", "Trophy"]
        for i, header in enumerate(headers):
            label = Label(
                header_frame,
                text=header,
                font=("Helvetica", 12, "bold"),
                bg="#34495E",
                fg="white",
                width=8 if i != 1 else 10
            )
            label.grid(row=0, column=i, padx=0, pady=5, sticky="ew")
        
        # Display ranking data
        if not leaderboard_data:
            no_data_label = Label(
                frame,
                text="No game records yet!\nPlay the Snake Game to get on the leaderboard!",
                font=("Helvetica", 11),
                bg="#2C3E50",
                fg="#BDC3C7",
                justify=CENTER
            )
            no_data_label.pack(pady=50)
        else:
            # Show Top 10
            for idx, (player, score) in enumerate(leaderboard_data[:10], 1):
                row_frame = Frame(frame, bg="#2C3E50" if idx % 2 == 1 else "#34495E")
                row_frame.pack(fill=X, pady=2)
                
                # ranking
                rank_label = Label(
                    row_frame,
                    text=str(idx),
                    font=("Helvetica", 11, "bold"),
                    bg=row_frame["bg"],
                    fg="white",
                    width=8
                )
                rank_label.grid(row=0, column=0, padx=2)
                
                # player names
                player_label = Label(
                    row_frame,
                    text=player[:15],  # 限制长度
                    font=("Helvetica", 11),
                    bg=row_frame["bg"],
                    fg="#3498DB",
                    width=15
                )
                player_label.grid(row=0, column=1, padx=2)
                
                # scores
                score_label = Label(
                    row_frame,
                    text=str(score),
                    font=("Helvetica", 11, "bold"),
                    bg=row_frame["bg"],
                    fg="#E74C3C",
                    width=8
                )
                score_label.grid(row=0, column=2, padx=2)
                
                # Trophy Icon
                trophy = "🏆" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                trophy_label = Label(
                    row_frame,
                    text=trophy,
                    font=("Helvetica", 12),
                    bg=row_frame["bg"],
                    fg="gold" if idx <= 3 else "silver",
                    width=8
                )
                trophy_label.grid(row=0, column=3, padx=2)
        
        # update time
        update_label = Label(
            leaderboard_win,
            text=f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            font=("Helvetica", 9),
            bg="#17202A",
            fg="#7F8C8D"
        )
        update_label.pack(pady=5)
        
        # refresh button
        refresh_button = Button(
            leaderboard_win,
            text="🔄 Refresh",
            font=("Helvetica", 10, "bold"),
            bg="#3498DB",
            fg="white",
            command=lambda: self.refresh_leaderboard(leaderboard_win)
        )
        refresh_button.pack(pady=10, ipadx=20, ipady=5)
        
        # close button
        close_button = Button(
            leaderboard_win,
            text="Close",
            font=("Helvetica", 10),
            bg="#E74C3C",
            fg="white",
            command=leaderboard_win.destroy
        )
        close_button.pack(pady=5, ipadx=30, ipady=3)    

    def refresh_leaderboard(self, window=None):
        """Refresh ranking data"""
        if window:
            window.destroy()
        # Request ranking data again
        leaderboard_msg = json.dumps({"action": "get_leaderboard"})
        self.send(leaderboard_msg)


    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()

            if len(peer_msg) > 0:
                try:
                    msg_json = json.loads(peer_msg)
                    
                    if msg_json.get("action") == "leaderboard":
                        leaderboard_data = msg_json.get("results", [])
                        # Update locally stored leaderboard data
                        self.leaderboard_data = leaderboard_data
                        
                        # Optional: If the leaderboard window is already open, update its contents.
                        if hasattr(self, 'current_leaderboard_window') and self.current_leaderboard_window.winfo_exists():
                            self.update_leaderboard_content(leaderboard_data)
                        
                        continue  

                except json.JSONDecodeError:
                    pass  
            
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                new_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""

                # Processing Received Messages - Performing Sentiment Analysis Only on Others' Messages
                if new_msg.strip() and self.sentiment_mode:
                    if not new_msg.startswith("【"):  # Skip system messages
                        lines = new_msg.split('\n')
                        processed = []

                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            # ----Square bracket format, such as [A] Hello there ----
                            if line.startswith("[") and "]" in line:
                                end = line.find("]")
                                sender = line[1:end]
                                message = line[end+1:].strip()

                                # Analyzing others, not the system, not oneself
                                if sender != self.name and sender != "🤖":
                                    label, emoji = analyze_sentiment(message)
                                    processed.append(f"[{sender}]{message} [{label} {emoji}]")
                                else:
                                    processed.append(line)
                            else:
                                processed.append(line)

                        new_msg = "\n".join(processed)



                self.textCons.config(state=NORMAL)
                # Record chat history (store plain text only)
                # ------------ Clean chat history logging ------------
                clean_lines = []

                for line in new_msg.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Example: [A] Hi → Remove the sender, leaving only the message
                    if line.startswith("[") and "]" in line:
                        end = line.find("]")
                        msg = line[end+1:].strip()

                        # Remove possible sentiment tag "[Positive 😊]"
                        msg = re.sub(r"\[[^\]]+\]$", "", msg).strip()

                        # Record msg whenever it contains content.
                        if msg:
                            clean_lines.append(msg)
                    else:
                        # For other messages (such as system messages), no processing is performed.
                        clean_lines.append(line)

                self.chat_history.extend(clean_lines)
        # ------------ END Clean chat history logging ------------


                self.textCons.insert(END, new_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

                        # ★★★ fix: clear system_msg
                self.system_msg = ""


    def run(self):
        self.login()

    def open_emoji_window(self):
        
        emoji_win = Toplevel(self.Window)
        emoji_win.title("Select Emoji")
        emoji_win.geometry("320x180")
        emoji_win.configure(bg = "#17202A")
        
        # emoji list
        emojis = [
            "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣",
            "😊", "😇", "🙂", "😉", "😍", "🥰", "😘", "😗",
            "😭", "😢", "😥", "😰", "😱", "😡", "😠", "🤬",
            "👍", "👎", "👌", "✌️", "🤞", "🙏", "👏", "💪",
            "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍",
            "🎉", "🎊", "🎈", "🎁", "🔥", "⭐", "✨", "💯"
        ]
        
        # emoji site
        row = 0
        col = 0
        for emoji in emojis:
            btn = Button(emoji_win,
                        text = emoji,
                        font = "Helvetica 14",
                        width = 3,
                        bg = "#ABB2B9",
                        command = lambda e=emoji: self.add_emoji(e))
            btn.grid(row=row, column=col, padx=3, pady=3)
            col += 1
            if col > 7:  # 8 emoji per line
                col = 0
                row += 1    
    
    def add_emoji(self, emoji):
        # insert emoji in the place
        self.entryMsg.insert(INSERT, emoji)
        # keep the focus
        self.entryMsg.focus_set()
    
    def toggle_chatbot(self):
        self.chatbot_mode = not self.chatbot_mode
        self.textCons.config(state=NORMAL)
        if self.chatbot_mode:
            self.textCons.insert(END, "【ChatBot Mode Start】\n\n")
            # Change the button color and text to let users know the bot is active.
            self.buttonBot.config(bg="#4CAF50", text="Bot: ON")
        else:
            self.textCons.insert(END, "【ChatBot Mode End】\n\n")
            # Restore the button to its original state
            self.buttonBot.config(bg="#445566", text="Bot: OFF")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    
    def open_personality_window(self):
        personality_win = Toplevel(self.Window)
        personality_win.title("ChatBot Personality")
        personality_win.geometry("250x200")
        personality_win.configure(bg="#17202A")
        
        Label(personality_win, 
            text="Select Personality:",
            bg="#17202A", fg="white",
            font="Helvetica 12 bold").pack(pady=10)
        
        # Obtain available personality options
        personalities = self.chatbot.get_personality_options()
        
        for personality in personalities:
            btn = Button(personality_win,
                        text=personality.capitalize(),
                        font="Helvetica 11",
                        width=15,
                        bg="#445566",
                        fg="white",
                        command=lambda p=personality: self.select_personality(p, personality_win))
            btn.pack(pady=5)

    def select_personality(self, personality, window):
        if self.chatbot.set_personality(personality):
            # Display character switching information in the chat window
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【ChatBot personality changed to: {personality}】\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            window.destroy()
    


# create a GUI class object
if __name__ == "__main__": 
    g = GUI()
