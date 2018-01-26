import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgits()

    def createWidgits(self):
        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.quitButton.grid()

        self.canv = tk.Canvas(self)
        self.canv.grid()

        self.img = tk.PhotoImage(file="grid.png")
        self.bm = self.canv.create_image(100, 100, image=self.img)
        self.bm

    def update_image(self):
        self.img = tk.PhotoImage(file="grid.png")
        self.canv.itemconfigure(self.bm, image=self.img)
        print("Test")
        self.canv.after(100, self.update_image)


app = Application()
app.master.title("Sample app")
app.update_image()
app.mainloop()
