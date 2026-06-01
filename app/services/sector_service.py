
from core.database import supabase
from fastapi import Depends

# extração de quantidade de demanda dos setores
async def demand_sector() -> dict:

    demandas = supabase.table('sectors').select("*").execute()

    sum_dem = sum(sector["demand"] for sector in demandas.data)

    sum_peo = sum(sector["peoples"] for sector in demandas.data)

    return demandas.data, sum_dem, sum_peo