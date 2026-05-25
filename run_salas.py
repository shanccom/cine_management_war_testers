import tkinter as tk
from ui.salas_ui import SalasUI

def main():
    root = tk.Tk()
    root.title("Ventana Principal (Temporal)")
    root.geometry("300x150")
    
    tk.Label(root, text="Simulador de Main", font=("Arial", 12)).pack(pady=10)
    
    app_salas = SalasUI(root)
    btn_abrir = tk.Button(
        root, 
        text="Abrir Modulo de Salas", 
        command=app_salas.show,
        bg="#008CBA",
        fg="white"
    )
    btn_abrir.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()