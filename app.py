from flask import Flask, jsonify, render_template_string, send_file
import random
import datetime
import uuid
import io
import json

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)

# ---------------- CORE DATA ----------------
BASE_NETWORK = {
    "Firewall": "healthy",
    "SSH Server": "healthy",
    "Web Portal": "healthy",
    "Database": "healthy",
    "Honey Vault": "healthy"
}

ATTACKER_IPS = [
    "185.220.101.1",
    "45.67.23.99",
    "103.44.55.66",
    "192.168.1.77"
]

THREAT_ACTORS = [
    "APT-BlueFox",
    "Shadow Lynx",
    "GhostWire",
    "Crimson Node"
]

MITRE_MAP = [
    {"phase": "Recon", "technique": "Active Scanning", "id": "T1595", "confidence": 92},
    {"phase": "Brute Force", "technique": "Password Guessing", "id": "T1110", "confidence": 96},
    {"phase": "Valid Access", "technique": "Valid Accounts", "id": "T1078", "confidence": 89},
    {"phase": "Discovery", "technique": "File Discovery", "id": "T1083", "confidence": 94},
    {"phase": "Credential Access", "technique": "Unsecured Credentials", "id": "T1552", "confidence": 99},
    {"phase": "Containment", "technique": "Sinkhole / Denylist", "id": "DEF-001", "confidence": 100}
]

LAST_REPORT = {}

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")


def build_scenario():
    global LAST_REPORT

    network = BASE_NETWORK.copy()
    attacker_ip = random.choice(ATTACKER_IPS)
    actor = random.choice(THREAT_ACTORS)
    session_id = str(uuid.uuid4())[:8]
    ioc_hash = uuid.uuid4().hex[:16]

    steps = [
        {
            "delay": 800,
            "telemetry": [f"[{now()}] Recon from {attacker_ip}: nmap -sV 10.0.0.5"],
            "alerts": [{"level": "MEDIUM", "msg": "Recon activity detected"}],
            "network": {"SSH Server": "suspicious"},
            "shell": []
        },
        {
            "delay": 1600,
            "telemetry": [
                f"[{now()}] Brute force attempt: admin/admin123",
                f"[{now()}] Brute force attempt: root/password",
                f"[{now()}] Brute force attempt: sysadmin/qwerty"
            ],
            "alerts": [{"level": "HIGH", "msg": "Multiple failed authentication attempts"}],
            "network": {},
            "shell": []
        },
        {
            "delay": 2400,
            "telemetry": [
                f"[{now()}] Honeypot intentionally granted fake shell access",
                f"[{now()}] Welcome to Ubuntu 22.04 LTS"
            ],
            "alerts": [],
            "network": {"SSH Server": "compromised"},
            "shell": [
                "$ whoami",
                "root",
                "",
                "$ pwd",
                "/root"
            ]
        },
        {
            "delay": 3400,
            "telemetry": [f"[{now()}] Attacker executed shell commands"],
            "alerts": [],
            "network": {},
            "shell": [
                "",
                "$ ls",
                "backup  finance  secrets  credentials.txt",
                "",
                "$ cat credentials.txt",
                "AWS_KEY=AKIA************",
                "db_admin:SuperSecret123"
            ]
        },
        {
            "delay": 4500,
            "telemetry": [f"[{now()}] DECEPTION ENGINE: attacker touched decoy credential file"],
            "alerts": [{"level": "CRITICAL", "msg": "Honeytoken triggered: credentials.txt accessed"}],
            "network": {"Honey Vault": "compromised"},
            "shell": [
                "",
                "[TRAP ACTIVATED]",
                "Honeytoken beacon fired",
                "Session fingerprint captured"
            ]
        },
        {
            "delay": 5600,
            "telemetry": [
                f"[{now()}] Attacker IP {attacker_ip} sinkholed",
                f"[{now()}] Session snapshot captured"
            ],
            "alerts": [{"level": "INFO", "msg": f"Firewall blocked {attacker_ip}"}],
            "network": {
                "Firewall": "isolated",
                "SSH Server": "isolated"
            },
            "shell": []
        }
    ]

    ioc = {
        "session_id": session_id,
        "attacker_ip": attacker_ip,
        "ioc_hash": ioc_hash,
        "trigger": "credentials.txt honeytoken access",
        "severity": "CRITICAL"
    }

    threat_intel = {
        "actor": actor,
        "attacker_ip": attacker_ip,
        "ioc_hash": ioc_hash,
        "ttp_cluster": "Credential Theft",
        "confidence": f"{random.randint(93,99)}%",
        "risk": "Critical"
    }

    LAST_REPORT = {
        "timestamp": str(datetime.datetime.now()),
        "ioc": ioc,
        "threat_intelligence": threat_intel,
        "mitre_mapping": MITRE_MAP,
        "steps": steps
    }

    return {
        "steps": steps,
        "mitre": MITRE_MAP,
        "ioc": ioc,
        "threat": threat_intel,
        "base_network": network
    }


@app.route("/simulate")
def simulate():
    return jsonify(build_scenario())


@app.route("/export")
def export():
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles["Title"]
    heading = styles["Heading2"]
    normal = styles["BodyText"]

    # Title
    elements.append(
        Paragraph("HoneyShield Nexus - Incident Forensic Report", title_style)
    )

    elements.append(
        Paragraph(
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            normal
        )
    )

    elements.append(Spacer(1, 20))

    # Executive summary
    elements.append(Paragraph("Executive Summary", heading))
    elements.append(
        Paragraph(
            "A simulated SSH intrusion was detected, monitored through a deception "
            "environment, honeytoken access was triggered, and automated containment "
            "was successfully applied.",
            normal
        )
    )

    elements.append(Spacer(1, 20))

    # IOC Table
    elements.append(Paragraph("IOC Summary", heading))

    ioc = LAST_REPORT.get("ioc", {})

    ioc_data = [
        ["Field", "Value"],
        ["Session ID", ioc.get("session_id", "-")],
        ["Attacker IP", ioc.get("attacker_ip", "-")],
        ["IOC Hash", ioc.get("ioc_hash", "-")],
        ["Trigger", ioc.get("trigger", "-")],
        ["Severity", ioc.get("severity", "-")]
    ]

    table = Table(ioc_data, colWidths=[180, 340])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkcyan),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Threat Intel
    elements.append(Paragraph("Threat Intelligence", heading))

    threat = LAST_REPORT.get("threat_intelligence", {})

    threat_data = [
        ["Field", "Value"],
        ["Threat Actor", threat.get("actor", "-")],
        ["TTP Cluster", threat.get("ttp_cluster", "-")],
        ["Confidence", threat.get("confidence", "-")],
        ["Risk", threat.get("risk", "-")]
    ]

    table2 = Table(threat_data, colWidths=[180, 340])

    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table2)
    elements.append(Spacer(1, 20))

    # MITRE Mapping
    elements.append(Paragraph("MITRE ATT&CK Mapping", heading))

    mitre_data = [["Phase", "Technique", "ID", "Confidence"]]

    for m in LAST_REPORT.get("mitre_mapping", []):
        mitre_data.append([
            m["phase"],
            m["technique"],
            m["id"],
            str(m["confidence"]) + "%"
        ])

    table3 = Table(mitre_data)

    table3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    elements.append(table3)
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph("Analyst Notes", heading))
    elements.append(
        Paragraph(
            "Automated deception and containment successfully identified adversary "
            "tradecraft and preserved forensic artifacts for review.",
            normal
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="HoneyShield_Forensic_Report.pdf",
        mimetype="application/pdf"
    )


@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HoneyShield NEXUS</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">

<style>
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:'Inter',sans-serif;
}
body{
    background:
    radial-gradient(circle at top right,#00ffd530,#00000000 30%),
    radial-gradient(circle at bottom left,#00b89425,#00000000 30%),
    linear-gradient(135deg,#061018,#081421,#050b13);
    color:white;
    min-height:100vh;
}
.container{
    width:95%;
    margin:auto;
    padding:30px 0;
}
.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:28px;
}
.brand{
    font-size:36px;
    font-weight:800;
    color:#16f2d1;
}
.subtitle{
    margin-top:8px;
    color:#94a3b8;
}
.btns{
    display:flex;
    gap:12px;
}
.btn{
    border:none;
    padding:22px 38px;
    border-radius:18px;
    font-weight:800;
    font-size:20px;
    min-width:240px;
    letter-spacing:.3px;
    cursor:pointer;
    color:#041018;
    background:linear-gradient(135deg,#16f2d1,#00b894);
    box-shadow:0 0 35px rgba(22,242,209,.35);
    transition:.25s;
}
.btn:hover{
    transform:translateY(-2px) scale(1.02);
}
.export{
    background:linear-gradient(135deg,#60a5fa,#2563eb);
    color:white;
}
.grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:24px;
    margin-bottom:24px;
}
.card{
    background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.08);
    backdrop-filter:blur(18px);
    border-radius:22px;
    padding:24px;
    box-shadow:0 20px 60px rgba(0,0,0,.35);
}
h2{
    margin-bottom:18px;
    color:#dffcff;
}
.log-box{
    height:330px;
    overflow:auto;
    line-height:1.8;
    color:#d6fef6;
    white-space:pre-wrap;
}
.alert{
    padding:14px;
    border-radius:14px;
    margin-bottom:12px;
    font-weight:600;
}
.MEDIUM{background:#f59e0b22;border-left:5px solid #f59e0b;}
.HIGH{background:#ff7b0022;border-left:5px solid #ff7b00;}
.CRITICAL{background:#ef444422;border-left:5px solid #ef4444;}
.INFO{background:#06b6d422;border-left:5px solid #06b6d4;}
.node{
    padding:16px;
    border-radius:14px;
    margin-bottom:12px;
    font-weight:700;
    text-align:center;
}
.healthy{background:#10b98122;border:1px solid #10b981;}
.suspicious{background:#f59e0b22;border:1px solid #f59e0b;}
.compromised{background:#ef444422;border:1px solid #ef4444;}
.isolated{background:#3b82f622;border:1px solid #3b82f6;}
.shell{
    background:#020617;
    border:1px solid #1e293b;
    border-radius:14px;
    padding:18px;
    color:#7ef7d5;
    font-family:monospace;
    line-height:1.8;
    min-height:250px;
}
.chart-wrap{
    width:100%;
    height:300px;
}
.badges{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin-top:18px;
}
.badge{
    padding:10px 14px;
    border-radius:999px;
    background:#0f172a;
    border:1px solid #1e293b;
}
table{
    width:100%;
    border-collapse:collapse;
}
td,th{
    padding:14px;
    border-bottom:1px solid rgba(255,255,255,.08);
    text-align:left;
}
th{color:#16f2d1;width:30%;}
</style>
</head>
<body>

<div class="container">
    <div class="header">
        <div>
            <div class="brand">HoneyShield NEXUS</div>
            <div class="subtitle">Interactive Honeypot Cyber Range • SSH Deception Environment</div>
        </div>

        <div class="btns">
            <button class="btn" onclick="runSimulation()">Launch Intrusion Simulation</button>
            <button class="btn export" onclick="window.location='/export'">Export Incident Report</button>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Attack Timeline</h2>
            <div id="telemetry" class="log-box">Waiting for simulation...</div>
        </div>

        <div class="card">
            <h2>Network Status</h2>
            <div id="network"></div>
        </div>

        <div class="card">
            <h2>Alert Queue</h2>
            <div id="alerts">Waiting for alerts...</div>
        </div>

        <div class="card">
            <h2>HoneyShell Session</h2>
            <div id="shell" class="shell">Waiting for attacker session...</div>
        </div>
    </div>

    <div class="card" style="margin-bottom:24px;">
        <h2>MITRE ATT&CK Mapping</h2>
        <div class="chart-wrap"><canvas id="mitreChart"></canvas></div>
        <div id="badges" class="badges"></div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Threat Intelligence</h2>
            <table><tbody id="threat"><tr><td colspan="2">No intelligence gathered yet.</td></tr></tbody></table>
        </div>

        <div class="card">
            <h2>IOC Forensic Report</h2>
            <table><tbody id="ioc"><tr><td colspan="2">No session captured yet.</td></tr></tbody></table>
        </div>
    </div>
</div>

<script>
let telemetry=[], alerts=[], shell=[], chart;
let network = {
    "Firewall":"healthy",
    "SSH Server":"healthy",
    "Web Portal":"healthy",
    "Database":"healthy",
    "Honey Vault":"healthy"
};

function renderNetwork(){
    document.getElementById("network").innerHTML =
        Object.entries(network).map(([k,v]) =>
            `<div class="node ${v}">${k} — ${v.toUpperCase()}</div>`
        ).join("");
}
renderNetwork();

function addTelemetry(lines){
    telemetry.push(...lines);
    document.getElementById("telemetry").innerHTML = telemetry.map(x=>`<div>${x}</div>`).join("");
}
function addAlerts(newAlerts){
    alerts.push(...newAlerts);
    document.getElementById("alerts").innerHTML =
        alerts.map(a=>`<div class="alert ${a.level}">[${a.level}] ${a.msg}</div>`).join("");
}
function addShell(lines){
    shell.push(...lines);
    document.getElementById("shell").innerHTML = shell.join("<br>");
}
function applyNetwork(change){
    Object.assign(network, change);
    renderNetwork();
}

function buildMitreChart(data){
    const ctx = document.getElementById('mitreChart').getContext('2d');
    if(chart) chart.destroy();

    chart = new Chart(ctx,{
        type:'bar',
        data:{
            labels:data.map(x=>x.id),
            datasets:[{
                data:new Array(data.length).fill(0),
                borderRadius:12,
                borderWidth:2,
                barPercentage:.72,
                categoryPercentage:.82,
                backgroundColor:[
                    'rgba(0,255,240,.75)',
                    'rgba(255,153,0,.75)',
                    'rgba(180,0,255,.75)',
                    'rgba(57,255,20,.75)',
                    'rgba(255,60,120,.75)',
                    'rgba(0,140,255,.75)'
                ],
                borderColor:[
                    '#00fff0','#ff9900','#b400ff','#39ff14','#ff3c78','#008cff'
                ]
            }]
        },
        options:{
            maintainAspectRatio:false,
            plugins:{legend:{display:false}},
            scales:{
                y:{
                    min:0,max:100,
                    ticks:{
                        stepSize:20,
                        color:'#dffcff',
                        callback:v => v===0 ? '' : v
                    },
                    grid:{color:'rgba(255,255,255,.06)'}
                },
                x:{
                    ticks:{color:'#dffcff'},
                    grid:{color:'rgba(255,255,255,.04)'}
                }
            }
        }
    });

    document.getElementById("badges").innerHTML =
        data.map(x=>`<div class="badge">${x.id} • ${x.phase}</div>`).join("");
}

function animateMitre(i,val){
    chart.data.datasets[0].data[i]=val;
    chart.update();
}

function resetUI(){
    telemetry=[]; alerts=[]; shell=[];
    network = {
        "Firewall":"healthy",
        "SSH Server":"healthy",
        "Web Portal":"healthy",
        "Database":"healthy",
        "Honey Vault":"healthy"
    };
    renderNetwork();
    document.getElementById("telemetry").innerHTML="Starting simulation...";
    document.getElementById("alerts").innerHTML="Monitoring...";
    document.getElementById("shell").innerHTML="Awaiting shell access...";
}

function runSimulation(){
    resetUI();

    fetch('/simulate')
    .then(r=>r.json())
    .then(data=>{

        buildMitreChart(data.mitre);

        document.getElementById("ioc").innerHTML = `
            <tr><th>Session ID</th><td>${data.ioc.session_id}</td></tr>
            <tr><th>Attacker IP</th><td>${data.ioc.attacker_ip}</td></tr>
            <tr><th>IOC Hash</th><td>${data.ioc.ioc_hash}</td></tr>
            <tr><th>Trigger</th><td>${data.ioc.trigger}</td></tr>
            <tr><th>Severity</th><td>${data.ioc.severity}</td></tr>
        `;

        document.getElementById("threat").innerHTML = `
            <tr><th>Threat Actor</th><td>${data.threat.actor}</td></tr>
            <tr><th>Attacker IP</th><td>${data.threat.attacker_ip}</td></tr>
            <tr><th>IOC Hash</th><td>${data.threat.ioc_hash}</td></tr>
            <tr><th>TTP Cluster</th><td>${data.threat.ttp_cluster}</td></tr>
            <tr><th>Confidence</th><td>${data.threat.confidence}</td></tr>
            <tr><th>Risk Level</th><td>${data.threat.risk}</td></tr>
        `;

        data.steps.forEach((step,index)=>{
            setTimeout(()=>{
                addTelemetry(step.telemetry);
                addAlerts(step.alerts);
                addShell(step.shell);
                applyNetwork(step.network);
                animateMitre(index, data.mitre[index].confidence);
            }, step.delay);
        });
    });
}
</script>

</body>
</html>
    """)


if __name__ == "__main__":
    app.run(debug=True)