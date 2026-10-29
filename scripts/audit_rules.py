from datetime import date

import yaml

# The fields every rule must have (our team standard)
REQUIRED = ["name", "ticket", "owner", "from_zone", "to_zone",
            "source", "destination", "service", "action", "log", "expires"]
# Fields that define what traffic a rule matches
MATCH_FIELDS = ["from_zone", "to_zone", "source", "destination", "service", "action"]

# 1. Open the rules file and turn the YAML into Python data
with open("rules/datacenter-atl.yml") as f:
    data = yaml.safe_load(f)

rules = data["rules"]
print(f"Loaded {len(rules)} rules\n")

# 2. Check each rule
for i, rule in enumerate(rules):
    name = rule["name"]

    # Check A: missing required fields
    for field in REQUIRED:
        if field not in rule:
            print(f"{name}: missing '{field}'")

    # Check B: logging must be on
    if rule["log"] == False:
        print(f"{name}: logging disabled")

    # Check C: flag unknown fields
    for field in rule:
        if field not in REQUIRED:
            print(f"{name}: unknown field '{field}'")
    # Check D: Flag for ANY ANY rule 
    for field in ["source", "destination", "service"]:
        if "any" in rule[field]:
            print(f"{name}: {field} is 'any'")
    # Check E: Flag for rules that are expired
    if "expires" in rule:
        expiry = date.fromisoformat(rule["expires"])
        if expiry < date.today():
            print(f"{name}: expired {rule['expires']}")
    # Check F:  Flag for duplicate Rules 
    for earlier in rules[:i]:
        same = True
        for field in MATCH_FIELDS:
            if earlier[field] != rule[field]:
                same = False
        if same:
            print(f"{name}: duplicate of {earlier['name']}")
    



