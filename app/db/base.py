from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importações com efeito colateral para registrar modelos no Base
# Evita circularidade usando import tardio
try:
	from ..models import user as _user_model  # noqa: F401
	from ..models import product as _product_model  # noqa: F401
	from ..models import machine as _machine_model  # noqa: F401
except Exception:
	# Durante ferramentas de análise/lint pode falhar sem dependências instaladas
	pass
