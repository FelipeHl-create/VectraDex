from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.machine import Machine
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine


Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
	# Usuário admin
	admin = db.query(User).filter(User.email == "admin@empresa.com.br").first()
	if not admin:
		admin = User(
			name="Admin",
			email="admin@empresa.com.br",
			hashed_password=hash_password("Admin123!"),
			role=UserRole.admin,
		)
		db.add(admin)

	# Usuário operador (restrito)
	oper = db.query(User).filter(User.email == "usuario.id@empresa.com.br").first()
	if not oper:
		oper = User(
			name="Operador",
			email="usuario.id@empresa.com.br",
			hashed_password=hash_password("User123!"),
			role=UserRole.operador,
		)
		db.add(oper)

	# Produto exemplo
	p = db.query(Product).filter(Product.code == "P001").first()
	if not p:
		p = Product(code="P001", name="Produto Exemplo", description="Item seed", quantity=100, unit="un", location="A1")
		db.add(p)

	# Máquina exemplo
	m = db.query(Machine).filter(Machine.name == "Injetora 01").first()
	if not m:
		m = Machine(name="Injetora 01", location="Linha A")
		db.add(m)

	db.commit()
	print("Seed concluído.")
finally:
	db.close()
