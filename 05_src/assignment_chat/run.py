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
        symbol = user_input.upper().split()[0]

        stock = get_stock_data(extract_symbol(symbol))
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
            if word in ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "NFLX"]:
                return word

        COMPANY_MAP = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "tesla": "TSLA",
        "amazon": "AMZN",
        "google": "GOOGL",
        "meta": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX"
    }

    for name, symbol in COMPANY_MAP.items():
        if name in str.lower(query):
            return symbol

    return None


# ---------------------------
# Main loop
# ---------------------------
def main():
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
            symbol = extract_symbol(query)

            if not symbol:
                print("No stock symbol detected.")
                continue

            stock = get_stock_data(symbol)
            news = get_company_news(symbol)

            if not stock:
                print("Failed to fetch stock data.")
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