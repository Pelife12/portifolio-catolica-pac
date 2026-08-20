"""Modelos do banco (fonte da verdade do schema).

Importar este pacote registra todas as tabelas em `Base.metadata`. O
`migrations/env.py` do Alembic importa daqui para que o autogenerate enxergue
o schema completo e produza as migrations automaticamente.
"""

from app.infrastructure.database.models.afericao import Afericao
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.audit_log import AuditLog
from app.infrastructure.database.models.leira import Leira
from app.infrastructure.database.models.leira_residuo import LeiraResiduo
from app.infrastructure.database.models.residuo import Residuo
from app.infrastructure.database.models.usina import Usina
from app.infrastructure.database.models.usuario import Usuario

__all__ = [
    "Afericao",
    "Alerta",
    "AuditLog",
    "Leira",
    "LeiraResiduo",
    "Residuo",
    "Usina",
    "Usuario",
]
