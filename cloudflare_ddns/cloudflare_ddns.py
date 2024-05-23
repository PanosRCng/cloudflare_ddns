import sys

from .core.Config import Config
from .core.Logger import Logger
from .core.PublicIP import PublicIP
from .core.CloudflareZonesApi import CloudflareZonesApi



def locate_dns_record(dns_records, name, type):

    dns_entry = None

    for entry in dns_records['result']:
        if (entry['name'] == name) and (entry['type'] == type):
            dns_entry = entry
            break

    if dns_entry is None:
         raise ValueError('cloud not locate dns entry for name: <{name}> and type: <{type}>'.format(name=name, type=type))

    return dns_entry


def needs_update(dns_record, current_ip):

    record_ip = dns_record['content']

    if record_ip == current_ip:
        Logger.log(__name__, 'dns record ip <{record_ip}> is up to date'.format(record_ip=record_ip))
        return False
    
    Logger.log(__name__, 'dns_record ip <{record_ip}> is outdated'.format(record_ip=record_ip), type='warning')
    return True



def main():

    dns_record = Config.get('dns_record')

    Logger.log(__name__, 'updating dns record <| {name} | {type} |> for zone_name: <{zone_name}>'.format(name=dns_record['name'],
                                                                                                      type=dns_record['type'],
                                                                                                      zone_name=dns_record['zone_name']))

    current_ip = PublicIP.get()

    if current_ip == '127.0.0.1':
        Logger.log(__name__, 'could not get public ip, exiting', type='error')
        sys.exit(1)

    try:

        zone_id = CloudflareZonesApi.retrieve_zone_id(dns_record['zone_name'])

        dns_records = CloudflareZonesApi.retrieve_dns_records(zone_id)

        entry = locate_dns_record(dns_records, dns_record['name'], dns_record['type'])

        if not needs_update(entry, current_ip):
            sys.exit(0)

        updated_dns_record = {
            'content': current_ip,
            'name': entry['name'],
            'proxied': entry['proxied'],
            'type': entry['type'],
            'comment': entry['comment'],
            'tags': entry['tags'],
            'ttl': entry['ttl']
        }

        CloudflareZonesApi.overwrite_dns_record(zone_id, entry['id'], updated_dns_record)

        Logger.log(__name__, 'dns record ip updated to <{current_ip}>'.format(current_ip=current_ip))
        sys.exit(0)
        
    except Exception as ex:
        Logger.log(__name__, str(ex), type='error')
        Logger.log(__name__, 'could not update dns record ip to <{current_ip}>'.format(current_ip=current_ip), type='error')
        sys.exit(1)





if __name__ == '__main__':
    main()