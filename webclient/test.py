import tkinter as tk

def update_label_text():
    label.config(text="Hello, Tkinter!")

# 윈도우 생성
window = tk.Tk()
window.title("Simple Tkinter GUI")
window.geometry("300x150")

# 라벨 생성
label = tk.Label(window, text="Press the button!")
label.pack(pady=20)

# 버튼 생성
button = tk.Button(window, text="Click Me!", command=update_label_text)
button.pack()

# 윈도우 실행
window.mainloop()
