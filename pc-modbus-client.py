from pymodbus.client import ModbusTcpClient
import time


def main():
    client = ModbusTcpClient('172.16.160.83', port=5020)  # Adres IP Pico
    try:
        while True:
            # Odczyt 3 rejestrów od adresu 0
            response = client.read_holding_registers(0, count=4, slave=1)
            if not response.isError():
                print("Rejestry:", response.registers)
            else:
                print("Błąd:", response)

            time.sleep(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()