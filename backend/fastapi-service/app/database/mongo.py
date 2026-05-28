import os                          # Lets Python read environment variables from your system
import logging                     # Lets us print clean logs/messages for debugging and monitoring
from motor.motor_asyncio import AsyncIOMotorClient  # Async MongoDB driver for Python
from typing import Optional        # Used for cleaner type hints

# motor is the driver used to convert Python code into MongoDB commands
# Create a logger object for this file
logger = logging.getLogger(__name__)


# Stores the MongoDB client connection globally (starts as None)
# we have a type hint that suggests it will eventually store MongoDB async connection client(optionally)
_client: Optional[AsyncIOMotorClient] = None

# store the selected db globally
_db= None

# Read MongoDB connection URL from environment variables
# If not found, default to local MongoDB server (local test and server deployment level in a single line of code)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Read database name from environment variables
# Defaults to "xai_stress_tester" if not provided
MONGO_DB = os.getenv("MONGO_DB", "xai_stress_tester")

async def connect_mongo():
    """ Starts and stores a MongoDB connection"""

    global _client, _db # allows modification of global variables


    # log connection attempt
    logger.info(f"Connecting to MongoDB at {MONGO_URI}")

    # Create the MongoDB client connection
    _client= AsyncIOMotorClient(MONGO_URI)
    # select a database from the MongoDB server
    _db=_client[MONGO_DB]

    logger.info("Applying DB collection indexes")
    # 1. giving unique run_id to each stress test
    await _db["test_runs"].create_index("run_id", unique=True)

    # 2. compound index for quick lookup of templates by domaian and category
    await _db["prompt_library"].create_index([("domain_hash", 1), ("category", 1)])
    
    logger.info("MongoDB connected and structural indexes applied.")


async def disconnect_mongo():
    """ closing the mongoDB connection"""
    global _client

    if _client:
        _client.close()

        logger.info("Disconnected")

def get_db():
    """function to safely expose the DB to other modules"""
    if _db is None:
        raise RuntimeError("CRITICAL: MongoDB is not connected! Run connect_mongo first.")
    return _db

# Connection helpers or CRUD operations in DB

# 1. used for inserting completed stress test data into mongoDB
async def insert_test_run(run: dict)-> str:
    """returns the auto-generated id"""
    
    # which db the doc should go in
    db=get_db()

    # async insert document into 'test_run' collection
    result= await db["test_runs"].insert_one(run)

    return str(result.inserted_id)

# 2. querying the db to extract a test run based on run_id
async def get_test_run(run_id:str)->Optional[dict]:
    db=get_db()
    return await db["test_runs"].find_one({"run_id":run_id})

# 3. list of recent runs for the dashboard
async def list_test_runs(limit: int=20)->list:
    db=get_db()
    # 1. Start an open search ({})
    # 2. excludeing MongoDB's internal "_id" from the output structure ({"_id": 0})
    # 3. Sort by creation time in descending order (-1 means newest first)
    # 4. Enforce a ceiling limit to prevent memory bloating
    cursor = db["test_runs"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    # the await tells python to wait until db fetches the docs
    return await cursor.to_list(length=limit)

async def cache_prompt_set(domain_hash: str, category: str, prompts: list):
    """Cache domain-adapted prompts (used in Week 2 by Groq adapter)."""
    db = get_db()
    await db["prompt_library"].update_one(
        {"domain_hash": domain_hash, "category": category},
        {"$set": {"prompts": prompts}},
        upsert=True,
    )

async def get_cached_prompts(domain_hash: str, category: str) -> Optional[list]:
    db = get_db()
    doc = await db["prompt_library"].find_one(
        {"domain_hash": domain_hash, "category": category}
    )
    return doc["prompts"] if doc else None