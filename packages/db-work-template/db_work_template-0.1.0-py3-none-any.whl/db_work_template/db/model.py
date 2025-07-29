from datetime import date, datetime
import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from typing import  Optional

class Documento(SQLModel, table=True):
    __tablename__ = "municipais_dados_sinteticos"
    id: Optional[int] = Field(
        default=None, sa_column=sa.Column(sa.BigInteger, primary_key=True)
    )
    id_account: Optional[int] = Field(default=None, sa_column=sa.Column(sa.BigInteger))
    id_attachment: Optional[int] = Field(
        default=None, sa_column=sa.Column(sa.BigInteger)
    )
    cnpj_filial: Optional[str] = Field(default=None, max_length=14)
    numero_documento: Optional[str] = Field(default=None, max_length=50)
    cnpj_participante: Optional[str] = Field(default=None, max_length=14)
    data_emissao: Optional[date] = None
    mes_lancamento: Optional[int] = None
    data_entrada_saida: Optional[date] = None
    municipio_declarante: Optional[str] = Field(default=None, max_length=100)
    nome_participante: Optional[str] = Field(default=None, max_length=255)
    municipio_participante: Optional[str] = Field(default=None, max_length=100)
    simples_nacional_participante: Optional[bool] = None
    iss_retido: Optional[bool] = None
    cod_servico_lc: Optional[str] = Field(default=None, max_length=50)
    codigo_serv_prefeitura: Optional[str] = Field(default=None, max_length=50)
    valor_contabil: Optional[float] = None
    valor_iss: Optional[float] = None
    situacao: Optional[str] = Field(default=None, max_length=50)
    status_escrit: Optional[str] = Field(default=None, max_length=50)
    descri_escrit: Optional[str] = Field(default=None, max_length=255)
    ref_municipio: Optional[str] = Field(default=None, max_length=100)
    num_debito: Optional[str] = Field(default=None, max_length=50)
    tipo_tributo: Optional[str] = Field(default=None, max_length=50)
    valor_principal: Optional[float] = None
    valor_residual: Optional[float] = None
    valor_juros: Optional[float] = None
    valor_multa: Optional[float] = None
    valor_outros: Optional[float] = None
    valor_total: Optional[float] = None
    origem: Optional[str] = Field(default=None, max_length=100)
    num_documento: Optional[str] = Field(default=None, max_length=50)
    guia_status: Optional[str] = Field(default=None, max_length=50)
    created_at: Optional[datetime] = Field(
        default=None, sa_column=sa.Column(sa.DateTime, server_default=sa.func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )