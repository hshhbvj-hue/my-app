from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import requests
import random
import string
import threading

class MailApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # تحويل الواجهة للإنجليزية بشكل مبسط لتجنب مشكلة المربعات والخطوط
        self.label = Label(text="Mail & Verification Code Generator", font_size='18sp', size_hint_y=None, height=40)
        self.add_widget(self.label)

        self.count_input = TextInput(text="1", hint_text="Number of emails", input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.count_input)

        self.btn_create = Button(text="Create Email & Get Code", size_hint_y=None, height=50, background_color=(0, 0.7, 0.9, 1))
        self.btn_create.bind(on_press=self.start_creation)
        self.add_widget(self.btn_create)

        self.scroll = ScrollView()
        self.log_output = Label(text="Status: Ready...", size_hint_y=None, markup=True)
        self.log_output.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.scroll.add_widget(self.log_output)
        self.add_widget(self.scroll)

    def log(self, text):
        self.log_output.text += f"\n{text}"

    def start_creation(self, instance):
        threading.Thread(target=self.create_email_logic).start()

    def create_email_logic(self):
        self.log_output.text = "Connecting to server..."
        base_url = "https://api.mail.tm"
        
        try:
            domain = requests.get(f"{base_url}/domains").json()["hydra:member"][0]["domain"]
            rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"user_{rand_str}@{domain}"
            password = "Password123!"

            res = requests.post(f"{base_url}/accounts", json={"address": email, "password": password})
            if res.status_code == 201:
                self.log(f"[COLOR=00FF00]✔ Email Created:[/COLOR]\n{email}")
                self.check_messages(base_url, email, password)
            else:
                self.log("[COLOR=FF0000]❌ Failed to create email.[/COLOR]")
        except Exception as e:
            self.log(f"[COLOR=FF0000]Error: {e}[/COLOR]")

    def check_messages(self, base_url, email, password):
        self.log("⏳ Waiting for OTP code (TikTok)...")
        token_res = requests.post(f"{base_url}/token", json={"address": email, "password": password}).json()
        token = token_res.get("token")
        
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            for _ in range(15):
                msg_res = requests.get(f"{base_url}/messages", headers=headers).json()
                messages = msg_res.get("hydra:member", [])
                if messages:
                    msg_id = messages[0]["id"]
                    msg_detail = requests.get(f"{base_url}/messages/{msg_id}", headers=headers).json()
                    self.log(f"[COLOR=FFFF00]🎉 Message Received:[/COLOR]\n{msg_detail.get('text')}")
                    return
                import time
                time.sleep(4)
            self.log("[COLOR=FF0000]❌ Timeout. No code received.[/COLOR]")

class MainApp(App):
    def build(self):
        return MailApp()

if __name__ == '__main__':
    MainApp().run()

