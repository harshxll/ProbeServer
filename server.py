from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os, json, math, random, time


TEAM_TOKENS_JSON = r"""{
  "ADMIN": "HARSHUL1744",
  "Onera": "TEAM-pecathon_acm_eic-1763031042140-XWXOGGD",
  "InnoForge": "TEAM-pecathon_acm_eic-1763287482576-FV0I9UL",
  "Ctrl Freaks": "TEAM-pecathon_acm_eic-1763285369804-S2WTBNS=",
  "The Matricks": "TEAM-pecathon_acm_eic-1763438101698-05WF9IE",
  "OMA": "TEAM-pecathon_acm_eic-1763284217373-IERVG59",
  "404FoundUs": "TEAM-pecathon_acm_eic-1763478789814-S60O8JA",
  "HelloHastar123": "TEAM-pecathon_acm_eic-1763353297758-4KDR79C",
  "PVP": "TEAM-pecathon_acm_eic-1763413702543-2WK0F6V",
  "Power Rangers": "TEAM-pecathon_acm_eic-1762862034327-6S25M00",
  "Wavez": "TEAM-pecathon_acm_eic-1763481007297-HCFEL13",
  "spider4U": "TEAM-pecathon_acm_eic-1763475327039-8G8GEXG",
  "Code Force": "TEAM-pecathon_acm_eic-1763395108004-O2BTKPJ",
  "404_FOUND": "TEAM-pecathon_acm_eic-1763442862805-ZLAMDCT",
  "AlgoKnights": "TEAM-pecathon_acm_eic-1763107053339-IMN6YSL",
  "deepak_ke_lal": "TEAM-pecathon_acm_eic-1763220220132-BYJADEV",
  "Tecnocrates": "TEAM-pecathon_acm_eic-1763212840010-KMOC0IU",
  "Technobytes": "TEAM-pecathon_acm_eic-1763462250725-KINX91V",
  "Brute_Force": "TEAM-pecathon_acm_eic-1763541308863-OGV24Q3",
  "Epidemia": "TEAM-pecathon_acm_eic-1763398726354-LNH7PTA",
  "Le Cowboy": "TEAM-pecathon_acm_eic-1763285374609-LZ6608W",
  "Kuch bhi karde yaar": "TEAM-pecathon_acm_eic-1763544908540-X1NPJR0",
  "Metamatrix": "TEAM-pecathon_acm_eic-1763524139780-4C4788Y",
  "Runtime Terror": "TEAM-pecathon_acm_eic-1763301956945-UB27VJ5",
  "Codestrike": "TEAM-pecathon_acm_eic-1763568791830-YQ4ATQG",
  "ASE": "TEAM-pecathon_acm_eic-1763543026831-5B7I5HV",
  "Espada": "TEAM-pecathon_acm_eic-1763533235905-MCPUFPM",
  "Pixel Passionfruit": "TEAM-pecathon_acm_eic-1763534023770-OLO0RJE",
  "Bro_Code": "TEAM-pecathon_acm_eic-1763389223953-9UDY7SY",
  "Team Rocket": "TEAM-pecathon_acm_eic-1763458884066-YXU54G3",
  "Code_Weiser": "TEAM-pecathon_acm_eic-1763441528428-Y4VLX3H",
  "Codingo": "TEAM-pecathon_acm_eic-1763493947015-IR7NA3D",
  "EdunoHacks": "TEAM-pecathon_acm_eic-1763491275163-GVREK8L",
  "Desyn Studio": "TEAM-pecathon_acm_eic-1763557833949-UYLPKV8",
  "ERROR FOUND": "TEAM-pecathon_acm_eic-1763461051929-H0GVTBM",
  "Buffer cult": "TEAM-pecathon_acm_eic-1763566020046-J7NV6IT",
  "Tech support": "TEAM-pecathon_acm_eic-1763534995600-LOIT7UV",
  "Revoniks": "TEAM-pecathon_acm_eic-1763061478938-K0FOS37",
  "Byte Me": "TEAM-pecathon_acm_eic-1763525247397-0H8NT67",
  "Tech_Titans": "TEAM-pecathon_acm_eic-1763536759471-AQQBU2K",
  "pecmen": "TEAM-pecathon_acm_eic-1763542857747-B8XD8ZN",
  "UnknownTeam": "TEAM-pecathon_acm_eic-1763573394115-2Q6LIKC",
  "Code_Legends": "TEAM-pecathon_acm_eic-1763385510312-E0KIQMN"
}"""



app = FastAPI()

TEAM_TOKENS = json.loads(os.getenv("TEAM_TOKENS_JSON", TEAM_TOKENS_JSON))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "HARSHUL1744")

PROBE_BUDGET = int(os.getenv("PROBE_BUDGET", "4000"))
NOISE_STD = float(os.getenv("NOISE_STD", "0.0005"))
RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "0.5"))
MAX_REQUESTS_PER_TEAM = int(os.getenv("MAX_REQUESTS_PER_TEAM", "800"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "1.15"))
GLOBAL_JITTER = float(os.getenv("GLOBAL_JITTER", "0.02"))
DOMAIN_MIN, DOMAIN_MAX = -3, 3

probes_used_global = 0
team_usage = {}
team_last_call = {}
team_backoff = {}
banned_teams = set()

def _f(x):
    num = math.sin(2*x) + 0.3*math.cos(7*x + 1.2)
    den = 1 + 0.1*(x*x) + 0.05*math.tanh(0.5*x)

    steps = 70
    a, b = 0.0, x
    if x == 0:
        I = 0.0
    else:
        if b < a:
            a, b = b, a
            sign = -1
        else:
            sign = 1
        dx = (b - a) / steps
        s, t = 0.0, a
        for _ in range(steps + 1):
            integrand = math.exp(-0.4*(t*t)) * (1 + 0.1*math.sin(3*t))
            s += integrand
            t += dx
        I = sign * s * dx

    return num/den + I

class ProbeRequest(BaseModel):
    x: float

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/probe")
async def probe(req: ProbeRequest, team_id: str = Header(None), token: str = Header(None)):
    global probes_used_global

    if team_id is None or token is None:
        raise HTTPException(401, "missing headers")

    is_admin = (team_id == "ADMIN" and token == ADMIN_TOKEN)

    if not is_admin:
        if team_id not in TEAM_TOKENS:
            raise HTTPException(401, "unknown team")
        if TEAM_TOKENS[team_id] != token:
            raise HTTPException(401, "invalid token")

    if not is_admin and team_id in banned_teams:
        raise HTTPException(403, "team banned")

    if probes_used_global >= PROBE_BUDGET and not is_admin:
        raise HTTPException(403, "global probe budget exceeded")

    if team_id not in team_usage:
        team_usage[team_id] = 0
        team_last_call[team_id] = 0
        team_backoff[team_id] = 0

    now = time.time()
    last = team_last_call[team_id]
    backoff = team_backoff[team_id]

    if not is_admin and (now - last) < (RATE_LIMIT_SECONDS + backoff):
        team_backoff[team_id] = backoff * BACKOFF_FACTOR + 0.1
        raise HTTPException(429, "rate limit")

    team_last_call[team_id] = now

    if not is_admin and team_usage[team_id] >= MAX_REQUESTS_PER_TEAM:
        banned_teams.add(team_id)
        raise HTTPException(403, "team banned (quota exceeded)")

    if not (DOMAIN_MIN <= req.x <= DOMAIN_MAX) and not is_admin:
        raise HTTPException(400, "x out of range")

    y = _f(req.x)
    y += random.gauss(0, NOISE_STD)
    y += random.uniform(-GLOBAL_JITTER, GLOBAL_JITTER)

    if not is_admin:
        probes_used_global += 1
        team_usage[team_id] += 1

    return {
        "x": req.x,
        "y_noisy": y,
        "remaining_global": PROBE_BUDGET - probes_used_global,
        "team_used": team_usage[team_id]
    }
