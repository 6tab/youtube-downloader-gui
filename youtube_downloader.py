import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
from tkinter.font import Font
import webbrowser

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=35, corner_radius=20, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg='#2C2C2C', **kwargs)
        self.command = command
        self.text = text
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        
        # Initial colors
        self.normal_color = '#E31937'
        self.hover_color = '#B8152C'
        self.current_color = self.normal_color
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
        self.draw()

    def draw(self):
        self.delete('all')
        # Create round rectangle
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, self.current_color)
        # Add text
        self.create_text(self.width/2, self.height/2, text=self.text, 
                        fill='white', font=('Arial Black', 10, 'bold'))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        self.create_polygon(points, smooth=True, fill=color)

    def on_enter(self, event):
        self.current_color = self.hover_color
        self.draw()

    def on_leave(self, event):
        self.current_color = self.normal_color
        self.draw()

    def on_click(self, event):
        if self.command:
            self.command()

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("700x700")
        self.root.configure(bg='#2C2C2C')
        
        # Make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Custom fonts
        self.title_font = ('Arial Black', 24, 'bold')
        self.label_font = ('Arial Black', 12, 'bold')
        self.button_font = ('Arial Black', 10, 'bold')
        
        # Create main frame with responsive grid
        self.main_frame = ttk.Frame(root, padding="20", style='Modern.TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Styles
        self.style = ttk.Style()
        self.style.configure('Modern.TFrame', background='#2C2C2C')
        self.style.configure('Modern.TLabel', 
                           background='#2C2C2C', 
                           foreground='white',
                           font=self.label_font)
        
        # Title with custom font
        title_label = tk.Label(self.main_frame,
                             text="YouTube Downloader",
                             font=self.title_font,
                             bg='#2C2C2C',
                             fg='white')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # URL Entry with rounded corners
        tk.Label(self.main_frame,
                text="Video URL:",
                font=self.label_font,
                bg='#2C2C2C',
                fg='white').grid(row=1, column=0, sticky='w', pady=5)
        
        # Custom Entry style
        self.url_entry = tk.Entry(self.main_frame,
                                width=50,
                                bg='#3D3D3D',
                                fg='white',
                                insertbackground='white',
                                relief='flat',
                                font=('Arial', 12))
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        
        # Save Location
        tk.Label(self.main_frame,
                text="Save to:",
                font=self.label_font,
                bg='#2C2C2C',
                fg='white').grid(row=2, column=0, sticky='w', pady=5)
        
        self.save_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.location_entry = tk.Entry(self.main_frame,
                                     textvariable=self.save_path,
                                     width=40,
                                     bg='#3D3D3D',
                                     fg='white',
                                     font=('Arial', 12),
                                     relief='flat')
        self.location_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        
        browse_button = RoundedButton(self.main_frame,
                                    text="Browse",
                                    command=self.browse_location,
                                    width=100,
                                    height=30)
        browse_button.grid(row=2, column=2, pady=5, padx=5)
        
        # Format Type Selection
        tk.Label(self.main_frame,
                text="Format:",
                font=self.label_font,
                bg='#2C2C2C',
                fg='white').grid(row=3, column=0, sticky='w', pady=5)
        
        self.format_type = tk.StringVar(value="video")
        
        # Custom radio button style
        radio_style = {'bg': '#2C2C2C',
                      'fg': 'white',
                      'selectcolor': '#E31937',
                      'font': self.button_font,
                      'activebackground': '#2C2C2C',
                      'activeforeground': 'white'}
        
        video_radio = tk.Radiobutton(self.main_frame,
                                   text="Video (MP4)",
                                   variable=self.format_type,
                                   value="video",
                                   command=self.update_quality_options,
                                   **radio_style)
        audio_radio = tk.Radiobutton(self.main_frame,
                                   text="Audio (MP3)",
                                   variable=self.format_type,
                                   value="audio",
                                   command=self.update_quality_options,
                                   **radio_style)
                                   
        video_radio.grid(row=3, column=1, sticky='w', pady=5)
        audio_radio.grid(row=3, column=2, sticky='w', pady=5)
        
        # Quality Selection
        tk.Label(self.main_frame,
                text="Quality:",
                font=self.label_font,
                bg='#2C2C2C',
                fg='white').grid(row=4, column=0, sticky='w', pady=5)
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(self.main_frame,
                                        textvariable=self.quality_var,
                                        state='readonly',
                                        font=('Arial', 12),
                                        width=48)
        self.quality_combo.grid(row=4, column=1, columnspan=2, sticky='ew', pady=5)
        self.update_quality_options()
        
        # File Size Preview
        self.size_label = tk.Label(self.main_frame,
                                 text="Estimated file size: -",
                                 font=self.label_font,
                                 bg='#2C2C2C',
                                 fg='white')
        self.size_label.grid(row=5, column=0, columnspan=3, sticky='w', pady=5)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.style.configure("Modern.Horizontal.TProgressbar",
                           troughcolor='#3D3D3D',
                           background='#E31937',
                           borderwidth=0)
        self.progress_bar = ttk.Progressbar(self.main_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          style="Modern.Horizontal.TProgressbar")
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Status Label
        self.status_label = tk.Label(self.main_frame,
                                   text="Ready",
                                   font=self.label_font,
                                   bg='#2C2C2C',
                                   fg='white')
        self.status_label.grid(row=7, column=0, columnspan=3, sticky='w', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.download_button = RoundedButton(button_frame,
                                           text="Download",
                                           command=self.start_download,
                                           width=150,
                                           height=40)
        self.download_button.grid(row=0, column=0, padx=10)
        
        preview_button = RoundedButton(button_frame,
                                     text="Preview Size",
                                     command=self.preview_size,
                                     width=150,
                                     height=40)
        preview_button.grid(row=0, column=1, padx=10)

        # Credits Button
        credits_button = RoundedButton(self.main_frame,
                                      text="Credits",
                                      command=lambda: webbrowser.open("https://github.com/6tab"),
                                      width=150,
                                      height=40)
        credits_button.grid(row=9, column=0, columnspan=3, pady=20)

    def update_quality_options(self):
        if self.format_type.get() == "video":
            qualities = [
                "2160p (4K)",
                "1440p (2K)",
                "1080p (Full HD)",
                "720p (HD)",
                "480p",
                "360p",
                "240p",
                "144p"
            ]
        else:
            qualities = [
                "320kbps (High Quality)",
                "256kbps (Good Quality)",
                "192kbps (Medium Quality)",
                "128kbps (Low Quality)"
            ]
        self.quality_combo['values'] = qualities
        self.quality_combo.set(qualities[2] if self.format_type.get() == "video" else qualities[0])

    def get_format_string(self):
        quality = self.quality_var.get()
        if self.format_type.get() == "video":
            resolution = quality.split()[0].replace('p', '')
            return f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'
        else:
            bitrate = quality.split()[0].replace('kbps', '')
            return f'bestaudio[abr<={bitrate}]/best'

    def preview_size(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
            
        self.status_label.config(text="Fetching size information...")
        threading.Thread(target=self._fetch_size, args=(url,), daemon=True).start()

    def _fetch_size(self, url):
        try:
            ydl_opts = {
                'format': self.get_format_string(),
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'filesize' in info:
                    size_mb = info['filesize'] / (1024 * 1024)
                    self.root.after(0, lambda: self.size_label.config(
                        text=f"Estimated file size: {size_mb:.1f} MB"))
                else:
                    self.root.after(0, lambda: self.size_label.config(
                        text="Couldn't estimate file size"))
        except Exception as e:
            self.root.after(0, lambda: self.size_label.config(
                text="Error fetching file size"))

    def browse_location(self):
        directory = filedialog.askdirectory(initialdir=self.save_path.get())
        if directory:
            self.save_path.set(directory)

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.progress_var.set(progress)
                    self.status_label.config(text=f"Downloading... {progress:.1f}%")
            except Exception as e:
                print(f"Progress update error: {e}")

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return

        self.download_button.config(state='disabled')
        self.status_label.config(text="Starting download...")
        
        ydl_opts = {
            'format': self.get_format_string(),
            'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
            'ffmpeg_location': os.path.dirname(__file__),  # Use local FFmpeg
        }

        if self.format_type.get() == "audio":
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text="Download completed!")
            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            self.status_label.config(text="Download failed!")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.download_button.config(state='normal')
            self.progress_var.set(0)

    def start_download(self):
        download_thread = threading.Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()

def main():
    root = tk.Tk()
    root.configure(bg='#2C2C2C')
    # Set minimum window size
    root.minsize(700, 700)
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()