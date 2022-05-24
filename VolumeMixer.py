from numpy import double
import pulsectl


class Mixer:
    def __init__(self, name="User"):
        self.pulse = pulsectl.Pulse(name)
        self.Cabecalhos = {"Iddle": 0, "Fonte": 1, "Geral": 2}
        self.NumeroMixers = 0

    def __del__(self):
        self.pulse.close()

    def GetFontePorNome(self, nome):
        sink_inputs = self.pulse.sink_input_list()
        Fontes = []
        for sink in sink_inputs:
            if sink.proplist["application.name"] == nome:
                Fontes.append(sink)
        return Fontes

    def GetNumeroMixers(self):
        return self.NumeroMixers

    def GetVolume(self, appName):
        # Volume das fontes de mesmo app deveriam ser as mesmas
        fontes = self.GetFontePorNome(appName)
        if fontes:
            return fontes[0].volume.value_flat
        else:
            return 0

    def GetNomeFontes(self):
        NomeFontes = []
        sink_inputs = self.pulse.sink_input_list()
        if sink_inputs:
            for sink in sink_inputs:
                nome = sink.proplist["application.name"]
                try:
                    i = NomeFontes.index(nome)
                except:
                    NomeFontes.append(nome)
        return NomeFontes

    def ExibeSinks(self):
        sink_inputs = self.pulse.sink_input_list()
        if sink_inputs:
            print("\nLista de fontes de saida:")
            for sink, i in zip(sink_inputs, range(len(sink_inputs))):
                print(
                    "[{0}] {1}(id:{2})".format(
                        i,
                        sink.proplist["application.name"],
                        sink.proplist["application.process.id"],
                    )
                )
        else:
            print("\nSem Saidas de Audio")
        print()

    # Traduz o index do mixer para a fonte que controla
    def GetFontePorIndex(self, MixerIndex):
        fonte = []
        if self.EhFonteValida(MixerIndex):
            sink_inputs = self.pulse.sink_input_list()
            try:

                fonteIndex = self.GetFontePorNome
                # O indice do mixer nao condiz necessariamente com o indice da fonte
                fonte = sink_inputs[MixerIndex]
            except:
                fonte = []
        return fonte

    def getVolumeFonte(self, fonte):
        return fonte.volume.value_flat

    def ComunicaUSB(self):
        print("COMANDO FISICO: AUMENTAR MIXER [0], DIMINUIR MIXER [1]")
        return [["F", "0", "0.9"], ["F", "1", "0.1"]]

    def ContaNumeroMixers(self, SinaisComandos):
        self.NumeroMixers = len(SinaisComandos)
        print("Numero de mixers conectados: ", self.NumeroMixers)

    def CapturaComando(self):

        # Captura as entradas usb em forma de lista de [canal, percentual]
        SinaisComandos = self.ComunicaUSB()

        # Faz contagem de mixers usados na mensagem
        self.ContaNumeroMixers(SinaisComandos)

        return SinaisComandos

    def VerificaNovoVolume(self, vol):
        if vol >= 1.2:
            print("\nVolume Maximo atingido")
            return 1.2
        elif vol <= 0:
            print("\nFontes Mutadas")
            return 0
        else:
            return vol

    def MudaVolumeFonte(self, volumeLevel_percent, fonte):
        newVol = self.VerificaNovoVolume(volumeLevel_percent)
        new_volume = pulsectl.PulseVolumeInfo(newVol, len(fonte.volume.values))
        self.pulse.volume_set(fonte, new_volume)

    def MuteAll(self):
        for fonte in self.pulse.sink_list():
            newVol = 0
            self.MudaVolumeFonte(volumeLevel_percent=newVol, fonte=fonte)

    def MuteFonte(self, fonte):
        if fonte:
            newVol = 0
            self.MudaVolumeFonte(volumeLevel_percent=newVol, fonte=fonte)

    def MudaVolumeGeral(self, volume_percent):
        for fonte in self.pulse.sink_list():
            newVol = volume_percent
            self.MudaVolumeFonte(volumeLevel_percent=newVol, fonte=fonte)

    # Verifica se o index esta no range corrento
    def EhFonteValida(self, fonteIndex):
        if fonteIndex < 0:
            print("Fonte invalida")
            return False
        else:
            sink_inputs = self.pulse.sink_input_list()
            nFontes = len(sink_inputs)
            if fonteIndex >= nFontes:
                print("Fonte invalida")
                return False
            else:
                return True

    def OperaComandos(self, SinaisInterpretados):

        for [cabecalho, fontes, volume_percent] in SinaisInterpretados:
            if cabecalho == self.Cabecalhos["Fonte"]:
                for fonte in fontes:
                    self.MudaVolumeFonte(volume_percent, fonte)

            elif cabecalho == self.Cabecalhos["Geral"]:
                self.MudaVolumeGeral(volume_percent)
