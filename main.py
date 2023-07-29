import tkinter as tk
from tkinter import ttk
import serial
import threading

def extract_channels(log_data):
    channels = {"BLE API": [], "FILE TRANSFER NAME": [], "FILE LENGTH": [], "Other": []}
    current_channel = None

    for line in log_data.splitlines():
        matched = False
        for tag in channels.keys():
            if tag in line:
                current_channel = tag
                channels[current_channel].append(line)
                matched = True
                break

        if not matched:
            channels["Other"].append(line)

    return channels

def update_log_text():
    global log_data
    channels = extract_channels(log_data.get("1.0", "end"))

    for channel, lines in channels.items():
        tab_text = "\n".join(lines)
        tab_text_widgets[channel].config(state="normal")
        tab_text_widgets[channel].delete("1.0", "end")
        tab_text_widgets[channel].insert("1.0", tab_text)
        tab_text_widgets[channel].config(state="disabled")

def clear_log_text(channel):
    tab_text_widgets[channel].config(state="normal")
    tab_text_widgets[channel].delete("1.0", "end")
    tab_text_widgets[channel].config(state="disabled")

def read_serial_data():
    try:
        with serial.Serial('/dev/pts/10', 115200, timeout=1) as ser:
            while not stop_reading:  # Read data until stop_reading becomes True
                line = ser.readline().decode().strip()
                if line:
                    log_data.insert("end", line + "\n")
                    log_data.see("end")
                    update_log_text()  # Update log channels on the fly
                    
        # The thread will exit only when stop_reading becomes True
        log_data.insert("end", "Stopped reading serial data.\n")
        log_data.see("end")
    except serial.SerialException as e:
        log_data.insert("end", f"Serial port error: {e}\n")
        log_data.see("end")

    stop_button.config(state=tk.DISABLED)  # Disable "Stop Reading" button
    start_button.config(state=tk.NORMAL)  # Enable "Start Reading" button

def start_reading_thread():
    global reading_thread, stop_reading
    stop_reading = False
    reading_thread = threading.Thread(target=read_serial_data)
    reading_thread.start()

    stop_button.config(state=tk.NORMAL)  # Enable "Stop Reading" button
    start_button.config(state=tk.DISABLED)  # Disable "Start Reading" button

def stop_reading_thread():
    global stop_reading
    stop_reading = True
    if reading_thread and reading_thread.is_alive():
        reading_thread.join()

app = tk.Tk()
app.title("Log Visualizer")

notebook = ttk.Notebook(app)
notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

log_data = tk.Text(app, wrap=tk.WORD, width=80, height=20)
log_data.pack()

start_button = tk.Button(app, text="Start Reading", command=start_reading_thread)
start_button.pack(pady=5)

stop_button = tk.Button(app, text="Stop Reading", command=stop_reading_thread, state=tk.DISABLED)
stop_button.pack(pady=5)

tab_text_widgets = {}
clear_buttons = {}
channels = ["BLE API", "FILE TRANSFER NAME", "FILE LENGTH", "Other"]
for channel in channels:
    tab_frame = ttk.Frame(notebook)
    tab_text_widgets[channel] = tk.Text(tab_frame, width=80, height=20)
    tab_text_widgets[channel].insert("1.0", "No data yet.")
    tab_text_widgets[channel].config(state="disabled")
    tab_text_widgets[channel].pack()
    notebook.add(tab_frame, text=channel)

    clear_buttons[channel] = tk.Button(tab_frame, text="Clear All", command=lambda ch=channel: clear_log_text(ch))
    clear_buttons[channel].pack()

app.mainloop()
