import pydot
import json
import tempfile
import os
import sys
from git import Repo

def parse_dot_content(dot_str):
    graphs = pydot.graph_from_dot_data(dot_str)
    return graphs[0] if graphs else None

def normalize_graph(graph):
    nodes = sorted((n.get_name(), dict(n.get_attributes())) for n in graph.get_nodes() if n.get_name() not in ('node', 'graph', 'edge'))
    edges = sorted((e.get_source(), e.get_destination(), dict(e.get_attributes())) for e in graph.get_edges())
    return nodes, edges

def diff_graphs(nodes_old, edges_old, nodes_new, edges_new):
    node_names_old = {n[0] for n in nodes_old}
    node_names_new = {n[0] for n in nodes_new}

    added_nodes = [n for n in nodes_new if n[0] not in node_names_old]
    removed_nodes = [n for n in nodes_old if n[0] not in node_names_new]

    changed_node_attrs = [
        (n_new[0], n_old[1], n_new[1])
        for n_old in nodes_old
        for n_new in nodes_new
        if n_old[0] == n_new[0] and n_old[1] != n_new[1]
    ]

    added_edges = [e for e in edges_new if e not in edges_old]
    removed_edges = [e for e in edges_old if e not in edges_new]

    changed_edge_attrs = [
        (e_new[0], e_new[1], e_old[2], e_new[2])
        for e_old in edges_old
        for e_new in edges_new
        if e_old[0:2] == e_new[0:2] and e_old[2] != e_new[2]
    ]

    return {
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "changed_node_attrs": changed_node_attrs,
        "added_edges": added_edges,
        "removed_edges": removed_edges,
        "changed_edge_attrs": changed_edge_attrs
    }

def create_diff_visualization_full(current_graph, diff, output_path="dot_diff_full_visual.png"):
    graph = pydot.Dot(graph_type=current_graph.get_type())

    # Keep track of what's already added to avoid duplicates
    added_node_names = set()
    added_edge_keys = set()

    # Add current nodes and highlight additions/changes
    for node in current_graph.get_nodes():
        name = node.get_name()
        if name in ("node", "graph", "edge"):
            continue
        attrs = node.get_attributes()
        style = {"style": "filled"}

        # Color based on diff
        if any(n[0] == name for n in diff['added_nodes']):
            style["fillcolor"] = "green"
        elif any(n[0] == name for n in diff['changed_node_attrs']):
            style["fillcolor"] = "yellow"
        else:
            style["fillcolor"] = "white"

        graph.add_node(pydot.Node(name, **attrs, **style))
        added_node_names.add(name)

    # Add deleted nodes (from diff)
    for name, attrs in diff['removed_nodes']:
        if name not in added_node_names:
            style = {"style": "filled,dashed", "fillcolor": "red"}
            graph.add_node(pydot.Node(name, **attrs, **style))
            added_node_names.add(name)

    # Add current edges and highlight additions/changes
    for edge in current_graph.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        attrs = edge.get_attributes()
        edge_key = (src, dst)
        color = "black"

        if edge_key in [(e[0], e[1]) for e in diff['added_edges']]:
            color = "green"
        elif edge_key in [(e[0], e[1]) for e in diff['changed_edge_attrs']]:
            color = "yellow"

        graph.add_edge(pydot.Edge(src, dst, color=color, **attrs))
        added_edge_keys.add(edge_key)

    # Add deleted edges
    for src, dst, attrs in diff['removed_edges']:
        edge_key = (src, dst)
        if edge_key not in added_edge_keys:
            graph.add_edge(pydot.Edge(src, dst, color="red", style="dashed", **attrs))
            added_edge_keys.add(edge_key)

    graph.write_png(output_path)
    print(f"[✓] Full diff visualization (with deletions) saved to: {output_path}")


def extract_file_from_commit(repo, commit_hash, file_path):
    try:
        blob = repo.commit(commit_hash).tree / file_path
        return blob.data_stream.read().decode()
    except Exception as e:
        print(f"[!] Error extracting {file_path} from {commit_hash}: {e}")
        return None

def run_pipeline(repo_path, dot_file_path, output_dir=".", commit_old="HEAD^", commit_new="HEAD"):
    repo = Repo(repo_path)

    dot_old = extract_file_from_commit(repo, commit_old, dot_file_path)
    dot_new = extract_file_from_commit(repo, commit_new, dot_file_path)

    os.makedirs(output_dir, exist_ok=True)
    visual_path = os.path.join(output_dir, "dot_diff_full_visual.png")

    # Case 1: New file added
    if not dot_old and dot_new:
        print(f"[+] {dot_file_path} was added.")
        graph_new = parse_dot_content(dot_new)
        if not graph_new:
            print(f"[!] Failed to parse new DOT file.")
            return

        nodes_new, edges_new = normalize_graph(graph_new)
        diff = {
            "added_nodes": nodes_new,
            "removed_nodes": [],
            "changed_node_attrs": [],
            "added_edges": edges_new,
            "removed_edges": [],
            "changed_edge_attrs": []
        }
        create_diff_visualization_full(graph_new, diff, output_path=visual_path)
        return

    # Case 2: File was deleted
    if dot_old and not dot_new:
        print(f"[-] {dot_file_path} was deleted.")
        graph_old = parse_dot_content(dot_old)
        if not graph_old:
            print(f"[!] Failed to parse old DOT file.")
            return

        nodes_old, edges_old = normalize_graph(graph_old)
        diff = {
            "added_nodes": [],
            "removed_nodes": nodes_old,
            "changed_node_attrs": [],
            "added_edges": [],
            "removed_edges": edges_old,
            "changed_edge_attrs": []
        }
        create_diff_visualization_full(graph_old, diff, output_path=visual_path)
        return

    # Case 3: Normal comparison
    if dot_old and dot_new:
        graph_old = parse_dot_content(dot_old)
        graph_new = parse_dot_content(dot_new)

        if not graph_old or not graph_new:
            print("[!] Failed to parse one or both DOT files.")
            return

        nodes_old, edges_old = normalize_graph(graph_old)
        nodes_new, edges_new = normalize_graph(graph_new)

        diff = diff_graphs(nodes_old, edges_old, nodes_new, edges_new)

        print("[i] Semantic diff JSON:")
        print(json.dumps(diff, indent=2))

        create_diff_visualization_full(graph_new, diff, output_path=visual_path)
        return

    # Case 4: File not present in either commit
    print(f"[!] {dot_file_path} not found in either commit.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dot_semantic_ci_diff.py <repo_path> <path/to/file.dot>")
        sys.exit(1)

    repo_path = sys.argv[1]
    file_path = sys.argv[2]

    run_pipeline(repo_path, file_path)
