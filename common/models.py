from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ROLES (Quién es quién)
class UserRole(str, Enum):
    PRODUCTION = "PRODUCTION"   # El Cliente: Pide y Recibe
    WAREHOUSE = "WAREHOUSE"     # El Proveedor: Surte y Entrega
    VIEWER = "VIEWER"           # Pantalla TV
    ROOT = "ROOT"               # Admin

# ESTADOS DEL KANBAN (El Ciclo de Vida)
class TaskStatus(str, Enum):
    REQUEST = "REQUEST"    # Petición creada
    TODO = "TODO"          # Aceptada por Almacén
    DOING = "DOING"        # En camino / Sutiendo
    DONE = "DONE"          # Entregada y Confirmada por Producción
    REJECTED = "REJECTED"  # Rechazada por Almacén
    CANCELED = "CANCELED"  # Cancelada por Producción

# MODELO DEL TICKET
class TicketModel(BaseModel):
    id: Optional[int] = None
    material_name: str
    quantity: str
    line_location: str
    notes: Optional[str] = ""
    status: TaskStatus = TaskStatus.REQUEST
    
    requester_user: str   # Usuario de Producción
    handler_user: Optional[str] = None # Usuario de Almacén
    
    created_at: datetime = Field(default_factory=datetime.now)
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# MODELO PARA ACTUALIZACIONES
class TicketUpdate(BaseModel):
    status: Optional[TaskStatus] = None