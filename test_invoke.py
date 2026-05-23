from app.graph import hr_engine
try:
    final_state = hr_engine.invoke({
        "employee_id": "EMP-101",
        "user_message": "I need to take leave",
        "extracted_dates": [],
    })
    print(final_state)
except Exception as e:
    import traceback
    traceback.print_exc()
