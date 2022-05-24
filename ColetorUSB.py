# import serial.tools.list_ports
# ports = serial.tools.list_ports.comports()
# for port, desc, hwid in sorted(ports):
#        print("{}: {} [{}]".format(port, desc, hwid))


class ColetorUSB:
    def __init__(self, BoundRate=0, Timeout=0, Port=-1):
        self.bundrate = BoundRate
        self.timeout = Timeout
        self.port = Port

    # Mensagens recebidas (Deve casar com o formato esperado), e numero de mixers
    def CapturaComando(self):
        print(
            "Simulacao port ",
            self.port,
            ": AUMENTAR MIXER [0], DIMINUIR MIXER [1]",
        )
        entradasFormatadas = [["F", "0", "0.9"], ["F", "1", "0.1"]]
        nMixers = len(entradasFormatadas)
        return [entradasFormatadas, nMixers]

    def SetPort(self, Port):
        self.port = Port
