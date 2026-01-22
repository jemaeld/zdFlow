from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import sys
import os

# Importar common (truco para que funcione la ruta)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.models import TicketModel, TicketUpdate, TaskStatus, UserRole

app = FastAPI(title="zdFlow Server", version="1.0.0")

# BASE DE DATOS EN MEMORIA
db_tickets: List[TicketModel] = []
ticket_counter = 1

@app.post("/tickets/", response_model=TicketModel)
def create_ticket(ticket: TicketModel):
    global ticket_counter
    ticket.id = ticket_counter
    ticket.status = TaskStatus.REQUEST
    ticket.created_at = datetime.now()
    ticket.handler_user = None
    db_tickets.append(ticket)
    ticket_counter += 1
    return ticket

@app.get("/tickets/", response_model=List[TicketModel])
def get_tickets():
    return db_tickets

@app.patch("/tickets/{ticket_id}/{user_role}/{username}")
def update_ticket_status(ticket_id: int, user_role: UserRole, username: str, update: TicketUpdate):
    ticket = next((t for t in db_tickets if t.id == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    new_status = update.status
    current_status = ticket.status

    # LÓGICA DE PRODUCCIÓN (CLIENTE)
    if user_role == UserRole.PRODUCTION:
        if new_status == TaskStatus.CANCELED:
            if ticket.requester_user != username:
                raise HTTPException(status_code=403, detail="No es tu ticket")
            if current_status not in [TaskStatus.REQUEST, TaskStatus.TODO]:
                raise HTTPException(status_code=400, detail="Ya lo están surtiendo")
            ticket.status = TaskStatus.CANCELED
            
        elif new_status == TaskStatus.DONE:
            if current_status != TaskStatus.DOING:
                raise HTTPException(status_code=400, detail="El material no está en camino")
            ticket.status = TaskStatus.DONE
            ticket.finished_at = datetime.now()
        else:
             raise HTTPException(status_code=403, detail="Acción no permitida")

    # LÓGICA DE ALMACÉN (PROVEEDOR)
    elif user_role == UserRole.WAREHOUSE:
        if new_status == TaskStatus.TODO: # Aceptar
            ticket.status = TaskStatus.TODO
            ticket.accepted_at = datetime.now()
            ticket.handler_user = username
        elif new_status == TaskStatus.DOING: # Surtir
            ticket.status = TaskStatus.DOING
            ticket.started_at = datetime.now()
            ticket.handler_user = username
        elif new_status == TaskStatus.REJECTED: # Rechazar
             ticket.status = TaskStatus.REJECTED
             ticket.handler_user = username
        else:
             raise HTTPException(status_code=403, detail="Acción no permitida")

    return ticket