
# Classe responsavel pela coleta de dados da porta USB,
#  formatacao da mensagem, e definicao do numero de modulos conectados

class ColetorUSB:
    def __init__(self, BoundRate=0, Timeout=0, Port=-1):
        self.bundrate = BoundRate
        self.timeout = Timeout
        self.port = Port

        #PARA TESTE
        self.i = 0
        self.percent = 0.1

    # Mensagens recebidas (Retorno deve casar com o formato esperado), e numero de mixers
    def CapturaComando(self):
        imax =5000
        percentMIN = 0.1

        entradasFormatadas = []
        self.i = (self.i+10) % imax
        self.percent = percentMIN + (self.i/imax)
        if(self.i < imax/5):
            print(
                "Simulacao port ",
                self.port,
                ": SILENCIO",
            )
        else:  

            print(
                "Simulacao port ",
                self.port,
                ": AUMENTAR MIXER [0], DIMINUIR MIXER [1]",
            )
            entradasFormatadas = [["F", "0", str(self.percent)], ["F", "1", "0.1"]]


        nMixers = len(entradasFormatadas)
        return [entradasFormatadas, nMixers]

    def SetPort(self, Port):
        self.port = Port
