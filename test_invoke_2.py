from app.graph import hr_engine
final_state = hr_engine.invoke({
    "employee_id": "EMP-101",
    "user_message": "I need to take leave",
    "extracted_dates": [],
})
try:
    final_response = final_state.get("final_response", "")
    if isinstance(final_response, list):
        final_response = "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in final_response
        )
    elif not isinstance(final_response, str):
        final_response = str(final_response) if final_response is not None else ""
    final_response = final_response.strip()
    print("Success")
except Exception as e:
    print(f"Error: {repr(e)}")

