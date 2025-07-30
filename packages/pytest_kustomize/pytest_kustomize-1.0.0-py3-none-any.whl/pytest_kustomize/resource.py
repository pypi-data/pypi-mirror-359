def split_dash(text):
    return text.split("-")[0]


def by_kind(manifest, kind, name_transform=split_dash):
    result = {}
    for resource in manifest:
        if resource["kind"] != kind:
            continue
        name = name_transform(resource["metadata"]["name"])
        result[name] = resource
    return result


def resolve_configmaps(manifest, name_transform=split_dash):
    result = {}
    configmaps = {k: v.get("data", {}) for k, v in by_kind(manifest, "ConfigMap").items()}
    for name, deployment in by_kind(manifest, "Deployment").items():
        config = result[name] = {}
        for container in deployment["spec"]["template"]["spec"]["containers"]:
            if "envFrom" in container:
                for item in container["envFrom"]:
                    if "configMapRef" not in item:
                        continue
                    config.update(configmaps[name_transform(item["configMapRef"]["name"])])
                # XXX Assumption of exactly one "real" Container per Deployment
                break
    return result


def extract_externalsecret_data(manifest, name_transform=split_dash):
    result = {}
    for name, item in by_kind(manifest, "ExternalSecret", name_transform).items():
        for secret in item["spec"]["data"]:
            result[name + secret["secretKey"]] = secret["remoteRef"]
    return result
