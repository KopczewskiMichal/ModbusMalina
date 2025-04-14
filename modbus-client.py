import usocket as socket
import network
import struct
import time

class ModbusTCPClient:
    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.sock = None
        
    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        
    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            
    def _create_request(self, slave_id, function_code, address, count):
        # Nagłówek Modbus TCP
        transaction_id = 0x0001
        protocol_id = 0x0000
        length = 0x0006
        
        # PDU Modbus
        unit_id = slave_id
        func_code = function_code
        start_addr = address
        reg_count = count
        
        return struct.pack('>HHHBBHH', 
                         transaction_id,
                         protocol_id,
                         length,
                         unit_id,
                         func_code,
                         start_addr,
                         reg_count)
    
    def _parse_response(self, data):
        # Parsowanie odpowiedzi Modbus TCP
        if len(data) < 9:
            raise ValueError("Nieprawidłowa odpowiedź Modbus")
            
        # Odczyt nagłówka
        _, _, length, unit_id, func_code = struct.unpack('>HHHBB', data[:9])
        
        # Sprawdzenie błędów
        if func_code & 0x80:
            error_code = data[8]
            raise Exception(f"Błąd Modbus: {error_code}")
            
        # Odczyt danych (dla funkcji 0x03)
        values = []
        byte_count = data[8]
        for i in range(9, 9 + byte_count, 2):
            values.append(struct.unpack('>H', data[i:i+2])[0])
            
        return values
        
    def read_holding_registers(self, slave_id, address, count):
        """Odczyt rejestrów holdingowych (funkcja 0x03)"""
        try:
            if not self.sock:
                self.connect()
                
            # Stwórz żądanie
            request = self._create_request(slave_id, 0x03, address, count)
            self.sock.send(request)
            
            # Odczytaj odpowiedź
            response = self.sock.recv(1024)
            
            # Parsuj odpowiedź
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Błąd: {e}")
            self.close()
            return None

# Przykład użycia z WiFi:
def main():
    # 1. Inicjalizacja WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Łączenie z WiFi...")
        wlan.connect('H2volt', 'Zielona!Sowa')
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Połączono z WiFi:", wlan.ifconfig())

    # 2. Użycie klienta Modbus
    client = ModbusTCPClient('172.16.160.64')  # Adres urządzenia Modbus
    try:
        # Odczyt 5 rejestrów od adresu 0
        while(True):
            registers = client.read_holding_registers(slave_id=1, address=0, count=5)
            print("Odczytane rejestry:", registers)
            time.sleep(1)
    finally:
        print("Nie udało się połączyć z serverem modbus")
        client.close()

if __name__ == '__main__':
    main()