from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

import spotipy
import uuid

from fastapi_versioning import VersionedFastAPI, version

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

## Personas

Tu puedes crear una persona.
Tu puedes listar personas.


## Artistas

You will be able to:

* **Crear artista** (_not implemented_).
"""

tags_metadata = [
    {
        "name":"personas",
        "description": "Permite realizar un crud completo de una persona (listar)"
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

class PersonaRepositorio (BaseModel):
    id: str
    nombre: str
    edad: int
    identificacion: Optional[str] = None
    ciudad: Optional[str] = None

class PersonaEntrada (BaseModel):
    nombre: str
    edad: int
    ciudad: Optional[str] = None

class PersonaEntradav2 (BaseModel):
    nombre: str
    edad: int
    identificacion: str
    ciudad: Optional[str] = None


personaList = []

@app.post("/personas", response_model=PersonaRepositorio, tags = ["personas"])
@version(1, 0)
async def crear_persona(person: PersonaEntrada):
    itemPersona = PersonaRepositorio(id=str(uuid.uuid4()), nombre= person.nombre, ciudad = person.ciudad, edad = person.edad)
    result = coleccion.insert_one(itemPersona.dict())
    return itemPersona

@app.post("/personas", response_model=PersonaRepositorio, tags = ["personas"])
@version(2, 0)
async def crear_personav2(person: PersonaEntradav2):
    itemPersona = PersonaRepositorio(id=str(uuid.uuid4()), nombre= person.nombre, ciudad = person.ciudad, edad = person.edad, identificacion = person.identificacion)
    result = coleccion.insert_one(itemPersona.dict())
    return itemPersona

@app.get("/personas", response_model=List[PersonaRepositorio], tags=["personas"])
@version(1, 0)
def get_personas():
    items = list(coleccion.find())
    print (items)
    return items

@app.get("/personas/{persona_id}", response_model=PersonaRepositorio , tags=["personas"])
@version(1, 0)
def obtener_persona (persona_id: str):
    item = coleccion.find_one({"id": persona_id})
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    

@app.delete("/personas/{persona_id}", tags=["personas"])
@version(1, 0)
def eliminar_persona (persona_id: str):    
    result = coleccion.delete_one({"id": persona_id})
    if result.deleted_count == 1:
        return {"mensaje": "Persona eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

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
