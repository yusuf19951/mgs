#!/usr/bin/env python3
"""
TürkGPT Masaüstü Uygulaması
Geliştirici: Kadir Tolga Erdoğan - MaviGlobalSoft

Kurulum:
1. Python 3.8+ yüklü olmalı
2. Gereksinimleri yükleyin: pip install requests tkinter
3. Çalıştırın: python turkgpt-desktop.py

EXE Yapmak İçin:
1. PyInstaller yükleyin: pip install pyinstaller
2. EXE oluşturun: pyinstaller --onefile --windowed --name TurkGPT turkgpt-desktop.py
3. EXE dosyası 'dist' klasöründe olacak
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import json
import threading
from datetime import datetime

# API Ayarları - Backend'e bağlı, tamamen ücretsiz!
BACKEND_URL = 'https://turkgpt-ai.preview.emergentagent.com'
API_URL = f'{BACKEND_URL}/api'

class TurkGPT:
    def __init__(self, root):
        self.root = root
        self.root.title("TürkGPT - Türkçe AI Asistan")
        self.root.geometry("800x600")
        self.root.configure(bg='#0f172a')
        
        self.session_id = None
        self.create_session()
        
        self.setup_ui()
        
    def create_session(self):
        """Yeni oturum oluştur"""
        try:
            response = requests.post(f'{API_URL}/sessions', 
                json={'title': 'Desktop Sohbet'},
                timeout=10
            )
            if response.status_code == 200:
                self.session_id = response.json()['id']
                print(f"Oturum oluşturuldu: {self.session_id}")
        except Exception as e:
            print(f"Oturum oluşturulamadı: {e}")
        
    def setup_ui(self):
        # Başlık
        title_frame = tk.Frame(self.root, bg='#0f172a')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 TürkGPT",
            font=('Arial', 24, 'bold'),
            bg='#0f172a',
            fg='#06b6d4'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Yapay Zeka Destekli Türkçe Asistan",
            font=('Arial', 10),
            bg='#0f172a',
            fg='#94a3b8'
        )
        subtitle_label.pack()
        
        dev_label = tk.Label(
            title_frame,
            text="Developed by Kadir Tolga Erdoğan • MaviGlobalSoft",
            font=('Arial', 9),
            bg='#0f172a',
            fg='#64748b'
        )
        dev_label.pack(pady=5)
        
        # Chat alanı
        chat_frame = tk.Frame(self.root, bg='#1e293b')
        chat_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#1e293b',
            fg='#e2e8f0',
            insertbackground='#06b6d4',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)
        
        # Tag'ler
        self.chat_area.tag_config('user', foreground='#06b6d4', font=('Arial', 11, 'bold'))
        self.chat_area.tag_config('assistant', foreground='#8b5cf6', font=('Arial', 11, 'bold'))
        self.chat_area.tag_config('message', foreground='#e2e8f0')
        self.chat_area.tag_config('time', foreground='#64748b', font=('Arial', 9))
        
        # Hoş geldin mesajı
        self.add_system_message("TürkGPT'ye hoş geldiniz! Size nasıl yardımcı olabilirim?")
        
        # Input alanı
        input_frame = tk.Frame(self.root, bg='#0f172a')
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.input_box = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='#1e293b',
            fg='#e2e8f0',
            insertbackground='#06b6d4',
            relief=tk.FLAT,
            bd=5
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_box.bind('<Return>', lambda e: self.send_message())
        
        self.send_button = tk.Button(
            input_frame,
            text="Gönder",
            command=self.send_message,
            font=('Arial', 11, 'bold'),
            bg='#06b6d4',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Temizle butonu
        clear_button = tk.Button(
            input_frame,
            text="Temizle",
            command=self.clear_chat,
            font=('Arial', 11),
            bg='#475569',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
    def add_system_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\n💡 Sistem: ", 'assistant')
        self.chat_area.insert(tk.END, message + "\n", 'message')
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        
    def add_user_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n👤 Siz ({timestamp}): ", 'user')
        self.chat_area.insert(tk.END, message + "\n", 'message')
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        
    def add_assistant_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n🤖 TürkGPT ({timestamp}): ", 'assistant')
        self.chat_area.insert(tk.END, message + "\n", 'message')
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        
    def send_message(self):
        message = self.input_box.get().strip()
        if not message:
            return
            
        self.input_box.delete(0, tk.END)
        self.send_button.config(state=tk.DISABLED, text="Bekleyin...")
        
        # Kullanıcı mesajını göster
        self.add_user_message(message)
        
        # Thread'de API çağrısı yap
        thread = threading.Thread(target=self.get_ai_response, args=(message,))
        thread.daemon = True
        thread.start()
        
    def get_ai_response(self, user_message):
        try:
            # Konuşma geçmişine ekle
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            
            # API çağrısı
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            }
            
            data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'system',
                        'content': "Sen TürkGPT'sin, Türkçe konuşan yardımsever bir yapay zeka asistanısın. Her zaman kibar, bilgili ve dostça bir şekilde yanıt verirsin."
                    }
                ] + self.conversation_history,
                'temperature': 0.7,
                'max_tokens': 1000
            }
            
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                
                # Konuşma geçmişine ekle
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': assistant_message
                })
                
                # UI'da göster
                self.root.after(0, self.add_assistant_message, assistant_message)
            else:
                error_msg = f"API Hatası: {response.status_code}"
                self.root.after(0, self.add_system_message, error_msg)
                
        except Exception as e:
            error_msg = f"Hata: {str(e)}"
            self.root.after(0, self.add_system_message, error_msg)
            
        finally:
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="Gönder"))
            self.root.after(0, lambda: self.input_box.focus())
            
    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.conversation_history = []
        self.add_system_message("Sohbet temizlendi. Yeni bir konuşma başlatabilirsiniz.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TurkGPT(root)
    root.mainloop()
