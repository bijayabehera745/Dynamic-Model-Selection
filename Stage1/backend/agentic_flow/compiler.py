import os
from openai import OpenAI
from django.conf import settings
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator
import textwrap
import json

class AgentState(TypedDict):
    input_text: str
    llm_output: Annotated[list[str], operator.add]
    final_display: str

# Node Factory: Text Input
def make_node_text_input(node_data):
    def node_text_input(state: AgentState):
        print("--- 📝 Executing Text Input Node ---")
        # Fetch the text typed directly into the React UI!
        user_prompt = node_data.get('text', '')
        if not user_prompt:
             user_prompt = state.get("input_text", "No input provided.")
        return {"input_text": user_prompt}
    return node_text_input

# Node Factory: Customizer (Gemma API)
def make_node_customizer(node_data):
    def node_customizer(state: AgentState):
        print("--- 🧠 Executing The Customizer Node (Gemma API) ---")
        current_text = state.get("input_text", "")
        system_prompt = node_data.get('prompt', 'You are a helpful AI.')
        
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY", "")
            )
            
            # The User's Trick: JSON Extraction
            strict_prompt = textwrap.dedent(f"""\
            Instruction: {system_prompt}
            Input text: {current_text}
            
            You must wrap your final verdict in a JSON object. Do not include any other text or markdown.
            Example format: {{"output": "your final verdict here"}}
            """)
            
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "user", "content": strict_prompt}
                ],
                max_tokens=1000
            )
            raw_text = response.choices[0].message.content.strip()
            
            # Extract the data inside the value of the key "output"
            try:
                # Gemma sometimes adds preamble text before the JSON. 
                # Find the first { and last } to isolate the JSON object.
                start_idx = raw_text.find('{')
                end_idx = raw_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = raw_text[start_idx:end_idx+1]
                    data = json.loads(json_str)
                    processed_text = data.get("output", raw_text) # Extract the key!
                else:
                    processed_text = raw_text
            except json.JSONDecodeError:
                # Fallback just in case
                processed_text = raw_text
            
        except Exception as e:
            processed_text = f"OpenRouter Error: {str(e)}"
            
        return {"llm_output": [processed_text]}
    return node_customizer

# Node Factory: Screen Display
def make_node_display(node_data):
    def node_display(state: AgentState):
        print("--- 💻 Executing Screen Display Node ---")
        outputs = state.get("llm_output", [])
        final_text = "\n".join(outputs) if outputs else state.get("input_text", "")
        return {"final_display": final_text}
    return node_display

# Generic fallback
def make_generic_node(node_data):
    def generic_placeholder_node(state: AgentState):
        print("--- ⚙️ Executing Generic Processing Node ---")
        return {"llm_output": [state.get("input_text", "") + f" [Processed by {node_data.get('label', 'generic node')}]"]}
    return generic_placeholder_node

# Node Factory: Merger
def make_node_merger(node_data):
    def node_merger(state: AgentState):
        print("--- 🔀 Executing Merger Node ---")
        merged_text = "\n---\n".join(state.get("llm_output", []))
        return {"input_text": merged_text}
    return node_merger


class ReactFlowCompiler:
    def __init__(self, flow_data):
        self.nodes = flow_data.get('nodes', [])
        self.edges = flow_data.get('edges', [])
        self.graph = StateGraph(AgentState)

    def compile(self):
        if not self.nodes:
            raise ValueError("Flow has no nodes.")

        # 1. Add all nodes to the StateGraph using our Factories!
        for node in self.nodes:
            node_id = node['id']
            node_type = node['type']
            node_data = node.get('data', {})
            
            if node_type in ['textInput', 'documentReader', 'visionScanner']:
                self.graph.add_node(node_id, make_node_text_input(node_data))
            elif node_type == 'customizer':
                self.graph.add_node(node_id, make_node_customizer(node_data))
            elif node_type in ['display', 'chartGenerator']:
                self.graph.add_node(node_id, make_node_display(node_data))
            elif node_type == 'merger':
                self.graph.add_node(node_id, make_node_merger(node_data))
            else:
                self.graph.add_node(node_id, make_generic_node(node_data))

        # 2. Connect the nodes (Edges)
        for edge in self.edges:
            self.graph.add_edge(edge['source'], edge['target'])

        # 3. Find Entry Points
        target_ids = {edge['target'] for edge in self.edges}
        entry_nodes = [n for n in self.nodes if n['id'] not in target_ids]
        if entry_nodes:
            self.graph.add_edge(START, entry_nodes[0]['id'])
        
        # 4. Find Exit Points
        source_ids = {edge['source'] for edge in self.edges}
        exit_nodes = [n for n in self.nodes if n['id'] not in source_ids]
        for exit_node in exit_nodes:
            self.graph.add_edge(exit_node['id'], END)

        return self.graph.compile()
