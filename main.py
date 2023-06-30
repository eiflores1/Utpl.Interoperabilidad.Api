from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

import spotipy
import uuid

from fastapi_versioning import VersionedFastAPI, version

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth import authenticate

#Importar libreria de mongodb
import pymongo

client = pymongo.MongoClient("mongodb+srv://utplapi2:C3uhv7iH7iBPQS2O@atlascluster.ndzxcix.mongodb.net/?retryWrites=true&w=majority")
database = client["biblioteca"]
coleccion = database["libros"]

sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
    client_id='3b6802d61157480c83ab90de72037e4a',
    client_secret='58e2866016ca4e9897e96e7edc2c6a09'
))

description = """
Utpl tnteroperabilidad API ayuda a describir las capacidades de un directorio. 🚀

## Estudiantes

Tu puedes crear un estudiante.
Tu puedes listar estudiantes.


## Artistas

You will be able to:

* **Crear artista** (_not implemented_).
"""

tags_metadata = [
    {
        "name":"estudiantes",
        "description": "Permite realizar un crud completo de un estudiante (listar)"
    },
    {
        "name":"canciones",
        "description": "Permite realizar un crud completo sobre canciones"
    }
]

app = FastAPI(
    title="Utpl Interoperabilidad APP",
    description= description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Eduardo Flores",
        "url": "http://x-force.example.com/contact/",
        "email": "eduflores98@outlook.es",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags = tags_metadata
)

#para agregar seguridad a nuestro api
security = HTTPBasic()

class Escuela (BaseModel):
    id: str
    nombre: str
    tiempo: int
    identificacion: Optional[str] = None
    ciudad: Optional[str] = None

class Colegio (BaseModel):
    nombre: str
    tiempo: int
    ciudad: Optional[str] = None

class Colegiov2 (BaseModel):
    nombre: str
    tiempo: int
    identificacion: str
    ciudad: Optional[str] = None


estudianteList = []

@app.post("/estudiantes", response_model=Escuela, tags = ["estudiantes"])
@version(1, 0)
async def crear_estudiante(estudiant: Colegio):
    itemEstudiante = Escuela(id=str(uuid.uuid4()), nombre= estudiant.nombre, ciudad = estudiant.ciudad, tiempo = estudiant.tiempo)
    result = coleccion.insert_one(itemEstudiante.dict())
    return itemEstudiante

@app.post("/estudiantes", response_model=Escuela, tags = ["estudiantes"])
@version(2, 0)
async def crear_estudiantev2(estudiant: Colegiov2):
    itemEstudiante = Escuela(id=str(uuid.uuid4()), nombre= estudiant.nombre, ciudad = estudiant.ciudad, tiempo = estudiant.tiempo, identificacion = estudiant.identificacion)
    result = coleccion.insert_one(itemEstudiante.dict())
    return itemEstudiante

@app.get("/estudiantes", response_model=List[Escuela], tags=["estudiantes"])
@version(1, 0)
def get_personas(credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    items = list(coleccion.find())
    print (items)
    return items

@app.get("/estudiantes/{estudiante_id}", response_model=Escuela , tags=["estudiantes"])
@version(1, 0)
def obtener_estudiante (estudiante_id: str):
    item = coleccion.find_one({"id": estudiante_id})
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    

@app.delete("/estudiantes/{estudiante_id}", tags=["estudiantes"])
@version(1, 0)
def eliminar_estudiante (estudiante_id: str):    
    result = coleccion.delete_one({"id": estudiante_id})
    if result.deleted_count == 1:
        return {"mensaje": "Estudiante eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

@app.get("/pista/{pista_id}", tags = ["canciones"])
@version(1, 0)
async def obtener_pista(pista_id: str):
    track = sp.track(pista_id)
    return track
    
@app.get("/artistas/{artista_id}", tags = ["canciones"])
@version(1, 0)
async def get_artista(artista_id: str):
    artista = sp.artist(artista_id)
    return artista


@app.get("/")
def read_root():
    return {"Hello": "Interoperabilidad 8"}

##encapsular
app = VersionedFastAPI(app)
