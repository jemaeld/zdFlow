import customtkinter as ctk
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.models import TaskStatus, UserRole

SERVER_URL = "http://127.0.0.1:8000"
REFRESH_RATE = 3000 

class ZdFlowClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("zdFlow - Industrial Client")
        self.geometry("900x600")
        
        self.current_user = None
        self.current_role = None

        # LOGIN FRAME
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(self.login_frame, text="zdFlow Acceso", font=("Arial", 24)).pack(pady=40)
        
        self.role_var = ctk.StringVar(value=UserRole.PRODUCTION.value)
        ctk.CTkOptionMenu(self.login_frame, variable=self.role_var, values=[UserRole.PRODUCTION.value, UserRole.WAREHOUSE.value]).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Usuario")
        self.username_entry.pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Entrar", command=self.login).pack(pady=20)

        # MAIN FRAME
        self.main_frame = ctk.CTkFrame(self)
        self.header_frame = ctk.CTkFrame(self.main_frame, height=50)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.user_label = ctk.CTkLabel(self.header_frame, text="--")
        self.user_label.pack(side="left", padx=10)
        self.btn_create = ctk.CTkButton(self.header_frame, text="+ Pedir Material", fg_color="green", command=self.open_create_dialog)
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def login(self):
        self.current_user = self.username_entry.get()
        if not self.current_user: return
        self.current_role = self.role_var.get()
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.user_label.configure(text=f"{self.current_user} [{self.current_role}]")
        if self.current_role == UserRole.WAREHOUSE.value: self.btn_create.pack_forget()
        self.refresh_tickets()

    def refresh_tickets(self):
        try:
            res = requests.get(f"{SERVER_URL}/tickets/")
            if res.status_code == 200: self.render_tickets(res.json())
        except: pass
        self.after(REFRESH_RATE, self.refresh_tickets)

    def render_tickets(self, tickets):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        for t in tickets:
            c = ctk.CTkFrame(self.scroll_frame)
            c.pack(fill="x", pady=2)
            # Colores
            color = "#95a5a6"
            if t['status'] == TaskStatus.REQUEST: color = "#e74c3c"
            elif t['status'] == TaskStatus.TODO: color = "#f39c12"
            elif t['status'] == TaskStatus.DOING: color = "#3498db"
            elif t['status'] == TaskStatus.DONE: color = "#27ae60"
            
            ctk.CTkLabel(c, text=f" {t['status']} ", fg_color=color, text_color="white", width=80).pack(side="left", padx=5)
            ctk.CTkLabel(c, text=f"{t['material_name']} ({t['quantity']}) - {t['line_location']}", font=("Arial", 14, "bold")).pack(side="left")
            
            btn_f = ctk.CTkFrame(c, fg_color="transparent")
            btn_f.pack(side="right")
            
            # BOTONES ALMACÉN
            if self.current_role == UserRole.WAREHOUSE.value:
                if t['status'] == TaskStatus.REQUEST:
                    ctk.CTkButton(btn_f, text="Aceptar", width=50, fg_color="#f39c12", command=lambda id=t['id']: self.upd(id, TaskStatus.TODO)).pack(side="left", padx=2)
                    ctk.CTkButton(btn_f, text="Rechazar", width=50, fg_color="gray", command=lambda id=t['id']: self.upd(id, TaskStatus.REJECTED)).pack(side="left", padx=2)
                if t['status'] == TaskStatus.TODO:
                    ctk.CTkButton(btn_f, text="Surtir", width=50, fg_color="#3498db", command=lambda id=t['id']: self.upd(id, TaskStatus.DOING)).pack(side="left", padx=2)
            
            # BOTONES PRODUCCIÓN
            if self.current_role == UserRole.PRODUCTION.value and t['requester_user'] == self.current_user:
                if t['status'] == TaskStatus.REQUEST:
                    ctk.CTkButton(btn_f, text="Cancelar", width=50, fg_color="#c0392b", command=lambda id=t['id']: self.upd(id, TaskStatus.CANCELED)).pack(side="left")
                if t['status'] == TaskStatus.DOING:
                    ctk.CTkButton(btn_f, text="Confirmar", width=50, fg_color="#27ae60", command=lambda id=t['id']: self.upd(id, TaskStatus.DONE)).pack(side="left")

    def upd(self, tid, stat):
        try: requests.patch(f"{SERVER_URL}/tickets/{tid}/{self.current_role}/{self.current_user}", json={"status": stat})
        except Exception as e: print(e)
        self.refresh_tickets()

    def open_create_dialog(self):
        d = ctk.CTkToplevel(self)
        d.geometry("300x250")
        inputs = {}
        for f in ["Material", "Cantidad", "Ubicación"]:
            ctk.CTkLabel(d, text=f).pack(); e = ctk.CTkEntry(d); e.pack(); inputs[f]=e
        def send():
            requests.post(f"{SERVER_URL}/tickets/", json={
                "material_name": inputs["Material"].get(), "quantity": inputs["Cantidad"].get(),
                "line_location": inputs["Ubicación"].get(), "requester_user": self.current_user,
                "status": TaskStatus.REQUEST
            }); d.destroy(); self.refresh_tickets()
        ctk.CTkButton(d, text="Enviar", command=send).pack(pady=10)

if __name__ == "__main__":
    app = ZdFlowClient()
    app.mainloop()