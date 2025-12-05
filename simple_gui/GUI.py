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
from tkinter import ttk
from chat_utils import *
import json
from chatbot import ChatBot
from snake_game import SnakeGame
from sentiment_tools import analyze_sentiment
from typing import List
from nlp_tools import extract_keywords_yake, summarize_with_sumy
import re


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
        
        # 在 layout 方法中
        self.buttonBot = Button(self.Window, 
                text="Bot: OFF",  # 初始状态为关闭
                font="Helvetica 10 bold",
                bg="#445566",
                fg="white",
                command=self.toggle_chatbot)

        # 放在右上角
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
        self.buttonSentiment.place(relx=0.18, rely=0.018, 
                                   relheight=0.045, relwidth=0.15)
          
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
    # 新增：切换情感分析功能
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
        检查消息中是否提及bot
        支持 @bot, @chatbot, @Bot, @ChatBot 等格式
        """
        pattern = r'@(bot|chatbot)'
        return re.search(pattern, msg.lower()) is not None  
    def remove_bot_mention(self, msg):
        """
        移除消息中的@bot标记，获取实际要处理的内容
        """
        pattern = r'@(bot|chatbot)\s*'
        return re.sub(pattern, '', msg, flags=re.IGNORECASE).strip()    

    def sendButton(self, msg):
        if len(msg) == 0:
            return

        
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "You: " + msg + "\n")
        # ------------ Add own message to chat history ------------
# 过滤命令，例如 /summary /keywords
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
            # 原始关键词
            result = extract_keywords_yake(self.chat_history, top_k=10)

            # 要过滤掉的垃圾关键词
            ban_list = {
                "Request", "requested", "Connect", "connected", "connecting",
                "chat", "you", "are", "with", "from", "to", "the"
            }

            # 过滤垃圾词（lowercase 匹配）
            cleaned = [w for w in result if w.lower() not in ban_list]

            # 如果删太多，至少保留前几个
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
            
            # 获取bot回复
            bot_reply = self.chatbot.get_response(actual_msg)
            
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, "🤖 Bot: " + bot_reply + "\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
            # 将bot回复广播给所有人
            # 构造特殊格式的消息，让其他客户端也能显示bot回复
            def send_bot_reply():
                import time
                time.sleep(0.1)  # 短暂延迟，确保原始消息先处理
                broadcast_msg = f"🤖 Bot: {bot_reply}"
                # 通过正常流程发送bot回复
                temp_msg = self.my_msg
                self.my_msg = broadcast_msg
                # 等待发送
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
        SnakeGame(self.Window)

    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                new_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""

                # 处理接收到的消息 - 只对别人的消息进行情感分析
                if new_msg.strip() and self.sentiment_mode:
                    if not new_msg.startswith("【"):  # 跳过系统消息
                        lines = new_msg.split('\n')
                        processed = []

                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            # ---- 方括号格式，如 [A]你好呀 ----
                            if line.startswith("[") and "]" in line:
                                end = line.find("]")
                                sender = line[1:end]
                                message = line[end+1:].strip()

                                # 只分析别人，不分析系统，不分析自己
                                if sender != self.name and sender != "🤖":
                                    label, emoji = analyze_sentiment(message)
                                    processed.append(f"[{sender}]{message} [{label} {emoji}]")
                                else:
                                    processed.append(line)
                            else:
                                processed.append(line)

                        new_msg = "\n".join(processed)



                self.textCons.config(state=NORMAL)
                # 记录聊天记录（只存纯文本）
                # ------------ Clean chat history logging ------------
                clean_lines = []

                for line in new_msg.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # 例子: [A]你好呀 → 去掉 sender，只留消息
                    if line.startswith("[") and "]" in line:
                        end = line.find("]")
                        msg = line[end+1:].strip()

                        # 去掉可能的 sentiment 标签 "[Positive 😊]"
                        msg = re.sub(r"\[[^\]]+\]$", "", msg).strip()

                        # 只要 msg 有内容就记录
                        if msg:
                            clean_lines.append(msg)
                    else:
                        # 对于其他消息（例如系统消息），不处理
                        clean_lines.append(line)

                self.chat_history.extend(clean_lines)
        # ------------ END Clean chat history logging ------------


                self.textCons.insert(END, new_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

                        # ★★★ fix: 清空 system_msg
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
            # 改变按钮颜色和文字，让用户知道Bot已开启
            self.buttonBot.config(bg="#4CAF50", text="Bot: ON")
        else:
            self.textCons.insert(END, "【ChatBot Mode End】\n\n")
            # 恢复按钮原始状态
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
        
        # 获取可用人格选项
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
            # 在聊天窗口显示人格切换信息
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"【ChatBot personality changed to: {personality}】\n\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            window.destroy()
    


# create a GUI class object
if __name__ == "__main__": 
    g = GUI()
