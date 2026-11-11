import os
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zela.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Report(Base):
    """Um relato feito pelo cidadão. É o registro comum a todas as disciplinas.

    O Airflow e o UiPath usam o mesmo `id` (report_id) e não mantêm cadastro
    paralelo. LGPD: não guardamos nome, CPF, telefone nem e-mail.
    """

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    # Endereço aproximado ou ponto de referência, digitado pelo cidadão.
    location: Mapped[str] = mapped_column(String(200))
    # Coordenadas são opcionais: o GPS do celular nem sempre está disponível.
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(255))
    # Categoria final: a sugestão da visão ou a escolha manual do cidadão.
    category: Mapped[str] = mapped_column(String(40), index=True)
    # recebido -> em_triagem -> encaminhado | descartado
    status: Mapped[str] = mapped_column(String(20), default="recebido", index=True)
    # cidadao = relato real; demo = dado simulado para demonstração
    source: Mapped[str] = mapped_column(String(20), default="cidadao", index=True)

    # Sugestão da visão computacional. Fica nula quando o modelo não está disponível.
    cv_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cv_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    cv_model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # True depois que o cidadão confirma ou corrige a categoria.
    cv_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Número da ordem de serviço gravado pelo robô RPA.
    service_order: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Segredo devolvido só na criação; permite que apenas quem enviou confirme a categoria.
    confirm_token: Mapped[str] = mapped_column(String(64))


class OrdemServico(Base):
    """Ordem de serviço do PORTAL DE DEMONSTRAÇÃO da fila de manutenção.

    Representa o sistema de destino que o robô UiPath preenche. É outro
    "sistema": não tem chave estrangeira para `reports`. O vínculo é só a
    referência externa digitada pelo robô (o report_id do Zela).
    """

    __tablename__ = "portal_ordens_servico"

    id: Mapped[int] = mapped_column(primary_key=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    endereco: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[str] = mapped_column(String(40))
    descricao: Mapped[str] = mapped_column(Text, default="")
    referencia_externa: Mapped[str] = mapped_column(String(40), default="")
    anexo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criada_por: Mapped[str] = mapped_column(String(60))

    @property
    def numero(self) -> str:
        return f"OS-{self.criada_em:%Y}-{self.id:06d}"


def init_db() -> None:
    Base.metadata.create_all(engine)
