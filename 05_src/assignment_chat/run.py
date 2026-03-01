from services.semantic_service import generate_answer
from services.api_service import get_stock_data, get_company_news, generate_stock_insight
from services.task_service import handle_task_request

# ---------------------------
# Router
# ---------------------------
def route_query(query: str):
    q = query.lower()

    # STOCK → api_service
    if any(word in q for word in ["stock", "price", "ticker", "market"]):
        return "api"

    # TASK → task_service
    elif any(word in q for word in ["task", "todo", "reminder"]):
        return "task"

    # DEFAULT → semantic search
    else:
        return "semantic"
    
def route_input(user_input: str):
    user_input_lower = user_input.lower()

    # Guardrails (required)
    banned = ["cat", "dog", "zodiac", "horoscope", "taylor swift"]
    if any(word in user_input_lower for word in banned):
        return "Sorry, I can't answer that."

    # Route to services
    if "stock" in user_input_lower or "price" in user_input_lower:
        symbol = user_input.upper().split()[-1]
        stock = get_stock_data(symbol)
        news = get_company_news(symbol)
        return generate_stock_insight(stock, news)

    elif "task" in user_input_lower or "todo" in user_input_lower:
        return handle_task_request(user_input)

    else:
        return generate_answer(user_input)


# ---------------------------
# Extract stock symbol
# ---------------------------
def extract_symbol(query: str):
    words = query.upper().split()

    for word in words:
        if word.isalpha() and 1 <= len(word) <= 5:
            return word

    return None


# ---------------------------
# Main loop
# ---------------------------
def main():
    print("🚀 Simple Chat Router")
    print("Type 'exit' to quit\n")

    while True:
        query = input("You: ")

        if query.lower() == "exit":
            break

        route = route_query(query)

        # -----------------------
        # API SERVICE
        # -----------------------
        if route == "api":
            print(query)
            symbol = extract_symbol(query)

            if not symbol:
                print("⚠️ No stock symbol detected.")
                continue

            print(symbol)
            stock = get_stock_data(symbol)
            news = get_company_news(symbol)

            print(symbol)
            print(news)

            if not stock:
                print("❌ Failed to fetch stock data.")
                continue

            result = generate_stock_insight(stock, news)
            print(result)

        # -----------------------
        # TASK SERVICE
        # -----------------------
        elif route == "task":
            result = handle_task_request(query)
            print(result)

        # -----------------------
        # SEMANTIC SERVICE
        # -----------------------
        else:
            result = generate_answer(query)
            print(result)


if __name__ == "__main__":
    main()