import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, messagebox
from transformers import pipeline
import cv2
import threading  # Import the threading module

# Initialize the text summarization pipeline
summarizer = pipeline("summarization")

# Create the main application window
root = tk.Tk()
root.title("Summarization App")
root.configure(bg="blue")

# Function to perform text summarization
def summarize_text():
    input_text = text_input.get("1.0", "end-1c")
    max_word_limit = 2000  # Set your desired maximum word limit
    min_word_limit = 10  # Set your desired minimum word limit
    word_count = len(input_text.split())
    if word_count < min_word_limit:
        messagebox.showerror("Word Limit Not Met", f"Please enter at least {min_word_limit} words.")
        return
    
    if word_count > max_word_limit:
        messagebox.showerror("Word Limit Exceeded", f"Please limit your input to {max_word_limit} words or less.")
        return
    
    # Rest of your summarization code here

    max_length = 600  # Set your desired maximum length for each chunk
    text_chunks = [input_text[i:i+max_length] for i in range(0, len(input_text), max_length)]
    
    summaries = []
    for chunk in text_chunks:
        summary = summarize_text_model(chunk)
        summaries.append(summary)
    
    combined_summary = "\n".join(summaries)
    
    text_output.delete("1.0", "end")
    text_output.insert("1.0", combined_summary)


# Function to perform video summarization
def summarize_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if file_path:
        output_path = "summarized_video.mp4"
        # Run the video summarization process in a separate thread
        threading.Thread(target=summarize_video_model, args=(file_path, output_path)).start()

def play_summarized_video(output_video_path):
    cap = cv2.VideoCapture(output_video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Summarized Video", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

# Text summarization function using transformers
def summarize_text_model(input_text):
    summary = summarizer(input_text, max_length=150, min_length=30, do_sample=True)[0]['summary_text']
    return summary

# Video summarization function using OpenCV
def summarize_video_model(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    selected_frames = [int(frame) for frame in range(0, total_frames, 30)]

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    for frame_num in selected_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            out.write(frame)
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    # Play the summarized video
    play_summarized_video(output_video_path)

# Create and arrange UI elements
text_input = Text(root, wrap=tk.WORD, height=20, width=40, bg="white")
text_input.pack(padx=10, pady=10)

text_summarize_button = tk.Button(root, text="Summarize Text", command=summarize_text)
text_summarize_button.pack()

text_output = Text(root, wrap=tk.WORD, height=10, width=40,bg="lightyellow")
text_output.pack(padx=10, pady=10)

video_summarize_button = tk.Button(root, text="Summarize Video", command=summarize_video)
video_summarize_button.pack()

# Start the main event loop
root.mainloop()