import os
from openai import OpenAI
from django.conf import settings
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator
import textwrap
import json
import base64
import fitz  # PyMuPDF
from docx import Document
import io

def update_outputs(base: dict, new: dict) -> dict:
    base = base.copy()
    base.update(new)
    return base

class AgentState(TypedDict):
    # Maps node_id -> output payload
    outputs: Annotated[dict, update_outputs]
    final_display: str

# Helper to fetch combined input from incoming edges
def get_combined_input(state: AgentState, incoming_edges: list) -> str:
    inputs = []
    outputs_dict = state.get("outputs", {})
    for src in incoming_edges:
        if src in outputs_dict:
            val = outputs_dict[src]
            if isinstance(val, str):
                inputs.append(val)
            else:
                inputs.append(json.dumps(val))
    return "\n\n".join(inputs)

# Node Factory: Text Input
def make_node_text_input(node_id, node_data):
    def node_text_input(state: AgentState):
        print(f"--- 📝 Executing Text Input ({node_id}) ---")
        user_prompt = node_data.get('text', '')
        if not user_prompt:
             user_prompt = state.get("outputs", {}).get("__initial__", "No input provided.")
        return {"outputs": {node_id: user_prompt}}
    return node_text_input

# Node Factory: Vision Scanner (File Upload)
def make_node_vision_scanner(node_id, node_data):
    def node_vision_scanner(state: AgentState):
        print(f"--- 📸 Executing Vision Scanner ({node_id}) ---")
        file_base64 = node_data.get('fileBase64')
        file_type = node_data.get('fileType', '')
        file_name = node_data.get('fileName', '')

        if not file_base64:
            return {"outputs": {node_id: "[No file uploaded to Vision Scanner]"}}

        try:
            # Strip data URL prefix
            if ',' in file_base64:
                _, base64_data = file_base64.split(',', 1)
            else:
                base64_data = file_base64
            
            raw_data = base64.b64decode(base64_data)

            if file_type.startswith('image/'):
                # Send to LLM for image analysis
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.environ.get("OPENROUTER_API_KEY", "")
                )
                
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this image in detail."},
                                {"type": "image_url", "image_url": {"url": f"data:{file_type};base64,{base64_data}"}}
                            ]
                        }
                    ],
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
                return {"outputs": {node_id: f"[Image Scan Result]\n{result}"}}
            
            elif file_type == 'application/pdf' or file_name.endswith('.pdf'):
                # Process PDF
                doc = fitz.open(stream=raw_data, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return {"outputs": {node_id: f"[Extracted from PDF: {file_name}]\n{text}"}}
            
            elif 'word' in file_type or file_name.endswith(('.doc', '.docx')):
                # Process Word Document
                doc_file = io.BytesIO(raw_data)
                doc = Document(doc_file)
                text = "\n".join([para.text for para in doc.paragraphs])
                return {"outputs": {node_id: f"[Extracted from Word Doc: {file_name}]\n{text}"}}
            
            else:
                return {"outputs": {node_id: f"[Unsupported file type: {file_type}]"}}

        except Exception as e:
            print(f"Error processing file in {node_id}: {e}")
            return {"outputs": {node_id: f"[Error extracting data from file: {str(e)}]"}}
            
    return node_vision_scanner

# Node Factory: Customizer
def make_node_customizer(node_id, node_data, incoming_edges):
    def node_customizer(state: AgentState):
        print(f"--- 🧠 Executing The Customizer Node ({node_id}) ---")
        current_text = get_combined_input(state, incoming_edges)
        system_prompt = node_data.get('prompt', 'You are a helpful AI.')
        
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY", "")
            )
            
            strict_prompt = textwrap.dedent(f"""\
            Instruction: {system_prompt}
            Input text: {current_text}
            
            You must wrap your final verdict in a JSON object. Do not include any other text or markdown.
            Example format: {{"output": "your final verdict here"}}
            """)
            
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": strict_prompt}],
                max_tokens=1000
            )
            raw_text = response.choices[0].message.content.strip()
            
            try:
                start_idx = raw_text.find('{')
                end_idx = raw_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = raw_text[start_idx:end_idx+1]
                    data = json.loads(json_str)
                    processed_text = data.get("output", raw_text)
                else:
                    processed_text = raw_text
            except json.JSONDecodeError:
                processed_text = raw_text
                
        except Exception as e:
            processed_text = f"OpenRouter Error: {str(e)}"
            
        return {"outputs": {node_id: processed_text}}
    return node_customizer

# Node Factory: Chart Generator
def make_node_chart_generator(node_id, node_data, incoming_edges):
    def node_chart_generator(state: AgentState):
        print(f"--- 📊 Executing Chart Generator ({node_id}) ---")
        current_text = get_combined_input(state, incoming_edges)
        
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY", "")
            )
            
            prompt = textwrap.dedent(f"""\
            Take the following data and format it into a JSON structure for charting.
            Supported chart types are "bar", "line", and "pie".
            The output MUST be raw JSON containing "type" and "data" array with "name" and "value" pairs.
            Do not include markdown fences, ONLY raw JSON.
            
            Example output format:
            {{
              "type": "bar",
              "data": [
                {{"name": "Apples", "value": 10}},
                {{"name": "Bananas", "value": 15}}
              ]
            }}
            
            Input Data:
            {current_text}
            """)
            
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            raw_text = response.choices[0].message.content.strip()
            
            if raw_text.startswith('```json'):
                raw_text = raw_text[7:]
            if raw_text.startswith('```'):
                raw_text = raw_text[3:]
            if raw_text.endswith('```'):
                raw_text = raw_text[:-3]
                
            final_json = raw_text.strip()
            return {"outputs": {node_id: final_json}, "final_display": final_json}
        except Exception as e:
            error_json = json.dumps({"error": str(e)})
            return {"outputs": {node_id: error_json}, "final_display": error_json}
    return node_chart_generator

# Generic placeholder
def make_generic_node(node_id, node_data, incoming_edges):
    def generic_node(state: AgentState):
        print(f"--- ⚙️ Executing Generic Node ({node_id}) ---")
        current_text = get_combined_input(state, incoming_edges)
        return {"outputs": {node_id: f"[Processed by {node_data.get('label', 'generic')}]\n{current_text}"}}
    return generic_node

# Node Factory: Merger
def make_node_merger(node_id, node_data, incoming_edges):
    def node_merger(state: AgentState):
        print(f"--- 🔀 Executing Merger Node ({node_id}) ---")
        merged_text = get_combined_input(state, incoming_edges)
        return {"outputs": {node_id: f"--- MERGED DATA ---\n{merged_text}"}}
    return node_merger

# Node Factory: Screen Display
def make_node_display(node_id, node_data, incoming_edges):
    def node_display(state: AgentState):
        print(f"--- 💻 Executing Screen Display ({node_id}) ---")
        final_text = get_combined_input(state, incoming_edges)
        return {"outputs": {node_id: final_text}, "final_display": final_text}
    return node_display


class ReactFlowCompiler:
    def __init__(self, flow_data):
        self.nodes = flow_data.get('nodes', [])
        self.edges = flow_data.get('edges', [])
        self.graph = StateGraph(AgentState)

    def compile(self):
        if not self.nodes:
            raise ValueError("Flow has no nodes.")

        # Pre-calculate incoming edges
        incoming_edges = {node['id']: [] for node in self.nodes}
        for edge in self.edges:
            incoming_edges[edge['target']].append(edge['source'])

        for node in self.nodes:
            node_id = node['id']
            node_type = node['type']
            node_data = node.get('data', {})
            sources = incoming_edges[node_id]
            
            if node_type in ['textInput', 'documentReader']:
                self.graph.add_node(node_id, make_node_text_input(node_id, node_data))
            elif node_type == 'visionScanner':
                self.graph.add_node(node_id, make_node_vision_scanner(node_id, node_data))
            elif node_type == 'customizer':
                self.graph.add_node(node_id, make_node_customizer(node_id, node_data, sources))
            elif node_type == 'chartGenerator':
                self.graph.add_node(node_id, make_node_chart_generator(node_id, node_data, sources))
            elif node_type == 'display':
                self.graph.add_node(node_id, make_node_display(node_id, node_data, sources))
            elif node_type == 'merger':
                self.graph.add_node(node_id, make_node_merger(node_id, node_data, sources))
            else:
                self.graph.add_node(node_id, make_generic_node(node_id, node_data, sources))

        for edge in self.edges:
            self.graph.add_edge(edge['source'], edge['target'])

        target_ids = {edge['target'] for edge in self.edges}
        entry_nodes = [n for n in self.nodes if n['id'] not in target_ids]
        
        # Connect START to ALL entry nodes (fixes parallel branch bug)
        for entry_node in entry_nodes:
            self.graph.add_edge(START, entry_node['id'])
        
        source_ids = {edge['source'] for edge in self.edges}
        exit_nodes = [n for n in self.nodes if n['id'] not in source_ids]
        
        for exit_node in exit_nodes:
            self.graph.add_edge(exit_node['id'], END)

        return self.graph.compile()
