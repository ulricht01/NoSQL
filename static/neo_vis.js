let neoViz;

function draw() {
    var config = {
        containerId: "viz",
        neo4j: {
            serverUrl: "bolt://localhost:7687",
            serverUser: "neo4j",
            serverPassword: "password"
        },
        visConfig: {
            nodes: {
            },
            groups:{
                Osoba: {color:{border:'#b67c5d', background:'#ccc98d', highlight: {border: "#b6925d", background:"#7bc482"}}, shape:"circle", font:{color: "black", size:8, strokeWidth: 0}, size:6},
                Téma: {color:{border:'#5d79b6', background:'#8d98cc', highlight: {border: "#5d6cb6", background:"#7b8cc4"}}, shape:"circle", font:{color: "black", size:8, strokeWidth: 0}, size:6},

            },
            interaction: {
                navigationButtons: true
            }
        },
        labels: {
            Osoba: {
                label: "jméno",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    static: {
                    group: "Osoba"
                    }
                }
            },
            Téma: {
                label: "název",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    static: {
                    group: "Téma"
                    }
                }
            },
        },
        relationships:{
            "PRACOVAL_NA": {
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    static: {
                        label: "PRACOVAL_NA"
                    }
                }
            }
        },
        initialCypher: "MATCH p=()-[r:PRACOVAL_NA]->() RETURN p LIMIT 25"

    };
    neoViz = new NeoVis.default(config);
    neoViz.render();
}
window.onload = draw()