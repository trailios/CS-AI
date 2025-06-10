import json

# Load JSON data
with open("bdaSandbox_WIP/realBDA.json", "r") as realBDA:
    realBDAData = json.load(realBDA)

with open("bdaSandbox_WIP/gennedBDA.json", "r") as gennedBDA:
    gennedBDAData = json.load(gennedBDA)

# Extract enhanced_fp block
def fetch_random_enhanced_fingerprint(data):
    enhanced_fp_entry = next((item for item in data if item["key"] == "enhanced_fp"), None)
    if enhanced_fp_entry:
        return {item["key"]: item["value"] for item in enhanced_fp_entry["value"]}
    return {}

gennedEFP = fetch_random_enhanced_fingerprint(gennedBDAData)
realEFP = fetch_random_enhanced_fingerprint(realBDAData)

# Compare keys and values
genned_keys = list(gennedEFP.keys())
real_keys = list(realEFP.keys())


if genned_keys != real_keys:
    print("⚠️ Order mismatch detected:")
    print("Generated EFP keys order:")
    print(genned_keys)
    print("Real EFP keys order:")
    print(real_keys)


extra_in_genned = [key for key in genned_keys if key not in real_keys]
extra_in_real = [key for key in real_keys if key not in genned_keys]

if extra_in_genned:
    print("\n➕ Keys present only in generated EFP:")
    for key in extra_in_genned:
        print(f"- {key}")

if extra_in_real:
    print("\n➖ Keys present only in real EFP:")
    for key in extra_in_real:
        print(f"- {key}")


print("\n🔍 Changed values:")
for key in set(genned_keys).intersection(real_keys):
    if gennedEFP[key] != realEFP[key]:
        print(f"- Key: {key}")
        print(f"  Real:    {realEFP[key]}")
        print(f"  Genned:  {gennedEFP[key]}")
