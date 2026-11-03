from datetime import date
import ipaddress
import sys

import yaml

# The fields every rule must have (our team standard)
REQUIRED = ["name", "ticket", "owner", "from_zone", "to_zone",
            "source", "destination", "service", "action", "log", "expires"]
# Fields that define what traffic a rule matches
MATCH_FIELDS = ["from_zone", "to_zone", "source", "destination", "service", "action"]



def addr_inside(addr, broader_list):
    """True if one address sits inside any address in broader_list."""
    if "any" in broader_list:
        return True                  # 'any' covers everything
    if addr == "any":
        return False                 # nothing narrower covers 'any'
    for broad in broader_list:
        if ipaddress.ip_network(addr).subnet_of(ipaddress.ip_network(broad)):
            return True
    return False


def covers(earlier, rule):
    """True if 'earlier' matches ALL the traffic 'rule' matches."""
    # 1. Zones: must be the same, or earlier uses 'any'
    for zone in ["from_zone", "to_zone"]:
        if earlier[zone] != "any" and earlier[zone] != rule[zone]:
            return False
    # 2. Every source and destination must sit inside earlier's
    for field in ["source", "destination"]:
        for addr in rule[field]:
            if not addr_inside(addr, earlier[field]):
                return False
    # 3. Services: earlier is 'any', or includes every service
    if "any" not in earlier["service"]:
        for svc in rule["service"]:
            if svc not in earlier["service"]:
                return False
    return True

# 1. Open the rules file and turn the YAML into Python data
with open("rules/datacenter-atl.yml") as f:
    data = yaml.safe_load(f)

rules = data["rules"]
print(f"Loaded {len(rules)} rules\n")

# 2. Check each rule
findings = 0
for i, rule in enumerate(rules):
    name = rule["name"]

    # Check A: missing required fields
    for field in REQUIRED:
        if field not in rule:
            print(f"{name}: missing '{field}'")
            findings += 1

    # Check B: logging must be on
    if rule["log"] == False:
        print(f"{name}: logging disabled")
        findings += 1

    # Check C: flag unknown fields
    for field in rule:
        if field not in REQUIRED:
            print(f"{name}: unknown field '{field}'")
            findings += 1
    # Check D: Flag for ANY ANY rule 
    for field in ["source", "destination", "service"]:
        if "any" in rule[field]:
            print(f"{name}: {field} is 'any'")
            findings += 1
    # Check E: Flag for rules that are expired
    if "expires" in rule:
        expiry = date.fromisoformat(rule["expires"])
        if expiry < date.today():
            print(f"{name}: expired {rule['expires']}")
            findings += 1
    # Check F:  Flag for duplicate Rules 
    for earlier in rules[:i]:
        same = True
        for field in MATCH_FIELDS:
            if earlier[field] != rule[field]:
                same = False
        if same:
            print(f"{name}: duplicate of {earlier['name']}")
            findings += 1
        elif covers(earlier, rule):
            print(f"{name}: shadowed by {earlier['name']}")
            findings += 1

print(f"\n{findings} finding(s)")
if findings > 0:
    sys.exit(1)


