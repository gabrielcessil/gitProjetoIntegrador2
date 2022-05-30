import VolumeController as vc
import GUIcontroller as guic
import ColetorUSB as cusb
import time


# Coordenacao entre interface, saida de som e coletor usb
class ModMixer:
    def __init__(self):
        self.mixerGUI = guic.GUI()
        self.usbColetor = cusb.ColetorUSB()
        self.mixer = vc.Mixer("User")
                
        
    # Traduz o sinal de index do modulo para um nome de aplicacao, e entao para uma fonte de som especificada
    def InterpretaSinal_ModuleIndex(self, moduleIndex_signal):
        # Casting da mensagem
        try:
            moduleIndex = int(moduleIndex_signal)
        except:
            moduleIndex = -1

        # Traduz o index do mixer fisico para um nome de fonte
        nomeFonte = self.mixerGUI.getNomeAplicacao(moduleIndex)

        # Mixer responde quais fontes pertencem este nome
        fontes = self.mixer.GetFontePorNome(nomeFonte)
        return fontes

    # Traduz sinal de magnitude do volume 
    def InterpretaSinal_Percentual(self, percentual_signal):
        try:
            percentual = float(percentual_signal)
        except:
            raise Exception(
                "Erro de comunicacao <Sinal desconhecido>: percentual = "
                + percentual_signal
            )
        return percentual

    # Traduz sinal de cabecalho para informacao conhecida pela interface
    def InterpretaSinal_Cabecalho(self, cabecalho_signal):
        if cabecalho_signal == "F":
            cabecalho = self.mixer.Cabecalhos["Fonte"]
        elif cabecalho_signal == "G":
            cabecalho = self.mixer.Cabecalhos["Geral"]
        else:
            cabecalho = self.mixer.Cabecalhos["Iddle"]
        return cabecalho

    # Traduz sinais dos modulos para informacoes pertinentes a interface
    def InterpretaSinais(self, Sinais):
        SinaisInterpretados = []
        for [cabecalho_signal, moduleIndex_signal, percentual_signal] in Sinais:
            comando = self.InterpretaSinal_Cabecalho(cabecalho_signal)
            fontes = self.InterpretaSinal_ModuleIndex(moduleIndex_signal)
            percentual = self.InterpretaSinal_Percentual(percentual_signal)
            SinaisInterpretados.append([comando, fontes, percentual])
        return SinaisInterpretados

                
    # Comunica com usb e interpreta sinais 
    def RecebeSinaisModulos(self):
        # Escuta por mixers fisicos para criar layout
        Sinais, nModules = self.usbColetor.CapturaComando()
        # Traduz sinais de index para comandos conhecidos pela GUI
        comandos = self.InterpretaSinais(Sinais)
        return(comandos, nModules)

    def AtuaEstadoJanela(self, estadoJanela, Comandos):
        if(estadoJanela == self.mixerGUI.dicEstadosJanela["Iniciando"]):
            print("Janela inicial")
            time.sleep(1)
        
        elif(estadoJanela == self.mixerGUI.dicEstadosJanela["Ativado"]):
            print("Janela de menus")
            # Atua na interface grafica
            self.mixerGUI.AtualizaVisibilidades(self.mixer)
            # Atua nas fontes de som
            self.mixer.OperaComandos(Comandos)

        else:
            print("Janela de aguardo por modulos")
            time.sleep(0.005)

    def loop(self):
        # Controle de iteracoes
        i = 0

        # Comunica e interpreta sinais do usb
        Comandos,nModules = self.RecebeSinaisModulos()

        # Atualiza informacoes pertinentes a GUI 
        self.mixerGUI.AtualizaInfos(nModules, self.mixer)

        # Define o estado inicial como uma tela de Boas-Vindas
        estadoJanela = self.mixerGUI.IniciaJanela()

        while(True):
            print("\n", i) #PARA TESTE
            i = (i+1)%5000 #PARA TESTE

            # Atua conforme o estado que identifica
            self.AtuaEstadoJanela(estadoJanela, Comandos)
                
            # Comunica e interpreta sinais de comando vindos dos modulos
            Comandos,nModules = self.RecebeSinaisModulos()

            # Atualiza informacoes pertinentes a GUI 
            self.mixerGUI.AtualizaInfos(nModules, self.mixer)

            # Atualiza layout da GUI
            estadoJanela = self.mixerGUI.AtualizaJanela()

            # Captura interacao do usuario com a janela
            if(not self.mixerGUI.InteracaoComUsuario()):
                self.mixerGUI.EncerraJanela()
                break;
            

