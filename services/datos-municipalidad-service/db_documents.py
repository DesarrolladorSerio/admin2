from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermissionLevel(str, Enum):  # Corregido: era "PermisionLevel"
    READ = "read"
    WRITE = "write"  # Corregido: era "WROTE"

class DocumentType(SQLModel, table=True):
    __tablename__ = "document_types"  # Corregido: era "__tablaname__"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type_name: str = Field(unique=True, index=True)
    description: str
    max_size_mb: int = Field(default=50)  # Incrementado para soportar archivos más grandes
    allowed_extensions: str  # JSON string con lista de extensiones
    allowed_mime_types: str  # JSON string con tipos MIME permitidos
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    documents: List["Document"] = Relationship(back_populates="document_type_rel")

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str  # Nombre en MinIO
    original_filename: str  # Nombre original del archivo
    file_path: str  # Ruta en MinIO (bucket/folder/file)
    file_size: int  # Tamaño en bytes
    mime_type: str  # Tipo MIME real del archivo
    user_id: int = Field(index=True)
    document_type: str = Field(foreign_key="document_types.type_name")
    description: Optional[str] = None
    tags: Optional[str] = None  # JSON string
    is_public: bool = Field(default=False)
    status: str = Field(default="active")  # active, deleted, archived
    checksum: Optional[str] = None  # Para verificar integridad
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    document_type_rel: Optional[DocumentType] = Relationship(back_populates="documents")
    shares: List["DocumentShare"] = Relationship(back_populates="document")

class DocumentShare(SQLModel, table=True):
    __tablename__ = "document_shares"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    shared_with_user_id: int = Field(index=True)
    permission_level: PermissionLevel = Field(default=PermissionLevel.READ)
    shared_by_user_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # Para enlaces temporales
    
    # Relationships
    document: Optional[Document] = Relationship(back_populates="shares")

# Modelos de respuesta
class DocumentResponse(SQLModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    document_type: str
    description: Optional[str]
    tags: Optional[List[str]]
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime
    type_description: Optional[str] = None

class DocumentTypeResponse(SQLModel):
    id: int
    type_name: str
    description: str
    max_size_mb: int
    allowed_extensions: List[str]
    allowed_mime_types: List[str]
    is_active: bool

class DocumentsDB:
    def __init__(self, db_url: str = "sqlite:///documents.db"):
        self.engine = create_engine(db_url, echo=False)
        self.create_tables()
        self.init_default_data()
    
    def create_tables(self):
        """Crear todas las tablas"""
        try:
            SQLModel.metadata.create_all(self.engine)
            logger.info("Tablas de documentos creadas correctamente")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            raise
    
    def init_default_data(self):
        """Inicializar tipos de documentos por defecto"""
        with Session(self.engine) as session:
            # Verificar si ya existen tipos de documentos
            existing_types = session.exec(select(DocumentType)).first()
            if existing_types:
                return
            
            default_types = [
                DocumentType(
                    type_name="cedula",
                    description="Cédula de Identidad",
                    max_size_mb=10,
                    allowed_extensions=json.dumps(["pdf", "jpg", "jpeg", "png"]),
                    allowed_mime_types=json.dumps([
                        "application/pdf", "image/jpeg", "image/png"
                    ]),
                    is_active=True
                ),
                DocumentType(
                    type_name="licencia_conducir",
                    description="Licencia de Conducir",
                    max_size_mb=10,
                    allowed_extensions=json.dumps(["pdf", "jpg", "jpeg", "png"]),
                    allowed_mime_types=json.dumps([
                        "application/pdf", "image/jpeg", "image/png"
                    ]),
                    is_active=True
                ),
                DocumentType(
                    type_name="documento_general",
                    description="Documento General",
                    max_size_mb=25,
                    allowed_extensions=json.dumps([
                        "pdf", "doc", "docx", "xls", "xlsx", "txt", "jpg", "jpeg", "png", "zip"
                    ]),
                    allowed_mime_types=json.dumps([
                        "application/pdf",
                        "application/msword",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "application/vnd.ms-excel",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "text/plain",
                        "image/jpeg",
                        "image/png",
                        "application/zip"
                    ]),
                    is_active=True
                ),
                DocumentType(
                    type_name="certificado_medico",
                    description="Certificado Médico",
                    max_size_mb=15,
                    allowed_extensions=json.dumps(["pdf", "jpg", "jpeg", "png"]),
                    allowed_mime_types=json.dumps([
                        "application/pdf", "image/jpeg", "image/png"
                    ]),
                    is_active=True
                ),
                DocumentType(
                    type_name="examen_psicotecnico",
                    description="Examen Psicotécnico",
                    max_size_mb=15,
                    allowed_extensions=json.dumps(["pdf", "jpg", "jpeg", "png"]),
                    allowed_mime_types=json.dumps([
                        "application/pdf", "image/jpeg", "image/png"
                    ]),
                    is_active=True
                ),
            ]
            
            for doc_type in default_types:
                session.add(doc_type)
            
            session.commit()
            logger.info("Tipos de documentos por defecto creados")
    
    def get_document_types(self) -> List[DocumentTypeResponse]:
        """Obtener todos los tipos de documentos activos"""
        with Session(self.engine) as session:
            statement = select(DocumentType).where(DocumentType.is_active == True)
            types = session.exec(statement).all()
            return [
                DocumentTypeResponse(
                    id=doc_type.id,
                    type_name=doc_type.type_name,
                    description=doc_type.description,
                    max_size_mb=doc_type.max_size_mb,
                    allowed_extensions=json.loads(doc_type.allowed_extensions),
                    allowed_mime_types=json.loads(doc_type.allowed_mime_types),
                    is_active=doc_type.is_active
                )
                for doc_type in types
            ]
    
    def create_document(self, document_data: dict) -> Document:
        """Crear un nuevo documento"""
        with Session(self.engine) as session:
            document = Document(**document_data)
            session.add(document)
            session.commit()
            session.refresh(document)
            return document
    
    def get_user_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentResponse]:
        """Obtener documentos de un usuario"""
        with Session(self.engine) as session:
            statement = (
                select(Document, DocumentType)
                .join(DocumentType, Document.document_type == DocumentType.type_name)
                .where(Document.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .order_by(Document.created_at.desc())
            )
            
            results = session.exec(statement).all()
            return [
                DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    original_filename=doc.original_filename,
                    file_size=doc.file_size,
                    mime_type=doc.mime_type,
                    document_type=doc_type.type_name,
                    description=doc.description,
                    tags=json.loads(doc.tags) if doc.tags else [],
                    is_public=doc.is_public,
                    status=doc.status,  # Ya es un string, no necesita .value
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    type_description=doc_type.description
                )
                for doc, doc_type in results
            ]
    
    def get_document_by_id(self, document_id: int, user_id: int = None) -> Optional[Document]:
        """Obtener un documento por ID"""
        with Session(self.engine) as session:
            statement = select(Document).where(Document.id == document_id)
            if user_id:
                statement = statement.where(Document.user_id == user_id)
            return session.exec(statement).first()
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Eliminar un documento"""
        with Session(self.engine) as session:
            statement = select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id
            )
            document = session.exec(statement).first()
            if document:
                session.delete(document)
                session.commit()
                return True
            return False

# Instancia global
documents_db = DocumentsDB()