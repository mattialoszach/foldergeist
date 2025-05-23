import json

# Parsing LLM Response and returning JSON Format
def parse_llm_response(output: str):
    try:
        json_start = output.find("{")
        json_end = output.rfind("}")
        instruction_str = output[json_start:json_end+1]

        instruction = json.loads(instruction_str)
        return instruction
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    test_str = f"""
        This is just a normal string for debugging / testing.
        This is just a normal string for debugging / testing.

        {{
        "action": "read_file",
        "args": {{
            "path": "src/main.py"
        }},
        "termination": false
        }}

        This is just a test.
        """
    
    instruction = parse_llm_response(test_str)
    # if 'error' in instruction: print("yes") Checking if action successful
    print(instruction)