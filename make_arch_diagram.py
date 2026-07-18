"""fig_pipeline.png — mining pipeline architecture (diagrams + graphviz)."""

from diagrams import Cluster, Diagram, Edge
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.onprem.network import Internet

graph_attr = {
    "dpi": "300",
    "fontsize": "13",
    "pad": "0.2",
    "splines": "spline",
    "nodesep": "0.35",
    "ranksep": "0.55",
}
node_attr = {"fontsize": "11"}

with Diagram(
    "",
    filename="fig_pipeline",
    outformat="png",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    direction="LR",
):
    registry = Internet("Terraform Registry API\ntop 500 x {aws, azurerm,\ngoogle} by downloads")
    github = Internet("GitHub REST API\nmetadata + 21,732 tags")

    with Cluster("collection (snapshot 2026-07-13)"):
        collect = Python("collect.py\n1,500 listings")
        meta = Python("github_meta.py\n1,449 repos resolve\n(44 vanished)")
        clone = Python("clone_and_scan.py\ntop 100/provider\ncheckov v3.3.8")

    with Cluster("raw dataset (published)"):
        mods = Storage("modules_*.csv")
        repos = Storage("repos_meta.csv\nrepo_tags.csv")
        scans = Storage("scan_*.csv")

    with Cluster("analysis"):
        rq13 = Python("analyze.py\nRQ1 semver + RQ3 health")
        rq2 = Python("rq2_analyze.py\nrule-level rates")
        vdiff = Python("variables_diff.py\nseeded bump sample\nvariables.tf as API")

    out = Storage("results + figures\n(all tables in paper)")

    registry >> collect >> mods
    mods >> meta
    github >> meta >> repos
    mods >> clone >> scans
    repos >> rq13
    scans >> rq2
    repos >> Edge(label="adjacent version pairs") >> vdiff
    rq13 >> out
    rq2 >> out
    vdiff >> out
