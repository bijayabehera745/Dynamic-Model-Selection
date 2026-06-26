from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import AgenticWorkflow
from .compiler import ReactFlowCompiler

@shared_task
def execute_langgraph_pipeline(workflow_id, initial_input="Explain how black holes work"):
    print(f"🚀 Starting background execution for Workflow ID: {workflow_id}")
    
    # Get the WebSocket channel layer
    channel_layer = get_channel_layer()
    group_name = f"workflow_{workflow_id}"
    
    try:
        # 1. Fetch the saved JSON Flow
        workflow = AgenticWorkflow.objects.get(id=workflow_id)
        
        # Send a starting message to the UI
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "flow_execution_update",
            "message": "Starting Graph Compilation...",
            "status": "running"
        })
        
        # 2. Compile the Graph
        compiler = ReactFlowCompiler(workflow.flow_data)
        app = compiler.compile()
        
        # 3. Execute it!
        result = app.invoke({"outputs": {"__initial__": initial_input}, "final_display": ""})
        outputs_dict = result.get('outputs', {})
        final_output = result.get('final_display', str(outputs_dict))
        
        print(f"✅ Execution Complete. Result: {final_output}")
        
        # Send the completion message to un-stick the UI button and show output!
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "flow_execution_update",
            "message": "Pipeline Execution Completed!",
            "status": "completed",
            "output": outputs_dict
        })
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Execution Failed: {error_msg}")
        
        # Send error to UI so the button un-sticks
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "flow_execution_update",
            "message": f"Execution Failed: {error_msg}",
            "status": "failed",
            "output": None
        })
        return error_msg
