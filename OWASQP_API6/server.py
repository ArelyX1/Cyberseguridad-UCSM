import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
import asyncio
import uvicorn

# Estado global del inventario
inventory = {"SNEAKER_LIMITED": 1}

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def buy_item(self, item_id: str) -> str:
        global inventory
        
        # EL GAP DE VULNERABILIDAD:
        # entren al bloque 'if' antes de que la primera reste el stock.
        current_stock = inventory.get(item_id, 0)
        await asyncio.sleep(2.0) 
        
        if current_stock > 0:
            inventory[item_id] -= 1
            return f"EXITO: Quedan {inventory[item_id]}"
        else:
            return "ERROR: AGOTADO"

@strawberry.type
class Query:
    @strawberry.field
    def stock(self, item_id: str) -> int:
        return inventory.get(item_id, 0)

schema = strawberry.Schema(query=Query, mutation=Mutation)
app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")

if __name__ == "__main__":
    # Escuchamos en todas las interfaces para evitar problemas de resolución
    uvicorn.run(app, host="0.0.0.0", port=8000)
