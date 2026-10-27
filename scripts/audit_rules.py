import yaml

# The fields every rule must have (our team standard)
REQUIRED = ["name", "ticket", "owner", "from_zone", "to_zone",
            "source", "destination", "service", "action", "log", "expires"]

# 1. Open the rules file and turn the YAML into Python data
with open("rules/datacenter-atl.yml") as f:
    data = yaml.safe_load(f)

rules = data["rules"]
print(f"Loaded {len(rules)} rules\n")

# 2. Check each rule
for rule in rules:
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
