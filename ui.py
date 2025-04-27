import customtkinter as ctk
from PIL import Image
import backend
import os

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Jarvis AI Assistant")
app.geometry("1000x600")
app.resizable(width=False, height=False)

# Load background image
bg_path = "C:/Users/Dev/Downloads/gradient.png"
try:
    bg_image = Image.open(bg_path)
    bg_ctk_image = ctk.CTkImage(light_image=bg_image, size=(1000, 600))
    bg_label = ctk.CTkLabel(app, image=bg_ctk_image, text="")
    bg_label.place(relwidth=1, relheight=1)
except Exception as e:
    print(f"Error loading background image: {e}")

# Chat Frame
chat_frame = ctk.CTkFrame(app, width=400, height=450, fg_color="black", corner_radius=10)
chat_frame.place(relx=0.5, rely=0.5, anchor="center")

# Chat history
chat_history = ctk.CTkTextbox(chat_frame, width=380, height=250, fg_color="black", text_color="white", wrap="word")
chat_history.pack(pady=10)

# Entry box
entry = ctk.CTkEntry(chat_frame, width=350, placeholder_text="Ask me anything...")
entry.pack(pady=5)

def truncate_text(text, word_limit=100):
    """Return the first 'word_limit' words of text, appending a message if text is longer."""
    words = text.split()
    if len(words) > word_limit:
        return " ".join(words[:word_limit]) + ". [Read the rest from the chat screen]"
    return text

# --- Animated Listening Label Functions ---
listening_label = None
listening_animation_running = False

def animate_listening(dot_count=0):
    global listening_animation_running, listening_label
    if listening_animation_running and listening_label:
        dots = "." * (dot_count % 4)  # cycles: "", ".", "..", "..."
        listening_label.configure(text="Listening" + dots)
        app.after(500, lambda: animate_listening(dot_count + 1))

def start_listening_animation():
    global listening_animation_running, listening_label
    listening_animation_running = True
    # Create the listening label as a child of chat_frame so it appears over the chat area
    if not listening_label:
        listening_label = ctk.CTkLabel(chat_frame, text="Listening", fg_color="transparent",
                                        text_color="white", font=("Helvetica", 16))
        listening_label.place(relx=0.5, rely=0.5, anchor="center")
    animate_listening()

def stop_listening_animation():
    global listening_animation_running, listening_label
    listening_animation_running = False
    if listening_label:
        listening_label.destroy()
        listening_label = None
# --- End Animated Listening Label Functions ---

def send_query():
    """Handles text input from the user."""
    query = entry.get().strip()
    if query:
        chat_history.insert("end", f"You: {query}\n")
        chat_history.see("end")
        entry.delete(0, "end")
        response = backend.execute_command(query)
        chat_history.insert("end", f"Jarvis: {response}\n")
        chat_history.see("end")
        truncated_response = truncate_text(response, 100)
        backend.say(truncated_response)

def speak_command():
    """Handles voice input from the user with an animated Listening overlay."""
    start_listening_animation()
    app.update()  # Force update so the label appears immediately
    query = backend.take_command()
    stop_listening_animation()
    if query:
        chat_history.insert("end", f"You (voice): {query}\n")
        chat_history.see("end")
        response = backend.execute_command(query)
        chat_history.insert("end", f"Jarvis: {response}\n")
        chat_history.see("end")
        truncated_response = truncate_text(response, 100)
        backend.say(truncated_response)

def clear_chat():
    """Clears the chat history."""
    chat_history.delete("1.0", "end")

def exit_app():
    """Force exit the application immediately."""
    app.quit()       # Gracefully exit the Tkinter mainloop.
    os._exit(0)      # Force exit the process immediately.

# Button frame
button_frame = ctk.CTkFrame(chat_frame, fg_color="black")
button_frame.pack(pady=5)

speak_btn = ctk.CTkButton(button_frame, text="🎙 Speak", command=speak_command, width=80, fg_color="blue")
speak_btn.grid(row=0, column=0, padx=5)

send_btn = ctk.CTkButton(button_frame, text="➡ Send", command=send_query, width=80, fg_color="green")
send_btn.grid(row=0, column=1, padx=5)

clear_btn = ctk.CTkButton(button_frame, text="🧹 Clear", command=clear_chat, width=80, fg_color="gray")
clear_btn.grid(row=0, column=2, padx=5)

exit_btn = ctk.CTkButton(chat_frame, text="❌ Exit", command=exit_app, fg_color="red", width=100)
exit_btn.pack(pady=10)

# Bind the Enter key to send the query when typing in the entry box
entry.bind("<Return>", lambda event: send_query())

app.mainloop()
