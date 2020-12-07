# Asset Tag Update Chunking
This script can be used to build and assign static tags to large numbers of Qualys assets.

## Requirements
- Python 3.7
- Requests library for Python 3

## Password security
For automation, passwords may be specified inline with the  `-p PASSWORD` argument.  For interactive use, passwords m

## Usage
    usage: main.py [-h] [-u USERNAME] [-p PASSWORD] [-f FILTER_TAG]
                   [-t TARGET_TAG] [-l LIMIT_PAGE_SIZE] [-c CHILD_TAG_PREFIX]
                   [-m MAX_ASSETS] [-a API_URL] [-D] [-P PROXY_ENABLE]
                   [-U PROXY_URL] [-s] [-d]
    
    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            (Required) API Username
      -p PASSWORD, --password PASSWORD
                            (Required) API Password (use - to prompt for password)
      -f FILTER_TAG, --filter_tag FILTER_TAG
                            (Required) Name of tag to filter assets
      -t TARGET_TAG, --target_tag TARGET_TAG
                            (Required) Name of tag to create
      -l LIMIT_PAGE_SIZE, --limit_page_size LIMIT_PAGE_SIZE
                            (Optional) Number of assets to return in a single API
                            call - default: 100
      -c CHILD_TAG_PREFIX, --child_tag_prefix CHILD_TAG_PREFIX
                            (Optional) Prefix for child tag names
      -m MAX_ASSETS, --max_assets MAX_ASSETS
                            (Optional) Maximum number of assets per tag - default:
                            6000
      -a API_URL, --api_url API_URL
                            (Optional) API Base URL - default:
                            https://qualysapi.qualys.eu
      -D, --delete_target_tag
                            (Optional) Delete the target tag if it already exists
                            (Child tags WILL be deleted)
      -P PROXY_ENABLE, --proxy-enable PROXY_ENABLE
                            (Optional) Enable HTTPS proxy
      -U PROXY_URL, --proxy-url PROXY_URL
                            (Required with -P) URL of HTTPS Proxy
      -s, --simulate        (Optional) Simulate only, do not create new tags
      -d, --debug           (Optional) Enable debugging output for API calls


Example:

- Create and assign tags for 5,250 assets
- When pulling asset data, cap each call at 400 assets
- Each tag should have no more than 500 assets assigned
- Update assets which have the 'Cloud Agent' tag
- Tags created should have a common parent named 'Chunked Assets'
- Created tags should have a prefix of 'CA' so they are distinct from others created by the same script
- The subscription is in the EU01 pod
- Existing parent tag should be deleted if it exists
- The connection to the Qualys API should be made through the proxy at 'https://proxy.internal'
- Simulate this operation by downloading the asset list, calculating and assigning static tags but do not create asset
tags or update assets

     
    $ python3 main.py -u USERNAME -p PASSWORD --filter_tag 'Cloud Agent' --target_tag 'Chunked Assets' \
            --limit_page_size 500 --child_tag_prefix 'CA' -m 500 --delete_target_tag --proxy-enable  \
            --proxy-url 'https://proxy.internal' --simulate
    
    OR
            
    $ python3 main.py -u USERNAME -p PASSWORD -f 'Cloud Agent' -t 'Chunked Assets' -l 300 -c 'CA' -m 500 -D -P \
                    -U 'https://proxy.internal' -s
                    
    Enter Password:
    Pulling Qualys Asset data filtered by tag: Cloud Agent
    Getting assets with tag: Cloud Agent
    Grabbing records 1 - 500
    Grabbing records 501 - 1000
    Grabbing records 1001 - 1500
    Grabbing records 1501 - 2000
    Grabbing records 2001 - 2500
    Grabbing records 2501 - 3000
    Grabbing records 3001 - 3500
    Grabbing records 3501 - 4000
    Grabbing records 4001 - 4500
    Grabbing records 4501 - 5000
    Grabbing records 5000 - 5500
    Pulled 5,250 assets
    Calculated tags: 11
    SIMULATE: Creating Qualys Asset Tag: Testing
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 1
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 2
    SIMULATE: Tag Created: ChildA|Block 2
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 3
    SIMULATE: Tag Created: ChildA|Block 3
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 4
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 5
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 6
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 7
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 8
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 9
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 10
    SIMULATE: Asset Count: 500
    Creating Tag: ChildA|Block 1
    SIMULATE: Tag Created: ChildA|Block 11
    SIMULATE: Asset Count: 250
    SIMULATE: Updating Host Assets: ChildA|Block 1
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 2
    SIMULATE: ChildA|Block 2 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 3
    SIMULATE: ChildA|Block 3 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 4
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 5
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 6
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 7
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 8
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 9
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 10
    SIMULATE: ChildA|Block 1 Assets Updated: 500
    SIMULATE: Updating Host Assets: ChildA|Block 11
    SIMULATE: ChildA|Block 1 Assets Updated: 250
    
    $