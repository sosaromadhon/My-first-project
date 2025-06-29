# main.py
# Kode Program Game "Ketuk Objek" - Versi Lengkap dan Final

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
import random

# Inisialisasi JsonStore untuk menyimpan skor tertinggi
# File highscores.json akan dibuat di direktori data aplikasi Kivy
store = JsonStore('highscores.json')

# --- Kelas Objek yang Bisa Diketuk ---
class TapObject(Button):
    def __init__(self, game_screen, life_time, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.size_hint = (None, None)
        self.size = (100, 100)  # Ukuran objek dalam piksel
        
        # Menggunakan gambar sebagai latar belakang objek
        # Pastikan 'object.png' dan 'object_tapped.png' ada di direktori yang sama
        self.background_normal = 'object.png'
        self.background_down = 'object_tapped.png' # Gambar saat objek diketuk
        self.text = '' # Hapus teks default tombol
        
        # Jadwalkan objek untuk menghilang secara otomatis setelah 'life_time' detik
        self.disappear_event = Clock.schedule_once(self.disappear, life_time)
        
        # Mengikat event saat objek diketuk
        self.bind(on_release=self.on_tap)

    def on_tap(self, instance):
        # Batalkan jadwal menghilang jika objek diketuk
        Clock.unschedule(self.disappear_event)
        self.game_screen.update_score(10) # Tambah skor
        self.parent.remove_widget(self) # Hapus objek dari layar

    def disappear(self, dt):
        """
        Dipanggil ketika objek menghilang secara otomatis (timeout) tanpa diketuk.
        Bisa ditambahkan logika pengurangan skor di sini jika diinginkan.
        """
        if self.parent: # Pastikan objek masih memiliki parent sebelum dihapus
            self.parent.remove_widget(self)

# --- Kelas untuk Layar Game Utama ---
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.time_left = 30 # Durasi game dalam detik
        self.spawn_interval = 0.8 # Interval (detik) antar spawn objek baru (lebih cepat dari 1.0)
        self.object_life_time = 1.0 # Durasi hidup objek di layar sebelum menghilang (lebih cepat dari 1.5)
        
        # Layout utama layar game (vertikal: top bar di atas, area game di bawah)
        main_layout = BoxLayout(orientation='vertical')
        
        # Area untuk menampilkan skor dan timer
        top_bar_layout = BoxLayout(size_hint_y=0.1) # Mengambil 10% tinggi layar
        self.score_label = Label(text=f'Skor: {self.score}', font_size='24sp')
        self.timer_label = Label(text=f'Waktu: {self.time_left}', font_size='24sp')
        top_bar_layout.add_widget(self.score_label)
        top_bar_layout.add_widget(self.timer_label)
        
        # Area game tempat objek akan muncul (menggunakan FloatLayout untuk posisi bebas)
        self.game_area = FloatLayout()
        
        main_layout.add_widget(top_bar_layout)
        main_layout.add_widget(self.game_area)
        self.add_widget(main_layout)

    def update_score(self, points):
        """Memperbarui skor pemain dan memperbarui tampilan Label skor."""
        self.score += points
        self.score_label.text = f'Skor: {self.score}'

    def update_timer(self, dt):
        """Fungsi ini dipanggil setiap detik untuk mengurangi waktu."""
        self.time_left -= 1
        self.timer_label.text = f'Waktu: {self.time_left}'
        if self.time_left <= 0:
            self.end_game() # Panggil end_game jika waktu habis

    def spawn_object(self, dt):
        """Memunculkan objek baru secara acak di area game."""
        if self.time_left > 0: # Hanya spawn objek jika waktu masih ada
            new_object = TapObject(self, self.object_life_time)
            
            # Mendapatkan ukuran area game untuk membatasi posisi acak
            game_area_width = self.game_area.width
            game_area_height = self.game_area.height
            
            # Hitung batas maksimum X dan Y agar objek tidak keluar dari layar
            # max(0, ...) untuk menghindari nilai negatif jika area game terlalu kecil
            max_x = max(0, int(game_area_width - new_object.width))
            max_y = max(0, int(game_area_height - new_object.height))

            if max_x >= 0 and max_y >= 0:
                new_object.pos = (random.randint(0, max_x), random.randint(0, max_y))
                self.game_area.add_widget(new_object)
            else:
                print("Warning: Game area is too small for the object to be placed randomly.")


    def on_enter(self, *args):
        """Dipanggil setiap kali layar GameScreen menjadi aktif."""
        self.score = 0
        self.time_left = 30 # Reset waktu saat layar aktif
        self.update_score(0)
        self.update_timer(0) # Perbarui tampilan timer awal
        self.game_area.clear_widgets() # Hapus objek dari sesi sebelumnya
        
        # Jadwalkan timer untuk dipanggil setiap 1 detik
        Clock.schedule_interval(self.update_timer, 1)
        # Jadwalkan spawn_object untuk dipanggil sesuai spawn_interval
        self.spawn_event = Clock.schedule_interval(self.spawn_object, self.spawn_interval)

    def on_leave(self, *args):
        """Dipanggil setiap kali layar GameScreen tidak lagi aktif."""
        # Hentikan semua event terjadwal saat meninggalkan layar
        Clock.unschedule(self.update_timer)
        Clock.unschedule(self.spawn_event)

    def end_game(self):
        """Menghentikan semua event terjadwal dan beralih ke layar Game Over."""
        Clock.unschedule(self.update_timer)
        Clock.unschedule(self.spawn_event)
        self.game_area.clear_widgets() # Hapus semua objek yang tersisa
        print(f"Game Selesai! Skor Akhir: {self.score}")
        self.manager.current = 'game_over_screen' # Navigasi ke layar game over

# --- Kelas untuk Layar Menu Utama ---
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        title_label = Label(text='Ketuk Objek Game', font_size='40sp')
        
        start_button = Button(text='Mulai Game', font_size='24sp', size_hint=(0.8, 0.2))
        start_button.bind(on_release=self.start_game)
        
        instructions_button = Button(text='Cara Bermain', font_size='24sp', size_hint=(0.8, 0.2))
        instructions_button.bind(on_release=self.show_instructions)
        
        exit_button = Button(text='Keluar', font_size='24sp', size_hint=(0.8, 0.2))
        # Mengikat tombol keluar ke fungsi stop aplikasi Kivy
        exit_button.bind(on_release=App.get_running_app().stop)
        
        layout.add_widget(title_label)
        layout.add_widget(start_button)
        layout.add_widget(instructions_button)
        layout.add_widget(exit_button)
        self.add_widget(layout)

    def start_game(self, instance):
        """Beralih ke GameScreen saat tombol Mulai Game diklik."""
        self.manager.current = 'game_screen'

    def show_instructions(self, instance):
        """Beralih ke InstructionsScreen saat tombol Cara Bermain diklik."""
        self.manager.current = 'instructions_screen'

# --- Kelas untuk Layar Instruksi/Cara Bermain ---
class InstructionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        instructions_label = Label(text='Ketuk objek yang muncul secepat mungkin!\nKumpulkan skor sebanyak mungkin sebelum waktu habis.\nObjek yang tidak diketuk akan menghilang.',
                                   font_size='20sp', halign='center', valign='middle',
                                   text_size=(self.width * 0.8, None)) # Sesuaikan lebar teks dengan 80% lebar layar
        
        back_button = Button(text='Kembali ke Menu', font_size='24sp', size_hint=(0.8, 0.2))
        back_button.bind(on_release=self.go_back)
        
        layout.add_widget(instructions_label)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_back(self, instance):
        """Beralih kembali ke layar menu utama."""
        self.manager.current = 'main_menu'

# --- Kelas untuk Layar Game Over ---
class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        self.final_score_label = Label(text='Skor Akhir: 0', font_size='32sp')
        
        restart_button = Button(text='Main Lagi', font_size='24sp', size_hint=(0.8, 0.2))
        restart_button.bind(on_release=self.restart_game)
        
        main_menu_button = Button(text='Menu Utama', font_size='24sp', size_hint=(0.8, 0.2))
        main_menu_button.bind(on_release=self.go_to_main_menu)
        
        layout.add_widget(self.final_score_label)
        layout.add_widget(restart_button)
        layout.add_widget(main_menu_button)
        self.add_widget(layout)

    def on_enter(self, *args):
        """
        Dipanggil setiap kali layar GameOverScreen menjadi aktif.
        Mengambil skor akhir dari GameScreen dan memperbarui skor tertinggi.
        """
        # Mendapatkan referensi ke GameScreen untuk mengambil skor
        game_screen = self.manager.get_screen('game_screen')
        final_score = game_screen.score
        
        # Dapatkan skor tertinggi saat ini dari JsonStore
        # Jika 'highscore' belum ada, defaultkan ke 0
        current_highscore = store.get('highscore')['score'] if store.exists('highscore') else 0
        
        score_text = f'Skor Akhir: {final_score}'
        
        if final_score > current_highscore:
            # Simpan skor tertinggi baru jika skor saat ini lebih tinggi
            store.put('highscore', score=final_score)
            score_text += '\nSkor Tertinggi Baru!'
        else:
            score_text += f'\nSkor Tertinggi: {current_highscore}'
        
        self.final_score_label.text = score_text

    def restart_game(self, instance):
        """Memulai ulang game dengan beralih kembali ke GameScreen."""
        self.manager.current = 'game_screen'

    def go_to_main_menu(self, instance):
        """Kembali ke layar menu utama."""
        self.manager.current = 'main_menu'

# --- Kelas Utama Aplikasi Kivy ---
class GameApp(App):
    def build(self):
        # ScreenManager untuk mengelola dan beralih antar layar
        sm = ScreenManager()
        
        # Tambahkan semua layar ke ScreenManager
        # Urutan penambahan tidak terlalu penting, yang penting adalah 'name'
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(InstructionsScreen(name='instructions_screen'))
        sm.add_widget(GameScreen(name='game_screen'))
        sm.add_widget(GameOverScreen(name='game_over_screen'))
        
        return sm

# Memastikan aplikasi berjalan hanya jika script ini dieksekusi secara langsung
if __name__ == '__main__':
    GameApp().run()
