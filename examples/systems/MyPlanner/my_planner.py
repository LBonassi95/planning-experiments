import sys

if __name__ == "__main__":
    print("Hello World!")

    search_engine = sys.argv[1]
    heuristic = sys.argv[2]
    
    domain = sys.argv[3]
    problem = sys.argv[4]
    solution = sys.argv[5]

    print("Starting planner...")
    print(f"Planner configuration: {search_engine} + {heuristic}")
    print(f"DOMAIN: {domain}")
    print(f"PROBLEM: {problem}")
    print("Starting search...")
    print("Solution found!")
    print(f"Writing solution to {solution}")

    open(solution, "w").write("(action1)\n(action2)\n(action3)")
