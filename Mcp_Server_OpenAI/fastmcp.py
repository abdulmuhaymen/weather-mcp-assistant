import inspect
import json

class FastMCP:
    def __init__(self, name: str):
        self.name = name
        self.llm = None
        self.system_prompt = None
        self.tools = {}

    def set_llm(self, llm):
        self.llm = llm

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    def _validate_parameters(self, tool_name, args):
        """Validate and fix common parameter issues"""
        if tool_name == 'apply_leave':
            emp_id = args.get('employee_id', '').strip()
            if not emp_id or emp_id in ['MISSING_EMP_ID', '']:
                return {"error": "Employee ID is required. Please provide your employee ID (e.g., 'I am emp001, I want to apply leave...')"}
        return None

    def _format_response_with_llm(self, user_query: str, tool_result: dict, tool_name: str) -> str:
        """Use LLM to convert JSON data into natural language response"""
        
        # Create a formatting prompt for the LLM
        format_prompt = f"""You are a meteorological assistant. A user asked: "{user_query}"

I executed the function '{tool_name}' and received this data:

{json.dumps(tool_result, indent=2)}

Please convert this data into a clear, natural, conversational response. Follow these guidelines:
- Explain what the data shows in simple terms
- Include specific numbers and details from the data
- Make it informative but easy to understand
- If there's an error in the data, explain it helpfully
- Don't include JSON formatting or raw data in your response
- Use natural language like you're talking to a person
- Be concise but complete

Your natural language response:"""

        try:
            # Use a simple text generation approach
            formatted_response = self._get_llm_text_response(format_prompt)
            return formatted_response
        except Exception as e:
            # Fallback to basic formatting if LLM fails
            return f"Found data for your query: {json.dumps(tool_result, indent=2)}\n(Note: LLM formatting failed: {str(e)})"

    def _get_llm_text_response(self, prompt: str) -> str:
        """Get a text response from LLM for formatting"""
        try:
            # Try to use chat_text method if available
            if hasattr(self.llm, 'chat_text'):
                return self.llm.chat_text(prompt)
            else:
                # Fallback: use the regular chat method but extract text from response
                response = self.llm.chat(prompt)
                
                # If response is a dict (like from chat method), try to extract text
                if isinstance(response, dict):
                    # Try common response patterns
                    if 'content' in response:
                        return str(response['content'])
                    elif 'text' in response:
                        return str(response['text'])
                    elif 'response' in response:
                        return str(response['response'])
                    else:
                        # If it's a structured response, convert to string
                        return str(response)
                else:
                    return str(response)
                    
        except Exception as e:
            raise Exception(f"LLM text generation failed: {str(e)}")

    def run_stdio(self):
        print(f"[{self.name}] MCP is running with tools: {list(self.tools.keys())}")
        print("Waiting for input...")

        while True:
            try:
                user_input = input(">> ")

                # Build prompt for LLM with function signatures
                tool_info = []
                for tool_name, func in self.tools.items():
                    sig = inspect.signature(func)
                    params = []
                    for name, param in sig.parameters.items():
                        param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'str'
                        params.append(f"{name}: {param_type}")
                    tool_info.append(f"{tool_name}({', '.join(params)})")

                prompt = f"""{self.system_prompt}

Available tools and their exact parameters:
{chr(10).join(tool_info)}

User Query: {user_input}

Reply only in this JSON format:
{{"tool": "tool_name", "args": {{"key": "value"}}}}"""

                try:
                    response = self.llm.chat(prompt)
                    print("LLM RAW RESPONSE:", response)  # Debug print

                    # Parse JSON response
                    if isinstance(response, str):
                        parsed = json.loads(response)
                    elif isinstance(response, dict):
                        parsed = response
                    else:
                        raise ValueError("LLM response is neither a string nor a dict.")

                    tool_name = parsed.get("tool")
                    args = parsed.get("args", {})

                    if tool_name in self.tools:
                        # Validate parameters first
                        validation_error = self._validate_parameters(tool_name, args)
                        if validation_error:
                            # Use LLM to format error response too
                            formatted_error = self._format_response_with_llm(user_input, validation_error, "error")
                            print(formatted_error)
                            continue

                        # Execute the tool
                        result = self.tools[tool_name](**args)
                        
                        # **KEY CHANGE**: Use LLM to format the response
                        formatted_response = self._format_response_with_llm(user_input, result, tool_name)
                        print(formatted_response)
                        
                    else:
                        error_msg = {"error": f"Unknown tool '{tool_name}'"}
                        formatted_error = self._format_response_with_llm(user_input, error_msg, "error")
                        print(formatted_error)

                except Exception as e:
                    error_data = {
                        "error": "Error executing function",
                        "llm_output": str(response) if 'response' in locals() else "No response",
                        "exception": str(e)
                    }
                    formatted_error = self._format_response_with_llm(user_input, error_data, "error")
                    print(formatted_error)

            except KeyboardInterrupt:
                print("\nExiting MCP...")
                break
            except Exception as e:
                print(f"System error: {str(e)}")