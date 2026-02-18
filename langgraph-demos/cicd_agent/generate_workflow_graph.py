#!/usr/bin/env python3
"""
Generate workflow visualization for the CI/CD Agent
"""
from graphviz import Digraph
import os

def create_workflow_graph(output_dir='.'):
    """Create a visual workflow diagram"""
    
    # Create a new directed graph
    dot = Digraph(comment='CI/CD Agent Workflow')
    dot.attr(rankdir='TB', size='20,20')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    
    # Color scheme
    colors = {
        'start_end': '#90EE90',      # Light green
        'discovery': '#87CEEB',       # Sky blue
        'validation': '#FFD700',      # Gold
        'decision': '#FFA500',        # Orange
        'fix': '#FF6B6B',             # Red
        'release': '#98FB98',         # Pale green
        'error': '#FF1493'            # Deep pink
    }
    
    # Start node
    dot.node('START', 'START', fillcolor=colors['start_end'], shape='oval')
    
    # Discovery
    dot.node('discover', 'Discover Files\nScan user paths for\n.tf, Dockerfile, Chart.yaml', 
             fillcolor=colors['discovery'])
    
    # Validation nodes (parallel)
    dot.node('val_tf', 'Validate Terraform\n• terraform validate\n• tflint\n• checkov', 
             fillcolor=colors['validation'])
    dot.node('val_docker', 'Validate Docker\n• docker build\n• hadolint', 
             fillcolor=colors['validation'])
    dot.node('val_helm', 'Validate Helm\n• helm lint\n• helm template', 
             fillcolor=colors['validation'])
    
    # Error collection
    dot.node('collect', 'Collect All Errors\nAggregate results from\nall validators', 
             fillcolor=colors['validation'])
    
    # Decision
    dot.node('decide', 'Decision Point\nAll validations passed?', 
             fillcolor=colors['decision'], shape='diamond')
    
    # Fix nodes
    dot.node('fix_tf', 'Fix Terraform\n• terraform fmt\n• Provider fixes\n(Max 3 attempts)', 
             fillcolor=colors['fix'])
    dot.node('fix_docker', 'Fix Docker\n• Update base images\n• Add WORKDIR/USER\n(Max 3 attempts)', 
             fillcolor=colors['fix'])
    dot.node('fix_helm', 'Fix Helm\n• Fix Chart.yaml\n• Add required fields\n(Max 3 attempts)', 
             fillcolor=colors['fix'])
    
    # Release nodes
    dot.node('prep_release', 'Prepare Release', fillcolor=colors['release'])
    dot.node('rel_docker', 'Release Docker\n• Build images\n• Tag with timestamp', 
             fillcolor=colors['release'])
    dot.node('rel_helm', 'Release Helm\n• Package charts\n• Push to registry', 
             fillcolor=colors['release'])
    dot.node('rel_tf', 'Release Terraform\n• terraform plan\n• terraform apply', 
             fillcolor=colors['release'])
    
    # End nodes
    dot.node('SUCCESS', 'SUCCESS', fillcolor=colors['start_end'], shape='oval')
    dot.node('FAIL', 'FAIL\nMax attempts reached', fillcolor=colors['error'], shape='oval')
    
    # Edges
    dot.edge('START', 'discover')
    
    # Parallel validation
    dot.edge('discover', 'val_tf')
    dot.edge('discover', 'val_docker')
    dot.edge('discover', 'val_helm')
    
    # To error collection
    dot.edge('val_tf', 'collect')
    dot.edge('val_docker', 'collect')
    dot.edge('val_helm', 'collect')
    
    # To decision
    dot.edge('collect', 'decide')
    
    # Decision branches
    dot.edge('decide', 'prep_release', label='Yes\n(All pass)', color='green', penwidth='2')
    dot.edge('decide', 'fix_tf', label='No\n(Has errors)', color='red', penwidth='2')
    dot.edge('decide', 'FAIL', label='No\n(Max attempts)', color='red', style='dashed')
    
    # Fix chain
    dot.edge('fix_tf', 'fix_docker')
    dot.edge('fix_docker', 'fix_helm')
    
    # Loop back to validation after fix
    dot.edge('fix_helm', 'val_tf', label='Re-validate', color='blue', style='dashed')
    
    # Release chain
    dot.edge('prep_release', 'rel_docker')
    dot.edge('rel_docker', 'rel_helm')
    dot.edge('rel_helm', 'rel_tf')
    dot.edge('rel_tf', 'SUCCESS')
    
    # Save files
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to render images (requires graphviz binary)
    try:
        # Save as PNG
        png_path = os.path.join(output_dir, 'cicd_workflow')
        dot.render(png_path, format='png', cleanup=False)
        print(f"✓ Generated: {png_path}.png")
        
        # Save as SVG
        svg_path = os.path.join(output_dir, 'cicd_workflow')
        dot.render(svg_path, format='svg', cleanup=False)
        print(f"✓ Generated: {svg_path}.svg")
    except Exception as e:
        print(f"⚠️  Could not render images (graphviz binary not found)")
        print(f"   Error: {e}")
        print(f"   Install graphviz from: https://graphviz.org/download/")
    
    # Save as DOT source (always works)
    dot_path = os.path.join(output_dir, 'cicd_workflow.dot')
    with open(dot_path, 'w') as f:
        f.write(dot.source)
    print(f"✓ Generated: {dot_path}")
    
    return dot


def create_mermaid_diagram(output_path='cicd_workflow.mmd'):
    """Create a Mermaid diagram for Markdown/GitHub"""
    
    mermaid_code = '''```mermaid
graph TD
    START([START]) --> DISCOVER[Discover Files<br/>Scan for .tf, Dockerfile, Chart.yaml]
    
    DISCOVER --> VAL_TF[Validate Terraform<br/>• terraform validate<br/>• tflint<br/>• checkov]
    DISCOVER --> VAL_DOCKER[Validate Docker<br/>• docker build<br/>• hadolint]
    DISCOVER --> VAL_HELM[Validate Helm<br/>• helm lint<br/>• helm template]
    
    VAL_TF --> COLLECT[Collect All Errors<br/>Aggregate validation results]
    VAL_DOCKER --> COLLECT
    VAL_HELM --> COLLECT
    
    COLLECT --> DECIDE{Decision Point<br/>All validations passed?}
    
    DECIDE -->|Yes| PREP[Prepare Release]
    DECIDE -->|No<br/>Has errors| FIX_TF[Fix Terraform<br/>• terraform fmt<br/>• Provider fixes<br/>Attempt: N/3]
    DECIDE -->|No<br/>Max attempts| FAIL([FAIL])
    
    FIX_TF --> FIX_DOCKER[Fix Docker<br/>• Update base images<br/>• Add WORKDIR/USER<br/>Attempt: N/3]
    FIX_DOCKER --> FIX_HELM[Fix Helm<br/>• Fix Chart.yaml<br/>• Add required fields<br/>Attempt: N/3]
    
    FIX_HELM -.->|Re-validate| VAL_TF
    
    PREP --> REL_DOCKER[Release Docker<br/>• Build images<br/>• Tag: timestamp]
    REL_DOCKER --> REL_HELM[Release Helm<br/>• Package charts<br/>• Push to registry]
    REL_HELM --> REL_TF[Release Terraform<br/>• terraform plan<br/>• terraform apply]
    REL_TF --> SUCCESS([SUCCESS])
    
    classDef startEnd fill:#90EE90,stroke:#333,stroke-width:2px
    classDef discovery fill:#87CEEB,stroke:#333
    classDef validation fill:#FFD700,stroke:#333
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px
    classDef fix fill:#FF6B6B,stroke:#333
    classDef release fill:#98FB98,stroke:#333
    classDef error fill:#FF1493,stroke:#333,stroke-width:2px
    
    class START,SUCCESS startEnd
    class FAIL error
    class DISCOVER discovery
    class VAL_TF,VAL_DOCKER,VAL_HELM,COLLECT validation
    class DECIDE decision
    class FIX_TF,FIX_DOCKER,FIX_HELM fix
    class PREP,REL_DOCKER,REL_HELM,REL_TF release
```'''
    
    with open(output_path, 'w') as f:
        f.write(mermaid_code)
    
    print(f"✓ Generated: {output_path}")
    return mermaid_code


if __name__ == "__main__":
    print("Generating CI/CD Agent workflow visualizations...")
    print("=" * 60)
    
    # Generate Graphviz visualization
    try:
        from graphviz import Digraph
        create_workflow_graph('.')
    except ImportError:
        print("⚠️  graphviz Python package not installed. Install with: pip install graphviz")
        print("   (You may also need to install system graphviz: brew install graphviz / apt-get install graphviz)")
    except Exception as e:
        print(f"⚠️  Could not render images: {e}")
        print("   DOT source file will still be generated")
        # Still generate the DOT file
        try:
            from graphviz import Digraph
            dot = create_workflow_graph('.')
        except:
            pass
    
    print()
    
    # Generate Mermaid diagram
    create_mermaid_diagram('cicd_workflow.mmd')
    
    print()
    print("=" * 60)
    print("Visualization files generated successfully!")
    print()
    print("Files created:")
    print("  • cicd_workflow.png  - High-res PNG image (requires graphviz binary)")
    print("  • cicd_workflow.svg  - Scalable vector graphic (requires graphviz binary)")
    print("  • cicd_workflow.dot  - Graphviz source file")
    print("  • cicd_workflow.mmd  - Mermaid diagram for GitHub/Markdown")
