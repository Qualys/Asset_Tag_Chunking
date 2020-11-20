def createTagSearchServiceRequest(tagName: str):
    sr = {
        "ServiceRequest": {
            "filters": {
                "Criteria": [{
                    "field": "name",
                    "operator": "EQUALS",
                    "value": tagName
                }]
            }
        }
    }

    return sr


def createAssetSearchServiceRequest(tagname: str, page_size: int = 100, offset: int = 0):
    sr = {
        "ServiceRequest": {
            "preferences": {
                "startFromOffset": offset,
                "limitResults": page_size
            },
            "filters": {
                "Criteria": [{
                    "field": "tagName",
                    "operator": "EQUALS",
                    "value": tagname
                }]
            }
        }
    }

    return sr


def createStaticTag(tagName: str, tagColor: str = None, tag_parent: int = None):
    sr = {
        "ServiceRequest": {
            "data": {
                "Tag": {
                    "name": tagName,
                }
            }
        }
    }

    if tagColor:
        sr['ServiceRequest']['data']['Tag']['color'] = tagColor
    if tag_parent:
        sr['ServiceRequest']['data']['Tag']['parentTagId'] = tag_parent

    return sr


def updateHostAssets():
    sr = {
        "ServiceRequest": {
            "filters": {
                "Criteria": [{
                    "field": "id",
                    "operator": "IN",
                    "value": ''
                }]
            },
            "data": {
                "HostAsset": {
                    "tags": {
                        "add": {
                            "TagSimple": {
                                "id": 0
                            }
                        }
                    }
                }
            }
        }
    }

    return sr
