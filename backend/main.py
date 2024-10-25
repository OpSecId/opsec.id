import uvicorn
from app.plugins import AskarWallet, BitstringStatusList
import asyncio

if __name__ == "__main__":
    asyncio.run(AskarWallet().provision(recreate=True))
    asyncio.run(BitstringStatusList().create())
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # workers=4,
    )
