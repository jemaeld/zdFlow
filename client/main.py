# CONTINUACIÓN DEL BLOQUE: ERES PRODUCCIÓN
                if ticket['status'] == TaskStatus.DOING:
                    # Botón Confirmar Recepción (Cierra el ciclo)
                    ctk.CTkButton(btn_frame, text="✅ Recibido", width=80, fg_color="#27ae60", 
                                  command=lambda: self.update_status(ticket['id'], TaskStatus.DONE)).pack(side="left", padx=2)
                
                if ticket['status'] == TaskStatus.REQUEST:
                    # Botón Cancelar (Si me arrepiento)
                    ctk.CTkButton(btn_frame, text="Cancelar", width=60, fg_color="#c0392b", 
                                  command=lambda: self.update_status(ticket['id'], TaskStatus.CANCELED)).pack(side="left", padx=2)

    def update_status(self, ticket_id, new_status):
        # Enviar petición al servidor
        try:
            url = f"{SERVER_URL}/tickets/{ticket_id}/{self.current_role}/{self.current_user}"
            payload = {"status": new_status}
            
            response = requests.patch(url, json=payload)
            
            if response.status_code == 200:
                print("Estatus actualizado")
                self.refresh_tickets() # Recargar inmediatamente
            else:
                print(f"Error del servidor: {response.text}")
                
        except Exception as e:
            print(f"Error de red: {e}")

    def open_create_dialog(self):
        # Ventana emergente simple para pedir material
        dialog = ctk.CTkToplevel(self)
        dialog.title("Solicitar Material")
        dialog.geometry("300x300")
        
        ctk.CTkLabel(dialog, text="Material:").pack(pady=5)
        entry_mat = ctk.CTkEntry(dialog)
        entry_mat.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Cantidad:").pack(pady=5)
        entry_qty = ctk.CTkEntry(dialog)
        entry_qty.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Línea / Ubicación:").pack(pady=5)
        entry_loc = ctk.CTkEntry(dialog)
        entry_loc.pack(pady=5)
        
        def send_request():
            data = {
                "material_name": entry_mat.get(),
                "quantity": entry_qty.get(),
                "line_location": entry_loc.get(),
                "requester_user": self.current_user,
                "status": TaskStatus.REQUEST
            }
            requests.post(f"{SERVER_URL}/tickets/", json=data)
            dialog.destroy()
            self.refresh_tickets()
            
        ctk.CTkButton(dialog, text="ENVIAR PEDIDO", fg_color="green", command=send_request).pack(pady=20)

if __name__ == "__main__":
    app = ZdFlowClient()
    app.mainloop()