from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import carregar_dados
from optimizerSCIP import resolver_grade
from ortools.linear_solver import pywraplp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'dados')
DISCIPLINAS_PATH = os.path.join(DATA_DIR, 'disciplinas.json')
OFERTAS_PATH = os.path.join(DATA_DIR, 'ofertas.json')

try:
    dados_globais = carregar_dados(DISCIPLINAS_PATH, OFERTAS_PATH)
except Exception as e:
    print(f"Error loading data: {e}")
    dados_globais = None

class OptimizeRequest(BaseModel):
    taken_courses: List[str]

@app.get("/disciplinas")
def get_disciplinas():
    if not dados_globais:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    lista = []
    for d_id, d_info in dados_globais["disciplinas"].items():
        lista.append({
            "id": d_id,
            "nome": d_info["nome"],
            "tipo": d_info.get("tipo", "Desconhecido"),
            "creditos": d_info.get("creditos", 0)
        })
    return lista

@app.post("/optimize")
def optimize_schedule(request: OptimizeRequest):
    if not dados_globais:
        raise HTTPException(status_code=500, detail="Data not loaded")

    NUM_SEMESTRES = 10
    CREDITOS_MAXIMOS_POR_SEMESTRE = 32
    CREDITOS_MINIMOS = {
        "restrita": 4,
        "condicionada": 40,
        "livre": 8
    }

    grade, creditos, status, obj_value, creditos_por_tipo = resolver_grade(
        dados_globais, 
        CREDITOS_MINIMOS, 
        NUM_SEMESTRES, 
        CREDITOS_MAXIMOS_POR_SEMESTRE,
        disciplinas_cursadas=request.taken_courses
    )

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        formatted_grade = []
        for s, disciplinas_objs in grade.items():
            semestre_data = {
                "semestre": s,
                "disciplinas": [],
                "creditos": creditos[s]
            }
            semestre_data["disciplinas"] = disciplinas_objs
            formatted_grade.append(semestre_data)
            
        return {
            "status": "success",
            "solution_status": "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE",
            "semestres": obj_value,
            "schedule": formatted_grade,
            "credits_summary": creditos_por_tipo
        }
    else:
        return {
            "status": "error",
            "solution_status": "INFEASIBLE" if status == pywraplp.Solver.INFEASIBLE else str(status),
            "message": "No solution found."
        }

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
