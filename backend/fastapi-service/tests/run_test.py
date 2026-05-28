# from app.model_loader import load_model, run_inference

# print("--- Step 1: Initializing Phi-2 on your CPU Work Laptop ---")
# # Passing use_4bit=False to completely bypass bitsandbytes hardware checks
# model, tokenizer = load_model("microsoft/phi-2", lora_adapter_path=None, use_4bit=False)

# print("\n--- Step 2: Running a Quick Deterministic Test ---")
# prompt_input = "What is the capital of France?"
# print(f"Prompt Sent: {prompt_input}")

# metrics_output = run_inference(prompt_input, max_new_tokens=5)

# print("\n--- Step 3: Success! Final Metrics Captured ---")
# print(f"Response: {metrics_output['response']}")
# print(f"Certainty: {metrics_output['avg_confidence'] * 100:.2f}%")

import asyncio
from app.database.mongo import connect_mongo, disconnect_mongo, get_db

async def test_database_connection():
    print("--- Testing Database Lifecycle Hooks ---")
    
    # 1. Test Startup Connection
    await connect_mongo()
    
    # 2. Verify that our getter can retrieve the database pointer object
    active_db = get_db()
    print(f"Retrieved active database handle name: '{active_db.name}'")
    
    # 3. Test Graceful Shutdown Disconnection
    await disconnect_mongo()
    print("Lifecycle execution test complete!")

# Run the asynchronous test function using the asyncio event loop
if __name__ == "__main__":
    asyncio.run(test_database_connection())


import asyncio
from app.database.mongo import connect_mongo, disconnect_mongo, insert_test_run

# async def test_database_write():
#     print("--- Testing Database Write Operations ---")
#     await connect_mongo()
    
#     # Mock data structured exactly like your model loader output dictionary
#     mock_test_run = {
#         "run_id": "run_test_001",
#         "model_name": "microsoft/phi-2",
#         "category": "adversarial",
#         "metrics": {
#             "prompt": "What is the capital of France?",
#             "response": "A) Paris",
#             "avg_confidence": 0.4762
#         }
#     }
    
#     print("Attempting to insert mock evaluation run...")
#     inserted_bson_id = await insert_test_run(mock_test_run)
    
#     print(f"🎉 Success! Document saved to local disk.")
#     print(f"MongoDB internal tracking code (_id): {inserted_bson_id}")
    
#     await disconnect_mongo()

# if __name__ == "__main__":
#     asyncio.run(test_database_write())


# import asyncio
# from app.database.mongo import connect_mongo, disconnect_mongo, get_test_run, list_test_runs

# async def test_database_reads():
#     print("\n--- Testing Database Read Operations ---")
#     await connect_mongo()
    
#     TARGET_ID = "run_test_001"
#     print(f"Attempting to fetch metrics for run_id: '{TARGET_ID}'...")
    
#     # 1. Test fetching a specific single document
#     retrieved_doc = await get_test_run(TARGET_ID)
    
#     if retrieved_doc:
#         print("🎉 Success! Single document recovered from disk.")
#         print(f"   Model Name Used: {retrieved_doc.get('model_name')}")
#         print(f"   Stored Metric Response: {retrieved_doc.get('metrics', {}).get('response')}")
#     else:
#         print("❌ Error: Target document not found.")
        
#     # 2. Test listing recent test histories
#     print("\nAttempting to compile history list for dashboard UI...")
#     history_list = await list_test_runs(limit=5)
#     print(f"🎉 Success! Found {len(history_list)} total active log documents.")
#     print(f"First historical log summary snippet: {history_list[0] if history_list else 'None'}")

#     await disconnect_mongo()

# if __name__ == "__main__":
#     asyncio.run(test_database_reads())

import asyncio
from app.database.mongo import connect_mongo, disconnect_mongo, cache_prompt_set, get_cached_prompts

async def test_prompt_caching():
    print("\n--- Testing Prompt Library Cache Operations ---")
    await connect_mongo()
    
    test_hash = "domain_medical_001"
    test_cat = "hallucination"
    mock_prompts = ["Verify dosage safety...", "Check patient history constraints..."]
    
    # 1. Simulate saving the prompts for the first time (Triggers Insert)
    print("Caching new medical prompt set...")
    await cache_prompt_set(test_hash, test_cat, mock_prompts)
    
    # 2. Retrieve them back immediately to verify presence
    cached_data = await get_cached_prompts(test_hash, test_cat)
    print(f" Recovered cached list: {cached_data}")
    
    # 3. Simulate running the exact same cache command again (Triggers Update)
    print("\nUpdating same cache block with an extra validation prompt...")
    updated_prompts = mock_prompts + ["Analyze drug interaction risks..."]
    await cache_prompt_set(test_hash, test_cat, updated_prompts)
    
    # 4. Final read check
    final_data = await get_cached_prompts(test_hash, test_cat)
    print(f"🎉 Verification after Upsert: {final_data}")
    
    await disconnect_mongo()

if __name__ == "__main__":
    asyncio.run(test_prompt_caching())