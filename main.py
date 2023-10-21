from math import log2
from textwrap import wrap

def is_empty(text):
    return text.strip() == ""

def is_correct_network_address(address):
    octets = address.split(".")
    if len(octets) != 4:
        return False
    for octet in octets:
        if not octet.isdigit() or int(octet) < 0 or int(octet) > 255:
            return False
    return True

def is_correct_endpoint_numbers_per_network(numbers):
    endpoints = numbers.split(",")
    for endpoint in endpoints:
        if not endpoint.isdigit() or int(endpoint) <= 0:
            return False
    return True

def is_correct_prefix(prefix):
    if not prefix.isdigit() or int(prefix) < 0 or int(prefix) > 32:
        return False
    return True

def power_bit_length(x):
    return 2 ** (x - 1).bit_length()

def get_mask_from_prefix(prefix):
    subnet_mask_dec = ""
    for octet in wrap(("0" * (32 - prefix)).rjust(32, "1"), 8):
        subnet_mask_dec += f"{int(octet, 2)}."
    return subnet_mask_dec[:-1]

def get_32bit_format(ip_address):
    format_32bit = ""
    for octet in ip_address.split("."):
        format_32bit += f'{bin(int(octet)).replace("0b", "").rjust(8, "0")}'
    return format_32bit

def get_ip_from_32bit_format(format_32bit):
    ip_dec = ""
    for octet in wrap(format_32bit, 8):
        ip_dec += f"{int(octet, 2)}."
    return ip_dec[:-1]

def get_first_addressable_ip(network_ip):
    first_addressable_ip_bin_32bit = bin(int(get_32bit_format(network_ip), 2) +
                                         int("1", 2)).replace("0b", "").rjust(32, "0")
    return get_ip_from_32bit_format(first_addressable_ip_bin_32bit)

def get_last_addressable_ip(network_ip, mask):
    broadcast_ip_32bit = get_32bit_format(get_broadcast_ip(network_ip, mask))
    last_addressable_ip_bin_32bit = bin(int(broadcast_ip_32bit, 2) -
                                        int("1", 2)).replace("0b", "").rjust(32, "0")
    return get_ip_from_32bit_format(last_addressable_ip_bin_32bit)

def get_broadcast_ip(network_ip, mask):
    broadcast_ip_32bit = f"{get_32bit_format(network_ip)[:-get_32bit_format(mask).count('0')]}" \
                         f"{'1' * get_32bit_format(mask).count('0')}"
    return get_ip_from_32bit_format(broadcast_ip_32bit)

def get_next_network_ip(network_ip, mask):
    broadcast_ip_32bit = get_32bit_format(get_broadcast_ip(network_ip, mask))
    next_network_ip_32bit = bin(int(broadcast_ip_32bit, 2) +
                                int("1", 2)).replace("0b", "").rjust(32, "0")
    return get_ip_from_32bit_format(next_network_ip_32bit)

def calculate_first_network(network_ip, prefix):
    ip_parts = network_ip.split(".")
    binary_ip = "".join(format(int(part), "08b") for part in ip_parts)
    binary_ip = binary_ip[:int(prefix)] + "0" * (32 - int(prefix))
    decimal_ip = ".".join(str(int(binary_ip[i:i + 8], 2)) for i in range(0, 32, 8))
    return str(decimal_ip)

def calculate_vlsm(network_ip, endpoint_numbers_per_network, prefix):
    subnets = []
    network_hosts = endpoint_numbers_per_network.split(",")
    length_of_subnets = []

    for hosts in network_hosts:
        if int(hosts) > 0:
            hosts = int(hosts) + 2
            length_of_subnets.append(power_bit_length(int(hosts)))

    length_of_subnets.sort(reverse=True)
    sum_all_hosts = sum(length_of_subnets)

    if is_empty(prefix):
        first_octet = int(network_ip.split(".")[0])

        if 1 <= first_octet < 128:
            if sum_all_hosts <= pow(2, 24):
                inject_data_to_dict(network_ip, length_of_subnets, subnets)
            else:
                print("El maximo de host excede el limite para una Red de Clase A.")

        elif 128 <= first_octet < 192:
            if sum_all_hosts <= pow(2, 16):
                inject_data_to_dict(network_ip, length_of_subnets, subnets)
            else:
                print("El maximo de host excede el limite para una Red de Clase B.")

        elif 192 <= first_octet < 224:
            if sum_all_hosts <= pow(2, 8):
                inject_data_to_dict(network_ip, length_of_subnets, subnets)
            else:
                print("El maximo de host excede el limite para una Red de Clase C.")

    else:
        if sum_all_hosts <= pow(2, 32 - int(prefix)):
            inject_data_to_dict(network_ip, length_of_subnets, subnets)
        else:
            print("La cantidad de hosts excede el límite máximo para la longitud de prefijo especificada.")

    return subnets

def inject_data_to_dict(network_ip, length_of_subnets, subnets):
    for network in length_of_subnets:
        hostbits = int(log2(network))
        prefix = 32 - hostbits
        mask = get_mask_from_prefix(prefix)

        subnets.append({
            "Dirección IP": network_ip,
            "Rango de IPs": f"{get_first_addressable_ip(network_ip)} - {get_last_addressable_ip(network_ip, mask)}",
            "Broadcast": get_broadcast_ip(network_ip, mask),
            "Mascara de subred": mask,
            "Prefijo": f"/{prefix}",
            "Hosts direccionables": pow(2, hostbits) - 2
        })
        network_ip = get_next_network_ip(network_ip, mask)

def main():
    network_ip = input("Ingrese la dirección de red: ")
    endpoint_numbers_per_network = input("Ingrese el número de hosts por red: ")
    prefix = input("Ingrese el prefijo de la máscara de subred (deje vacío para el valor predeterminado según la dirección de red): ")

    if is_correct_network_address(network_ip) and is_correct_endpoint_numbers_per_network(endpoint_numbers_per_network):
        first_network_ip = calculate_first_network(network_ip, prefix)

        if is_correct_network_address(first_network_ip):
            subnets = calculate_vlsm(first_network_ip, endpoint_numbers_per_network, prefix)

            for subnet in subnets:
                print("\nInformación de la subred (Subnet Information)")
                print("Dirección de Red:", subnet["Dirección IP"])
                print("Prefijo:", subnet["Prefijo"])
                print("Rango de IPs:", subnet["Rango de IPs"])
                print("Dirección de Broadcast:", subnet["Broadcast"])
                print("Máscara de Subred:", subnet["Mascara de subred"])
                print("Hosts direccionables:", subnet["Hosts direccionables"])
        else:
            print("Primera IP calculada inválida.")
    else:
        print("Entrada inválida")

if __name__ == "__main__":
    main()