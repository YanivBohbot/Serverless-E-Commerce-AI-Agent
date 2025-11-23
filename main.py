import warnings
from langchain_core.messages import HumanMessage
from src.graph import graph

# Suppress unnecessary warnings for a cleaner console
warnings.filterwarnings("ignore")


def run_interactive_agent():
    # Unique session ID.
    # In a real app, this would be the User ID or Session ID.
    config = {"configurable": {"thread_id": "user-db-hitl-english"}}

    print("\n=== ENTERPRISE AGENT (DynamoDB + Human Validation) ===")
    print("Type 'q' or 'quit' to exit.\n")

    while True:
        try:
            # 1. CHECK GRAPH STATE
            # We inspect the graph to see if it is paused (waiting for human input)
            snapshot = graph.get_state(config)

            # If 'next' is set, it means the graph stopped at an interruption point
            if snapshot.next:
                # Check if the next node is the risky tool
                if snapshot.next[0] == "risky_tools":
                    print(
                        "\n🚨 MANAGER ALERT: The agent wants to execute a sensitive action (Refund)."
                    )
                    print("   This requires your approval.")

                    approval = input("   Authorize this action? (yes/no): ")

                    if approval.lower() in ["yes", "y"]:
                        print("   ✅ Action APPROVED. Resuming workflow...")
                        # passing None resumes execution from where it paused
                        result = graph.invoke(None, config)
                    else:
                        print("   ❌ Action DENIED.")
                        print("   Canceling operation and resetting conversation loop.")
                        # We break the loop or handle the rejection logic here.
                        # For simplicity, we just wait for a new input or break.
                        break
                else:
                    # Normal case (just in case another interruption exists)
                    user_input = input("User: ")
                    if user_input.lower() in ["q", "quit"]:
                        break
                    result = graph.invoke(
                        {"messages": [HumanMessage(content=user_input)]}, config
                    )

            else:
                # 2. STANDARD FLOW (Graph is idle, waiting for new input)
                user_input = input("User: ")
                if user_input.lower() in ["q", "quit"]:
                    print("Goodbye!")
                    break

                print("⏳ Processing...")
                result = graph.invoke(
                    {"messages": [HumanMessage(content=user_input)]}, config
                )

            # 3. DISPLAY RESPONSE
            # Extract the last message from the AI
            last_msg = result["messages"][-1]
            if last_msg.content:
                print(f"\n🤖 AI: {last_msg.content}\n")
                print("-" * 50)

        except Exception as e:
            print(f"\n❌ System Error: {e}")


if __name__ == "__main__":
    run_interactive_agent()
