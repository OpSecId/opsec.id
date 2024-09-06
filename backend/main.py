import uvicorn
from app.plugins import AskarWallet
import asyncio

if __name__ == "__main__":
    asyncio.run(AskarWallet().provision())
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # workers=8,
    )
