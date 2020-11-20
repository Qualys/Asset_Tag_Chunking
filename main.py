import QualysAPI
import QualysAssetTagging
import argparse
from sys import exit
from getpass import getpass
from pprint import pprint


# Declare global variables
global enable_debug, enable_proxy, base_url, proxy_url, max_assets, root_tag_id, page_size
global search_hostassets_uri, update_hostassets_uri, create_tag_uri, search_tag_uri, delete_tag_uri, headers


def get_assets(filter_tag: str):
    print('Pulling Qualys Asset data filtered by tag: %s' % filter_tag)
    global search_hostassets_uri, base_url, proxy_url, enable_proxy, enable_debug, headers, page_size
    more_records = True
    offset = 1
    print('Getting assets with tag: %s' % filter_tag)
    assets = []

    while more_records:
        print("Grabbing records %d - %d" % (offset, offset+page_size))
        search_sr = QualysAssetTagging.createAssetSearchServiceRequest(tagname=filter_tag, page_size=page_size,
                                                                       offset=offset)
        call_resp = api.makeCall(url='%s%s' % (base_url, search_hostassets_uri), payload=search_sr, headers=headers,
                                     json_body=True)
        if call_resp['ServiceResponse']['responseCode'] != "SUCCESS":
            print("ERROR: %s" % call_resp['ServiceResponse']['responseCode'])
            print("%s" % call_resp['ServiceResponse']['responseErrorDetails']['errorMessage'])
            return None

        if (call_resp['ServiceResponse']['hasMoreRecords'] == 'false') \
                or ('hasMoreRecords' not in call_resp['ServiceResponse'].keys()):
            more_records = False
        else:
            offset += page_size
        for asset in call_resp['ServiceResponse']['data']:
            assets.append(asset)

    del call_resp
    return assets


if __name__ == '__main__':
    # Init main variables
    enable_debug = False
    enable_proxy = False
    base_url = 'https://qualysapi.qualys.eu'
    proxy_url = ''
    max_assets = 6000
    root_tag_id = 0
    child_tag_prefix = ''
    page_size = 100

    # Init API endpoint URIs
    search_hostassets_uri = '/qps/rest/2.0/search/am/hostasset'
    update_hostassets_uri = '/qps/rest/2.0/update/am/hostasset'
    create_tag_uri = '/qps/rest/2.0/create/am/tag'
    search_tag_uri = '/qps/rest/2.0/search/am/tag'
    delete_tag_uri = '/qps/rest/2.0/delete/am/tag'

    # Init request headers
    headers = {
        'X-Requested-With': 'python3/requests',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='(Required) API Username')
    parser.add_argument('-p', '--password', help='(Required) API Password (use - to prompt for password)')
    parser.add_argument('-f', '--filter_tag', help='(Required) Name of tag to filter assets')
    parser.add_argument('-t', '--target_tag', help='(Required) Name of tag to create')
    parser.add_argument('-l', '--limit_page_size', help='(Optional) Number of assets to return in a single API call '
                                                        '- default: 100')
    parser.add_argument('-c', '--child_tag_prefix', help='(Optional) Prefix for child tag names')
    parser.add_argument('-m', '--max_assets', help='(Optional) Maximum number of assets per tag - default: 6000')
    parser.add_argument('-a', '--api_url', help='(Optional) API Base URL - default: https://qualysapi.qualys.eu')
    parser.add_argument('-D', '--delete_target_tag', action='store_true', help='(Optional) Delete the target tag if it '
                                                                               'already exists (Child tags WILL be '
                                                                               'deleted)')
    parser.add_argument('-P', '--proxy-enable', help='(Optional) Enable HTTPS proxy')
    parser.add_argument('-U', '--proxy-url', help='(Required with -P) URL of HTTPS Proxy')

    parser.add_argument('-s', '--simulate', action='store_true', help='(Optional) Simulate only, do not create new '
                                                                      'tags')
    parser.add_argument('-d', '--debug', action='store_true', help="(Optional) Enable debugging output for API calls")

    args = parser.parse_args()

    # Process arguments
    # Check for required arguments
    if not args.username or args.username == '':
        print('ERROR: Username required')
        exit(1)

    if not args.password or args.password == '':
        print('ERROR: Password required')
        exit(1)

    if args.password == '-':
        args.password = getpass("Enter Password: ")

    if not args.filter_tag or args.filter_tag == '':
        print('ERROR: Filter tag required')
        exit(1)

    if not args.target_tag or args.target_tag == '':
        print('ERROR: Target tag required')
        exit(1)

    # Check optional arguments
    if args.limit_page_size:
        page_size = int(args.limit_page_size)

    if args.child_tag_prefix:
        child_tag_prefix = args.child_tag_prefix

    if args.max_assets:
        max_assets = int(args.max_assets)

    if args.proxy_enable:
        enable_proxy = True
        if args.proxy_url:
            proxy_url = args.proxy_url
        else:
            print('FATAL: Proxy Enabled but no Proxy URL specified')
            exit(1)

    if args.api_url:
        base_url = args.api_url

    if args.debug:
        enable_debug = True

    # Create an API object to handle the actual API calls
    api = QualysAPI.QualysAPI(svr=base_url, usr=args.username, passwd=args.password, proxy=proxy_url,
                              enableProxy=enable_proxy, debug=enable_debug)

    # Get assets with filter tag
    call_response = get_assets(filter_tag=args.filter_tag)
    if call_response is None:
        print('FATAL: Could not get list of assets')
        exit(1)
    host_asset_count = len(call_response)
    print('Pulled %d assets' % host_asset_count)

    # Calculate the number of tags required
    tags_count = (host_asset_count // max_assets)
    if (host_asset_count % max_assets) > 0:
        tags_count += 1
    print('Calculated tags: %s' % str(tags_count))

    # Create the root tag (delete it if required, otherwise delete its children)
    root_tag_exists = False
    root_tag_search_sr = QualysAssetTagging.createTagSearchServiceRequest(args.target_tag)
    root_tag_search_resp = api.makeCall("%s%s" % (base_url, search_tag_uri), payload=root_tag_search_sr,
                                        headers=headers, json_body=True)
    if root_tag_search_resp['ServiceResponse']['count'] > 0:
        root_tag_exists = True
        if args.delete_target_tag:
            print('Existing tag found, deleting tag')
            root_tag_id = root_tag_search_resp['ServiceResponse']['data'][0]['Tag']['id']
            # Delete the tag here
            fullurl = "%s%s/%s" % (base_url, delete_tag_uri, root_tag_id)
            if args.simulate:
                print("SIMULATE: DELETE TAG ID %s" % str(root_tag_id))
                print(fullurl)
            else:
                resp = api.makeCall(fullurl)
            root_tag_id = None
        else:
            print('Existing tag found')
            root_tag_id = root_tag_search_resp['ServiceResponse']['data'][0]['Tag']['id']
            if 'children' in root_tag_search_resp['ServiceResponse']['data'][0]['Tag'].keys():
                # Tag has children
                print('Deleting child tags')
                for child in root_tag_search_resp['ServiceResponse']['data'][0]['Tag']['children']['list']:
                    fullurl = "%s%s/%s" % (base_url, delete_tag_uri, child['TagSimple']['id'])
                    if args.simulate:
                        print("SIMULATE: DELETE TAG ID %s" % str(child['TagSimple']['id']))
                        print(fullurl)
                    else:
                        print('Deleting Tag with ID = %d' % child['TagSimple']['id'])
                        resp = api.makeCall(fullurl)
            else:
                print('No child tags found')

    # Create the root tag object
    root_tag = QualysAssetTagging.createStaticTag(tagName=args.target_tag)
    if args.simulate:
        # Simulating
        if root_tag_exists:
            print('SIMULATE: Re-using Qualys Asset Tag: %s' % args.target_tag)
        else:
            print('SIMULATE: Creating Qualys Asset Tag: %s' % args.target_tag)
    else:
        if root_tag_exists:
            print('Re-using Qualys Asset Tag: %s' % args.target_tag)
        else:
            # Create the tag in Qualys
            print('Creating Qualys Asset Tag: %s' % args.target_tag)
            sr = QualysAssetTagging.createStaticTag(tagName=args.target_tag)
            resp = api.makeCall("%s%s" % (base_url, create_tag_uri), payload=sr, headers=headers, json_body=True)
            root_tag_id = resp['ServiceResponse']['data'][0]['Tag']['id']
            print('Root Tag ID %s created' % root_tag_id)

    # Create list of tag dictionaries and distribute the assets between them
    tags = []
    while len(call_response) > 0:
        for i in range(1, tags_count+1):
            # Create a new tag
            tagName = 'Block %s' % i
            if child_tag_prefix == '':
                tag_prefix = ''
            else:
                tag_prefix = "%s|" % child_tag_prefix

            tag = {
                'name': "%s%s" % (tag_prefix, tagName),
                'parent': root_tag_id,
                'assets': [],
                'asset_count': 0
            }
            tags.append(tag)

            # Add asset IDs up to max_assets limit
            for j in range(1, max_assets+1):
                if len(call_response) > 0:
                    host = call_response.pop(0)
                    tag['assets'].append(str(host['HostAsset']['id']))
                    tag['asset_count'] = j

    # Create tags
    simulate_id = 1
    for tag in tags:
        print('Creating Tag: %s' % tag['name'])
        qtag = QualysAssetTagging.createStaticTag(tagName=tag['name'], tag_parent=tag['parent'])
        full_url = "%s%s" % (base_url, create_tag_uri)
        if args.simulate:
            print('SIMULATE: Tag Created: %s' % tag['name'])
            print('SIMULATE: Asset Count: %d' % tag['asset_count'])
            simulate_id += 1
        else:
            resp = api.makeCall(url=full_url, payload=qtag, headers=headers, json_body=True)

            if resp['ServiceResponse']['responseCode'] == 'SUCCESS':
                tag['id'] = resp['ServiceResponse']['data'][0]['Tag']['id']
                print('Tag Created: id=%s' % tag['id'])
                print('Asset Count: %s' % tag['asset_count'])
            else:
                print("ERROR: %s" % resp['ServiceResponse']['responseCode'])
                print("%s" % resp['ServiceResponse']['responseErrorDetails']['errorMessage'])
                tag['id'] = -1

    # Update assets
    for tag in tags:
        if args.simulate:
            print('SIMULATE: Updating Host Assets: %s' % tag['name'])
            print('SIMULATE: %s Assets Updated: %d' % (tag['name'], len(tag['assets'])))
        else:
            if tag['id'] == -1:
                print('Skipping Update for %s - tag was not created' % tag['name'])
            else:
                print('Updating Host Assets: %s' % tag['name'])
                # Update host assets to add this tag
                update_sr = QualysAssetTagging.updateHostAssets()
                update_sr['ServiceRequest']['filters']['Criteria'][0]['value'] = ",".join(tag['assets'])
                update_sr['ServiceRequest']['data']['HostAsset']['tags']['add']['TagSimple']['id'] = int(tag['id'])
                full_url = "%s%s" % (base_url, update_hostassets_uri)
                resp = api.makeCall(url=full_url, payload=update_sr, headers=headers, json_body=True)
                if resp['ServiceResponse']['responseCode'] == 'SUCCESS':
                    print('%s Assets Updated: %s' % (tag['name'], resp['ServiceResponse']['count']))
                else:
                    print("ERROR: %s" % resp['ServiceResponse']['responseCode'])
                    print("%s" % resp['ServiceResponse']['responseErrorDetails']['errorMessage'])
